#!/usr/bin/env python3
"""Shared path/config constants for the Haque pipeline.

Generalized from the original hardcoded paths so the pipeline is portable.
Adjust BASE_DIR / WORK_DIR / DEST_DIR to your environment.
"""
import os

# --- your environment --------------------------------------------------------
BASE_DIR = os.environ.get("HAQUE_BASE", "/path/to/Haque")   # project root
WORK_DIR = os.path.join(BASE_DIR, "work", "polyebook")
DEST_DIR = os.path.join(BASE_DIR, "master")                 # where PDFs land
BOOKS_DIR = os.path.join(BASE_DIR, "Books")                 # organized dept/sem tree
ARCH_DIR = os.path.join(BASE_DIR, "archives")
REPO_DIR = os.path.join(BASE_DIR, "publish_repo")
SRC_DIR = os.path.join(BASE_DIR, "work", "source_data")
# -----------------------------------------------------------------------------

os.makedirs(WORK_DIR, exist_ok=True)
os.makedirs(DEST_DIR, exist_ok=True)
