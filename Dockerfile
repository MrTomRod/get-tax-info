# Stage 1: Download BUSCO lineages
FROM docker.io/ezlabgva/busco:v6.0.0_cv1 AS downloader
USER root
RUN busco --download bacteria_odb12 --download_path /busco_downloads

# Prepare a minimal structure with only the config files (enough for get-tax-info to index)
RUN mkdir /minimal && \
    cd /busco_downloads && \
    find lineages -name "dataset.cfg" -exec cp --parents {} /minimal \;

# Stage 2: Final image
FROM ghcr.io/astral-sh/uv:python3.14-alpine

# Install get-tax-info
RUN uv pip install --system get-tax-info

# Create database directory
ENV GET_TAX_INFO_DB="/database/taxdump.db"
RUN mkdir -p /database

# Download NCBI taxonomy data
RUN get-tax-info init

# Copy ONLY the minimal lineages structure from downloader stage, index, and cleanup in one layer
COPY --from=downloader /minimal /busco_downloads
RUN get-tax-info taxid-to-busco-dataset --taxid 2 --busco_download_path /busco_downloads && \
    rm -rf /busco_downloads

WORKDIR /data

# podman build . --tag taxid-tools:latest
# podman run --rm taxid-tools:latest get-tax-info taxid-to-busco-dataset --taxid 2
