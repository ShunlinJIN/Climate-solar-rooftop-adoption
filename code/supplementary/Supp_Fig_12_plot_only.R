# Supplementary Fig. 12: Annual estimates of the extreme-heat response.
# Plot-only reproduction from finalized aggregate coefficient estimates.

args_all <- commandArgs(trailingOnly=FALSE)
script_arg <- grep("^--file=", args_all, value=TRUE)
script_dir <- if (length(script_arg)==1L) dirname(normalizePath(sub("^--file=","",script_arg),winslash="/")) else normalizePath(getwd(),winslash="/")
source(file.path(script_dir, "_supp_fig11_14_common.R"))

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
