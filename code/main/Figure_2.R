# Figure 2: temperature, terrain and income heterogeneity.
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
  root <- dirname(script_dir)
  required <- c("ggplot2", "ggprism", "patchwork")
  missing <- required[!vapply(required, requireNamespace, logical(1), quietly = TRUE)]
  if (length(missing)) {
    stop("Missing R packages: ", paste(missing, collapse = ", "),
         ". In R, run install.packages(c(\"ggplot2\", \"ggprism\", \"patchwork\"), repos=\"https://cloud.r-project.org\").")
  }
  suppressPackageStartupMessages({library(ggplot2); library(ggprism); library(patchwork)})

  read_figure_source <- function(path, columns) {
    if (!file.exists(path)) stop("Missing source data: ", path)
    x <- read.csv(path, check.names = FALSE, stringsAsFactors = FALSE, fileEncoding = "UTF-8-BOM")
    if (length(setdiff(columns, names(x)))) stop("Missing columns in ", path, ": ", paste(setdiff(columns, names(x)), collapse = ", "))
    x
  }

  figure2_theme <- function() {
    theme_prism(base_size = 10, base_family = "sans", base_fontface = "plain") +
      theme(axis.text = element_text(size = 8, face = "plain", colour = "black"),
            axis.title = element_text(size = 9.3, face = "plain", colour = "black"),
            axis.title.x = element_text(margin = margin(t = 5)),
            axis.title.y = element_text(margin = margin(r = 5)),
            axis.line = element_line(linewidth = .35),
            axis.ticks = element_line(linewidth = .3),
            axis.ticks.length = grid::unit(2, "pt"),
            legend.position = "top", legend.title = element_blank(),
            legend.text = element_text(size = 7.2),
            legend.key.size = grid::unit(9, "pt"),
            legend.key.width = grid::unit(13, "pt"),
            legend.spacing.x = grid::unit(2, "pt"),
            legend.spacing.y = grid::unit(0, "pt"),
            legend.margin = margin(0, 0, 2, 0),
            legend.box.spacing = grid::unit(2, "pt"),
            plot.tag = element_text(size = 11, face = "bold"),
            plot.tag.position = "topleft", plot.margin = margin(4, 7, 4, 4))
  }

  add_pairwise_bracket <- function(plot, x1, x2, label) {
    force(x1); force(x2); force(label)
    y <- 14.6
    plot +
      annotate("segment", x = x1, xend = x1, y = y - .35, yend = y, colour = "darkgreen", linewidth = .4) +
      annotate("segment", x = x1, xend = x2, y = y, yend = y, colour = "darkgreen", linetype = "dashed", linewidth = .4) +
      annotate("segment", x = x2, xend = x2, y = y, yend = y - .35, colour = "darkgreen", linewidth = .4) +
      annotate("text", x = (x1 + x2) / 2, y = y + .55,
               label = sub("^p", "italic(p)", label), parse = TRUE, size = 2.7, colour = "black")
  }

  offset_y_axis <- function() {
    if ("cap" %in% names(formals(ggplot2::guide_axis))) {
      ggplot2::guide_axis(cap = "both")
    } else {
      ggprism::guide_prism_offset()
    }
  }

  subgroup_panel <- function(dat, tests, source_panel, tag, xlabel) {
    x <- dat[dat$panel == source_panel, ]; x <- x[order(x$x_order), ]
    contrast <- tests[tests$panel == source_panel, ]
    n_expected <- if (source_panel %in% c("a", "b")) 4L else 2L
    stopifnot(nrow(x) == n_expected, nrow(contrast) == n_expected / 2,
              all(is.finite(x$estimate)), all(x$ci_lower <= x$estimate), all(x$ci_upper >= x$estimate))
    labels <- x$x_label
    if (source_panel == "c") labels <- c("High\n(steeper)", "Low\n(flatter)")
    plot <- ggplot(x, aes(x = x_order, y = 100 * estimate)) +
      geom_col(aes(fill = "Estimated impacts"), width = .58, alpha = .8) +
      geom_errorbar(aes(ymin = 100 * ci_lower, ymax = 100 * ci_upper, colour = "95% CI"),
                    width = .11, linewidth = .4) +
      scale_x_continuous(name = xlabel, breaks = x$x_order, labels = labels,
                         limits = c(.4, nrow(x) + .6), expand = c(0, 0)) +
      scale_y_continuous(name = "Estimated impacts (%)", breaks = seq(0, 15, 3),
                         limits = c(0, 16.1), expand = expansion(mult = c(.045, 0)),
                         guide = offset_y_axis()) +
      scale_fill_manual(values = c("Estimated impacts" = "cyan4")) +
      scale_colour_manual(values = c("95% CI" = "black")) +
      guides(fill = guide_legend(order = 1), colour = guide_legend(order = 2)) +
      figure2_theme() + labs(tag = tag)
    for (i in seq_len(nrow(contrast))) {
      plot <- add_pairwise_bracket(plot, 2 * i - 1, 2 * i, contrast$p_label[i])
    }
    plot
  }

  save_figure2 <- function(plot, directory, stem, width, height) {
    if (!capabilities("cairo")) stop("This R installation needs Cairo support to export SVG and PDF.")
    dir.create(directory, recursive = TRUE, showWarnings = FALSE)
    for (ext in c("svg", "pdf", "png")) {
      file <- file.path(directory, paste0(stem, ".", ext))
      if (ext == "svg") ggsave(file, plot, width = width, height = height, units = "in", device = grDevices::svg, bg = "white")
      if (ext == "pdf") ggsave(file, plot, width = width, height = height, units = "in", device = grDevices::cairo_pdf, bg = "white")
      if (ext == "png") ggsave(file, plot, width = width, height = height, units = "in", dpi = 600, device = "png", type = "cairo", bg = "white")
      message(normalizePath(file, winslash = "/", mustWork = TRUE))
    }
  }
  dat <- read_figure_source(file.path(root, "data/figure2_plot_data.csv"),
                            c("panel", "x_order", "x_label", "estimate", "ci_lower", "ci_upper"))
  tests <- read_figure_source(file.path(root, "data/figure2_pairwise_tests.csv"), c("panel", "p_label"))
  panels <- list(
    subgroup_panel(dat, tests, "a", "a", "Historical average temperature"),
    subgroup_panel(dat, tests, "b", "b", "Historical temperature fluctuation"),
    subgroup_panel(dat, tests, "c", "c", "Land slope"),
    subgroup_panel(dat, tests, "d", "d", "Income level")
  )
  figure <- wrap_plots(panels, ncol = 2, guides = "collect") & theme(legend.position = "top")
  save_figure2(figure, file.path(root, "output"), "Figure_2", width = 7.2, height = 5.9)
})
