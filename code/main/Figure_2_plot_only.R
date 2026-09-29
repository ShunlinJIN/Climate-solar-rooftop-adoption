
rm(list = ls())
source(file.path(dirname(normalizePath(sub("^--file=", "", commandArgs(trailingOnly=FALSE)[grep("^--file=", commandArgs(trailingOnly=FALSE))]), winslash="/")), "_paths_and_note.R"))

required_packages <- c("ggplot2","ggprism","patchwork")
missing <- required_packages[!vapply(required_packages, requireNamespace, logical(1), quietly=TRUE)]
if (length(missing)) stop("Missing R package(s): ", paste(missing, collapse=", "))
suppressPackageStartupMessages({
  library(ggplot2); library(ggprism); library(patchwork)
})

dat <- read.csv(file.path(data_dir,"figure2_plot_data.csv"), stringsAsFactors=FALSE, check.names=FALSE)
tests <- read.csv(file.path(data_dir,"figure2_pairwise_tests.csv"), stringsAsFactors=FALSE, check.names=FALSE)

text_size_axis_text <- 14
text_size_axis_title <- 16
text_size_legend_text <- 14
text_size_annotate_text <- 5
text_size_plot_tag <- 18

common_plot_theme <- function() {
  theme_prism() +
    theme(
      axis.text=element_text(size=text_size_axis_text, face="plain", color="black"),
      axis.title=element_text(size=text_size_axis_title, face="plain", color="black"),
      axis.ticks=element_line(linewidth=0.5),
      axis.line=element_line(linewidth=0.5),
      axis.text.x=element_text(angle=0,hjust=0.5),
      legend.position="top",
      legend.text=element_text(size=text_size_legend_text),
      legend.title=element_blank(),
      panel.spacing=unit(1.5,"cm"),
      plot.title=element_text(hjust=0.5),
      plot.margin=unit(c(0.5,0.5,0.5,0.5),"cm")
    )
}

add_bracket <- function(p, x1, x2, y, label, height=0.7, label_offset=0.85) {
  p +
    annotate("segment", x=x1, xend=x1+0.1, y=y, yend=y, color="darkgreen", linewidth=0.5) +
    annotate("segment", x=x1+0.1, xend=x2-0.1, y=y, yend=y, color="darkgreen", linetype="dashed", linewidth=0.5) +
    annotate("segment", x=x2-0.1, xend=x2, y=y, yend=y, color="darkgreen", linewidth=0.5) +
    annotate("segment", x=x1, xend=x1, y=y-height, yend=y, color="darkgreen", linewidth=0.5) +
    annotate("segment", x=x2, xend=x2, y=y-height, yend=y, color="darkgreen", linewidth=0.5) +
    annotate("text", x=(x1+x2)/2, y=y+label_offset, label=label, size=text_size_annotate_text)
}

make_bar <- function(panel_id, xlabel) {
  x <- dat[dat$panel == panel_id, , drop=FALSE]
  x <- x[order(x$x_order),]
  x$x_label <- factor(x$x_label, levels=x$x_label)
  p <- ggplot(x, aes(x=x_label, y=100*estimate)) +
    geom_col(aes(fill="Estimated Impacts"), width=0.6, alpha=0.8) +
    geom_errorbar(aes(ymin=100*ci_lower, ymax=100*ci_upper, color="95% CI"), width=0.1, linewidth=0.5) +
    scale_y_continuous(name="Estimated Impacts (%)", breaks=seq(0,15,3), limits=c(0,16), guide="prism_offset") +
    scale_x_discrete(name=xlabel) +
    scale_fill_manual(values=c("Estimated Impacts"="cyan4")) +
    scale_color_manual(values=c("95% CI"="black")) +
    common_plot_theme()
  p
}

p2a <- make_bar("a","Different historical average temperature")
p2a <- add_bracket(p2a,1,2,14.0,subset(tests,panel=="a")$p_label[1])
p2a <- add_bracket(p2a,3,4,14.45,subset(tests,panel=="a")$p_label[2])

p2b <- make_bar("b","Different historical temperature fluctuation")
p2b <- add_bracket(p2b,1,2,14.0,subset(tests,panel=="b")$p_label[1])
p2b <- add_bracket(p2b,3,4,14.0,subset(tests,panel=="b")$p_label[2])

p2c <- make_bar("c","Solar radiation")
p2c <- add_bracket(p2c,1,2,14.0,subset(tests,panel=="c")$p_label[1])

p2d <- make_bar("d","Land slope")
p2d <- add_bracket(p2d,1,2,14.0,subset(tests,panel=="d")$p_label[1])

p2e <- make_bar("e","Income level")
p2e <- add_bracket(p2e,1,2,14.0,subset(tests,panel=="e")$p_label[1])

f <- subset(dat, panel=="f")
f <- f[order(f$x_order),]
f$x_label <- factor(f$x_label, levels=f$x_label)
p2f <- ggplot(f, aes(x=x_label, y=estimate, group=1)) +
  geom_ribbon(aes(ymin=ci_lower,ymax=ci_upper,fill="95% CI"),alpha=0.8) +
  geom_line(aes(color="Estimated Coefficients"),linewidth=1) +
  geom_point(aes(color="Estimated Coefficients"),size=3) +
  geom_vline(xintercept=which(levels(f$x_label)=="-1"),linetype="dashed",linewidth=0.5) +
  geom_hline(yintercept=0,linetype="dashed",linewidth=0.5) +
  scale_y_continuous(name="Estimated Coefficients",
                     breaks=c(-0.025,0,0.025,0.050,0.075),
                     limits=c(-0.025,0.075),guide="prism_offset") +
  xlab("Months before and after PV loans rollout") +
  scale_color_manual(values=c("Estimated Coefficients"="azure4")) +
  scale_fill_manual(values=c("95% CI"="cyan4")) +
  common_plot_theme()

combined <- (p2a+p2b+p2c)/(p2d+p2e+p2f) +
  plot_annotation(tag_levels='a') &
  theme(plot.tag.position='topleft',
        plot.tag=element_text(face='bold',size=text_size_plot_tag))

ggsave(file.path(output_dir,"Figure_2.pdf"),combined,width=18,height=12,device=cairo_pdf,bg="white",limitsize=FALSE)
ggsave(file.path(output_dir,"Figure_2.png"),combined,width=18,height=12,dpi=300,bg="white",limitsize=FALSE)
message("Figure 2 reproduced successfully.")
