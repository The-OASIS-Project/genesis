import os
import io
import json
import pygame
import time
import subprocess
import base64
import requests
import re
import logging
import yaml
from PIL import Image
from io import BytesIO
import numpy as np
import RPi.GPIO as GPIO  # For GPIO control on Raspberry Pi

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vision_trigger.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize pygame
pygame.init()

# Default configuration values
DEFAULT_CONFIG = {
    'led_pin': 17,
    'screen_width': 800,
    'screen_height': 600,
    'camera_width': 1920,
    'camera_height': 1080,
    'capture_interval': 5,
    'max_image_width': 1920,
    'max_image_height': 1080,
    'trigger_words': ["example", "test", "detect", "word"],
    'min_api_interval': 1
}

# Load configuration from YAML file
CONFIG_FILE = 'config.yaml'
try:
    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f)
    # Use default values if specific keys are missing
    for key, default_value in DEFAULT_CONFIG.items():
        if key not in config:
            config[key] = default_value
            logger.warning(f"Using default value for {key}: {default_value}")
except FileNotFoundError:
    logger.warning(f"Configuration file {CONFIG_FILE} not found, using defaults")
    config = DEFAULT_CONFIG

# Extract configuration values
LED_PIN = config['led_pin']
SCREEN_WIDTH = config['screen_width']
SCREEN_HEIGHT = config['screen_height']
CAMERA_WIDTH = config['camera_width']
CAMERA_HEIGHT = config['camera_height']
CAPTURE_INTERVAL = config['capture_interval']
trigger_words = config['trigger_words']
MIN_API_INTERVAL = config['min_api_interval']

# GPIO setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.output(LED_PIN, GPIO.LOW)

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY environment variable not set")
    raise ValueError("Please set the OPENAI_API_KEY environment variable")

# Rate limiting variables
last_api_call = 0

# Set up the pygame display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pi ChatGPT Vision Trigger")

def build_camera_command():
    """Build the libcamera-still command with resolution parameters"""
    return [
        "libcamera-still",
        "-o", "-",
        "--width", str(CAMERA_WIDTH),
        "--height", str(CAMERA_HEIGHT),
        "--immediate",
        "--nopreview"
    ]

def capture_image():
    """Capture an image using libcamera-still with configured parameters"""
    try:
        capture_command = build_camera_command()
        logger.debug("Capturing image with command: %s", " ".join(capture_command))
        
        process = subprocess.Popen(capture_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        image_data, stderr = process.communicate(timeout=10)
        
        if process.returncode != 0:
            logger.error(f"Camera capture failed: {stderr.decode()}")
            return None

        # Load the original image
        original_image = Image.open(BytesIO(image_data))
        
        # Create display version if needed
        if (CAMERA_WIDTH != SCREEN_WIDTH) or (CAMERA_HEIGHT != SCREEN_HEIGHT):
            display_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
            display_image = original_image.copy()
            display_image.thumbnail(display_size, Image.LANCZOS)
            return original_image, display_image
        
        return original_image, original_image

    except subprocess.TimeoutExpired:
        logger.error("Camera capture timed out")
        process.kill()
        return None
    except Exception as e:
        logger.error(f"Error capturing image: {str(e)}")
        return None

def resize_image(image, max_width, max_height):
    """
    Resize image to fit within maximum dimensions while maintaining aspect ratio.
    Uses high-quality LANCZOS resampling.
    
    Args:
        image: PIL Image object
        max_width: Maximum allowed width
        max_height: Maximum allowed height
        
    Returns:
        PIL Image object resized to fit within bounds while maintaining aspect ratio
    """
    original_width, original_height = image.size
    
    # Calculate aspect ratios
    width_ratio = max_width / original_width
    height_ratio = max_height / original_height
    
    # Use the smaller ratio to ensure image fits within bounds
    ratio = min(width_ratio, height_ratio)
    
    # Calculate new dimensions
    new_width = int(original_width * ratio)
    new_height = int(original_height * ratio)
    
    logger.debug(
        "Resizing image from %dx%d to %dx%d (max: %dx%d)", 
        original_width, original_height, 
        new_width, new_height,
        max_width, max_height
    )
    
    if ratio < 1:  # Only resize if image is larger than max dimensions
        return image.resize((new_width, new_height), Image.LANCZOS)
    
    return image

def encode_image_to_base64(image):
    """Convert PIL image to base64 string"""
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    img_bytes = buffered.getvalue()
    base64_image = base64.b64encode(img_bytes).decode('utf-8')
    return base64_image

def perform_ocr_with_openai(image):
    """Perform OCR using OpenAI's Vision API"""
    base64_image = encode_image_to_base64(image)
    
    # Rate limiting
    global last_api_call
    current_time = time.time()
    if current_time - last_api_call < MIN_API_INTERVAL:
        logger.warning("Rate limit hit, skipping API call")
        return ""
    last_api_call = current_time

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Please extract all text from the following image. Return only the text in a json format with the following entries: {\"type\": \"reply\", \"text\": \"The text you extracted\"}. Don't include line breaks or special characters."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 1000
    }

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        response_data = response.json()

        ocr_text_raw = response_data['choices'][0]['message']['content'].strip()
        logger.debug("Raw OCR JSON Response: %s", ocr_text_raw)

        json_pattern = re.compile(r'```json\s*(\{.*?\})\s*```', re.DOTALL)
        match = json_pattern.search(ocr_text_raw)

        json_str = match.group(1) if match else ocr_text_raw

        try:
            ocr_text_data = json.loads(json_str)
            ocr_text = ocr_text_data.get('text', '')
            logger.info("Extracted OCR Text: %s", ocr_text)
            return ocr_text
        except json.JSONDecodeError as json_err:
            logger.error("JSON decoding error: %s", json_err)
            logger.debug("Extracted JSON string: %s", json_str)
            return ""

    except requests.exceptions.RequestException as e:
        logger.error("Request error: %s", e)
        return ""
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        return ""

def pil_to_pygame(image):
    """Convert PIL image to pygame surface"""
    return pygame.image.fromstring(image.tobytes(), image.size, image.mode)

def check_trigger_words(ocr_text):
    """Check if any trigger words are present in the text"""
    return any(word.lower() in ocr_text.lower() for word in trigger_words)

def main():
    running = True
    last_capture_time = 0
    ocr_text = ""
    pygame_image = None

    logger.info("Starting Pi ChatGPT Vision Trigger")
    logger.info("Camera resolution: %dx%d", CAMERA_WIDTH, CAMERA_HEIGHT)
    logger.info("Display resolution: %dx%d", SCREEN_WIDTH, SCREEN_HEIGHT)
    logger.info("Capture interval: %d seconds", CAPTURE_INTERVAL)
    logger.info("Trigger words: %s", trigger_words)

    while running:
        current_time = time.time()

        if current_time - last_capture_time > CAPTURE_INTERVAL:
            capture_result = capture_image()
            if capture_result:
                original_image, display_image = capture_result
                
                # Resize for API submission
                api_image = original_image.copy()
                api_image = resize_image(
                    api_image, 
                    config['max_image_width'],
                    config['max_image_height']
                )
                
                # Process with API
                ocr_text = perform_ocr_with_openai(api_image)
                
                # Convert for display
                pygame_image = pil_to_pygame(display_image)
                last_capture_time = current_time

                # Check trigger words and control GPIO
                if check_trigger_words(ocr_text):
                    GPIO.output(LED_PIN, GPIO.HIGH)
                    logger.info("Trigger word detected! GPIO HIGH")
                else:
                    GPIO.output(LED_PIN, GPIO.LOW)

            else:
                logger.error("Failed to capture image")

        # Display the image and text
        if pygame_image:
            screen.fill((0, 0, 0))
            screen.blit(pygame_image, (0, 0))

            font = pygame.font.SysFont(None, 36)
            for idx, line in enumerate(ocr_text.split('\n')):
                text_surface = font.render(line, True, (255, 255, 255))
                screen.blit(text_surface, (10, 10 + idx * 40))

            pygame.display.flip()

        # Handle pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        time.sleep(0.1)

    logger.info("Shutting down...")
    try:
        GPIO.cleanup()
        pygame.quit()
    except Exception as e:
        logger.error("Error during cleanup: %s", e)

if __name__ == "__main__":
    main()
