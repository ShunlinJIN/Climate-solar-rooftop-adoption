# Supplementary Fig. 18:
# Mean hourly electricity-flow profiles.
#
# Corrected plot-only reproduction:
# - reads the existing aggregate source used for Supplementary Fig. 26;
# - restores the blue/orange series colors and panel-specific legends;
# - repositions panel tags so they do not overlap y-axis tick labels.
#
# No household-hour microdata are read and no model is re-estimated.

args <- commandArgs(trailingOnly = FALSE)
script_arg <- grep("^--file=", args, value = TRUE)

script_dir <- if (length(script_arg) == 1L) {
  dirname(normalizePath(sub("^--file=", "", script_arg), winslash = "/"))
} else {
  normalizePath(getwd(), winslash = "/")
}

source(file.path(script_dir, "_supp_fig17_18_common.R"))

d <- fread(
  file.path(
    DATA_DIR,
    "supp_fig26_hourly_flow_composition.csv"
  )
)

required <- c(
  "system", "hour",
  "pv_generation", "total_load",
  "pv_to_load", "grid_to_load", "pv_to_grid",
  "pv_to_battery", "battery_to_load"
)

absent <- setdiff(required, names(d))
if (length(absent)) {
  stop(
    "Existing Fig. 26 aggregate input is missing: ",
    paste(absent, collapse = ", ")
  )
}

d[, hour := as.integer(hour)]

if (
  nrow(d[system == "RRPV-only"]) != 24L ||
  nrow(d[system == "RRPV-BS"]) != 24L ||
  !all(sort(unique(d$hour)) == 0:23)
) {
  stop(
    "The aggregate hourly-flow source must contain ",
    "24 clock-hour rows for each system."
  )
}

only <- d[system == "RRPV-only"][order(hour)]
bs   <- d[system == "RRPV-BS"][order(hour)]

make_two_line_panel <- function(
  first,
  second,
  label_first,
  label_second,
  panel_tag,
  title_text
) {

  z <- rbindlist(list(
    data.table(
      hour = 0:23,
      series = label_first,
      value = as.numeric(first)
    ),
    data.table(
      hour = 0:23,
      series = label_second,
      value = as.numeric(second)
    )
  ))

  z[, series := factor(
    series,
    levels = c(label_first, label_second)
  )]

  # Dynamic named vector is essential: names must equal the actual legend labels.
  series_colours <- setNames(
    c(BLUE, ORANGE),
    c(label_first, label_second)
  )

  y_spec <- pretty_nonnegative_spec(
    max(z$value, na.rm = TRUE),
    n = 5L,
    padding = 0.08
  )

  p <- ggplot(
    z,
    aes(
      x = hour,
      y = value,
      colour = series,
      group = series
    )
  ) +
    geom_line(linewidth = 0.85) +
    scale_colour_manual(
      values = series_colours,
      breaks = c(label_first, label_second),
      labels = c(label_first, label_second),
      drop = FALSE
    ) +
    scale_x_continuous(
      breaks = c(0, 4, 8, 12, 16, 20, 23),
      expand = expansion(mult = 0)
    ) +
    scale_y_continuous(
      breaks = y_spec$breaks,
      expand = expansion(mult = 0)
    ) +
    labs(
      tag = panel_tag,
      title = title_text,
      x = "Hour of day",
      y = "Mean hourly flow (kWh)",
      colour = NULL
    ) +
    theme_reference() +
    theme(
      # Current SI shows a separate legend above each panel.
      legend.position = "top",
      legend.direction = "horizontal",
      legend.justification = "center",
      legend.text = element_text(
        family = "sans",
        size = 8.5,
        colour = BLACK
      ),
      legend.key.width = unit(1.05, "cm"),
      legend.spacing.x = unit(0.18, "cm"),
      legend.margin = margin(t = 0, r = 0, b = 2, l = 0),
      # Put panel letters outside the plotting region rather than on top of ticks.
      plot.tag.position = "topleft",
      plot.tag = element_text(
        family = "sans",
        face = "bold",
        size = 15,
        colour = BLACK,
        hjust = 0,
        vjust = 1
      ),
      plot.margin = margin(10, 14, 12, 18)
    )

  add_separated_axes(
    p,
    c(-0.8, 23.8),
    y_spec$limits
  )
}

p_a <- make_two_line_panel(
  only$total_load,
  bs$total_load,
  "RRPV-only",
  "RRPV-BS",
  "a",
  "Household load"
)

p_b <- make_two_line_panel(
  only$grid_to_load,
  bs$grid_to_load,
  "RRPV-only",
  "RRPV-BS",
  "b",
  "Grid electricity supplied to load"
)

p_c <- make_two_line_panel(
  only$pv_to_grid,
  bs$pv_to_grid,
  "RRPV-only",
  "RRPV-BS",
  "c",
  "PV electricity exported to grid"
)

p_d <- make_two_line_panel(
  bs$pv_to_battery,
  bs$battery_to_load,
  "PV charged into battery",
  "Battery supplied to load",
  "d",
  "RRPV-BS battery operation"
)

row1 <- cowplot::plot_grid(
  p_a, p_b,
  ncol = 2,
  align = "hv",
  axis = "tblr"
)

row2 <- cowplot::plot_grid(
  p_c, p_d,
  ncol = 2,
  align = "hv",
  axis = "tblr"
)

fig <- cowplot::plot_grid(
  row1,
  row2,
  ncol = 1,
  rel_heights = c(1, 1)
)

save_public_figure(
  fig,
  18,
  width = 10.8,
  height = 8.4
)
