#!/bin/bash

# Install system dependencies including build requirements
sudo apt-get update
sudo apt-get install -y \
    python3-gi \
    python3-gst-1.0 \
    gstreamer1.0-rtsp \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    libcairo2-dev \
    pkg-config \
    python3-dev \
    libgirepository1.0-dev \
    gir1.2-gstreamer-1.0 \
    gir1.2-gst-rtsp-server-1.0 \
    v4l-utils

# Note: ZED SDK should be installed separately from the ZED website
# https://www.stereolabs.com/developers/release/

# Create and activate virtual environment
python3 -m venv env
source env/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install pycairo PyGObject

echo "Setup complete! Use 'source env/bin/activate' to activate the virtual environment"
