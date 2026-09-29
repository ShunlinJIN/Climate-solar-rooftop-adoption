

library(ggplot2)
library(ggprism)
library(patchwork)

text_size_axis_text_y <- 18
text_size_axis_text_x <- 12
text_size_axis_title <- 20
text_size_legend_text <- 18
text_size_plot_tag <- 22
text_size_annotation <- 6

common_plot_theme_base <- function() {
  theme_prism() +
    theme(
      axis.text.y = element_text(size = text_size_axis_text_y, face = "plain", color = "black"),
      axis.title = element_text(size = text_size_axis_title, face = "plain", color = "black"),
      axis.ticks = element_line(linewidth = 0.5, color = "black"),
      axis.line = element_line(linewidth = 0.5, color = "black"),
      legend.position = "top",
      legend.text = element_text(size = text_size_legend_text, color = "black"),
      legend.title = element_blank(),
      plot.title = element_text(hjust = 0.5, size = text_size_axis_title),
      plot.tag.position = 'topleft',
      plot.tag = element_text(face = 'bold', size = text_size_plot_tag)
    )
}

script_arg <- grep("^--file=", commandArgs(trailingOnly = FALSE), value = TRUE)
if (length(script_arg)) {
  script_dir <- dirname(normalizePath(sub("^--file=", "", script_arg[1]), winslash = "/"))
} else {
  source_file <- tryCatch(sys.frame(1)$ofile, error = function(e) NULL)
  script_dir <- if (!is.null(source_file)) dirname(normalizePath(source_file, winslash = "/")) else getwd()
  if (!file.exists(file.path(script_dir, "Figure_4_plot_only.R")) && dir.exists(file.path(script_dir, "code"))) script_dir <- file.path(script_dir, "code")
}
package_root <- normalizePath(file.path(script_dir, ".."), winslash = "/")
output_dir <- file.path(package_root, "output")
dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
plot_data <- read.csv(file.path(package_root, "data", "figure4_plot_data.csv"), fileEncoding = "UTF-8-BOM", stringsAsFactors = FALSE)
plot_data <- plot_data[order(plot_data$panel, plot_data$x_order), ]
stopifnot(identical(as.integer(table(plot_data$panel)), c(5L, 5L, 11L, 4L)))
stopifnot(max(abs(plot_data$ci_lower - (plot_data$estimate - 1.96 * plot_data$std_error))) < 1e-8)
stopifnot(max(abs(plot_data$ci_upper - (plot_data$estimate + 1.96 * plot_data$std_error))) < 1e-8)
stopifnot(abs(plot_data$estimate[plot_data$panel == "a" & plot_data$x_order == 1] - 0.079) < 1e-8)
for (id in c("a", "b")) {
  z <- plot_data[plot_data$panel == id, ]
  stopifnot(abs(z$estimate[1] - sum(z$estimate[-1])) < 1e-8)
}


coef_p1 <- plot_data[plot_data$panel == "a", "estimate"]
lower_ci_p1 <- plot_data[plot_data$panel == "a", "ci_lower"]
upper_ci_p1 <- plot_data[plot_data$panel == "a", "ci_upper"]

Income_Level_p1 <- c("Total Effect", "Current", "Lag 1", "Lag 2", "Lag 3")

data_p1 <- data.frame(
  Income_Level = factor(Income_Level_p1, levels = Income_Level_p1),
  coef = coef_p1,
  lower_ci = lower_ci_p1,
  upper_ci = upper_ci_p1
)

p1 <- ggplot(data_p1, aes(x = Income_Level, y = coef)) +
  geom_errorbar(aes(ymin = lower_ci, ymax = upper_ci, color = "95% CI"), width = 0.2, linewidth = 0.5) +
  geom_point(aes(color = "Coefficients"), size = 3) +
  geom_hline(yintercept = 0, linetype = "dashed", color = "black", linewidth = 0.5) +
  scale_y_continuous(
    name = expression(paste("Estimated Coefficients (", beta[k], ")")),
    breaks = seq(-0.06, 0.12, by = 0.06),
    limits = c(-0.06, 0.12),
    guide = "prism_offset"
  ) +
  xlab("Lagged variables (RRPV-only adopter)") +
  scale_color_manual(name = "Legend", values = c("Coefficients" = "darkcyan", "95% CI" = "black")) +
  common_plot_theme_base() +
  labs(tag = "a") +
  theme(
    axis.text.x = element_text(size = text_size_axis_text_x, face = "plain", angle = 0, hjust = 0.5, vjust = 0.5),
    plot.margin = unit(c(0.5, 0.5, 0.5, 0.5), "cm")
  )

coef_p2 <- plot_data[plot_data$panel == "b", "estimate"]
lower_ci_p2 <- plot_data[plot_data$panel == "b", "ci_lower"]
upper_ci_p2 <- plot_data[plot_data$panel == "b", "ci_upper"]

Income_Level_p2 <- c("Total Effect", "Current", "Lag 1", "Lag 2", "Lag 3")

data_p2 <- data.frame(
  Income_Level = factor(Income_Level_p2, levels = Income_Level_p2),
  coef = coef_p2,
  lower_ci = lower_ci_p2,
  upper_ci = upper_ci_p2
)

p2 <- ggplot(data_p2, aes(x = Income_Level, y = coef)) +
  geom_errorbar(aes(ymin = lower_ci, ymax = upper_ci, color = "95% CI"), width = 0.2, linewidth = 0.5) +
  geom_point(aes(color = "Coefficients"), size = 3) +
  geom_hline(yintercept = 0, linetype = "dashed", color = "black", linewidth = 0.5) +
  scale_y_continuous(
    name = expression(paste("Estimated Coefficients (", beta[k], ")")),
    breaks = seq(-0.05, 0.15, by = 0.05),
    limits = c(-0.05, 0.15),
    guide = "prism_offset"
  ) +
  xlab("Lagged variables (RRPV-BS adopter)") +
  scale_color_manual(name = "Legend", values = c("Coefficients" = "darkcyan", "95% CI" = "black")) +
  common_plot_theme_base() +
  labs(tag = "b") +
  theme(
    axis.text.x = element_text(size = text_size_axis_text_x, face = "plain", angle = 0, hjust = 0.5, vjust = 0.5),
    plot.margin = unit(c(0.5, 0.5, 0.5, 0.5), "cm")
  )


coef_p3 <- plot_data[plot_data$panel == "c", "estimate"]

lower_ci_p3 <- plot_data[plot_data$panel == "c", "ci_lower"]

upper_ci_p3 <- plot_data[plot_data$panel == "c", "ci_upper"]

Income_Level_p3 <- c(
  "baseline", "≤10%", "10-20%", "20-30%", "30-40%",
  "40-50%", "50-60%", "60-70%", "70-80%", "80-90%", "≥90%"
)

data_p3 <- data.frame(
  Income_Level = factor(Income_Level_p3, levels = Income_Level_p3),
  coef = coef_p3,
  lower_ci = lower_ci_p3,
  upper_ci = upper_ci_p3
)

p3 <- ggplot(data_p3, aes(x = Income_Level, y = coef)) +
  geom_errorbar(
    aes(ymin = lower_ci, ymax = upper_ci, color = "95% CI"),
    width = 0.2,
    linewidth = 0.5
  ) +
  geom_point(aes(color = "Coefficients"), size = 3) +
  geom_hline(
    yintercept = 0,
    linetype = "dashed",
    color = "black",
    linewidth = 0.5
  ) +
  annotate(
    "text",
    x = 2.2,
    y = 0.079,
    label = "All samples (0.0790)",
    size = text_size_annotation,
    hjust = 0,
    color = "black"
  ) +
  annotate(
    "segment",
    x = 2.1,
    xend = 1.3,
    y = 0.079,
    yend = 0.079,
    arrow = arrow(length = unit(0.2, "cm"), type = "closed"),
    color = "red",
    linewidth = 0.8
  ) +
  scale_y_continuous(
    name = "Estimated Coefficients",
    breaks = seq(-0.05, 0.2, by = 0.05),
    limits = c(-0.05, 0.2),
    guide = "prism_offset"
  ) +
  scale_x_discrete(
    name = "Income level (RRPV-only adopter)",
    labels = c(
      "baseline",
      expression(phantom(.) <= 10 * "%"),
      "10-20%", "20-30%", "30-40%", "40-50%",
      "50-60%", "60-70%", "70-80%", "80-90%",
      expression(phantom(.) >= 90 * "%")
    )
  ) +
  scale_color_manual(
    name = "Legend",
    values = c(
      "Coefficients" = "darkcyan",
      "95% CI" = "black"
    )
  ) +
  common_plot_theme_base() +
  labs(tag = "c") +
  theme(
    axis.text.x = element_text(
      size = text_size_axis_text_x,
      face = "plain",
      angle = 0,
      hjust = 0.5,
      vjust = 0.5
    ),
    plot.margin = unit(c(0.5, 0.5, 0.5, 0.5), "cm")
  )

coef_p4 <- plot_data[plot_data$panel == "d", "estimate"]

lower_ci_p4 <- plot_data[plot_data$panel == "d", "ci_lower"]

upper_ci_p4 <- plot_data[plot_data$panel == "d", "ci_upper"]

Income_Level_p4 <- c("baseline", "Low income", "Middle income", "High income")

data_p4 <- data.frame(
  Income_Level = factor(Income_Level_p4, levels = Income_Level_p4),
  coef = coef_p4,
  lower_ci = lower_ci_p4,
  upper_ci = upper_ci_p4
)

p4 <- ggplot(data_p4, aes(x = Income_Level, y = coef)) +
  geom_errorbar(
    aes(ymin = lower_ci, ymax = upper_ci, color = "95% CI"),
    width = 0.2,
    linewidth = 0.5
  ) +
  geom_point(aes(color = "Coefficients"), size = 3) +
  geom_hline(
    yintercept = 0,
    linetype = "dashed",
    color = "black",
    linewidth = 0.5
  ) +
  annotate(
    "text",
    x = 1.4,
    y = 0.114,
    label = "All samples (0.1140)",
    size = text_size_annotation,
    hjust = 0,
    color = "black"
  ) +
  annotate(
    "segment",
    x = 1.36,
    xend = 1.10,
    y = 0.114,
    yend = 0.114,
    arrow = arrow(length = unit(0.2, "cm"), type = "closed"),
    color = "red",
    linewidth = 0.8
  ) +
  scale_y_continuous(
    name = "Estimated Coefficients",
    breaks = seq(-0.05, 0.20, by = 0.05),
    limits = c(-0.05, 0.20),
    guide = "prism_offset"
  ) +
  scale_x_discrete(name = "Income level (RRPV-BS adopter)", labels = Income_Level_p4) +
  scale_color_manual(
    name = "Legend",
    values = c(
      "Coefficients" = "darkcyan",
      "95% CI" = "black"
    )
  ) +
  common_plot_theme_base() +
  labs(tag = "d") +
  theme(
    axis.text.x = element_text(
      size = text_size_axis_text_x,
      face = "plain",
      angle = 0,
      hjust = 0.5,
      vjust = 0.5
    ),
    plot.margin = unit(c(0.5, 0.5, 0.5, 0.5), "cm")
  )




final_combined_plot_4 <- (p1 | p2) / (p3 | p4)


for (fmt in c("pdf", "png", "svg")) {
  dest <- file.path(output_dir, paste0("Figure_4.", fmt))
  if (fmt == "pdf") {
    ggsave(dest, final_combined_plot_4, width=18, height=14, device=grDevices::cairo_pdf, bg="white", limitsize=FALSE)
  } else if (fmt == "svg") {
    ggsave(dest, final_combined_plot_4, width=18, height=14, device=grDevices::svg, bg="white", limitsize=FALSE)
  } else {
    ggsave(dest, final_combined_plot_4, width=18, height=14, dpi=300, device="png", type="cairo", bg="white", limitsize=FALSE)
  }
  message("Saved: ", normalizePath(dest, winslash="/"))
}
