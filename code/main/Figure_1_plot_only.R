# Figure 1: contemporaneous and cumulative temperature effects on adoption.
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
  source(file.path(script_dir, "_figure1_supp7.R"), local = TRUE, encoding = "UTF-8")
  paths <- plot_locations(script_dir)
  dat <- read_source(file.path(paths$main, "figure1_plot_data.csv"),
                     c("panel", "series", "x_order", "x_label", "estimate", "ci_lower", "ci_upper", "count"))
  panels <- adoption_main(dat)
  figure <- (panels$a | panels$b) + plot_layout(widths = c(1, 1))
  save_figure(figure, paths$output, "Figure_1", width = 7.2, height = 3.2)
})
