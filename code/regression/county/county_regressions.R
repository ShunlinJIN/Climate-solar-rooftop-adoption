# County adoption models, main-text Equations (1)-(3).
paths <- list(
  installations = "D:/solar_install/county_monthly_installations.csv",
  sample = "D:/solar_install/county_sample.csv",
  weather = "D:/weather/county_daily_weather.parquet",
  covariates = "D:/county_covariates/county_monthly_covariates.csv",
  characteristics = "D:/county_covariates/county_characteristics.csv",
  output = "D:/solar_results/main_regressions/county"
)
analysis_start <- as.Date("2018-01-01")
analysis_end <- as.Date("2022-12-01")
event_date <- as.Date("2021-09-01")
event_window <- c(-8L, 14L) # Reporting window; pre-period times <= -8 are pooled.
event_temperature_controls <- FALSE
expected_counties <- c(rrpv_only = 335L, rrpv_bs = 91L)

temperature_bins <- c("le_neg5", "neg5_0", "0_5", "5_10", "10_15",
                      "15_20", "20_25", "25_30", "gt30")
temperature_terms <- paste0("temp_", setdiff(temperature_bins, "15_20"))
weather_terms <- c("direct_solar_radiation_kwh_m2_day", "rainfall_daily_mm", "relative_humidity_pct", "wind_speed_ms")
control_terms <- c(weather_terms, paste0(weather_terms, "_sq"),
                   "pm25", "income_per_capita", "pv_firms")
heterogeneity_variables <- c("temp_mean_20yr", "temp_mean_5yr", "temp_variability_interannual",
                            "temp_variability_intraannual", "slope_degrees", "income_2017")

for (package in c("data.table", "fixest")) {
  if (!requireNamespace(package, quietly = TRUE)) stop("Required R package: ", package)
}
library(data.table)

read_table <- function(path) {
  if (!file.exists(path)) stop("Input file not found: ", path, call. = FALSE)
  ext <- tolower(tools::file_ext(path))
  out <- switch(ext,
    csv = data.table::fread(path, colClasses = c(county_code = "character")),
    rds = data.table::as.data.table(readRDS(path)),
    parquet = {
      if (!requireNamespace("arrow", quietly = TRUE)) stop("Install arrow to read Parquet inputs.")
      data.table::as.data.table(arrow::read_parquet(path))
    }, stop("Supported input formats: CSV, RDS, Parquet."))
  if ("county_code" %in% names(out)) {
    out[, county_code := as.character(county_code)]
    if (anyNA(out$county_code) || any(!grepl("^[1-9][0-9]{5}$", out$county_code)))
      stop("Invalid county_code in ", path)
  }
  out
}

require_columns <- function(d, columns, label) {
  missing <- setdiff(columns, names(d))
  if (length(missing)) stop(label, " is missing: ", paste(missing, collapse = ", "))
}

unique_keys <- function(d, keys, label) {
  require_columns(d, keys, label)
  if (anyNA(d[, ..keys]) || anyDuplicated(d[, ..keys])) stop(label, ": missing or duplicate keys.")
}

finite_columns <- function(d, columns, label) {
  require_columns(d, columns, label)
  bad <- columns[!vapply(d[, ..columns], function(x) is.numeric(x) && all(is.finite(x)), logical(1))]
  if (length(bad)) stop(label, ": missing/nonfinite/nonnumeric values in ", paste(bad, collapse = ", "))
}

parse_date <- function(x, label, monthly = FALSE) {
  if (inherits(x, "Date")) out <- as.Date(x) else if (inherits(x, "POSIXct")) {
    if (any(!is.finite(as.numeric(x))) || any(as.numeric(x) %% 86400 != 0))
      stop(label, " timestamps must represent midnight UTC dates.")
    out <- as.Date(x, tz = "UTC")
  } else {
    if (!is.character(x) || anyNA(x) || any(!grepl("^[0-9]{4}-[0-9]{2}-[0-9]{2}$", x)))
      stop(label, " must contain ISO dates YYYY-MM-DD.")
    out <- as.Date(x, format = "%Y-%m-%d")
    if (anyNA(out) || any(format(out, "%Y-%m-%d") != x)) stop("Invalid dates in ", label)
  }
  if (anyNA(out)) stop("Missing dates in ", label)
  if (monthly && any(format(out, "%d") != "01")) stop(label, " must use the first day of each month.")
  out
}

month_index <- function(x) as.integer(format(x, "%Y")) * 12L + as.integer(format(x, "%m"))

join_required <- function(left, right, keys, label) {
  unique_keys(right, keys, label)
  right <- data.table::copy(right)
  right[, join_present__ := TRUE]
  out <- merge(left, right, by = keys, all.x = TRUE, sort = FALSE)
  if (anyNA(out$join_present__)) stop("Missing matching rows in ", label)
  out[, join_present__ := NULL]
  out
}

fit_model <- function(d, terms, fixed_effects = "county_code + year_month") {
  finite_columns(d, c("log_installations", terms), "Regression sample")
  f <- as.formula(paste("log_installations ~", paste(terms, collapse = " + "), "|", fixed_effects))
  model <- fixest::feols(f, data = d, vcov = ~county_code, fixef.rm = "none",
    ssc = fixest::ssc(K.adj = TRUE, K.fixef = "nonnested", G.adj = TRUE,
                      G.df = "min", t.df = "min"))
  if (stats::nobs(model) != nrow(d)) stop("The regression dropped observations.")
  model
}

linear_result <- function(model, terms, weights = rep(1, length(terms)), d, label) {
  b <- stats::coef(model)
  if (!all(terms %in% names(b))) stop("Unidentified required coefficients: ", paste(setdiff(terms, names(b)), collapse = ", "))
  V <- stats::vcov(model)[terms, terms, drop = FALSE]
  variance <- as.numeric(t(weights) %*% V %*% weights)
  if (!is.finite(variance) || variance <= 0) stop("Invalid contrast variance: ", label)
  se <- sqrt(variance)
  estimate <- sum(weights * b[terms])
  groups <- data.table::uniqueN(d$county_code)
  df <- groups - 1L
  if (df < 1L) stop("At least two county clusters are required.")
  statistic <- estimate / se
  data.table::data.table(term = label, estimate = estimate, std_error = se,
    conf_low = estimate - stats::qt(.975, df) * se,
    conf_high = estimate + stats::qt(.975, df) * se,
    statistic = statistic, df = df, p_value = 2 * stats::pt(abs(statistic), df, lower.tail = FALSE),
    observations = nrow(d), counties = groups)
}

save_fit <- function(model, d, terms, name) {
  saveRDS(model, file.path(paths$output, paste0(name, ".rds")))
  result <- data.table::rbindlist(lapply(terms, function(term) linear_result(model, term, d = d, label = term)))
  data.table::fwrite(result, file.path(paths$output, paste0(name, ".csv")))
  invisible(result)
}

build_panel <- function() {
  sample <- read_table(paths$sample)
  require_columns(sample, c("county_code", "rrpv_only", "rrpv_bs"), "County sample")
  unique_keys(sample, "county_code", "County sample")
  sample <- sample[, .(county_code, rrpv_only, rrpv_bs)]
  for (flag in c("rrpv_only", "rrpv_bs")) {
    if (anyNA(sample[[flag]]) || any(!sample[[flag]] %in% 0:1)) stop("Sample flags must be 0 or 1.")
    if (sum(sample[[flag]]) != expected_counties[[flag]]) stop("Unexpected county count for ", flag)
  }
  sample <- sample[rrpv_only == 1L | rrpv_bs == 1L]
  if (any(!substr(sample$county_code, 1L, 2L) %in% c("21", "32", "35", "42")))
    stop("County sample must be in Liaoning, Jiangsu, Fujian or Hubei.")
  months <- seq(analysis_start, analysis_end, by = "month")
  panel <- data.table::CJ(county_code = sample$county_code, month = months, sorted = TRUE)
  panel <- join_required(panel, sample, "county_code", "County sample")

  installs <- read_table(paths$installations)
  require_columns(installs, c("county_code", "month", "rrpv_only_installations", "rrpv_bs_installations"), "Installations")
  installs[, month := parse_date(month, "Installations month", TRUE)]
  installs <- installs[, .(county_code, month, rrpv_only_installations, rrpv_bs_installations)]
  unique_keys(installs, c("county_code", "month"), "Installations")
  panel <- join_required(panel, installs, c("county_code", "month"), "Installations")
  for (system in c("rrpv_only", "rrpv_bs")) {
    v <- paste0(system, "_installations")
    target <- panel[get(system) == 1L]
    finite_columns(target, v, paste(system, "installations"))
    if (any(target[[v]] <= 0 | target[[v]] != floor(target[[v]])))
      stop("Monthly installations must be positive integers for log(Install): ", system)
  }

  weather <- read_table(paths$weather)
  required_weather <- c("county_code", "date", "daily_mean_temp", weather_terms)
  require_columns(weather, required_weather, "Daily county weather")
  weather <- weather[, ..required_weather]
  weather[, date := parse_date(date, "Weather date")]
  weather_start <- seq(analysis_start, by = "-1 month", length.out = 3L)[3L]
  weather_end <- seq(analysis_end, by = "1 month", length.out = 2L)[2L] - 1L
  weather <- weather[county_code %in% sample$county_code & date >= weather_start & date <= weather_end]
  unique_keys(weather, c("county_code", "date"), "Daily county weather")
  expected <- data.table::CJ(county_code = sample$county_code,
                            date = seq(weather_start, weather_end, by = "day"))
  if (nrow(weather) != nrow(expected) || nrow(expected[!weather, on = .(county_code, date)]))
    stop("Daily county weather must cover every county-day, including the two preceding months.")
  finite_columns(weather, "daily_mean_temp", "Daily county weather")
  finite_columns(weather[date >= analysis_start], weather_terms, "Daily county weather")
  if (weather[date >= analysis_start, any(direct_solar_radiation_kwh_m2_day < 0 | relative_humidity_pct < 0 | relative_humidity_pct > 100 | wind_speed_ms < 0)])
    stop("Weather variable outside its physical range.")
  weather[, month := as.Date(format(date, "%Y-%m-01"))]
  weather[, bin := as.character(cut(daily_mean_temp,
    breaks = c(-Inf, -5, 0, 5, 10, 15, 20, 25, 30, Inf), labels = temperature_bins, right = TRUE))]
  monthly <- weather[, c(setNames(lapply(temperature_bins, function(b) sum(bin == b)), paste0("temp_", temperature_bins)),
                         lapply(.SD, mean)), by = .(county_code, month), .SDcols = weather_terms]
  data.table::setorder(monthly, county_code, month)
  for (term in temperature_terms) {
    for (lag in 1:2) monthly[, (paste0(term, "_lag", lag)) := data.table::shift(get(term), lag), by = county_code]
  }
  panel <- join_required(panel, monthly[month >= analysis_start], c("county_code", "month"), "Monthly weather")
  for (term in weather_terms) panel[, (paste0(term, "_sq")) := get(term)^2]

  covariates <- read_table(paths$covariates)
  require_columns(covariates, c("county_code", "month", "pm25", "income_per_capita", "pv_firms"), "Monthly covariates")
  covariates[, month := parse_date(month, "Covariate month", TRUE)]
  covariates <- covariates[, .(county_code, month, pm25, income_per_capita, pv_firms)]
  panel <- join_required(panel, covariates, c("county_code", "month"), "Monthly covariates")
  finite_columns(panel, c(control_terms, temperature_terms, paste0(temperature_terms, "_lag1"), paste0(temperature_terms, "_lag2")), "County analysis panel")
  if (any(panel$pm25 < 0 | panel$income_per_capita <= 0 | panel$pv_firms < 0 | panel$pv_firms != floor(panel$pv_firms)))
    stop("Invalid PM2.5, income or PV-firm counts.")

  characteristics <- read_table(paths$characteristics)
  require_columns(characteristics, c("county_code", heterogeneity_variables), "County characteristics")
  characteristics <- characteristics[, c("county_code", heterogeneity_variables), with = FALSE]
  unique_keys(characteristics, "county_code", "County characteristics")
  only <- join_required(sample[rrpv_only == 1L, .(county_code)], characteristics, "county_code", "County characteristics")
  finite_columns(only, heterogeneity_variables, "County characteristics")
  for (term in heterogeneity_variables) {
    only[, (paste0(term, "_high")) := as.integer(get(term) > stats::median(get(term)))]
  }
  # Characteristics are required for the RRPV-only heterogeneity sample.
  panel <- merge(panel, only, by = "county_code", all.x = TRUE, sort = FALSE)
  panel[, year_month := format(month, "%Y-%m")]
  data.table::setorder(panel, county_code, month)
  panel
}

estimate_county_models <- function(panel) {
  for (system in c("rrpv_only", "rrpv_bs")) {
    d <- data.table::copy(panel[get(system) == 1L])
    d[, log_installations := log(get(paste0(system, "_installations")))]
    model <- fit_model(d, c(temperature_terms, control_terms))
    save_fit(model, d, temperature_terms, paste0("eq1_", system))
  }

  d <- data.table::copy(panel[rrpv_only == 1L])
  d[, log_installations := log(rrpv_only_installations)]
  cumulative <- list()
  for (K in 1:2) {
    lag_terms <- unlist(lapply(seq_len(K), function(k) paste0(temperature_terms, "_lag", k)))
    model <- fit_model(d, c(temperature_terms, lag_terms, control_terms))
    save_fit(model, d, c(temperature_terms, lag_terms), paste0("eq2_lags_", K))
    cumulative[[K]] <- data.table::rbindlist(lapply(temperature_terms, function(term) {
      result <- linear_result(model, c(term, paste0(term, "_lag", seq_len(K))), d = d, label = term)
      result[, lag_horizon := K]
      result
    }))
  }
  data.table::fwrite(data.table::rbindlist(cumulative), file.path(paths$output, "eq2_cumulative_effects.csv"))

  contrasts <- list()
  for (dimension in heterogeneity_variables) {
    flag <- paste0(dimension, "_high")
    d[, high := get(flag)]
    if (data.table::uniqueN(d$high) != 2L) stop("Heterogeneity split has fewer than two groups: ", dimension)
    for (group in 0:1) {
      dg <- d[high == group]
      model <- fit_model(dg, c(temperature_terms, control_terms))
      save_fit(model, dg, "temp_gt30", paste0("fig2_", dimension, if (group) "_high" else "_low"))
    }
    # Fully interact all slopes and calendar fixed effects to reproduce separate group fits.
    base_terms <- c(temperature_terms, control_terms)
    interaction_terms <- paste0(base_terms, "_high_interaction")
    for (j in seq_along(base_terms)) d[, (interaction_terms[j]) := get(base_terms[j]) * high]
    d[, group_year_month := interaction(high, year_month, drop = TRUE)]
    joint <- fit_model(d, c(base_terms, interaction_terms), "county_code + group_year_month")
    direction <- if (dimension == "slope_degrees") -1 else 1
    contrast <- linear_result(joint, "temp_gt30_high_interaction", weights = direction,
                             d = d, label = dimension)
    contrast[, contrast := if (direction == -1) "low_minus_high" else "high_minus_low"]
    contrasts[[dimension]] <- contrast
    saveRDS(joint, file.path(paths$output, paste0("fig2_", dimension, "_joint.rds")))
  }
  data.table::fwrite(data.table::rbindlist(contrasts), file.path(paths$output, "fig2_group_contrasts.csv"))

  event_months <- setdiff(seq(event_window[1], event_window[2]), -1L)
  event_controls <- c(if (event_temperature_controls) temperature_terms, control_terms)
  for (system in c("rrpv_only", "rrpv_bs")) {
    d <- data.table::copy(panel[get(system) == 1L])
    d[, treated := as.integer(substr(county_code, 1L, 2L) == "21")]
    d[, event_time_raw := month_index(month) - month_index(event_date)]
    # Retain all observations. Estimate later event months separately so that
    # unreported post-event observations do not enter the omitted reference.
    d[, event_time := ifelse(treated == 1L,
                            pmax(event_time_raw, event_window[1]), -1L)]
    if (data.table::uniqueN(d$treated) != 2L) stop("Rationing analysis requires both treatment and comparison counties.")
    if (!(-1L %in% d[treated == 1L, event_time])) stop("The rationing sample lacks the treated reference month -1.")
    d[, log_installations := log(get(paste0(system, "_installations")))]
    later_months <- sort(unique(d[treated == 1L & event_time > event_window[2], event_time]))
    fitted_months <- c(event_months, later_months)
    event_names <- ifelse(fitted_months < 0, paste0("event_m", abs(fitted_months)), paste0("event_p", fitted_months))
    for (j in seq_along(fitted_months)) d[, (event_names[j]) := as.integer(treated == 1L & event_time == fitted_months[j])]
    model <- fit_model(d, c(event_names, event_controls))
    result <- save_fit(model, d, event_names, paste0("eq3_rationing_", system))
    result[, event_month := fitted_months[match(term, event_names)]]
    result[, event_category := ifelse(event_month == event_window[1],
                                     paste0("<=", event_window[1]), as.character(event_month))]
    result[, reported := event_month %in% event_months]
    data.table::fwrite(result, file.path(paths$output, paste0("eq3_rationing_", system, "_all_periods.csv")))
    data.table::fwrite(result[reported == TRUE], file.path(paths$output, paste0("eq3_rationing_", system, ".csv")))
  }
}

panel <- build_panel()
dir.create(paths$output, recursive = TRUE, showWarnings = FALSE)
estimate_county_models(panel)
writeLines(capture.output(sessionInfo()), file.path(paths$output, "sessionInfo.txt"))
message("County regression results written to ", paths$output)
