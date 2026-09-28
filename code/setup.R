minimum_versions <- c(
  cowplot = "1.2.0", data.table = "1.14.10", dplyr = "1.1.4",
  ggplot2 = "4.0.3", ggprism = "1.0.7", gridExtra = "2.3",
  patchwork = "1.3.2", readr = "2.1.5", scales = "1.4.0", tidyr = "1.3.1"
)
needs_install <- names(minimum_versions)[vapply(names(minimum_versions), function(p) {
  # Read installed metadata without loading an older package namespace.
  tryCatch(
    utils::packageVersion(p, lib.loc = .libPaths()) < package_version(minimum_versions[[p]]),
    error = function(e) TRUE
  )
}, logical(1))]
if (length(needs_install)) {
  install.packages(needs_install, repos = "https://cloud.r-project.org")
}
unavailable <- names(minimum_versions)[vapply(names(minimum_versions), function(p) {
  # Read installed metadata without loading an older package namespace.
  tryCatch(
    utils::packageVersion(p, lib.loc = .libPaths()) < package_version(minimum_versions[[p]]),
    error = function(e) TRUE
  )
}, logical(1))]
if (length(unavailable)) stop("Required packages are unavailable or too old: ", paste(unavailable, collapse = ", "))
message("R package setup complete.")
