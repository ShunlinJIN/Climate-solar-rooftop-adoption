# Supplementary Figure 26: hourly electricity-flow composition.
# Plot-only reproduction from the accompanying non-identifying plotting inputs.
# No model is re-estimated.

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

flow <- fread(file.path(data_dir,"supp_fig26_hourly_flow_composition.csv"))

set.seed(20260725L)
font_family <- "Arial"
max_points <- 50000L
display_quantile <- .9975
point_colour <- "#2C7FB8"
reference_colour <- "#D7301F"

component_order <- c("Direct PV use","PV-to-battery","Battery-to-load","PV export","Grid-to-load")
component_palette <- c("Direct PV use"="#E76F51","PV-to-battery"="#E9C46A",
  "Battery-to-load"="#7B2CBF","PV export"="#2A9D8F","Grid-to-load"="#457B9D")

theme_pub <- theme_classic(base_size=11,base_family=font_family) +
  theme(axis.line=element_line(colour="black",linewidth=.5),
        axis.ticks=element_line(colour="black",linewidth=.5),
        axis.text=element_text(colour="black",size=10),
        axis.title=element_text(colour="black",size=11),
        plot.title=element_text(hjust=.5,face="bold",size=13,margin=margin(b=5)),
        plot.tag=element_text(face="bold",size=15),
        plot.tag.position=c(0,1),plot.margin=margin(10,10,10,12))

make_flow <- function(sys,components,total_col,title) {
  d <- copy(flow[system==sys])
  long <- rbindlist(lapply(names(components),function(display) {
    data.table(hour=d$hour,component=display,value=pmax(0,as.numeric(d[[components[[display]]]])))
  }))
  long[,component:=factor(component,levels=names(components))]
  total <- data.table(hour=d$hour,total=pmax(0,as.numeric(d[[total_col]])))
  ggplot() +
    geom_area(data=long,aes(hour,value,fill=component),position=position_stack(reverse=TRUE),
              alpha=.92,linewidth=0,show.legend=FALSE) +
    geom_line(data=total,aes(hour,total),colour="black",linewidth=.8,show.legend=FALSE) +
    scale_fill_manual(values=component_palette) +
    scale_x_continuous(breaks=c(0,3,6,9,12,15,18,21,23),limits=c(0,23),expand=expansion(mult=c(0,0))) +
    scale_y_continuous(expand=expansion(mult=c(0,.06))) +
    labs(title=title,x="Hour of day",y="Average hourly electricity (kWh per household)") +
    theme_pub + theme(legend.position="none")
}

fa <- make_flow("RRPV-only",c("Direct PV use"="pv_to_load","PV export"="pv_to_grid"),
                "pv_generation","RRPV-only: allocation of PV generation")
fb <- make_flow("RRPV-only",c("Direct PV use"="pv_to_load","Grid-to-load"="grid_to_load"),
                "total_load","RRPV-only: sources of household load")
fc <- make_flow("RRPV-BS",c("Direct PV use"="pv_to_load","PV-to-battery"="pv_to_battery","PV export"="pv_to_grid"),
                "pv_generation","RRPV-BS: allocation of PV generation")
fd <- make_flow("RRPV-BS",c("Direct PV use"="pv_to_load","Battery-to-load"="battery_to_load","Grid-to-load"="grid_to_load"),
                "total_load","RRPV-BS: sources of household load")

flow_fig <- wrap_plots(fa,fb,fc,fd,ncol=2,nrow=2) + plot_annotation(tag_levels="a")
ggsave(file.path(out_dir,"Supplementary_Fig_26.pdf"),flow_fig,width=11.5,height=8.5,device=cairo_pdf,bg="white")
ggsave(file.path(out_dir,"Supplementary_Fig_26.png"),flow_fig,width=11.5,height=8.5,dpi=1200,bg="white")
message("Supplementary Fig. 26 reproduced; no models re-estimated.")
