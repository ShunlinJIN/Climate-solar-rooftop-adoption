
# Shared helper for standalone main-figure reproduction scripts.

get_script_dir <- function() {
  args <- commandArgs(trailingOnly = FALSE)
  file_arg <- grep("^--file=", args, value = TRUE)
  if (length(file_arg) == 1L) {
    return(dirname(normalizePath(sub("^--file=", "", file_arg), winslash = "/", mustWork = TRUE)))
  }
  return(normalizePath(getwd(), winslash = "/", mustWork = TRUE))
}

script_dir <- get_script_dir()
package_root <- normalizePath(file.path(script_dir, ".."), winslash = "/", mustWork = FALSE)
data_dir <- file.path(package_root, "data")
output_dir <- file.path(package_root, "output")
if (!dir.exists(output_dir)) dir.create(output_dir, recursive = TRUE)

data_access_note <- paste(
  "The household-, installation-, and provider-level microdata used to estimate",
  "some results in this figure are subject to data-use restrictions and",
  "cannot be publicly released. This script reproduces the published figure",
  "from non-identifying aggregate plotting inputs supplied with the package;",
  "it does not re-estimate restricted-data models."
)
message(data_access_note)

