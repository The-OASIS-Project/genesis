# Pi ChatGPT Vision Trigger

A Raspberry Pi application that uses computer vision and OCR to trigger GPIO pins based on detected text. The script captures images using a camera, performs OCR using OpenAI's Vision API, and activates a GPIO pin when specific trigger words are detected.

## Features

- Real-time image capture using libcamera
- Text detection using OpenAI's Vision API
- GPIO control based on detected trigger words
- Live preview with pygame display
- Configurable trigger words
- GPIO output for connecting various devices
- Advanced logging system for debugging and monitoring
- Rate limiting for API calls
- Automatic image resizing with aspect ratio preservation
- High-quality image processing using LANCZOS resampling

## Prerequisites

- Raspberry Pi (tested on Raspberry Pi 4)
- Compatible camera module
- Device connected to GPIO pin 17 (configurable)
- Python 3.7+
- OpenAI API key
- Camera enabled via raspi-config

## Hardware Setup

1. Connect your camera module to the Raspberry Pi
2. Connect your output device to GPIO pin 17 (BCM numbering) and ground
   - LED: Include an appropriate resistor
   - Relay: Can be used to control larger devices
   - Servo: For motion control
   - Buzzer: For audio feedback
   - Motor driver: For controlling motors
   - Other compatible GPIO devices

Note: The script can be modified to control multiple GPIO pins or use different pins. Ensure your connected device matches the GPIO specifications (3.3V logic level, maximum current draw).

## Installation

1. Clone the repository and set up a Python virtual environment:
```bash
git clone https://github.com/The-OASIS-Project/genesis.git
cd genesis/pi_chatgpt_vision_trigger
python -m venv env
source env/bin/activate
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Obtain an OpenAI API key:
   - Visit [OpenAI's Platform](https://platform.openai.com/signup)
   - Follow the signup process
   - Create an API key at [API Keys](https://platform.openai.com/api-keys)
   - See [OpenAI's Quick Start Guide](https://platform.openai.com/docs/quickstart) for detailed instructions

## Configuration

The `config.yaml` file in the project directory contains all adjustable settings. Here's a detailed explanation of each setting:

### GPIO Settings
```yaml
led_pin: 17               # BCM pin number for output device
```

### Display Settings
```yaml
screen_width: 800         # Preview window width
screen_height: 600        # Preview window height
```

### Camera Settings
```yaml
camera_width: 1920        # Native camera resolution width
camera_height: 1080       # Native camera resolution height
capture_interval: 5       # Seconds between captures
```

### Image Processing
```yaml
max_image_width: 1920     # Maximum width for API submission
max_image_height: 1080    # Maximum height for API submission
```

### Trigger Words and API Settings
```yaml
trigger_words:           # List of words that trigger the GPIO
  - example
  - test
  - detect
  - word

min_api_interval: 1      # Minimum seconds between API calls
```

### Configuration Notes

1. **Camera Operation**:
   - The camera uses automatic settings for optimal image quality
   - Native resolution is configured via camera_width and camera_height
   - Automatic exposure, gain, and white balance provide best results for most situations

2. **Resolution Chain**:
   - Camera captures at native resolution (camera_width × camera_height)
   - Display shows preview at screen resolution (screen_width × screen_height)
   - API receives image limited to max dimensions (max_image_width × max_image_height)
   - All resizing maintains aspect ratio using high-quality LANCZOS resampling

3. **Camera Maximum Resolutions**:
   - Camera Module v2: Up to 3280 x 2464 pixels
   - Camera Module v3: Up to 4608 x 2592 pixels
   - HQ Camera: Up to 4056 x 3040 pixels

## Usage

1. Export your OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

2. Run the script:
```bash
python pi_chatgpt_vision_trigger.py
```

3. To exit the application:
   - Press ESC
   - Or close the pygame window
   - Or Ctrl+C if running headless

## Logging

The script includes comprehensive logging:

- Logs are written to both console and `vision_trigger.log`
- Log levels:
  - INFO: Normal operation messages
  - WARNING: Non-critical issues
  - ERROR: Critical problems
  - DEBUG: Detailed diagnostic information

View logs in real-time:
```bash
tail -f vision_trigger.log
```

## Cost Optimization

The script includes several features to minimize API costs:

1. **Image Optimization**:
   - Automatic resizing while maintaining aspect ratio
   - Separate resolutions for display and API

2. **Rate Limiting**:
   - Configurable minimum interval between API calls
   - Adjustable capture interval
   - Skips API calls when rate limit is hit

3. **Configuration Tips**:
   - Reduce max_image_width/height for lower API costs
   - Increase capture_interval to reduce API calls

## Troubleshooting

Common issues and solutions:

1. **Poor Text Recognition**:
   - Improve lighting conditions
   - Ensure camera is focused correctly
   - Try different camera positions
   - Check for glare or reflections

2. **Performance Issues**:
   - Reduce camera resolution
   - Increase capture interval
   - Lower preview window resolution
   - Check CPU temperature and throttling

3. **Camera Problems**:
   - Enable camera in raspi-config
   - Check camera cable connection
   - Verify camera module compatibility
   - Check `vision_trigger.log` for errors

4. **GPIO Issues**:
   - Verify pin numbers use BCM mode
   - Check device connections
   - Ensure proper ground connection
   - Verify GPIO permissions

## Credits

This project was developed with the assistance of:
- OpenAI's ChatGPT - Initial code development and improvements
- Anthropic's Claude 3 - Code refinement, documentation, and architectural improvements

## License

This project is licensed under the GNU General Public License v3 (GPLv3). This means:

- You are free to use, modify, and distribute this software
- If you distribute modified versions, you must:
  - Make your source code available
  - License it under GPLv3
  - Document your changes
- No warranty is provided with this software

For the full license text, see [GNU GPLv3](https://www.gnu.org/licenses/gpl-3.0.html)

## Contributing

We welcome contributions to the Pi ChatGPT Vision Trigger project!

### Getting Started
1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Make your changes
4. Submit a pull request

### Guidelines
- Follow the existing code style
- Add comments for non-obvious functionality
- Update documentation for changed features
- Test thoroughly before submitting

### Areas for Contribution
- Additional GPIO device support
- Cost reduction features
- Performance improvements
- Documentation updates
- Bug fixes

### Reporting Issues
- Use the GitHub issue tracker
- Include clear reproduction steps
- Provide system information
- Include relevant log excerpts
- Specify hardware configuration

Remember: By contributing to this project, you agree to license your contributions under GPLv3.
