# Shared plotting helpers for Supplementary Figs. 11-14.

suppressPackageStartupMessages({
  library(ggplot2)
  library(ggprism)
  library(cowplot)
  library(dplyr)
  library(readr)
  library(grid)
})

BLUE <- "#147D9F"
GREY <- "#666666"
LIGHT_BLUE <- "#B9DEEA"

get_script_dir <- function() {
  x <- grep("^--file=", commandArgs(trailingOnly = FALSE), value = TRUE)
  if (length(x) == 1L) {
    return(dirname(normalizePath(sub("^--file=", "", x), winslash = "/")))
  }
  normalizePath(getwd(), winslash = "/")
}

CODE_DIR <- get_script_dir()
ROOT_DIR <- normalizePath(file.path(CODE_DIR, ".."), winslash = "/", mustWork = FALSE)
DATA_DIR <- file.path(ROOT_DIR, "data")
OUTPUT_DIR <- file.path(ROOT_DIR, "output")
dir.create(OUTPUT_DIR, recursive = TRUE, showWarnings = FALSE)

make_y_axis <- function(lower, upper, n = 6, include_zero = TRUE) {
  values <- c(lower, upper)
  values <- values[is.finite(values)]
  if (!length(values)) stop("No finite values available for y-axis.")
  if (include_zero) values <- c(values, 0)
  data_range <- range(values)
  span <- diff(data_range)
  if (!is.finite(span) || span <= 0) span <- max(abs(data_range), 1) * 0.20
  panel_min <- data_range[1] - 0.08 * span
  panel_max <- data_range[2] + 0.08 * span
  breaks <- pretty(c(panel_min, panel_max), n = n)
  breaks <- breaks[breaks >= panel_min & breaks <= panel_max]
  if (include_zero) breaks <- sort(unique(c(breaks, 0)))
  list(
    breaks = breaks,
    axis_min = min(breaks),
    axis_max = max(breaks),
    panel_min = panel_min,
    panel_max = panel_max
  )
}

extract_white_legend <- function(p) {
  cowplot::get_legend(
    p + theme(
      legend.position = "top",
      legend.background = element_rect(fill = "white", colour = NA),
      legend.box.background = element_rect(fill = "white", colour = NA),
      legend.key = element_rect(fill = "white", colour = NA),
      plot.background = element_rect(fill = "white", colour = NA)
    )
  )
}

theme_academic <- ggprism::theme_prism(base_size = 12.5) +
  theme(
    panel.border = element_blank(),
    panel.grid = element_blank(),
    axis.line.x = element_blank(),
    axis.line.y = element_blank(),
    axis.text = element_text(size = 10.8, colour = "black", face = "plain"),
    axis.title.x = element_text(size = 12.5, colour = "black", face = "plain", margin = margin(t = 8)),
    axis.title.y = element_text(size = 12.5, colour = "black", face = "plain", margin = margin(r = 8)),
    axis.ticks = element_line(linewidth = 0.50, colour = "black"),
    axis.ticks.length = unit(0.09, "cm"),
    legend.position = "top",
    legend.title = element_blank(),
    legend.text = element_text(size = 10.8, face = "plain"),
    legend.background = element_rect(fill = "white", colour = NA),
    legend.box.background = element_rect(fill = "white", colour = NA),
    legend.key = element_rect(fill = "white", colour = NA),
    panel.background = element_rect(fill = "white", colour = NA),
    plot.background = element_rect(fill = "white", colour = NA),
    plot.margin = margin(t = 6, r = 10, b = 7, l = 9)
  )

save_figure <- function(plot, number, width, height) {
  plot <- plot + theme(plot.background = element_rect(fill = "white", colour = NA))
  pdf <- file.path(OUTPUT_DIR, sprintf("Supplementary_Fig_%02d.pdf", number))
  png <- file.path(OUTPUT_DIR, sprintf("Supplementary_Fig_%02d.png", number))
  ggsave(pdf, plot, width = width, height = height, units = "in",
         device = grDevices::cairo_pdf, bg = "white", limitsize = FALSE)
  ggsave(png, plot, width = width, height = height, units = "in",
         dpi = 600, bg = "white", limitsize = FALSE)
  message("Supplementary Fig. ", number, " reproduced.")
}
