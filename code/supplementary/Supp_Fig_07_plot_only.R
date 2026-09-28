#===============================================================================
# Supplementary Figure 7: Baidu search, temperature, and temperature-bin effects
#
# PUBLIC PLOT-ONLY REPRODUCTION
#
# This script is intentionally kept as close as possible to the historical
# final R/ggplot code that generated the SI figure.
#
# Public inputs:
#   data/supp_fig07_search_temperature.csv
#   data/supp_fig07_temperature_bin_estimates.csv
#
# Outputs:
#   output/Supplementary_Fig_07.png
#   output/Supplementary_Fig_07.pdf
#
# No county names, county IDs, province names, or household identifiers are used.
#===============================================================================

suppressPackageStartupMessages({
  library(ggplot2)
  library(scales)
  library(ggprism)
  library(grid)
  library(gridExtra)
})

#-------------------------------------------------------------------------------
# 1. Paths
#-------------------------------------------------------------------------------

args <- commandArgs(trailingOnly = FALSE)
file_arg <- grep("^--file=", args, value = TRUE)

if (length(file_arg) == 1) {
  script_path <- normalizePath(
    sub("^--file=", "", file_arg),
    winslash = "/",
    mustWork = TRUE
  )
  code_dir <- dirname(script_path)
} else {
  code_dir <- normalizePath(getwd(), winslash = "/", mustWork = TRUE)
}

root_dir <- dirname(code_dir)
data_dir <- file.path(root_dir, "data")
output_dir <- file.path(root_dir, "output")

if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}

search_file <- file.path(data_dir, "supp_fig07_search_temperature.csv")
estimate_file <- file.path(data_dir, "supp_fig07_temperature_bin_estimates.csv")

if (!file.exists(search_file)) {
  stop("Missing public input: ", search_file)
}
if (!file.exists(estimate_file)) {
  stop("Missing public input: ", estimate_file)
}

# English month labels, matching the historical code.
try(Sys.setlocale("LC_TIME", "C"), silent = TRUE)

#-------------------------------------------------------------------------------
# 2. Panel a data
#-------------------------------------------------------------------------------

data <- read.csv(
  search_file,
  stringsAsFactors = FALSE,
  check.names = FALSE
)

required_a <- c(
  "week_date",
  "baidu_weekly",
  "baidu_monthly",
  "avg_temperature_c"
)

missing_a <- setdiff(required_a, names(data))
if (length(missing_a) > 0) {
  stop(
    "Fig. 7 panel-a public CSV is missing: ",
    paste(missing_a, collapse = ", ")
  )
}

# Map the public column names back to the exact variable names used by
# the historical final plotting script.
data$Week <- as.Date(data$week_date)
data$Baidu.week <- as.numeric(data$baidu_weekly)
data$Baidu.month <- as.numeric(data$baidu_monthly)
data$Average.temperature <- as.numeric(data$avg_temperature_c)

data <- data[order(data$Week), ]

min_date <- min(data$Week, na.rm = TRUE)
max_date <- max(data$Week, na.rm = TRUE)

#-------------------------------------------------------------------------------
# 3. Panel a: exact historical plotting specification
#-------------------------------------------------------------------------------

p1 <- ggplot(data) +
  geom_line(
    aes(
      x = Week,
      y = Baidu.month,
      color = "Baidu search (monthly)"
    ),
    size = 1
  ) +
  geom_point(
    aes(
      x = Week,
      y = Baidu.week,
      color = "Baidu search (weekly)"
    ),
    size = 2,
    shape = 1,
    alpha = 0.6
  ) +
  geom_line(
    aes(
      x = Week,
      y = Average.temperature * 25,
      color = "Avg Temperature"
    ),
    size = 0.5,
    alpha = 0.8
  ) +
  scale_x_date(
    date_labels = "%b %Y",
    date_breaks = "4 months",
    limits = c(min_date, max_date),
    expand = c(0.02, 0)
  ) +
  scale_y_continuous(
    name = "Baidu Search",
    breaks = seq(0, 3000, by = 500),
    guide = "prism_offset",
    sec.axis = sec_axis(
      ~ . / 25,
      name = "Temperature (°C)",
      breaks = seq(0, 120, by = 20),
      guide = "prism_offset"
    )
  ) +
  scale_color_manual(
    values = c(
      "Baidu search (monthly)" = "red",
      "Baidu search (weekly)" = "blue",
      "Avg Temperature" = "#00CED1"
    )
  ) +
  theme_prism() +
  theme(
    axis.text.y = element_text(
      size = 17,
      face = "plain"
    ),
    axis.text.x = element_text(
      size = 14,
      angle = 45,
      hjust = 1,
      vjust = 1,
      face = "plain"
    ),
    axis.title = element_text(
      size = 20,
      face = "plain"
    ),
    legend.text = element_text(
      size = 17
    ),
    axis.ticks = element_line(
      linewidth = 0.5
    ),
    axis.line = element_line(
      linewidth = 0.5
    ),
    legend.position = "top",
    legend.title = element_blank()
  ) +
  labs(
    x = "Week",
    tag = "a"
  ) +
  theme(
    plot.tag = element_text(
      face = "bold",
      size = 28
    ),
    plot.tag.position = c(0.02, 0.98)
  )

#-------------------------------------------------------------------------------
# 4. Panel b data from public estimate CSV
#-------------------------------------------------------------------------------

data2 <- read.csv(
  estimate_file,
  stringsAsFactors = FALSE,
  check.names = FALSE
)

required_b <- c(
  "temperature_bin",
  "estimate",
  "ci_low",
  "ci_high",
  "days_in_bin"
)

missing_b <- setdiff(required_b, names(data2))
if (length(missing_b) > 0) {
  stop(
    "Fig. 7 panel-b public CSV is missing: ",
    paste(missing_b, collapse = ", ")
  )
}

# Preserve the exact order from the public estimate CSV.
temperature_levels <- data2$temperature_bin

data2$temperature_bins <- factor(
  data2$temperature_bin,
  levels = temperature_levels
)
data2$coef <- as.numeric(data2$estimate)
data2$lower_ci <- as.numeric(data2$ci_low)
data2$upper_ci <- as.numeric(data2$ci_high)
data2$days_in_bins <- as.numeric(data2$days_in_bin)

#-------------------------------------------------------------------------------
# 5. Panel b upper: exact historical specification
#-------------------------------------------------------------------------------

line_plot <- ggplot(
  data2,
  aes(
    x = temperature_bins,
    y = coef,
    group = 1
  )
) +
  geom_ribbon(
    aes(
      ymin = lower_ci,
      ymax = upper_ci,
      fill = "95% CI"
    ),
    alpha = 0.5
  ) +
  geom_line(
    aes(
      color = "Estimated Coefficients"
    ),
    size = 1
  ) +
  geom_point(
    color = "deepskyblue4",
    size = 3
  ) +
  geom_hline(
    yintercept = 0,
    linetype = "dashed",
    color = "black"
  ) +
  scale_x_discrete(
    expand = expansion(
      mult = c(0.0555, 0.0642)
    )
  ) +
  scale_y_continuous(
    limits = c(-0.1, 0.3),
    expand = c(0, 0),
    breaks = seq(-0.1, 0.3, by = 0.1)
  ) +
  scale_color_manual(
    name = "Legend",
    values = c(
      "Estimated Coefficients" = "deepskyblue4"
    )
  ) +
  scale_fill_manual(
    name = "Legend",
    values = c(
      "95% CI" = "deepskyblue"
    )
  ) +
  guides(
    color = guide_legend(order = 1),
    fill = guide_legend(order = 2)
  ) +
  theme_minimal() +
  theme(
    panel.grid = element_blank(),
    axis.title.x = element_blank(),
    axis.text.x = element_blank(),
    axis.ticks.x = element_blank(),
    axis.ticks.y = element_line(
      color = "black",
      linewidth = 0.5
    ),
    axis.title.y = element_text(
      color = "black",
      size = 20
    ),
    axis.text.y = element_text(
      color = "black",
      size = 17
    ),
    legend.text = element_text(
      size = 17
    ),
    axis.line.y = element_line(
      color = "black"
    ),
    plot.margin = unit(
      c(1, 1, -0.5, 1),
      "lines"
    ),
    legend.position = "top",
    legend.title = element_blank(),
    legend.direction = "horizontal"
  ) +
  ylab(
    "Estimated Coefficients"
  ) +
  labs(
    tag = "b"
  ) +
  theme(
    plot.tag = element_text(
      face = "bold",
      size = 28
    ),
    plot.tag.position = c(0.02, 0.98)
  )

#-------------------------------------------------------------------------------
# 6. Panel b lower: exact historical specification
#-------------------------------------------------------------------------------

bar_plot <- ggplot(
  data2,
  aes(
    x = temperature_bins,
    y = days_in_bins
  )
) +
  geom_bar(
    stat = "identity",
    fill = "grey70",
    width = 0.5
  ) +
  theme_minimal() +
  theme(
    panel.grid = element_blank(),
    axis.title.y = element_blank(),
    axis.text.y = element_blank(),
    axis.ticks.y = element_blank(),
    axis.title.x = element_text(
      color = "black",
      size = 20
    ),
    axis.text.x = element_text(
      color = "black",
      size = 14,
      face = "plain"
    ),
    axis.ticks.x = element_line(
      color = "black",
      linewidth = 0.5
    ),
    axis.line.x = element_line(
      color = "black"
    ),
    plot.margin = unit(
      c(-1.3, 2, 1, 4),
      "lines"
    )
  ) +
  xlab(
    "Temperature bins"
  ) +
  coord_cartesian(
    clip = "off",
    expand = FALSE
  )

#-------------------------------------------------------------------------------
# 7. Exact historical alignment and combination
#-------------------------------------------------------------------------------

g_line <- ggplotGrob(line_plot)
g_bar <- ggplotGrob(bar_plot)

maxWidth_right <- grid::unit.pmax(
  g_line$widths[2:5],
  g_bar$widths[2:5]
)

g_line$widths[2:5] <- maxWidth_right
g_bar$widths[2:5] <- maxWidth_right

g_right_aligned <- arrangeGrob(
  g_line,
  g_bar,
  ncol = 1,
  heights = c(3, 0.6)
)

g1 <- ggplotGrob(p1)

combined_grob <- arrangeGrob(
  g1,
  g_right_aligned,
  ncol = 2
)

#-------------------------------------------------------------------------------
# 8. Save — same dimensions as historical final script
#-------------------------------------------------------------------------------

png_file <- file.path(
  output_dir,
  "Supplementary_Fig_07.png"
)

pdf_file <- file.path(
  output_dir,
  "Supplementary_Fig_07.pdf"
)

ggsave(
  filename = png_file,
  plot = combined_grob,
  width = 18,
  height = 8,
  units = "in",
  dpi = 1200,
  bg = "white"
)

ggsave(
  filename = pdf_file,
  plot = combined_grob,
  width = 18,
  height = 8,
  units = "in",
  device = grDevices::cairo_pdf
)

message("Supplementary Fig. 7 reproduced from public CSVs.")
message(png_file)
message(pdf_file)

#===============================================================================
# END
#===============================================================================
