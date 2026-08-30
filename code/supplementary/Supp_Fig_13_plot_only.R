# Supplementary Fig. 13: Utility-scale solar penetration and the extreme-heat response.
# Plot-only reproduction from finalized marginal-effect curves and observed penetration support.

args_all <- commandArgs(trailingOnly=FALSE)
script_arg <- grep("^--file=", args_all, value=TRUE)
script_dir <- if (length(script_arg)==1L) dirname(normalizePath(sub("^--file=","",script_arg),winslash="/")) else normalizePath(getwd(),winslash="/")
source(file.path(script_dir, "_supp_fig11_14_common.R"))

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
