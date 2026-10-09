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


# -----------------------------------------------------------------------------
# Local functions and setup
# -----------------------------------------------------------------------------
# Local plotting functions for Supplementary Figure 10.
suppressPackageStartupMessages({
  library(data.table)
  library(ggplot2)
  library(ggprism)
  library(patchwork)
  library(grid)
})

get_script_dir <- function() {
  x <- grep("^--file=", commandArgs(trailingOnly=FALSE), value=TRUE)
  if (length(x)==1L) return(dirname(normalizePath(sub("^--file=","",x),winslash="/")))
  normalizePath(getwd(),winslash="/")
}
code_dir <- get_script_dir()
root <- normalizePath(file.path(code_dir,".."),winslash="/",mustWork=FALSE)
data_dir <- file.path(root,"data")
out_dir <- file.path(root,"output")
dir.create(out_dir,recursive=TRUE,showWarnings=FALSE)

text_size_axis_text <- 14
text_size_axis_title <- 16
text_size_legend_text <- 14
text_size_plot_tag <- 20

event_levels <- c("≤-8","-7","-6","-5","-4","-3","-2","-1","0","1","2","3","4","5","6","7","≥8")

common_theme <- function() {
  theme_prism() +
    theme(
      axis.text  = element_text(size=text_size_axis_text,face="plain",color="black"),
      axis.title = element_text(size=text_size_axis_title,face="plain",color="black"),
      axis.ticks = element_line(linewidth=.5,color="black"),
      axis.line  = element_line(linewidth=.5,color="black"),
      legend.position="top",
      legend.text=element_text(size=text_size_legend_text,color="black"),
      legend.title=element_blank(),
      plot.title=element_text(hjust=.5),
      plot.tag.position="topleft",
      plot.tag=element_text(face="bold",size=text_size_plot_tag)
    )
}

make_placebo_panel <- function(d,xlab_text,tag_text,ymin=-0.02,ymax=0.04) {
  d <- copy(d)
  d[,event_time:=factor(event_time,levels=event_levels)]
  if (nrow(d)!=17L) stop("Each placebo panel must contain 17 event-time points.")
  if (any(!is.finite(d$estimate)) || any(!is.finite(d$ci_lower)) || any(!is.finite(d$ci_upper))) {
    stop("Non-finite coefficient or confidence interval.")
  }

  ggplot(d,aes(x=event_time,y=estimate,group=1)) +
    geom_ribbon(aes(ymin=ci_lower,ymax=ci_upper,fill="95% CI"),alpha=.5,color=NA) +
    geom_line(aes(color="Estimated Coefficients"),linewidth=1) +
    geom_point(aes(color="Estimated Coefficients"),size=3) +
    geom_vline(
      xintercept=which(levels(d$event_time)=="-1"),
      linetype="dashed",color="black",linewidth=.5
    ) +
    geom_hline(yintercept=0,linetype="dashed",color="black",linewidth=.5) +
    scale_y_continuous(
      name="Estimated Coefficients",
      breaks=seq(ymin,ymax,by=.01),
      guide="prism_offset"
    ) +
    coord_cartesian(ylim=c(ymin,ymax)) +
    xlab(xlab_text) +
    scale_color_manual(name=NULL,values=c("Estimated Coefficients"="springgreen4")) +
    scale_fill_manual(name=NULL,values=c("95% CI"="aquamarine2")) +
    common_theme() +
    theme(
      axis.text.x=element_text(size=text_size_axis_text,angle=0,hjust=.5,color="black"),
      axis.title.x=element_text(size=text_size_axis_title,color="black"),
      plot.margin=unit(c(.5,.5,.5,.5),"cm")
    ) +
    labs(tag=tag_text) +
    guides(fill=guide_legend(order=1),color=guide_legend(order=2))
}

# -----------------------------------------------------------------------------
# Data, panels and export
# -----------------------------------------------------------------------------


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
