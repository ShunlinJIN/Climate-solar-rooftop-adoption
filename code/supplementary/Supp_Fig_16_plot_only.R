# Supplementary Fig. 16:
# Comparability of households with complete hourly archives and the full daily panels.
# Plot-only reproduction from aggregate kernel-density curves.

args <- commandArgs(trailingOnly = FALSE)
script_arg <- grep("^--file=", args, value = TRUE)
script_dir <- if (length(script_arg) == 1L) {
  dirname(normalizePath(sub("^--file=", "", script_arg), winslash = "/"))
} else {
  normalizePath(getwd(), winslash = "/")
}
source(file.path(script_dir, "_supp_fig16_17_common.R"))

d <- fread(file.path(DATA_DIR, "supp_fig16_comparability_density.csv"))

required <- c(
  "panel", "title", "x_label", "sample", "value", "density",
  "overlap", "x_lower", "x_upper", "y_upper"
)
absent <- setdiff(required, names(d))
if (length(absent)) {
  stop("Fig. 16 plotting input is missing: ", paste(absent, collapse = ", "))
}

d[, sample := factor(
  sample,
  levels = c(
    "Complete hourly-record households",
    "Full daily panel"
  )
)]

make_panel <- function(panel_code, show_legend = FALSE) {
  z <- d[panel == panel_code]
  if (!nrow(z)) stop("Missing Fig. 16 panel ", panel_code)

  meta <- unique(
    z[, .(title, x_label, overlap, x_lower, x_upper, y_upper)]
  )
  if (nrow(meta) != 1L) stop("Inconsistent metadata in panel ", panel_code)

  x_limits <- c(meta$x_lower, meta$x_upper)
  y_limits <- c(0, meta$y_upper)

  p <- ggplot(
    z,
    aes(
      x = value,
      y = density,
      colour = sample,
      linetype = sample
    )
  ) +
    geom_line(linewidth = 0.90) +
    scale_colour_manual(
      values = c(
        "Complete hourly-record households" = ORANGE,
        "Full daily panel" = BLUE
      )
    ) +
    scale_linetype_manual(
      values = c(
        "Complete hourly-record households" = "solid",
        "Full daily panel" = "dashed"
      )
    ) +
    scale_x_continuous(expand = expansion(mult = 0)) +
    scale_y_continuous(expand = expansion(mult = 0)) +
    annotate(
      "text",
      x = x_limits[1] + 0.75 * diff(x_limits),
      y = y_limits[1] + 0.90 * diff(y_limits),
      label = sprintf("Overlap = %.2f", meta$overlap),
      size = 3.6
    ) +
    labs(
      tag = panel_code,
      title = meta$title,
      x = meta$x_label,
      y = "Density"
    ) +
    theme_reference()

  if (!show_legend) {
    p <- p + theme(legend.position = "none")
  }

  add_separated_axes(p, x_limits, y_limits)
}

p_a_legend <- make_panel("a", show_legend = TRUE)

shared_legend <- cowplot::get_legend(
  p_a_legend + theme(legend.position = "top")
)

p_a <- p_a_legend + theme(legend.position = "none")
p_b <- make_panel("b")
p_c <- make_panel("c")
p_d <- make_panel("d")

row1 <- cowplot::plot_grid(p_a, p_b, ncol = 2, align = "hv", axis = "tblr")
row2 <- cowplot::plot_grid(p_c, p_d, ncol = 2, align = "hv", axis = "tblr")

body <- cowplot::plot_grid(
  row1,
  row2,
  ncol = 1,
  rel_heights = c(1, 1)
)

fig <- cowplot::plot_grid(
  shared_legend,
  body,
  ncol = 1,
  rel_heights = c(0.09, 1)
)

save_public_figure(fig, 16, 10.8, 8.4)
