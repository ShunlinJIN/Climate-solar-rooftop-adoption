
rm(list = ls())
source(file.path(dirname(normalizePath(sub("^--file=", "", commandArgs(trailingOnly=FALSE)[grep("^--file=", commandArgs(trailingOnly=FALSE))]), winslash="/")), "_paths_and_note.R"))

required_packages <- c("ggplot2","ggprism","patchwork")
missing <- required_packages[!vapply(required_packages, requireNamespace, logical(1), quietly=TRUE)]
if (length(missing)) stop("Missing R package(s): ", paste(missing, collapse=", "))
suppressPackageStartupMessages({
  library(ggplot2); library(ggprism); library(patchwork)
})

dat <- read.csv(file.path(data_dir,"figure4_plot_data.csv"),stringsAsFactors=FALSE,check.names=FALSE)

text_size_axis_text_y <- 18
text_size_axis_text_x <- 12
text_size_axis_title <- 20
text_size_legend_text <- 18
text_size_plot_tag <- 22
text_size_annotation <- 6

theme_base <- function() {
  theme_prism() +
    theme(
      axis.text.y=element_text(size=text_size_axis_text_y,face="plain",color="black"),
      axis.title=element_text(size=text_size_axis_title,face="plain",color="black"),
      axis.ticks=element_line(linewidth=0.5,color="black"),
      axis.line=element_line(linewidth=0.5,color="black"),
      legend.position="top",
      legend.text=element_text(size=text_size_legend_text,color="black"),
      legend.title=element_blank(),
      plot.tag.position="topleft",
      plot.tag=element_text(face="bold",size=text_size_plot_tag)
    )
}

make_lag_panel <- function(panel_id, xlabel, ylim, breaks) {
  x <- dat[dat$panel == panel_id, , drop=FALSE]
  x <- x[order(x$x_order),]
  x$x_label <- factor(x$x_label,levels=x$x_label)
  ggplot(x,aes(x=x_label,y=estimate)) +
    geom_errorbar(aes(ymin=ci_lower,ymax=ci_upper,color="95% CI"),width=0.2,linewidth=0.5) +
    geom_point(aes(color="Coefficients"),size=3) +
    geom_hline(yintercept=0,linetype="dashed",linewidth=0.5) +
    scale_y_continuous(name=expression(paste("Estimated Coefficients (",beta[k],")")),
                       breaks=breaks,limits=ylim,guide="prism_offset") +
    xlab(xlabel) +
    scale_color_manual(values=c("Coefficients"="darkcyan","95% CI"="black")) +
    theme_base() +
    theme(axis.text.x=element_text(size=text_size_axis_text_x,face="plain",angle=0,hjust=0.5))
}

p4a <- make_lag_panel("a","Lagged variables (RRPV-only adopter)",c(-0.06,0.12),seq(-0.06,0.12,0.06)) + labs(tag="a")
p4b <- make_lag_panel("b","Lagged variables (RRPV-BS adopter)",c(-0.05,0.15),seq(-0.05,0.15,0.05)) + labs(tag="b")

make_income_panel <- function(panel_id, xlabel, tag) {
  x <- dat[dat$panel == panel_id, , drop=FALSE]
  x <- x[order(x$x_order),]
  x$x_label <- factor(x$x_label,levels=x$x_label)
  all_est <- x$estimate[x$x_order==1][1]
  p <- ggplot(x,aes(x=x_label,y=estimate)) +
    geom_errorbar(aes(ymin=ci_lower,ymax=ci_upper,color="95% CI"),width=0.2,linewidth=0.5) +
    geom_point(aes(color="Coefficients"),size=3) +
    geom_hline(yintercept=0,linetype="dashed",linewidth=0.5) +
    annotate("text",x=2.2,y=all_est,label=sprintf("All samples (%.4f)",all_est),
             size=text_size_annotation,hjust=0,color="black") +
    annotate("segment",x=2.1,xend=1.3,y=all_est,yend=all_est,
             arrow=arrow(length=unit(0.2,"cm"),type="closed"),color="red",linewidth=0.8) +
    scale_y_continuous(name="Estimated Coefficients",
                       breaks=seq(-0.05,0.20,0.05),limits=c(-0.05,0.20),guide="prism_offset") +
    xlab(xlabel) +
    scale_color_manual(values=c("Coefficients"="darkcyan","95% CI"="black")) +
    theme_base() +
    theme(axis.text.x=element_text(size=text_size_axis_text_x,face="plain",angle=0,hjust=0.5)) +
    labs(tag=tag)
  p
}
p4c <- make_income_panel("c","Income level (RRPV-only adopter)","c")
p4d <- make_income_panel("d","Income level (RRPV-BS adopter)","d")

final_plot <- (p4a|p4b)/(p4c|p4d)
ggsave(file.path(output_dir,"Figure_4.pdf"),final_plot,width=18,height=14,device=cairo_pdf,bg="white",limitsize=FALSE)
ggsave(file.path(output_dir,"Figure_4.png"),final_plot,width=18,height=14,dpi=300,bg="white",limitsize=FALSE)
message("Figure 4 reproduced successfully.")
