# =============================================================================
# Supplementary Fig. 27: Conditional out-of-sample validation of hourly battery
# dispatch and residual grid flows
#
# PUBLIC PLOT-ONLY REPRODUCTION
# -----------------------------
# Uses only de-identified plotting pairs + aggregate complete-sample metrics.
# It does NOT read restricted-source household telemetry and does NOT re-estimate the
# battery-dispatch model.
# =============================================================================

rm(list = ls())

required <- c("data.table", "ggplot2", "patchwork")
missing <- required[
  !vapply(required, requireNamespace, logical(1), quietly = TRUE)
]
if (length(missing)) {
  stop("Install missing R package(s): ", paste(missing, collapse = ", "))
}

suppressPackageStartupMessages({
  library(data.table)
  library(ggplot2)
  library(patchwork)
})

get_script_dir <- function() {
  x <- grep("^--file=", commandArgs(trailingOnly = FALSE), value = TRUE)
  if (length(x) == 1L) {
    return(dirname(normalizePath(sub("^--file=", "", x), winslash = "/")))
  }
  normalizePath(getwd(), winslash = "/")
}

code_dir <- get_script_dir()
root <- normalizePath(file.path(code_dir, ".."), winslash = "/", mustWork = FALSE)
data_dir <- file.path(root, "data")
out_dir <- file.path(root, "output")
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

plot_file <- file.path(data_dir, "supp_fig27_battery_dispatch_plot.csv")
metric_file <- file.path(data_dir, "supp_fig27_battery_dispatch_metrics.csv")

if (!file.exists(plot_file)) {
  stop(
    "Missing de-identified Fig.27 plotting data:\n", plot_file,
    "\nOn the author's local machine first run:\n",
    "  export_supp_fig27_plot_data_LOCAL_ONLY.R"
  )
}
if (!file.exists(metric_file)) stop("Missing Fig.27 metrics: ", metric_file)

plot_data <- fread(plot_file)
metrics <- fread(metric_file)

required_plot <- c("flow", "observed", "predicted")
if (!identical(names(plot_data), required_plot)) {
  stop(
    "Fig.27 plotting CSV must contain ONLY: ",
    paste(required_plot, collapse = ", ")
  )
}

plot_flows <- c(
  "PV-to-battery",
  "Battery-to-load",
  "Grid-to-load",
  "PV export"
)

if (!setequal(unique(plot_data$flow), plot_flows)) {
  stop("Fig.27 plotting data do not contain the four expected flows.")
}

display_quantile <- 0.9975
point_colour <- "#1f77b4"
reference_colour <- "#d62728"

make_panel <- function(flow_name, tag) {
  d <- plot_data[
    flow == flow_name &
      is.finite(observed) &
      is.finite(predicted)
  ]
  m <- metrics[flow == flow_name]

  if (nrow(m) != 1L) {
    stop("Expected one metric row for ", flow_name)
  }

  x_limit <- as.numeric(
    quantile(d$observed, display_quantile, na.rm = TRUE, names = FALSE)
  )
  y_limit <- as.numeric(
    quantile(d$predicted, display_quantile, na.rm = TRUE, names = FALSE)
  )
  common_limit <- max(x_limit, y_limit, 1e-6)

  metric_text <- sprintf(
    paste0(
      "Predictive R虏 = %.3f\n",
      "RMSE = %.3f kWh\n",
      "MAE = %.3f kWh\n",
      "Bias = %.3f kWh"
    ),
    m$predictive_r_squared,
    m$rmse_kwh,
    m$mae_kwh,
    m$bias_kwh
  )

  ggplot(d, aes(x = observed, y = predicted)) +
    geom_point(alpha = 0.18, size = 0.65, colour = point_colour) +
    geom_abline(
      intercept = 0, slope = 1,
      linetype = "dashed", colour = reference_colour, linewidth = 0.8
    ) +
    annotate(
      "text",
      x = 0.04 * common_limit,
      y = 0.96 * common_limit,
      label = metric_text,
      hjust = 0, vjust = 1,
      size = 3.2, family = "Arial", lineheight = 1.03
    ) +
    coord_equal(
      xlim = c(0, common_limit),
      ylim = c(0, common_limit),
      expand = FALSE
    ) +
    labs(
      title = flow_name,
      tag = tag,
      x = paste("Observed hourly", flow_name, "(kWh)"),
      y = paste("Predicted hourly", flow_name, "(kWh)")
    ) +
    theme_classic(base_size = 11, base_family = "Arial") +
    theme(
      plot.title = element_text(hjust = 0.5, face = "bold"),
      plot.tag = element_text(face = "bold", size = 15),
      axis.text = element_text(colour = "black")
    )
}

panels <- Map(make_panel, plot_flows, c("a", "b", "c", "d"))
fig <- (panels[[1]] + panels[[2]]) / (panels[[3]] + panels[[4]])

ggsave(
  file.path(out_dir, "Supplementary_Fig_27.pdf"),
  fig, width = 10, height = 9, units = "in",
  device = cairo_pdf, bg = "white"
)
ggsave(
  file.path(out_dir, "Supplementary_Fig_27.png"),
  fig, width = 10, height = 9, units = "in",
  dpi = 1200, bg = "white"
)

message("Supplementary Fig. 27 reproduced from de-identified plotting inputs.")

