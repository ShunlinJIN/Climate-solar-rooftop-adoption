# hash:sha256:46eed2043457611915a4ff5c9e8175c5faec6c84612802460501659bf66465cd
FROM registry.codeocean.com/codeocean/r-studio:r-4.5.1-1.2204.0-rstudio-server-2025.05.1-513-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        python3-geopandas=0.10.2-1ubuntu0.1 \
        python3-matplotlib=3.5.1-2build1 \
        python3-numpy=1:1.21.5-1ubuntu22.04.1 \
        python3-pandas=1.3.5+dfsg-3 \
        python3-scipy=1.8.0-1exp2ubuntu1 \
        python3-shapely=1.8.0-1build1 \
    && rm -rf /var/lib/apt/lists/*

RUN Rscript -e 'remotes::install_version("MatchIt", "4.7.2")' \
    && Rscript -e 'remotes::install_version("broom", "1.0.13")' \
    && Rscript -e 'remotes::install_version("cobalt", "4.6.2")' \
    && Rscript -e 'remotes::install_version("cowplot", "1.2.0")' \
    && Rscript -e 'remotes::install_version("dplyr", "1.2.1")' \
    && Rscript -e 'remotes::install_version("exactextractr")' \
    && Rscript -e 'remotes::install_version("fixest", "0.14.0")' \
    && Rscript -e 'remotes::install_version("flextable")' \
    && Rscript -e 'remotes::install_version("ggplot2", "4.0.3")' \
    && Rscript -e 'remotes::install_version("ggprism", "1.0.7")' \
    && Rscript -e 'remotes::install_version("gt", "1.3.0")' \
    && Rscript -e 'remotes::install_version("lmtest", "0.9-40")' \
    && Rscript -e 'remotes::install_version("lubridate", "1.9.5")' \
    && Rscript -e 'remotes::install_version("ncdf4")' \
    && Rscript -e 'remotes::install_version("officer", "0.7.3")' \
    && Rscript -e 'remotes::install_version("patchwork", "1.3.2")' \
    && Rscript -e 'remotes::install_version("readr", "2.2.0")' \
    && Rscript -e 'remotes::install_version("scales", "1.4.0")' \
    && Rscript -e 'remotes::install_version("sf")' \
    && Rscript -e 'remotes::install_version("stringr", "1.6.0")' \
    && Rscript -e 'remotes::install_version("terra")' \
    && Rscript -e 'remotes::install_version("tidyr", "1.3.2")' \
    && Rscript -e 'remotes::install_version("tidyverse", "2.0.0")' \
    && Rscript -e 'remotes::install_version("zoo", "1.8-15")'

COPY postInstall /
RUN /postInstall
