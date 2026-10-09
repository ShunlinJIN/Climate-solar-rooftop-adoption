# Supplementary Fig. 24: Daily/hourly PV prediction validation
# Plot-only reproduction from non-identifying archived plotting pairs and complete-sample metrics.
# No model is estimated or recalibrated.

suppressPackageStartupMessages({
  library(data.table)
  library(ggplot2)
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

daily_only <- fread(file.path(data_dir,"supp_fig24_daily_rrpv_only_plot.csv"))
daily_bs <- fread(file.path(data_dir,"supp_fig24_daily_rrpv_bs_plot.csv"))
hourly <- fread(file.path(data_dir,"supp_fig24_hourly_plot.csv"))
metrics <- fread(file.path(data_dir,"supp_fig24_validation_metrics.csv"))

set.seed(20260723L)
max_points <- 50000L
scope <- "Observed or predicted generation > 0.01 kWh"
point_colour <- "#1f77b4"
reference_colour <- "#d62728"
font_family <- "Arial"

sample_plot <- function(d) {
  if (nrow(d)<=max_points) return(copy(d))
  d[sample.int(.N,max_points,replace=FALSE)]
}
metric_row <- function(res,sys) {
  z <- metrics[resolution==res & system==sys]
  if (nrow(z)!=1L) stop("Metric row missing/duplicated: ",res," ",sys)
  z
}
metric_label <- function(m) sprintf(
  "R² = %.3f\nRMSE = %.3f kWh\nMAE = %.3f kWh\nBias = %.3f kWh",
  m$r_squared,m$rmse_kwh,m$mae_kwh,m$bias_kwh)

theme_v <- theme_classic(base_size=11,base_family=font_family) +
  theme(axis.line=element_line(colour="black",linewidth=.5),
        axis.ticks=element_line(colour="black",linewidth=.5),
        axis.text=element_text(colour="black",size=11),
        axis.title=element_text(colour="black",size=12),
        plot.title=element_text(hjust=.5,face="bold",size=13),
        plot.tag=element_text(face="bold",size=16),legend.position="none",
        plot.margin=margin(8,8,8,8))

make_panel <- function(d,m,title,tag,xlab,ylab,xlim=NULL,ylim=NULL) {
  plotd <- sample_plot(d)
  if (is.null(xlim)) xlim <- max(plotd$observed_generation_kwh,na.rm=TRUE)
  if (is.null(ylim)) ylim <- max(plotd$predicted_generation_kwh,na.rm=TRUE)
  ggplot(plotd,aes(x=observed_generation_kwh,y=predicted_generation_kwh)) +
    geom_point(alpha=.20,size=.65,colour=point_colour) +
    geom_abline(intercept=0,slope=1,colour=reference_colour,linetype="dashed",linewidth=.85) +
    annotate("text",x=.04*xlim,y=.96*ylim,label=metric_label(m),
             hjust=0,vjust=1,size=3.6,family=font_family,lineheight=1.08) +
    coord_cartesian(xlim=c(0,xlim),ylim=c(0,ylim),expand=FALSE,clip="on") +
    labs(title=title,x=xlab,y=ylab,tag=tag) + theme_v
}

bs_x <- quantile(daily_bs$observed_generation_kwh,.995,na.rm=TRUE,names=FALSE)
bs_y <- quantile(daily_bs$predicted_generation_kwh,.995,na.rm=TRUE,names=FALSE)

pa <- make_panel(daily_only,metric_row("Daily","RRPV-only"),"RRPV-only","a",
                 "Observed daily generation (kWh)","Predicted daily generation (kWh)")
pb <- make_panel(daily_bs,metric_row("Daily","RRPV-BS"),"RRPV-BS","b",
                 "Observed daily generation (kWh)","Predicted daily generation (kWh)",bs_x,bs_y)
pc <- make_panel(hourly[system=="RRPV-only"],metric_row("Hourly","RRPV-only"),"RRPV-only","c",
                 "Observed hourly generation (kWh)","Predicted hourly generation (kWh)")
pd <- make_panel(hourly[system=="RRPV-BS"],metric_row("Hourly","RRPV-BS"),"RRPV-BS","d",
                 "Observed hourly generation (kWh)","Predicted hourly generation (kWh)")

fig <- (pa+pb)/(pc+pd) + plot_layout(widths=c(1,1),heights=c(1,1))
ggsave(file.path(out_dir,"Supplementary_Fig_24.pdf"),fig,width=10,height=9,device=cairo_pdf,bg="white")
ggsave(file.path(out_dir,"Supplementary_Fig_24.png"),fig,width=10,height=9,dpi=1200,bg="white")
message("Supplementary Fig. 24 reproduced; no model re-estimated.")
