# GENESIS

**GEneral Nexus for Experimental Software and Informative Scripts (Odds and Ends)**

## Overview
GENESIS is a collection of experimental software tools and informative scripts focused on computer vision, camera integration, and hardware interaction for Raspberry Pi and NVIDIA Jetson platforms. The repository provides ready-to-use solutions for various computer vision and streaming applications.

## Components

### 1. Pi ChatGPT Vision Trigger
A sophisticated computer vision application that uses OpenAI's Vision API for GPIO control:
- Real-time image capture using libcamera
- Text detection via OpenAI's Vision API
- Configurable GPIO triggers based on detected text
- Live preview with pygame display
- Comprehensive logging system
- Rate limiting for API cost optimization
- Support for various GPIO devices (LEDs, relays, servos, etc.)

[Learn more about Pi ChatGPT Vision Trigger](pi_chatgpt_vision_trigger/README.md)

### 2. NVIDIA RTSP Server (WIP)
A flexible RTSP streaming server for NVIDIA Jetson platforms:
- Support for multiple camera types:
  - CSI cameras
  - USB cameras
  - ZED cameras
- Configurable resolution, framerate, and bitrate
- H264 hardware encoding using NVIDIA encoders
- Easy-to-use command line interface
- Supports multiple camera configurations

### 3. Simple PiCamera HUD
A lightweight heads-up display implementation for Raspberry Pi cameras:
- Real-time camera feed display
- FPS counter
- System time overlay
- Support for different resolutions
- Rotation options
- Fullscreen toggle support
- Clean shutdown capabilities

## Installation

Each component has its own installation requirements. Please refer to the respective directories for detailed setup instructions:

- [Pi ChatGPT Vision Trigger Installation](pi_chatgpt_vision_trigger/README.md#installation)
- Jetson RTSP Server setup instructions are available in the `jetson_rtsp_server` directory
- PiCamera HUD can be run directly with Python after installing the required dependencies

## Common Requirements
- Python 3.7+
- Appropriate hardware (Raspberry Pi or NVIDIA Jetson)
- Camera modules (specific requirements vary by component)

## License
This project is licensed under the GNU General Public License v3.0 (GPLv3). See the [LICENSE](LICENSE) file for details.

## Credits
- Author and Maintainer: Kris Kersey <kris@kerseyfabrications.com>
- Original PiCamera HUD Concept: Jamie (@MrInquisitiveFace)
- Development Assistance: OpenAI's ChatGPT and Anthropic's Claude

## Contributing
Contributions are welcome! Please feel free to submit pull requests or create issues for bugs and feature requests.

---
*Part of The OASIS Project*
