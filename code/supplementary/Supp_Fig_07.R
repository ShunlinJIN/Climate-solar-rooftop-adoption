# Supplementary Figure 7: search evidence and policy robustness.
# Complete figure-specific code; no separate helper file is required.
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

  # ──────────────────────────────────────────────────────────────────────────
  # 1. Dependencies, input paths and figure style
  # ──────────────────────────────────────────────────────────────────────────

  required <- c("ggplot2", "ggprism", "patchwork")
  missing <- required[!vapply(required, requireNamespace, logical(1), quietly = TRUE)]
  if (length(missing)) {
    stop("Missing R packages: ", paste(missing, collapse = ", "),
         ". In R, run install.packages(c(\"ggplot2\", \"ggprism\", \"patchwork\"), repos=\"https://cloud.r-project.org\").")
  }
  suppressPackageStartupMessages({library(ggplot2); library(ggprism); library(patchwork)})

  plot_locations <- function(script_dir, supplementary = FALSE) {
    root <- normalizePath(file.path(script_dir, ".."), winslash = "/", mustWork = TRUE)
    list(main = file.path(root, "data"), supplementary = file.path(root, "data"),
         output = file.path(root, "output"))
  }

  read_source <- function(path, columns) {
    if (!file.exists(path)) stop("Missing source data: ", path)
    x <- read.csv(path, check.names = FALSE, stringsAsFactors = FALSE, fileEncoding = "UTF-8-BOM")
    if (length(setdiff(columns, names(x)))) stop("Missing columns in ", path, ": ", paste(setdiff(columns, names(x)), collapse = ", "))
    x
  }

  bin_labels <- function(x) {
    # Put the common unit in the axis title to leave space between the nine bins.
    x <- sub("°C$", "", x)
    x <- sub("^-5-0$", "−5–0", x)
    x <- sub("^≤-5$", "≤−5", x)
    gsub("(?<=[0-9])-(?=[0-9])", "–", x, perl = TRUE)
  }

  figure_theme <- function() {
    theme_prism(base_size = 10, base_family = "sans", base_fontface = "plain") +
      theme(axis.text = element_text(size = 8, colour = "black", face = "plain"),
            axis.text.x = element_text(size = 6.8),
            axis.title = element_text(size = 9.5, colour = "black", face = "plain"),
            axis.title.x = element_text(margin = margin(t = 5)),
            axis.title.y = element_text(margin = margin(r = 5)),
            axis.ticks = element_line(linewidth = 0.3),
            axis.line = element_line(linewidth = 0.3),
            axis.ticks.length = grid::unit(2, "pt"),
            legend.position = "top", legend.title = element_blank(),
            legend.text = element_text(size = 7.3),
            legend.key.size = grid::unit(9, "pt"),
            legend.key.width = grid::unit(12, "pt"),
            legend.spacing.x = grid::unit(2, "pt"),
            legend.spacing.y = grid::unit(0, "pt"),
            legend.margin = margin(0, 0, 2, 0),
            legend.box.spacing = grid::unit(2, "pt"),
            plot.tag = element_text(size = 11, face = "bold"),
            plot.tag.position = "topleft", plot.margin = margin(4, 5, 3, 4))
  }

  offset_y_axis <- function() {
    if ("cap" %in% names(formals(ggplot2::guide_axis))) {
      ggplot2::guide_axis(cap = "both")
    } else {
      ggprism::guide_prism_offset()
    }
  }

  coefficient_scale <- function(limits = c(-0.04, 0.16), breaks = seq(-0.04, 0.16, .04)) {
    scale_y_continuous(name = "Estimated Coefficients", limits = limits,
                       breaks = breaks, expand = expansion(mult = c(0.045, 0.02)),
                       guide = offset_y_axis())
  }

  temperature_scale <- function(labels, title = "Temperature bins (°C)") {
    scale_x_continuous(name = title, breaks = seq_along(labels), labels = bin_labels(labels),
                       limits = c(0.55, length(labels) + 0.45), expand = c(0, 0))
  }

  bin_histogram <- function(d, tag, limits = c(-0.04, .16), breaks = seq(-.04, .16, .04), fill = "lightblue") {
    d$x <- seq_len(nrow(d))
    line <- ggplot(d, aes(x = x, y = estimate)) +
      geom_ribbon(aes(ymin = lo, ymax = hi, fill = "95% CI"), alpha = .5) +
      geom_line(aes(colour = "Estimated Coefficients"), linewidth = .55) +
      geom_point(aes(colour = "Estimated Coefficients"), size = 1.6) +
      geom_hline(yintercept = 0, linetype = "dashed", linewidth = .3) +
      coefficient_scale(limits, breaks) + temperature_scale(d$label) +
      scale_colour_manual(values = c("Estimated Coefficients" = "deepskyblue4")) +
      scale_fill_manual(values = c("95% CI" = fill)) + figure_theme() +
      theme(axis.text.x = element_blank(), axis.title.x = element_blank(),
            axis.ticks.x = element_blank(), axis.line.x = element_blank(),
            plot.margin = margin(4, 5, 0, 4)) + labs(tag = tag)
    bars <- ggplot(d, aes(x = x, y = count)) +
      geom_col(fill = "grey70", width = .50) + temperature_scale(d$label) +
      scale_y_continuous(expand = expansion(mult = c(0, .05))) + figure_theme() +
      theme(axis.line.y = element_blank(), axis.ticks.y = element_blank(),
            axis.text.y = element_blank(), axis.title.y = element_blank(),
            legend.position = "none", plot.margin = margin(0, 5, 3, 4))
    (line / bars) + plot_layout(heights = c(3.3, .8))
  }

  # ──────────────────────────────────────────────────────────────────────────
  # 2. Draw search evidence and policy comparisons
  # ──────────────────────────────────────────────────────────────────────────

  policy_panels <- function(dat) {
    cdat <- dat[dat$panel == "c", ]; cdat <- cdat[order(cdat$x_order), ]
    stopifnot(nrow(cdat) == 17)
    pc <- ggplot(cdat, aes(x = x_order, y = estimate)) +
      geom_ribbon(aes(ymin = ci_lower, ymax = ci_upper, fill = "95% CI"), alpha = .5) +
      geom_line(aes(colour = "Estimated Coefficients"), linewidth = .55) +
      geom_point(aes(colour = "Estimated Coefficients"), size = 1.5) +
      geom_vline(xintercept = cdat$x_order[cdat$x_label == "-1"], linetype = "dashed", linewidth = .3) +
      geom_hline(yintercept = 0, linetype = "dashed", linewidth = .3) + coefficient_scale() +
      scale_x_continuous(name = "Pilot month", breaks = cdat$x_order, labels = cdat$x_label,
                         limits = c(.55, 17.45), expand = c(0, 0)) +
      scale_colour_manual(values = c("Estimated Coefficients" = "deepskyblue4")) +
      scale_fill_manual(values = c("95% CI" = "lightblue")) + figure_theme() +
      theme(axis.text.x = element_text(size = 7.2)) + labs(tag = "c")
    d <- dat[dat$panel == "d", ]
    levels <- c("Baseline", "In Pilot Policy Counties", "No Pilot", "No Subsidy", "Pre-COVID")
    stopifnot(nrow(d) == 45, all(table(d$series) == 9))
    d$series <- factor(d$series, levels = levels)
    base <- d[d$series == "Baseline", ]; base <- base[order(base$x_order), ]
    rest <- d[d$series != "Baseline", ]
    colours <- c("Baseline" = "deepskyblue4", "In Pilot Policy Counties" = "red", "No Pilot" = "orange", "No Subsidy" = "purple", "Pre-COVID" = "blue")
    types <- c("Baseline" = "blank", "In Pilot Policy Counties" = "dotdash", "No Pilot" = "dotted", "No Subsidy" = "twodash", "Pre-COVID" = "dashed")
    shapes <- c("Baseline" = 22, "In Pilot Policy Counties" = 21, "No Pilot" = 24, "No Subsidy" = 23, "Pre-COVID" = 18)
    pd <- ggplot() +
      geom_ribbon(data = base, aes(x = x_order, ymin = ci_lower, ymax = ci_upper, fill = "Baseline CI"), alpha = .5) +
      geom_line(data = rest, aes(x = x_order, y = estimate, colour = series, linetype = series), linewidth = .5) +
      geom_point(data = d, aes(x = x_order, y = estimate, colour = series, shape = series), fill = "white", size = 1.7, stroke = .55) +
      geom_hline(yintercept = 0, linetype = "dashed", linewidth = .3) + coefficient_scale() + temperature_scale(base$x_label) +
      scale_fill_manual(values = c("Baseline CI" = "lightblue")) +
      scale_colour_manual(values = colours, breaks = levels, drop = FALSE) +
      scale_linetype_manual(values = types, breaks = levels, drop = FALSE) +
      scale_shape_manual(values = shapes, breaks = levels, drop = FALSE) + figure_theme() +
      guides(fill = guide_legend(order = 1),
             colour = guide_legend(nrow = 3, byrow = TRUE, order = 2),
             linetype = guide_legend(nrow = 3, byrow = TRUE, order = 2),
             shape = guide_legend(nrow = 3, byrow = TRUE, order = 2)) +
      theme(legend.text = element_text(size = 6.3)) + labs(tag = "d")
    list(c = pc, d = pd)
  }

  search_panels <- function(series, bins) {
    series$date <- as.Date(series$week_date); series <- series[order(series$date), ]
    stopifnot(nrow(bins) == 9, !anyNA(series$date), !anyDuplicated(series$date))
    try(Sys.setlocale("LC_TIME", "C"), silent = TRUE)
    pa <- ggplot(series) +
      geom_line(aes(x = date, y = baidu_monthly, colour = "Baidu search (monthly)"), linewidth = .50) +
      geom_point(aes(x = date, y = baidu_weekly, colour = "Baidu search (weekly)"), size = .85, shape = 1, alpha = .6, stroke = .3) +
      geom_line(aes(x = date, y = avg_temperature_c * 25, colour = "Avg Temperature"), linewidth = .3, alpha = .8) +
      scale_x_date(name = "Week", date_labels = "%b %Y", date_breaks = "4 months",
                   limits = range(series$date), expand = expansion(mult = c(.02, 0))) +
      scale_y_continuous(name = "Baidu Search", breaks = seq(0, 3000, 500), guide = "axis",
                         sec.axis = sec_axis(~ . / 25, name = "Temperature (°C)", breaks = seq(0, 120, 20), guide = "axis")) +
      scale_colour_manual(values = c("Avg Temperature" = "#00CED1", "Baidu search (monthly)" = "red", "Baidu search (weekly)" = "blue"),
                           breaks = c("Avg Temperature", "Baidu search (monthly)", "Baidu search (weekly)")) + figure_theme() +
      guides(colour = guide_legend(nrow = 2, byrow = TRUE, override.aes = list(alpha = 1))) +
      theme(axis.text.x = element_text(size = 7.2, angle = 45, hjust = 1, vjust = 1),
            axis.title.y.right = element_text(margin = margin(l = 4)),
            legend.text = element_text(size = 6.8)) + labs(tag = "a")
    pb <- bin_histogram(data.frame(label = bins$temperature_bin, estimate = bins$estimate,
                                   lo = bins$ci_low, hi = bins$ci_high, count = bins$days_in_bin),
                         "b", limits = c(-.1, .3), breaks = seq(-.1, .3, .1), fill = "deepskyblue")
    list(a = pa, b = pb)
  }

  # ──────────────────────────────────────────────────────────────────────────
  # 3. Export and assemble Supplementary Figure 7
  # ──────────────────────────────────────────────────────────────────────────

  save_figure <- function(plot, output_dir, stem, width, height) {
    if (!capabilities("cairo")) stop("This R installation needs Cairo support to export SVG and PDF.")
    dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
    for (ext in c("svg", "pdf", "png")) {
      dest <- file.path(output_dir, paste0(stem, ".", ext))
      if (ext == "svg") ggsave(dest, plot, width = width, height = height, units = "in", device = grDevices::svg, bg = "white")
      if (ext == "pdf") ggsave(dest, plot, width = width, height = height, units = "in", device = grDevices::cairo_pdf, bg = "white")
      if (ext == "png") ggsave(dest, plot, width = width, height = height, units = "in", dpi = 600, device = "png", type = "cairo", bg = "white")
      message(normalizePath(dest, winslash = "/", mustWork = TRUE))
    }
  }

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
