# Supplementary Fig. 14: Projected near-term temperature-induced growth in RRPV-only and RRPV-BS adoption.
# Plot-only reproduction from supplied scenario-level projection summaries.

args_all <- commandArgs(trailingOnly=FALSE)
script_arg <- grep("^--file=", args_all, value=TRUE)
script_dir <- if (length(script_arg)==1L) dirname(normalizePath(sub("^--file=","",script_arg),winslash="/")) else normalizePath(getwd(),winslash="/")
source(file.path(script_dir, "_supp_fig11_14_common.R"))

d <- read_csv(file.path(DATA_DIR,"supp_fig14_projection.csv"),show_col_types=FALSE) %>%
  mutate(
    system=as.character(system),
    scenario=factor(as.character(scenario),levels=c("SSP1-2.6","SSP2-4.5","SSP5-8.5")),
    estimate=as.numeric(estimate),ci_lower=as.numeric(ci_lower),ci_upper=as.numeric(ci_upper),
    x=as.numeric(scenario),cap_left=x-.13,cap_right=x+.13
  ) %>% arrange(system,scenario)

yy <- make_y_axis(d$ci_lower,d$ci_upper,n=6,include_zero=TRUE)

make_panel <- function(df, system_label) {
  label_gap <- .035*(yy$axis_max-yy$axis_min)
  label_floor <- max(.30,yy$panel_min+.055*(yy$panel_max-yy$panel_min))
  df <- mutate(df,label_y=pmax(ci_lower-label_gap,label_floor))

  ggplot(df,aes(x=x,y=estimate)) +
    annotate("segment",x=.72,xend=3.28,y=yy$panel_min,yend=yy$panel_min,
             linewidth=.58,colour="black") +
    annotate("segment",x=.50,xend=.50,y=yy$axis_min,yend=yy$axis_max,
             linewidth=.58,colour="black") +
    geom_col(width=.58,fill=LIGHT_BLUE,alpha=.90) +
    geom_linerange(aes(ymin=ci_lower,ymax=ci_upper),linewidth=.75,colour="black") +
    geom_segment(aes(x=cap_left,xend=cap_right,y=ci_lower,yend=ci_lower),linewidth=.75,colour="black") +
    geom_segment(aes(x=cap_left,xend=cap_right,y=ci_upper,yend=ci_upper),linewidth=.75,colour="black") +
    geom_text(aes(y=label_y,label=sprintf("%.1f%%",estimate)),size=4.0,
              colour=BLUE,fontface="bold",vjust=1.10) +
    scale_x_continuous(breaks=1:3,labels=c("SSP1-2.6","SSP2-4.5","SSP5-8.5"),expand=c(0,0)) +
    scale_y_continuous(breaks=yy$breaks,labels=function(x)sprintf("%.0f",x),expand=c(0,0)) +
    coord_cartesian(xlim=c(.50,3.50),ylim=c(yy$panel_min,yy$panel_max),clip="off") +
    labs(x=paste0("Climate Scenario (",system_label,")"),
         y="Projected Adoption Change Relative to 2022 (%)") +
    theme_academic + theme(legend.position="none")
}

p1 <- make_panel(filter(d,system=="RRPV-only"),"RRPV-only")
p2 <- make_panel(filter(d,system=="RRPV-BS"),"RRPV-BS")
fig <- cowplot::plot_grid(
  p1,p2,ncol=2,labels=c("a","b"),label_size=22,label_fontface="bold",
  label_x=.012,label_y=.995,hjust=0,vjust=1,align="hv",axis="tb"
) + theme(plot.background=element_rect(fill="white",colour=NA))
save_figure(fig,14,12.8,5.8)
