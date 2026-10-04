# Supplementary Figure 7: search evidence and policy robustness.
local({
  source_files <- vapply(sys.frames(), function(f) {
    if (exists("ofile", envir = f, inherits = FALSE)) as.character(get("ofile", envir = f)) else ""
  }, character(1))
  source_files <- source_files[nzchar(source_files)]
  script_file <- if (length(source_files)) tail(source_files, 1) else {
    arg <- grep("^--file=", commandArgs(FALSE), value = TRUE)
    if (length(arg) != 1) stop("Run this file with Rscript or source(...).")
    sub("^--file=", "", arg)
  }
  script_dir <- dirname(normalizePath(script_file, winslash = "/", mustWork = TRUE))
  helper <- file.path(script_dir, "_figure1_supp7.R")
  if (!file.exists(helper)) stop("Missing shared plotting file: _figure1_supp7.R")
  source(helper, local = TRUE, encoding = "UTF-8")
  paths <- plot_locations(script_dir, supplementary = TRUE)
  series <- read_source(file.path(paths$supplementary, "supp_fig07_search_temperature.csv"),
                        c("week_date", "baidu_weekly", "baidu_monthly", "avg_temperature_c"))
  bins <- read_source(file.path(paths$supplementary, "supp_fig07_temperature_bin_estimates.csv"),
                      c("temperature_bin", "estimate", "ci_low", "ci_high", "days_in_bin"))
  dat <- read_source(file.path(paths$supplementary, "supp_fig07_policy_estimates.csv"),
                     c("panel", "series", "x_order", "x_label", "estimate", "ci_lower", "ci_upper"))
  search <- search_panels(series, bins)
  policy <- policy_panels(dat)
  figure <- wrap_plots(list(search$a, search$b, policy$c, policy$d), ncol = 2,
                      widths = c(1, 1), heights = c(1.08, 1))
  save_figure(figure, paths$output, "Supplementary_Fig_07", width = 7.2, height = 6.7)
})
