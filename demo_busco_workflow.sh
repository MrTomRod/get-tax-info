#!/bin/bash
set -e

# demo_busco_workflow.sh
# This script demonstrates how to download BUSCO lineages using Podman
# and use get-tax-info to map TaxIDs to these datasets.

BUSCO_IMAGE="docker.io/ezlabgva/busco:v6.0.0_cv1"
LINEAGE="bacteria_odb12"
DOWNLOAD_DIR="$(pwd)/busco_downloads"

echo "=== 1. Creating download directory ==="
mkdir -p "$DOWNLOAD_DIR"

echo "=== 2. Downloading BUSCO lineage using Podman ==="
# Note: Using :Z for SELinux compatibility on Fedora
podman run --rm \
    -v "$DOWNLOAD_DIR":/busco_downloads:Z \
    "$BUSCO_IMAGE" \
    busco --download "$LINEAGE" --download_path /busco_downloads

echo "=== 3. Mapping a TaxID to the BUSCO dataset ==="
# This will scan 'busco_downloads' and create 'busco_datasets.json' in your cache
# TaxID 2 (Bacteria) should map to 'prokaryota_odb10'
uv run get-tax-info taxid-to-busco-dataset \
    --taxid 2 \
    --busco_download_path "$DOWNLOAD_DIR"

echo "=== Success ==="
echo "The mapping is now stored in your local cache (~/.cache/get-tax-info/)."
echo "Future calls to 'taxid-to-busco-dataset' for descendants of Bacteria (TaxID 2) will be instant."
