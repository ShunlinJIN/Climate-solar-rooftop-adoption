# Supplementary Fig. 18: Intraday load shifting
# Plot-only reproduction. No regressions are re-estimated.

suppressPackageStartupMessages({
  library(data.table)
  library(ggplot2)
  library(patchwork)
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

hour_results <- fread(file.path(data_dir,"supp_fig18_hourly_coefficients.csv"))
window_results <- fread(file.path(data_dir,"supp_fig18_window_coefficients.csv"))

FONT_FAMILY <- "Arial"
COL_RRPV_ONLY <- "#159D94"
COL_RRPV_BS <- "#3F6FA6"
COL_ZERO <- "#777777"
COL_TEXT <- "#222222"
WINDOW_COLORS_ONLY <- c("06:00–18:59"="#159D94","06:00–17:59"="#66B8B1","07:00–17:59"="#A6D7D2")
WINDOW_COLORS_BS <- c("06:00–18:59"="#3F6FA6","06:00–17:59"="#6E91BF","07:00–17:59"="#A8BCDA")
WINDOW_SHAPES <- c("06:00–18:59"=16,"06:00–17:59"=17,"07:00–17:59"=15)

theme_final <- function() {
  theme_classic(base_size=11,base_family=FONT_FAMILY) +
    theme(panel.grid=element_blank(),axis.text=element_text(colour=COL_TEXT,size=9),
          axis.title=element_text(colour=COL_TEXT,size=10),plot.title=element_text(hjust=0.5,size=11),
          plot.tag=element_text(face="bold",size=13),legend.position="top",
          legend.title=element_blank(),legend.text=element_text(size=9),
          plot.margin=margin(7,10,7,7))
}
sys_col <- function(x) if (x=="RRPV-only") COL_RRPV_ONLY else COL_RRPV_BS

make_hour_panel <- function(system_name, tag) {
  d <- hour_results[system==system_name]
  cc <- sys_col(system_name)
  ggplot(d,aes(x=hour,y=coefficient)) +
    annotate("rect",xmin=5.5,xmax=18.5,ymin=-Inf,ymax=Inf,fill=cc,alpha=0.045) +
    geom_hline(yintercept=0,linetype="dashed",linewidth=0.40,colour=COL_ZERO) +
    geom_errorbar(aes(ymin=confidence_low,ymax=confidence_high),width=0.18,linewidth=0.52,colour=cc) +
    geom_point(size=2.05,colour=cc) +
    scale_x_continuous(breaks=c(0,3,6,9,12,15,18,21,23),limits=c(-0.25,23.25)) +
    labs(x="Hour of day",
         y="Hourly electricity-consumption response (kWh)\nper 1-SD increase in daily PV generation",
         title=system_name,tag=tag) +
    theme_final() + theme(legend.position="none")
}

period_data <- copy(window_results)
period_data[,period_label:=factor(outcome,
  levels=c("nonpv_period_load_kwh","pv_period_load_kwh"),
  labels=c("Non-PV hours","PV-production hours"))]
period_data[,window_label:=fifelse(window_definition=="Primary: 06:00-18:59","06:00–18:59",
  fifelse(window_definition=="Sensitivity: 06:00-17:59","06:00–17:59",
  fifelse(window_definition=="Sensitivity: 07:00-17:59","07:00–17:59",NA_character_)))]
period_data[,window_label:=factor(window_label,levels=c("06:00–18:59","06:00–17:59","07:00–17:59"))]

make_window_panel <- function(system_name,tag) {
  d <- period_data[system==system_name]
  manual_cols <- if (system_name=="RRPV-only") WINDOW_COLORS_ONLY else WINDOW_COLORS_BS
  ggplot(d,aes(x=coefficient,y=period_label,colour=window_label,shape=window_label)) +
    geom_vline(xintercept=0,linetype="dashed",linewidth=0.40,colour=COL_ZERO) +
    geom_errorbarh(aes(xmin=confidence_low,xmax=confidence_high),
                   position=position_dodge(width=0.58),height=0.10,linewidth=0.50) +
    geom_point(position=position_dodge(width=0.58),size=2.05) +
    scale_colour_manual(values=manual_cols,drop=FALSE) +
    scale_shape_manual(values=WINDOW_SHAPES,drop=FALSE) +
    labs(x="Electricity-consumption response (kWh)\nper 1-SD increase in daily PV generation",
         y=NULL,title=system_name,tag=tag) + theme_final()
}

final_fig <- (make_hour_panel("RRPV-only","a") | make_hour_panel("RRPV-BS","b")) /
             (make_window_panel("RRPV-only","c") | make_window_panel("RRPV-BS","d"))

ggsave(file.path(out_dir,"Supplementary_Fig_18.pdf"),final_fig,width=13,height=9,device=cairo_pdf,bg="white")
ggsave(file.path(out_dir,"Supplementary_Fig_18.png"),final_fig,width=13,height=9,dpi=600,bg="white")
message("Supplementary Fig. 18 reproduced; no regressions re-estimated.")
