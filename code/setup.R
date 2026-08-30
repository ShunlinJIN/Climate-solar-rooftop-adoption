packages <- c(
  "cowplot",
  "data.table",
  "dplyr",
  "ggplot2",
  "ggprism",
  "gridExtra",
  "patchwork",
  "readr",
  "scales",
  "tidyr"
)

missing <- packages[
  !vapply(packages, requireNamespace, logical(1), quietly = TRUE)
]

if (length(missing) > 0) {
  install.packages(
    missing,
    repos = "https://cloud.r-project.org"
  )
}

message("R package setup complete.")