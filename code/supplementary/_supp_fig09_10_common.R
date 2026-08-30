# Shared helpers for current Supplementary Figs. 9-10.
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
      limits=c(ymin,ymax),
      guide="prism_offset"
    ) +
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
