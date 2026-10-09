# Shared plotting helpers for current Supplementary Figs. 17-18.

suppressPackageStartupMessages({
  library(data.table)
  library(ggplot2)
  library(cowplot)
  library(grid)
})

BLUE <- "#1f77b4"
ORANGE <- "#ff7f0e"
BLACK <- "#222222"

get_script_dir <- function() {
  x <- grep("^--file=", commandArgs(trailingOnly = FALSE), value = TRUE)
  if (length(x) == 1L) {
    return(dirname(normalizePath(sub("^--file=", "", x), winslash = "/")))
  }
  normalizePath(getwd(), winslash = "/")
}

CODE_DIR <- get_script_dir()
ROOT_DIR <- normalizePath(
  file.path(CODE_DIR, ".."),
  winslash = "/",
  mustWork = FALSE
)
DATA_DIR <- file.path(ROOT_DIR, "data")
OUTPUT_DIR <- file.path(ROOT_DIR, "output")
dir.create(OUTPUT_DIR, recursive = TRUE, showWarnings = FALSE)

theme_reference <- function() {
  theme_classic(base_size = 11) +
    theme(
      axis.line = element_blank(),
      axis.ticks = element_line(colour = BLACK, linewidth = 0.45),
      axis.ticks.length = unit(0.13, "cm"),
      axis.text = element_text(
        family = "sans",
        face = "plain",
        colour = BLACK,
        size = 9
      ),
      axis.title = element_text(
        family = "sans",
        face = "plain",
        colour = BLACK,
        size = 10
      ),
      legend.position = "top",
      legend.title = element_blank(),
      legend.text = element_text(family = "sans", size = 9),
      legend.key.width = unit(1.5, "cm"),
      legend.background = element_rect(fill = "white", colour = NA),
      panel.grid = element_blank(),
      plot.title = element_text(
        family = "sans",
        face = "plain",
        size = 11,
        hjust = 0.5,
        margin = margin(b = 5)
      ),
      plot.tag = element_text(
        family = "sans",
        face = "bold",
        size = 15,
        colour = BLACK,
        hjust = 0,
        vjust = 1
      ),
      plot.tag.position = c(0.015, 0.985),
      plot.background = element_rect(fill = "white", colour = NA),
      panel.background = element_rect(fill = "white", colour = NA),
      plot.margin = margin(15, 16, 14, 18)
    )
}

pretty_nonnegative_spec <- function(high, n = 5L, padding = 0.08) {
  if (!is.finite(high) || high <= 0) high <- 1
  upper_raw <- high * (1 + padding)
  breaks <- pretty(c(0, upper_raw), n = n)
  breaks <- breaks[breaks >= 0]
  upper <- max(breaks[breaks <= max(breaks)])
  if (upper < upper_raw) upper <- max(breaks)
  list(
    breaks = breaks[breaks <= upper],
    limits = c(0, upper)
  )
}

add_separated_axes <- function(plot_object, x_limits, y_limits) {
  x_gap <- 0.025 * diff(x_limits)
  y_gap <- 0.040 * diff(y_limits)

  plot_object +
    annotate(
      "segment",
      x = x_limits[1] + x_gap,
      xend = x_limits[2],
      y = y_limits[1],
      yend = y_limits[1],
      linewidth = 0.55,
      colour = BLACK
    ) +
    annotate(
      "segment",
      x = x_limits[1],
      xend = x_limits[1],
      y = y_limits[1] + y_gap,
      yend = y_limits[2],
      linewidth = 0.55,
      colour = BLACK
    ) +
    coord_cartesian(
      xlim = x_limits,
      ylim = y_limits,
      expand = FALSE,
      clip = "off"
    )
}

save_public_figure <- function(plot, number, width, height) {
  ggsave(
    file.path(OUTPUT_DIR, sprintf("Supplementary_Fig_%02d.pdf", number)),
    plot,
    width = width,
    height = height,
    units = "in",
    device = cairo_pdf,
    bg = "white",
    limitsize = FALSE
  )
  ggsave(
    file.path(OUTPUT_DIR, sprintf("Supplementary_Fig_%02d.png", number)),
    plot,
    width = width,
    height = height,
    units = "in",
    dpi = 600,
    bg = "white",
    limitsize = FALSE
  )
  message("Supplementary Fig. ", number, " reproduced.")
}
