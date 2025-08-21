#!/usr/bin/env bash
set -e

DATASET="owner/dataset-slug"    # ← replace once
TARGET_DIR="data"               # keep relative to project root

kaggle datasets download -d "$DATASET" -p "$TARGET_DIR" --unzip --force
echo "[$(date)]  Dataset refreshed."
