# Supplementary Fig. 12: Annual estimates of the extreme-heat response.
# Plot-only reproduction from supplied aggregate coefficient estimates.

args_all <- commandArgs(trailingOnly=FALSE)
script_arg <- grep("^--file=", args_all, value=TRUE)
script_dir <- if (length(script_arg)==1L) dirname(normalizePath(sub("^--file=","",script_arg),winslash="/")) else normalizePath(getwd(),winslash="/")

# -----------------------------------------------------------------------------
# Local functions and setup
# -----------------------------------------------------------------------------
# Local plotting functions for Supplementary Figure 12.

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


d <- read_csv(file.path(DATA_DIR, "supp_fig12_annual_heat_effects.csv"), show_col_types=FALSE) %>%
  mutate(
    system=as.character(system), sample=as.character(sample),
    year=as.integer(year), estimate=as.numeric(estimate),
    ci_lower=as.numeric(ci_lower), ci_upper=as.numeric(ci_upper)
  )

d <- d %>%
  mutate(
    year_plot=if_else(sample=="All counties", year-.12, year+.12),
    cap_left=year_plot-.055, cap_right=year_plot+.055,
    sample=factor(sample,levels=c("Excluding pilot counties","All counties"))
  ) %>% arrange(system,year,sample)

yy <- make_y_axis(d$ci_lower,d$ci_upper,n=7,include_zero=TRUE)
cols <- c("Excluding pilot counties"=BLUE,"All counties"=GREY)
shapes <- c("Excluding pilot counties"=16,"All counties"=0)

make_panel <- function(df, system_label) {
  ggplot(df) +
    annotate("segment",x=2017.72,xend=2022.28,y=yy$panel_min,yend=yy$panel_min,
             linewidth=.58,colour="black") +
    annotate("segment",x=2017.50,xend=2017.50,y=yy$axis_min,yend=yy$axis_max,
             linewidth=.58,colour="black") +
    geom_hline(yintercept=0,linewidth=.45,linetype="dotted",colour="#999999") +
    geom_linerange(aes(x=year_plot,ymin=ci_lower,ymax=ci_upper,colour=sample),linewidth=.75) +
    geom_segment(aes(x=cap_left,xend=cap_right,y=ci_lower,yend=ci_lower,colour=sample),linewidth=.75) +
    geom_segment(aes(x=cap_left,xend=cap_right,y=ci_upper,yend=ci_upper,colour=sample),linewidth=.75) +
    geom_point(aes(x=year_plot,y=estimate,colour=sample,shape=sample),size=3.2,stroke=.95) +
    scale_colour_manual(values=cols) + scale_shape_manual(values=shapes) +
    scale_x_continuous(breaks=2018:2022,labels=2018:2022,expand=c(0,0)) +
    scale_y_continuous(breaks=yy$breaks,labels=function(x)sprintf("%.2f",x),expand=c(0,0)) +
    coord_cartesian(xlim=c(2017.50,2022.50),ylim=c(yy$panel_min,yy$panel_max),clip="off") +
    labs(x=paste0("Year (",system_label," Adoption)"),y="Coefficient on Days Above 30°C") +
    guides(colour=guide_legend(override.aes=list(size=3.0)),shape="none") +
    theme_academic
}

p1 <- make_panel(filter(d,system=="RRPV-only"),"RRPV-only")
p2 <- make_panel(filter(d,system=="RRPV-BS"),"RRPV-BS")
legend <- extract_white_legend(p1)
row <- cowplot::plot_grid(
  p1+theme(legend.position="none"),p2+theme(legend.position="none"),
  ncol=2,labels=c("a","b"),label_size=22,label_fontface="bold",
  label_x=.012,label_y=.995,hjust=0,vjust=1,align="hv",axis="tb"
)
fig <- cowplot::plot_grid(legend,row,ncol=1,rel_heights=c(.105,1)) +
  theme(plot.background=element_rect(fill="white",colour=NA))
save_figure(fig,12,13.0,5.9)
