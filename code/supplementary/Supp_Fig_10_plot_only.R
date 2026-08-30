# Supplementary Fig. 10: Cross-province placebo event-study estimates
# of power-rationing effects.
#
# Plot-only reproduction from aggregate event-time coefficients and
# 95% confidence intervals.
#
# This version increases horizontal space and panel margins so that
# the Fujian x-axis title is not clipped in the exported figure.

args <- commandArgs(trailingOnly = FALSE)
script_arg <- grep("^--file=", args, value = TRUE)

script_dir <- if (length(script_arg) == 1L) {
  dirname(
    normalizePath(
      sub("^--file=", "", script_arg),
      winslash = "/"
    )
  )
} else {
  normalizePath(getwd(), winslash = "/")
}

source(file.path(script_dir, "_supp_fig09_10_common.R"))

# -------------------------------------------------------------------------
# Read current aggregate plotting input
# -------------------------------------------------------------------------

d <- fread(
  file.path(
    data_dir,
    "supp_fig10_cross_province_placebo.csv"
  )
)

required <- c(
  "pseudo_treated_province",
  "event_time",
  "estimate",
  "ci_lower",
  "ci_upper"
)

if (!all(required %in% names(d))) {
  stop("Fig. 10 input is missing required columns.")
}

expected_provinces <- c("Jiangsu", "Hubei", "Fujian")

if (!setequal(unique(d$pseudo_treated_province), expected_provinces)) {
  stop("Fig. 10 input must contain Jiangsu, Hubei, and Fujian.")
}

# -------------------------------------------------------------------------
# Build the three current Supplementary Fig. 10 panels
# -------------------------------------------------------------------------

p_a <- make_placebo_panel(
  d[pseudo_treated_province == "Jiangsu"],
  "Months relative to pseudo-event (Jiangsu)",
  "a",
  ymin = -0.02,
  ymax = 0.04
) +
  theme(
    plot.margin = unit(c(0.5, 0.75, 0.5, 0.55), "cm")
  )

p_b <- make_placebo_panel(
  d[pseudo_treated_province == "Hubei"],
  "Months relative to pseudo-event (Hubei)",
  "b",
  ymin = -0.02,
  ymax = 0.04
) +
  theme(
    plot.margin = unit(c(0.5, 0.75, 0.5, 0.55), "cm")
  )

p_c <- make_placebo_panel(
  d[pseudo_treated_province == "Fujian"],
  "Months relative to pseudo-event (Fujian)",
  "c",
  ymin = -0.02,
  ymax = 0.04
) +
  theme(
    # Slightly more right-hand space for the longest x-axis title.
    plot.margin = unit(c(0.5, 1.25, 0.5, 0.55), "cm")
  )

# -------------------------------------------------------------------------
# Combine panels
# -------------------------------------------------------------------------

fig <- (
  p_a + p_b + p_c +
    plot_layout(
      ncol = 3,
      guides = "collect",
      widths = c(1, 1, 1)
    )
) &
  theme(
    legend.position = "top",
    plot.background = element_rect(
      fill = "white",
      colour = NA
    )
  )

# -------------------------------------------------------------------------
# Export
# -------------------------------------------------------------------------

ggsave(
  file.path(
    out_dir,
    "Supplementary_Fig_10.png"
  ),
  fig,
  dpi = 1200,
  width = 14.8,
  height = 5.0,
  units = "in",
  bg = "white",
  limitsize = FALSE
)

ggsave(
  file.path(
    out_dir,
    "Supplementary_Fig_10.pdf"
  ),
  fig,
  width = 14.8,
  height = 5.0,
  units = "in",
  device = cairo_pdf,
  bg = "white",
  limitsize = FALSE
)

message("Supplementary Fig. 10 reproduced.")
