
rm(list = ls())
source(file.path(dirname(normalizePath(sub("^--file=", "", commandArgs(trailingOnly=FALSE)[grep("^--file=", commandArgs(trailingOnly=FALSE))]), winslash="/")), "_paths_and_note.R"))

required_packages <- c("ggplot2","ggprism","cowplot","grid")
missing <- required_packages[!vapply(required_packages, requireNamespace, logical(1), quietly=TRUE)]
if (length(missing)) stop("Missing R package(s): ", paste(missing, collapse=", "))
suppressPackageStartupMessages({
  library(ggplot2); library(ggprism); library(cowplot); library(grid)
})

dat <- read.csv(file.path(data_dir,"figure3_plot_data.csv"),stringsAsFactors=FALSE,check.names=FALSE)

text_size_axis_text <- 18
text_size_axis_title <- 20
text_size_legend_text <- 18
text_size_plot_tag <- 22
text_size_survey_x <- 10.5
shared_y_limits_fig3 <- c(-0.03,0.07)
shared_y_breaks_fig3 <- c(-0.03,0,0.03,0.06)

theme_base <- function() {
  theme_prism() +
    theme(
      axis.text=element_text(size=text_size_axis_text,face="plain",color="black"),
      axis.title=element_text(size=text_size_axis_title,face="plain",color="black"),
      axis.ticks=element_line(linewidth=0.5,color="black"),
      axis.line=element_line(linewidth=0.5,color="black"),
      legend.position="top",legend.justification="center",
      legend.direction="horizontal",
      legend.text=element_text(size=text_size_legend_text,color="black"),
      legend.title=element_blank(),
      plot.tag=element_text(face="bold",size=text_size_plot_tag)
    )
}

make_coef_panel <- function(panel_id, xlabel) {
  x <- dat[dat$panel == panel_id, , drop=FALSE]
  x <- x[order(x$x_order),]
  x$x_label <- factor(x$x_label,levels=x$x_label)
  ggplot(x,aes(x=x_label,y=estimate,group=1)) +
    geom_ribbon(aes(ymin=ci_lower,ymax=ci_upper,fill="95% CI"),alpha=0.5,color=NA) +
    geom_line(aes(color="Estimated Coefficients"),linewidth=1) +
    geom_point(aes(color="Estimated Coefficients"),size=3) +
    geom_hline(yintercept=0,linetype="dashed",linewidth=0.5) +
    scale_y_continuous(name="Estimated Coefficients",limits=shared_y_limits_fig3,
                       breaks=shared_y_breaks_fig3,guide="prism_offset") +
    xlab(xlabel) +
    scale_color_manual(values=c("Estimated Coefficients"="springgreen4")) +
    scale_fill_manual(values=c("95% CI"="aquamarine2")) +
    theme_base()
}

p3a <- make_coef_panel("a","Temperature bins")

b <- subset(dat,panel=="b")
b <- b[order(b$x_order),]
b$x_label <- factor(b$x_label,levels=b$x_label)
p3b <- ggplot(b,aes(x=x_label,y=share_percent)) +
  geom_errorbar(aes(ymin=ci_lower,ymax=ci_upper,color="95% CI"),width=0.12,linewidth=1.05) +
  geom_point(aes(color="Ranked among top three"),size=3.3) +
  scale_color_manual(values=c("95% CI"="aquamarine3","Ranked among top three"="springgreen4"),
                     breaks=c("95% CI","Ranked among top three")) +
  scale_y_continuous(name="Share ranking motive among top three (%)",
                     limits=c(-2,50),breaks=seq(0,50,10),
                     labels=function(x) paste0(x,"%"),guide="prism_offset") +
  xlab(NULL) + theme_base() +
  theme(axis.text.x=element_text(size=text_size_survey_x,lineheight=0.85,margin=margin(t=8)))

p3c <- make_coef_panel("c","Months before and after electricity outage") +
  geom_vline(xintercept=8, linetype="dashed", linewidth=0.5)
p3d <- make_coef_panel("d","Months before and after electricity outage") +
  geom_vline(xintercept=8, linetype="dashed", linewidth=0.5)

# Build directly as 2x2 while preserving final panel titles.
p3a <- p3a + ggtitle("RRPV-BS: temperature response")
p3b <- p3b + ggtitle("RRPV-BS: reliability motives")
p3c <- p3c + ggtitle("RRPV-BS: electricity-outage response")
p3d <- p3d + ggtitle("RRPV-only: electricity-outage response")

final_plot <- plot_grid(
  p3a,p3b,p3c,p3d,
  labels=c("a","b","c","d"),
  label_size=text_size_plot_tag,
  ncol=2,align="hv",axis="tblr"
)

ggsave(file.path(output_dir,"Figure_3.pdf"),final_plot,width=22,height=14,device=cairo_pdf,bg="white",limitsize=FALSE)
ggsave(file.path(output_dir,"Figure_3.png"),final_plot,width=22,height=14,dpi=300,bg="white",limitsize=FALSE)
message("Figure 3 reproduced successfully.")
