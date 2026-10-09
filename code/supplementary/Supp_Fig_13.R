# Supplementary Fig. 13: Utility-scale solar penetration and the extreme-heat response.
# Plot-only reproduction from supplied marginal-effect curves and observed penetration support.

args_all <- commandArgs(trailingOnly=FALSE)
script_arg <- grep("^--file=", args_all, value=TRUE)
script_dir <- if (length(script_arg)==1L) dirname(normalizePath(sub("^--file=","",script_arg),winslash="/")) else normalizePath(getwd(),winslash="/")

# -----------------------------------------------------------------------------
# Local functions and setup
# -----------------------------------------------------------------------------
# Local plotting functions for Supplementary Figure 13.

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


curve <- read_csv(file.path(DATA_DIR,"supp_fig13_marginal_effect_curve.csv"),show_col_types=FALSE)
support <- read_csv(file.path(DATA_DIR,"supp_fig13_observed_penetration.csv"),show_col_types=FALSE)

observed_min <- min(support$penetration_pct,na.rm=TRUE)
observed_max <- max(support$penetration_pct,na.rm=TRUE)
yy <- make_y_axis(curve$ci_lower,curve$ci_upper,n=6,include_zero=TRUE)

x_axis_min <- floor(observed_min*2)/2
x_axis_max <- ceiling(observed_max*2)/2
x_span <- x_axis_max-x_axis_min
x_panel_min <- x_axis_min-.02*x_span
x_panel_max <- x_axis_max+.02*x_span
x_breaks <- pretty(c(x_axis_min,x_axis_max),n=6)
x_breaks <- x_breaks[x_breaks>=x_axis_min & x_breaks<=x_axis_max]

system_colors <- c("RRPV-only"=BLUE,"RRPV-BS"=GREY)
system_fills <- c("RRPV-only"=LIGHT_BLUE,"RRPV-BS"="#D9D9D9")
system_linetypes <- c("RRPV-only"="solid","RRPV-BS"="dashed")

p <- ggplot(curve,aes(
  x=penetration_pct,y=marginal_effect,colour=system,fill=system,linetype=system
)) +
  annotate("segment",x=x_axis_min+.02*x_span,xend=x_axis_max-.02*x_span,
           y=yy$panel_min,yend=yy$panel_min,linewidth=.58,colour="black") +
  annotate("segment",x=x_panel_min,xend=x_panel_min,
           y=yy$axis_min,yend=yy$axis_max,linewidth=.58,colour="black") +
  geom_hline(yintercept=0,linewidth=.42,linetype="dotted",colour="#999999") +
  geom_ribbon(aes(ymin=ci_lower,ymax=ci_upper,group=system),alpha=.24,colour=NA,linetype=0) +
  geom_line(linewidth=1.05) +
  geom_rug(data=support,aes(x=penetration_pct),inherit.aes=FALSE,sides="b",
           length=unit(.085,"cm"),linewidth=.42,colour="#777777",alpha=.85) +
  scale_colour_manual(values=system_colors,breaks=c("RRPV-only","RRPV-BS")) +
  scale_fill_manual(values=system_fills,breaks=c("RRPV-only","RRPV-BS")) +
  scale_linetype_manual(values=system_linetypes,breaks=c("RRPV-only","RRPV-BS")) +
  scale_x_continuous(breaks=x_breaks,labels=function(x)sprintf("%.0f",x),expand=c(0,0)) +
  scale_y_continuous(breaks=yy$breaks,labels=function(x)sprintf("%.2f",x),expand=c(0,0)) +
  coord_cartesian(xlim=c(x_panel_min,x_panel_max),ylim=c(yy$panel_min,yy$panel_max),clip="off") +
  labs(x="Utility-scale solar penetration (%)",y="Marginal effect of an additional day above 30°C") +
  guides(colour=guide_legend(override.aes=list(linewidth=1.05,alpha=1)),
         fill="none",linetype="none") +
  theme_academic +
  theme(panel.grid=element_blank(),axis.line.x=element_blank(),axis.line.y=element_blank(),
        legend.position="top",plot.margin=margin(t=6,r=15,b=12,l=10))

save_figure(p,13,7.6,5.8)
