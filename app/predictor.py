from PIL import Image
import numpy as np
import tensorflow as tf
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import os
import random

MAX_PAGES = 3
IMAGE_SIZE = (48, 48)
CONTRAST_THRESHOLD = 4.5
OUTPUT_DIR = "scraped_images"
os.makedirs(OUTPUT_DIR, exist_ok=True)

model = tf.saved_model.load("../notebooks/HTMLConvolutional")
infer = model.signatures["my_custom_infer"]

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver_path = '/opt/homebrew/bin/chromedriver'
driver = webdriver.Chrome(service=Service(driver_path), options=chrome_options)
driver.set_window_size(1200, 939)

# Function to construct the CSS selector
def get_css_selector(element):
    selector = element.name
    
    if element.get('id'):
        selector += f'#{element["id"]}'
    
    if element.get('class'):
        selector += '.' + '.'.join(element["class"])
    
    for attribute, value in element.attrs.items():
        if attribute not in ['id', 'class']:
            selector += f'[{attribute}="{value}"]'
    
    return selector

def screenshot_element(driver, element):
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    time.sleep(1) 

    # Step 2: Take a screenshot of the entire page
    screenshot_path = "full_page_screenshot.png"
    driver.save_screenshot(screenshot_path)
    
    location = element.location
    size = element.size
    
    # Step 3: Crop the image to the element's location and size
    image = Image.open(screenshot_path)
    image = image.resize((1200, 939), Image.Resampling.LANCZOS)

    width, height = image.size
    
    left = location['x']
    top = 0
    right = min(width, left + size['width']) 
    bottom = min(size['height'], height)

    print(element.text, size)
    
    # Crop the image using Pillow
    cropped_image = image.crop((left, top, right, bottom))

    # Step 4: Save the cropped screenshot
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    element_screenshot_path = os.path.join(OUTPUT_DIR, f"screenshot_{random.randint(1, 1000000)}.png")
    cropped_image.save(element_screenshot_path)

    # Return the path of the cropped screenshot
    return element_screenshot_path

def preprocess_image(image_path):
    """Resize and preprocess image for CNN."""
    image = Image.open(image_path).convert('L')  # Convert to grayscale
    image = image.resize(IMAGE_SIZE)  # Resize to (48, 48)
    image_array = np.array(image, dtype=np.float32)
    
    # Add a channel dimension: [48, 48, 1]
    image_array = np.expand_dims(image_array, axis=-1)  # Add channel dimension
    
    # # Add a batch dimension: [1, 48, 48, 1]
    # image_array = np.expand_dims(image_array, axis=0)  # Add batch dimension
    
    image_tensor = tf.convert_to_tensor(image_array, dtype=tf.float32)
    return image_tensor

def fetch_html(url):
    try:
        driver.get(url)
        time.sleep(3)
        response = requests.get(url, timeout=3)
        response.raise_for_status()  # Will raise an exception for HTTP errors
        return driver.page_source
    except RequestException as e:
        print(f"Error fetching {url}: {e}")
        
def getElements(link): 
    elements = []
    
    try:
        html_content = fetch_html(link)
        if html_content:
            soup = BeautifulSoup(html_content, "html.parser")
    
            # Extract elements with text and background styles
            for element in soup.find('body').find_all(['h1', 'h2']):
                text = element.get_text(strip=True)

                if text and not element.find_all(True):
                    try:
                        css_selector = get_css_selector(element)
                        driverElements = driver.find_elements(By.CSS_SELECTOR, css_selector)
                
                        if driverElements:                        
                            for driverElement in driverElements:
                                screenshot_path = screenshot_element(driver, driverElement)
                                image = preprocess_image(screenshot_path)    
                                elements.append(image)
                                
                    except Exception as e:
                            print(f"Error processing element with selector {css_selector}: {e}")
                else: continue
    except Exception as e:
        print(f"Error processing {link}: {e}")
        
    return elements

def predict_validity(url):
    elements = getElements(url)
    
    if len(elements) == 0:
        return None  # Handle case where no valid elements are found
    
    # Stack all the images into a batch
    batch_elements = tf.stack(elements)  # Stack list of tensors into a single tensor (batch)
    
    # Perform inference
    predictions = infer(batch_elements)
    
    print(predictions);
    
    # Get the predicted class
    predicted_classes = np.argmax(predictions['output_0'], axis=1)  # Get the index of the max value for each image
    
    return predicted_classes
