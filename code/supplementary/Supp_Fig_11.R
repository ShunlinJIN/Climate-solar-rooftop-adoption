# Supplementary Fig. 11: Out-of-sample validation of monthly rooftop-solar adoption in 2022.
# Plot-only reproduction from supplied aggregate figure source.

args_all <- commandArgs(trailingOnly=FALSE)
script_arg <- grep("^--file=", args_all, value=TRUE)
script_dir <- if (length(script_arg)==1L) dirname(normalizePath(sub("^--file=","",script_arg),winslash="/")) else normalizePath(getwd(),winslash="/")

# -----------------------------------------------------------------------------
# Local functions and setup
# -----------------------------------------------------------------------------
# Local plotting functions for Supplementary Figure 11.

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

# -----------------------------------------------------------------------------
# Data, panels and export
# -----------------------------------------------------------------------------


d <- read_csv(file.path(DATA_DIR, "supp_fig11_oos_monthly.csv"), show_col_types = FALSE)
required <- c("system","month","observed","m1","m2","m2_lower","m2_upper")
if (!all(required %in% names(d))) stop("supp_fig11_oos_monthly.csv is missing required columns.")
d <- d %>%
  transmute(
    system = as.character(system),
    month = as.integer(month),
    observed = as.numeric(observed),
    m1 = as.numeric(m1),
    m2 = as.numeric(m2),
    m2_lower = as.numeric(m2_lower),
    m2_upper = as.numeric(m2_upper)
  ) %>% arrange(system, month)

if (nrow(d) != 24L || any(table(d$system) != 12L) || !all(sort(unique(d$month)) == 1:12)) {
  stop("Supplementary Fig. 11 input must contain 12 months for each of the two systems.")
}

yy <- make_y_axis(
  lower = c(d$m2_lower, d$observed, d$m1, d$m2),
  upper = c(d$m2_upper, d$observed, d$m1, d$m2),
  n = 6, include_zero = FALSE
)

make_panel <- function(df, system_label) {
  df <- arrange(df, month)
  ggplot(df, aes(x = month, group = 1)) +
    annotate("segment", x=.72, xend=12.28, y=yy$panel_min, yend=yy$panel_min,
             linewidth=.58, colour="black") +
    annotate("segment", x=.50, xend=.50, y=yy$axis_min, yend=yy$axis_max,
             linewidth=.58, colour="black") +
    geom_ribbon(aes(ymin=m2_lower, ymax=m2_upper), fill=LIGHT_BLUE, alpha=.34, colour=NA) +
    geom_line(aes(y=m2_lower), colour=BLUE, linewidth=.35, alpha=.70) +
    geom_line(aes(y=m2_upper), colour=BLUE, linewidth=.35, alpha=.70) +
    geom_line(aes(y=observed, colour="Observed 2022"), linewidth=.95) +
    geom_point(aes(y=observed, colour="Observed 2022"), size=2.8) +
    geom_line(aes(y=m1, colour="M1: without temperature bins"), linewidth=.85, linetype="dashed") +
    geom_point(aes(y=m1, colour="M1: without temperature bins"), size=2.5, shape=1, stroke=.9) +
    geom_line(aes(y=m2, colour="M2: with temperature bins"), linewidth=.95) +
    geom_point(aes(y=m2, colour="M2: with temperature bins"), size=2.8, shape=15) +
    scale_colour_manual(
      values=c(
        "M1: without temperature bins"=GREY,
        "M2: with temperature bins"=BLUE,
        "Observed 2022"="black"
      ),
      breaks=c("M1: without temperature bins","M2: with temperature bins","Observed 2022")
    ) +
    scale_x_continuous(breaks=1:12, labels=1:12, expand=c(0,0)) +
    scale_y_continuous(breaks=yy$breaks, expand=c(0,0)) +
    coord_cartesian(xlim=c(.50,12.50), ylim=c(yy$panel_min,yy$panel_max), clip="off") +
    labs(x=paste0("Month in 2022 (", system_label, ")"), y="Monthly Installation Index") +
    guides(colour=guide_legend(override.aes=list(linewidth=.8,size=2.6))) +
    theme_academic
}

p1 <- make_panel(filter(d, system=="RRPV-only"), "RRPV-only")
p2 <- make_panel(filter(d, system=="RRPV-BS"), "RRPV-BS")
legend <- extract_white_legend(p1)
row <- cowplot::plot_grid(
  p1 + theme(legend.position="none"),
  p2 + theme(legend.position="none"),
  ncol=2, labels=c("a","b"), label_size=22, label_fontface="bold",
  label_x=.012, label_y=.995, hjust=0, vjust=1, align="hv", axis="tb"
)
fig <- cowplot::plot_grid(legend, row, ncol=1, rel_heights=c(.105,1)) +
  theme(plot.background=element_rect(fill="white",colour=NA))
save_figure(fig, 11, 13.0, 5.9)
