# Supplementary Fig. 9: Timing placebo event-study estimates of power rationing effects.
# Plot-only reproduction from aggregate event-time coefficients and 95% confidence intervals.

args <- commandArgs(trailingOnly=FALSE)
script_arg <- grep("^--file=",args,value=TRUE)
script_dir <- if (length(script_arg)==1L) dirname(normalizePath(sub("^--file=","",script_arg),winslash="/")) else normalizePath(getwd(),winslash="/")
source(file.path(script_dir,"_supp_fig09_10_common.R"))

d <- fread(file.path(data_dir,"supp_fig09_timing_placebo.csv"))
required <- c("system","event_time","estimate","ci_lower","ci_upper")
if (!all(required %in% names(d))) stop("Fig. 9 input is missing required columns.")

p_a <- make_placebo_panel(
  d[system=="RRPV-BS"],
  "Months relative to placebo event (RRPV-BS)",
  "a",
  ymin=-0.02,ymax=0.04
)
p_b <- make_placebo_panel(
  d[system=="RRPV-only"],
  "Months relative to placebo event (RRPV-only)",
  "b",
  ymin=-0.02,ymax=0.04
)

fig <- (p_a+p_b+plot_layout(ncol=2,guides="collect")) &
  theme(legend.position="top")

ggsave(file.path(out_dir,"Supplementary_Fig_09.png"),fig,dpi=1200,width=12,height=6,units="in",bg="white")
ggsave(file.path(out_dir,"Supplementary_Fig_09.pdf"),fig,width=12,height=6,units="in",device=cairo_pdf,bg="white")
message("Supplementary Fig. 9 reproduced.")
