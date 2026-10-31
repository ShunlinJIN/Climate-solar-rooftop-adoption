# Main daily consumption regressions: Equation (4), Figure 4.
suppressPackageStartupMessages({
  library(data.table)
  library(fixest)
})

rebound_config <- list(
  electricity = "D:/household_electricity/household_daily_electricity.parquet",
  weather = "D:/weather/county_daily_weather.parquet",
  income_groups = "D:/county_covariates/rebound_county_income_groups.csv",
  output = "D:/solar_results/main_regressions/rebound",
  start = as.Date("2018-06-01"),
  end = as.Date("2020-12-31")
)

read_input <- function(path) {
  if (!file.exists(path)) stop("Input not found: ", path)
  if (tolower(tools::file_ext(path)) == "parquet") {
    if (!requireNamespace("arrow", quietly = TRUE)) stop("Package 'arrow' is required for Parquet inputs.")
    return(as.data.table(arrow::read_parquet(path)))
  }
  if (tolower(tools::file_ext(path)) == "csv") return(fread(path))
  stop("Expected a CSV or Parquet input: ", path)
}

require_columns <- function(x, columns, label) {
  absent <- setdiff(columns, names(x))
  if (length(absent)) stop(label, ": missing columns: ", paste(absent, collapse = ", "))
}

validate_keys <- function(x, columns, label) {
  if (anyNA(x[, ..columns])) stop(label, ": missing key values.")
  if (anyDuplicated(x, by = columns)) stop(label, ": duplicate keys.")
}

parse_day <- function(x, label) {
  if (inherits(x, "Date")) return(as.IDate(x))
  if (inherits(x, "POSIXct")) {
    if (any(!is.finite(as.numeric(x))) || any(as.numeric(x) %% 86400 != 0))
      stop(label, ": timestamps must represent midnight UTC dates.")
    return(as.IDate(as.Date(x, tz = "UTC")))
  }
  if (!is.character(x) || anyNA(x) || any(!grepl("^[0-9]{4}-[0-9]{2}-[0-9]{2}$", x))) {
    stop(label, ": dates must be Date values or ISO YYYY-MM-DD strings.")
  }
  out <- as.IDate(x)
  if (anyNA(out) || any(format(out, "%Y-%m-%d") != x)) stop(label, ": invalid date.")
  out
}

normalise_county <- function(x) {
  out <- as.character(x)
  if (anyNA(out) || any(!grepl("^[1-9][0-9]{5}$", out))) stop("county_code must contain six-digit administrative codes.")
  out
}

weather_terms <- c("daily_mean_temp", "direct_solar_radiation_kwh_m2_day", "rainfall_daily_mm",
                   "relative_humidity_pct", "wind_speed_ms")
flow_terms <- c("pv_generation_kwh", "direct_pv_use_kwh", "grid_import_kwh", "battery_to_load_kwh")
electricity_columns <- c("household_id", "county_code", "date", "system_type", "holiday", flow_terms)
electricity <- read_input(rebound_config$electricity)
require_columns(electricity, electricity_columns, "Electricity")
electricity <- electricity[, ..electricity_columns]
electricity[, `:=`(household_id = as.character(household_id), county_code = normalise_county(county_code),
                   date = parse_day(date, "Electricity"))]
validate_keys(electricity, c("household_id", "date"), "Electricity")
if (any(!nzchar(electricity$household_id))) stop("Empty household_id.")
if (anyNA(electricity$system_type) || any(!electricity$system_type %chin% c("RRPV-only", "RRPV-BS"))) stop("Unknown system_type.")
if (electricity[, any(uniqueN(county_code) != 1L | uniqueN(system_type) != 1L), by = household_id]$V1 |> any()) {
  stop("Each household must have one county and one system type.")
}
for (v in flow_terms) {
  if (!is.numeric(electricity[[v]])) stop("Non-numeric electricity field: ", v)
  if (any(!is.na(electricity[[v]]) & !is.finite(electricity[[v]]))) stop("Infinite electricity value: ", v)
  if (any(electricity[[v]] < 0, na.rm = TRUE)) stop("Negative electricity value: ", v)
}
if (!is.numeric(electricity$holiday) && !is.logical(electricity$holiday)) stop("holiday must be 0 or 1.")
if (any(!electricity$holiday %in% c(0, 1))) stop("holiday must be observed and coded 0 or 1.")
if (electricity[system_type == "RRPV-only", any(is.na(battery_to_load_kwh) | battery_to_load_kwh != 0)]) {
  stop("RRPV-only battery_to_load_kwh must be zero.")
}

# Construct exact calendar-day lags before selecting the analysis period.
setorder(electricity, household_id, date)
for (k in 1:3) {
  name <- paste0("pv_generation_lag", k)
  electricity[, (name) := shift(pv_generation_kwh, k), by = household_id]
  electricity[, (name) := fifelse(!is.na(shift(date, k)) & as.integer(date - shift(date, k)) == k,
                                  get(name), NA_real_), by = household_id]
}
electricity <- electricity[date >= rebound_config$start & date <= rebound_config$end]
if (!nrow(electricity)) stop("No electricity observations in the analysis period.")
electricity[, total_load_kwh := direct_pv_use_kwh + grid_import_kwh + battery_to_load_kwh]

weather <- read_input(rebound_config$weather)
weather_columns <- c("county_code", "date", weather_terms)
require_columns(weather, weather_columns, "Weather")
weather <- weather[, ..weather_columns]
weather[, `:=`(county_code = normalise_county(county_code), date = parse_day(date, "Weather"))]
validate_keys(weather, c("county_code", "date"), "Weather")
for (v in weather_terms) {
  if (!is.numeric(weather[[v]]) || any(!is.na(weather[[v]]) & !is.finite(weather[[v]]))) stop("Invalid weather field: ", v)
}
weather[, weather_record := TRUE]
panel <- merge(electricity, weather, by = c("county_code", "date"), all.x = TRUE, sort = FALSE)
if (anyNA(panel$weather_record)) stop("County-day weather keys are missing.")

groups <- read_input(rebound_config$income_groups)
require_columns(groups, c("county_code", "system_type", "income_2017", "income_group"), "Income groups")
groups <- groups[, .(county_code, system_type, income_2017, income_group)]
groups[, county_code := normalise_county(county_code)]
validate_keys(groups, c("county_code", "system_type"), "Income groups")
if (anyNA(groups$income_group) || any(!groups$income_group %chin% c("low", "middle", "high"))) stop("Invalid income_group.")
if (!is.numeric(groups$income_2017) || any(!is.finite(groups$income_2017)) || any(groups$income_2017 < 0)) stop("Invalid income_2017.")
panel <- merge(panel, groups, by = c("county_code", "system_type"), all.x = TRUE, sort = FALSE)
if (anyNA(panel$income_group)) stop("County income groups are missing.")
for (s in unique(panel$system_type)) {
  g <- unique(panel[system_type == s, .(county_code, income_2017, income_group)])
  if (!all(c("low", "middle", "high") %chin% g$income_group)) stop("All three county-income groups are required for ", s)
  if (max(g[income_group == "low", income_2017]) > min(g[income_group == "middle", income_2017]) ||
      max(g[income_group == "middle", income_2017]) > min(g[income_group == "high", income_2017])) stop("Income groups are not ordered by 2017 income.")
}
panel[, `:=`(year = as.integer(format(date, "%Y")), year_month = format(date, "%Y-%m"),
             weekend = as.integer(as.integer(format(date, "%u")) >= 6L))]
panel[, household_year := interaction(household_id, year, drop = TRUE)]
generation_terms <- c("pv_generation_kwh", paste0("pv_generation_lag", 1:3))
rhs <- c(generation_terms, weather_terms, paste0("I(", weather_terms, "^2)"), "holiday", "weekend")
formula_main <- as.formula(paste("total_load_kwh ~", paste(rhs, collapse = " + "), "| household_year + year_month"))
required_numeric <- c("total_load_kwh", generation_terms, weather_terms, "holiday", "weekend")
panel[, complete_observation := Reduce(`&`, lapply(.SD, is.finite)), .SDcols = required_numeric]
sample_log <- panel[, .(input_rows = .N, complete_rows = sum(complete_observation),
                        omitted_rows = sum(!complete_observation)), by = .(system_type, income_group)]
panel <- panel[complete_observation == TRUE]

estimate <- function(x, system, group) {
  if (!nrow(x)) stop("Empty regression sample: ", system, "/", group)
  households <- uniqueN(x$household_id)
  if (households < 3L) stop("Fewer than three households: ", system, "/", group)
  fit <- feols(formula_main, data = x, vcov = ~household_id, fixef.rm = "none",
               ssc = ssc(K.adj = TRUE, K.fixef = "nonnested", G.adj = TRUE,
                         G.df = "min", t.df = "min"))
  b <- coef(fit)
  V <- vcov(fit)
  if (!all(generation_terms %in% names(b))) stop("A PV-generation coefficient is unidentified: ", system, "/", group)
  if (any(!is.finite(b)) || any(!is.finite(V))) stop("Nonfinite regression estimates.")
  degrees <- households - 1L
  critical <- qt(0.975, df = degrees)
  coefficients <- data.table(term = names(b), estimate = unname(b), std_error = sqrt(diag(V)))
  coefficients[, `:=`(t_statistic = estimate / std_error,
                       p_value = 2 * pt(-abs(estimate / std_error), df = degrees),
                       ci_lower = estimate - critical * std_error, ci_upper = estimate + critical * std_error)]
  total <- sum(b[generation_terms])
  total_variance <- sum(V[generation_terms, generation_terms, drop = FALSE])
  if (!is.finite(total_variance) || total_variance < 0) stop("Invalid cumulative-effect variance.")
  total_se <- sqrt(total_variance)
  coefficients <- rbind(coefficients, data.table(term = "total_rebound_effect", estimate = total,
    std_error = total_se, t_statistic = total / total_se,
    p_value = 2 * pt(-abs(total / total_se), df = degrees),
    ci_lower = total - critical * total_se, ci_upper = total + critical * total_se))
  coefficients[, `:=`(system_type = system, income_group = group, observations = nobs(fit),
                       households = households, counties = uniqueN(x$county_code), degrees_freedom = degrees)]
  covariance <- as.data.table(as.table(V))
  setnames(covariance, c("term_1", "term_2", "covariance"))
  covariance[, `:=`(system_type = system, income_group = group)]
  list(coefficients = coefficients, covariance = covariance)
}

fits <- list()
for (s in c("RRPV-only", "RRPV-BS")) {
  fits[[paste(s, "all")]] <- estimate(panel[system_type == s], s, "all")
  for (g in c("low", "middle", "high")) fits[[paste(s, g)]] <- estimate(panel[system_type == s & income_group == g], s, g)
}
dir.create(rebound_config$output, recursive = TRUE, showWarnings = FALSE)
fwrite(rbindlist(lapply(fits, `[[`, "coefficients")), file.path(rebound_config$output, "rebound_coefficients.csv"))
fwrite(rbindlist(lapply(fits, `[[`, "covariance")), file.path(rebound_config$output, "rebound_covariance.csv"))
fwrite(sample_log, file.path(rebound_config$output, "rebound_sample_counts.csv"))
writeLines(capture.output(sessionInfo()), file.path(rebound_config$output, "session_info.txt"))
message("Daily rebound regressions completed: ", rebound_config$output)
