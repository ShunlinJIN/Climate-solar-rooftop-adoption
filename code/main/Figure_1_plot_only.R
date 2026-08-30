
rm(list = ls())
source(file.path(dirname(normalizePath(sub("^--file=", "", commandArgs(trailingOnly=FALSE)[grep("^--file=", commandArgs(trailingOnly=FALSE))]), winslash="/")), "_paths_and_note.R"))

required_packages <- c("ggplot2","ggprism","patchwork")
missing <- required_packages[!vapply(required_packages, requireNamespace, logical(1), quietly=TRUE)]
if (length(missing)) stop("Missing R package(s): ", paste(missing, collapse=", "))
suppressPackageStartupMessages({
  library(ggplot2); library(ggprism); library(patchwork)
})

dat <- read.csv(file.path(data_dir, "figure1_plot_data.csv"), check.names=FALSE, stringsAsFactors=FALSE)

text_size_axis_text <- 20
text_size_axis_title <- 24
text_size_legend_text <- 20
text_size_plot_tag <- 26
text_size_x_axis_bar_plot <- 18
shared_y_limits_fig1 <- c(-0.04, 0.16)
shared_y_breaks_fig1 <- seq(-0.04, 0.16, by=0.04)

common_plot_theme <- function() {
  theme_prism() +
    theme(
      axis.text=element_text(size=text_size_axis_text, face="plain", color="black"),
      axis.title=element_text(size=text_size_axis_title, face="plain", color="black"),
      axis.ticks=element_line(linewidth=0.5, color="black"),
      axis.line=element_line(linewidth=0.5, color="black"),
      legend.position="top",
      legend.text=element_text(size=text_size_legend_text, color="black"),
      legend.title=element_blank(),
      plot.title=element_text(hjust=0.5, size=text_size_axis_title),
      plot.tag.position="topleft",
      plot.tag=element_text(face="bold", size=text_size_plot_tag)
    )
}

# Panel a
a <- subset(dat, panel=="a")
a <- a[order(a$x_order),]
a$x_label <- factor(a$x_label, levels=a$x_label)

line_a <- ggplot(a, aes(x=x_label, y=estimate, group=1)) +
  geom_ribbon(aes(ymin=ci_lower, ymax=ci_upper, fill="95% CI"), alpha=0.5) +
  geom_line(aes(color="Estimated Coefficients"), linewidth=1) +
  geom_point(aes(color="Estimated Coefficients"), size=3) +
  geom_hline(yintercept=0, linetype="dashed", color="black") +
  scale_y_continuous(name="Estimated Coefficients", limits=shared_y_limits_fig1,
                     breaks=shared_y_breaks_fig1, guide="prism_offset") +
  scale_color_manual(values=c("Estimated Coefficients"="deepskyblue4")) +
  scale_fill_manual(values=c("95% CI"="lightblue")) +
  common_plot_theme() +
  theme(axis.text.x=element_blank(), axis.title.x=element_blank(),
        axis.ticks.x=element_blank(), axis.line.x=element_blank(),
        plot.margin=unit(c(0.5,0.5,0,0.5),"cm")) +
  labs(tag="a")

bar_a <- ggplot(a, aes(x=x_label, y=count)) +
  geom_col(fill="grey70", width=0.5) +
  scale_x_discrete(name="Temperature bins") +
  scale_y_continuous(limits=c(0,12000), breaks=seq(0,12000,4000), expand=c(0,0)) +
  theme_classic() +
  theme(
    axis.line.y=element_blank(), axis.ticks.y=element_blank(),
    axis.text.y=element_blank(), axis.title.y=element_blank(),
    axis.text.x=element_text(size=text_size_x_axis_bar_plot, color="black"),
    axis.title.x=element_text(size=text_size_axis_title, color="black"),
    panel.grid=element_blank(), plot.margin=unit(c(0,0.5,0.5,0.5),"cm")
  )
p1a <- line_a / bar_a + plot_layout(heights=c(3,1))

# Panel b
b <- subset(dat, panel=="b")
b$x_label <- factor(b$x_label, levels=unique(b$x_label[order(b$x_order)]))
b1 <- subset(b, series=="cumulative_lag1")
b2 <- subset(b, series=="cumulative_lag2")
bb <- merge(
  b1[,c("x_label","x_order","estimate","ci_lower","ci_upper")],
  b2[,c("x_label","estimate","ci_lower","ci_upper")],
  by="x_label", suffixes=c("_lag1","_lag2")
)
bb <- bb[order(bb$x_order),]
bb$x_label <- factor(bb$x_label, levels=bb$x_label)

p1b <- ggplot(bb, aes(x=x_label)) +
  geom_ribbon(aes(ymin=ci_lower_lag1, ymax=ci_upper_lag1, fill="95% CI (Lag 1)", group=1), alpha=0.3) +
  geom_ribbon(aes(ymin=ci_lower_lag2, ymax=ci_upper_lag2, fill="95% CI (Lag 2)", group=1), alpha=0.3) +
  geom_line(aes(y=estimate_lag1, color="Lag 1", group=1), linewidth=1) +
  geom_point(aes(y=estimate_lag1, color="Lag 1"), size=3) +
  geom_line(aes(y=estimate_lag2, color="Lag 2", group=1), linewidth=1, linetype="dashed") +
  geom_point(aes(y=estimate_lag2, color="Lag 2"), size=3, shape=21, fill="white") +
  geom_hline(yintercept=0, linetype="dashed", color="black") +
  scale_y_continuous(name="Estimated Coefficients", limits=shared_y_limits_fig1,
                     breaks=shared_y_breaks_fig1, guide="prism_offset") +
  xlab("Temperature bins") +
  scale_fill_manual(values=c("95% CI (Lag 1)"="lightblue","95% CI (Lag 2)"="lightpink")) +
  scale_color_manual(values=c("Lag 1"="blue","Lag 2"="red")) +
  common_plot_theme() + labs(tag="b")

# Panel c
c <- subset(dat, panel=="c")
c <- c[order(c$x_order),]
c$x_label <- factor(c$x_label, levels=c$x_label)
p1c <- ggplot(c, aes(x=x_label, y=estimate, group=1)) +
  geom_ribbon(aes(ymin=ci_lower, ymax=ci_upper, fill="95% CI"), alpha=0.5) +
  geom_line(aes(color="Estimated Coefficients"), linewidth=1) +
  geom_point(aes(color="Estimated Coefficients"), size=3) +
  geom_vline(xintercept=which(levels(c$x_label)=="-1"), linetype="dashed", linewidth=0.5) +
  geom_hline(yintercept=0, linetype="dashed", linewidth=0.5) +
  scale_y_continuous(name="Estimated Coefficients", limits=shared_y_limits_fig1,
                     breaks=shared_y_breaks_fig1, guide="prism_offset") +
  xlab("Pilot month") +
  scale_color_manual(values=c("Estimated Coefficients"="deepskyblue4")) +
  scale_fill_manual(values=c("95% CI"="lightblue")) +
  common_plot_theme() + labs(tag="c")

# Panel d
d <- subset(dat, panel=="d")
d$x_label <- factor(d$x_label, levels=unique(d$x_label[order(d$x_order)]))
baseline_d <- subset(d, series=="Baseline")
pilot_d <- subset(d, series=="In Pilot Policy Counties")
nopilot_d <- subset(d, series=="No Pilot")
nosub_d <- subset(d, series=="No Subsidy")
precovid_d <- subset(d, series=="Pre-COVID")

p1d <- ggplot() +
  geom_ribbon(
    data=baseline_d,
    aes(x=x_label, ymin=ci_lower, ymax=ci_upper, fill="Baseline CI", group=1),
    alpha=0.5
  ) +
  geom_point(
    data=baseline_d,
    aes(x=x_label, y=estimate, color="Baseline"),
    size=3, shape=22, fill="deepskyblue4"
  ) +
  geom_line(
    data=pilot_d,
    aes(x=x_label, y=estimate, color="In Pilot Policy Counties", group=1),
    linewidth=1, linetype="dotdash"
  ) +
  geom_point(
    data=pilot_d,
    aes(x=x_label, y=estimate, color="In Pilot Policy Counties"),
    size=3, shape=21, fill="red"
  ) +
  geom_line(
    data=nopilot_d,
    aes(x=x_label, y=estimate, color="No Pilot", group=1),
    linewidth=1, linetype="dotted"
  ) +
  geom_point(
    data=nopilot_d,
    aes(x=x_label, y=estimate, color="No Pilot"),
    size=3, shape=24, fill="orange"
  ) +
  geom_line(
    data=nosub_d,
    aes(x=x_label, y=estimate, color="No Subsidy", group=1),
    linewidth=1, linetype="twodash"
  ) +
  geom_point(
    data=nosub_d,
    aes(x=x_label, y=estimate, color="No Subsidy"),
    size=3, shape=23, fill="purple"
  ) +
  geom_line(
    data=precovid_d,
    aes(x=x_label, y=estimate, color="Pre-COVID", group=1),
    linewidth=1, linetype="dashed"
  ) +
  geom_point(
    data=precovid_d,
    aes(x=x_label, y=estimate, color="Pre-COVID"),
    size=3, shape=18, fill="blue"
  ) +
  geom_hline(yintercept=0, linetype="dashed", color="black") +
  scale_y_continuous(
    name="Estimated Coefficients",
    limits=shared_y_limits_fig1,
    breaks=shared_y_breaks_fig1,
    guide="prism_offset"
  ) +
  xlab("Temperature bins") +
  scale_fill_manual(values=c("Baseline CI"="lightblue")) +
  scale_color_manual(
    values=c(
      "Baseline"="deepskyblue4",
      "In Pilot Policy Counties"="red",
      "No Pilot"="orange",
      "No Subsidy"="purple",
      "Pre-COVID"="blue"
    ),
    breaks=c("Baseline","In Pilot Policy Counties","No Pilot","No Subsidy","Pre-COVID")
  ) +
  common_plot_theme() +
  guides(color=guide_legend(nrow=2, byrow=TRUE)) +
  labs(tag="d")

final_plot <- (p1a | p1b) / (p1c | p1d)

ggsave(file.path(output_dir,"Figure_1.pdf"), final_plot, width=22, height=14,
       device=cairo_pdf, bg="white", limitsize=FALSE)
ggsave(file.path(output_dir,"Figure_1.png"), final_plot, width=22, height=14,
       dpi=300, bg="white", limitsize=FALSE)
message("Figure 1 reproduced successfully.")
