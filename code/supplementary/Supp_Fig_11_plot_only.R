# Supplementary Fig. 11: Out-of-sample validation of monthly rooftop-solar adoption in 2022.
# Plot-only reproduction from finalized aggregate figure source.

args_all <- commandArgs(trailingOnly=FALSE)
script_arg <- grep("^--file=", args_all, value=TRUE)
script_dir <- if (length(script_arg)==1L) dirname(normalizePath(sub("^--file=","",script_arg),winslash="/")) else normalizePath(getwd(),winslash="/")
source(file.path(script_dir, "_supp_fig11_14_common.R"))

d <- read_csv(file.path(DATA_DIR, "supp_fig11_oos_monthly.csv"), show_col_types = FALSE)
required <- c("system","month","observed","m1","m2","m2_lower","m2_upper")
if (!all(required %in% names(d))) stop("supp_fig11_oos_monthly.csv is missing required columns.")
d <- d %>%
  transmute(
    system = as.character(system),
    month = as.integer(month),
    observed = as.numeric(observed),
    m1 = as.numeric(m1),
    m2 = as.numeric(m2),
    m2_lower = as.numeric(m2_lower),
    m2_upper = as.numeric(m2_upper)
  ) %>% arrange(system, month)

if (nrow(d) != 24L || any(table(d$system) != 12L) || !all(sort(unique(d$month)) == 1:12)) {
  stop("Supplementary Fig. 11 input must contain 12 months for each of the two systems.")
}

yy <- make_y_axis(
  lower = c(d$m2_lower, d$observed, d$m1, d$m2),
  upper = c(d$m2_upper, d$observed, d$m1, d$m2),
  n = 6, include_zero = FALSE
)

make_panel <- function(df, system_label) {
  df <- arrange(df, month)
  ggplot(df, aes(x = month, group = 1)) +
    annotate("segment", x=.72, xend=12.28, y=yy$panel_min, yend=yy$panel_min,
             linewidth=.58, colour="black") +
    annotate("segment", x=.50, xend=.50, y=yy$axis_min, yend=yy$axis_max,
             linewidth=.58, colour="black") +
    geom_ribbon(aes(ymin=m2_lower, ymax=m2_upper), fill=LIGHT_BLUE, alpha=.34, colour=NA) +
    geom_line(aes(y=m2_lower), colour=BLUE, linewidth=.35, alpha=.70) +
    geom_line(aes(y=m2_upper), colour=BLUE, linewidth=.35, alpha=.70) +
    geom_line(aes(y=observed, colour="Observed 2022"), linewidth=.95) +
    geom_point(aes(y=observed, colour="Observed 2022"), size=2.8) +
    geom_line(aes(y=m1, colour="M1: without temperature bins"), linewidth=.85, linetype="dashed") +
    geom_point(aes(y=m1, colour="M1: without temperature bins"), size=2.5, shape=1, stroke=.9) +
    geom_line(aes(y=m2, colour="M2: with temperature bins"), linewidth=.95) +
    geom_point(aes(y=m2, colour="M2: with temperature bins"), size=2.8, shape=15) +
    scale_colour_manual(
      values=c(
        "M1: without temperature bins"=GREY,
        "M2: with temperature bins"=BLUE,
        "Observed 2022"="black"
      ),
      breaks=c("M1: without temperature bins","M2: with temperature bins","Observed 2022")
    ) +
    scale_x_continuous(breaks=1:12, labels=1:12, expand=c(0,0)) +
    scale_y_continuous(breaks=yy$breaks, expand=c(0,0)) +
    coord_cartesian(xlim=c(.50,12.50), ylim=c(yy$panel_min,yy$panel_max), clip="off") +
    labs(x=paste0("Month in 2022 (", system_label, ")"), y="Monthly Installation Index") +
    guides(colour=guide_legend(override.aes=list(linewidth=.8,size=2.6))) +
    theme_academic
}

p1 <- make_panel(filter(d, system=="RRPV-only"), "RRPV-only")
p2 <- make_panel(filter(d, system=="RRPV-BS"), "RRPV-BS")
legend <- extract_white_legend(p1)
row <- cowplot::plot_grid(
  p1 + theme(legend.position="none"),
  p2 + theme(legend.position="none"),
  ncol=2, labels=c("a","b"), label_size=22, label_fontface="bold",
  label_x=.012, label_y=.995, hjust=0, vjust=1, align="hv", axis="tb"
)
fig <- cowplot::plot_grid(legend, row, ncol=1, rel_heights=c(.105,1)) +
  theme(plot.background=element_rect(fill="white",colour=NA))
save_figure(fig, 11, 13.0, 5.9)
