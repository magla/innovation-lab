import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
from PIL import Image
import numpy as np
import os
import random

# Scrape configuration
IMAGE_SIZE = (48, 48)
CONTRAST_THRESHOLD = 4.5
OUTPUT_DIR = "static/scraped_images"
SCREENSHOT_PATH = "static/full_page_screenshot.png"
FINAL_SCREENSHOT_PATH = "static/final_screenshot.png"
chrome_driver_path = '/opt/homebrew/bin/chromedriver'
targetElements = ['h1', 'h2', 'h3']

class CustomModel:
    def __init__(self, model=None):
        self.model = model
        self.driver = self._initialize_webdriver()
        self.selector_map = {}
        self.X = []
        self.y = []

    def _initialize_webdriver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(service=Service(chrome_driver_path), options=chrome_options)
        return driver
    
    def find_unique_xpath(self, element, soup):
        parts = []
        current = element

        while current and current.name != '[document]':  # Traverse up to the root
            if current.has_attr('id'):
                parts.insert(0, f"//{current.name}[@id='{current['id']}']")
                break  # IDs are unique; no need to go further
            
            if current.has_attr('class'):
                class_attr = ' '.join(current['class'])  # Classes are space-separated
                siblings = current.find_previous_siblings(name=current.name, class_=class_attr)
                index = len(siblings) + 1  # XPath indices are 1-based
                parts.insert(0, f"{current.name}[contains(@class, '{class_attr}')][{index}]")        
            else:
                siblings = current.find_previous_siblings(name=current.name)
                index = len(siblings) + 1  # XPath indices are 1-based
                parts.insert(0, f"{current.name}[{index}]")

            current = current.parent  # Move to the parent element

        # Combine all parts into a full XPath
        xpath = "/" + "/".join(parts)
        
        return xpath.replace("///", "//")

    def screenshot_element(self, element):    
        """Takes a screenshot of the target element and saves it."""
        element_location = element.location
        element_size = element.size
        screenshot = Image.open(SCREENSHOT_PATH)
        screenshot_width, screenshot_height = screenshot.size
        
        element_left = element_location['x']
        element_top = element_location['y']
        element_right = min(screenshot_width, element_left + element_size['width']) 
        element_bottom = min(element_top + element_size['height'], screenshot_height)
        
        # Crop the image using Pillow
        cropped_image = screenshot.crop((element_left, element_top, element_right, element_bottom))

        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
        
        element_screenshot_path = os.path.join(OUTPUT_DIR, f"screenshot_{random.randint(1, 1000000)}.png")
        cropped_image.save(element_screenshot_path)
        return element_screenshot_path

    def preprocess_image(self, image_path):
        """Resize and preprocess image for CNN."""
        image = Image.open(image_path).convert('L')
        image = image.resize((48, 48))
        return np.array(image)

    def fetch_html(self, url):
        """Fetch the HTML of a webpage."""
        try:
            self.driver.get(url)
            time.sleep(3)
            response = requests.get(url, timeout=3)
            response.raise_for_status()  # Will raise an exception for HTTP errors
            return self.driver.page_source
        except RequestException as e:
            print(f"Error fetching {url}: {e}")
    
    
    def is_element_visible(self, element):
        try:        
            # Check if the element is displayed using is_displayed()
            if element.is_displayed():
                # Check if the element is within the viewport using JavaScript
                is_in_viewport = self.driver.execute_script("""
                    var elem = arguments[0];
                    var rect = elem.getBoundingClientRect();
                    return (
                        rect.top >= 0 &&
                        rect.left >= 0 &&
                        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
                    );
                """, element)
                
                if is_in_viewport:
                    return True
                else:
                    print("Error: Element is not in the viewport")
                    return False
            else:
                print("Error: Element is not displayed")
                return False

        except TimeoutException:
            print("Timeout: Element not found or not visible within the timeout period.")
            return False
        except NoSuchElementException:
            print("Error: Element not found.")
            return False
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return False

    def scrape_site(self, link):   
        elements = []
             
        try:
            html_content = self.fetch_html(link)
            if html_content:
                soup = BeautifulSoup(html_content, "html.parser")

                # Set window size to current width, and max height
                window_size = self.driver.get_window_size()                            
                full_page_height = self.driver.execute_script("return document.documentElement.scrollHeight;") 
                self.driver.set_window_size(window_size['width'],full_page_height)
                self.driver.save_screenshot(SCREENSHOT_PATH) 
                
                screenshot = Image.open(SCREENSHOT_PATH)
                screenshot_width, screenshot_height = screenshot.size
                
                ratio = screenshot_width / screenshot_height    
                screenshot = screenshot.resize((window_size['width'], int(window_size['width'] / ratio)))
                screenshot.save(SCREENSHOT_PATH)

                # Extract target elements from body
                for element in soup.find_all(targetElements):
                    text = element.get_text(strip=True)
                    if text:
                        try:
                            selector = self.find_unique_xpath(element, soup)
                                                        
                            if (not selector):
                                continue
                            
                            driverElement = self.driver.find_element(By.XPATH, selector)
                            
                            if driverElement: 
                                is_visible = self.is_element_visible(driverElement)
                                
                                if (not is_visible):
                                    continue
                                                         
                                screenshot_path = self.screenshot_element(driverElement)
                                image = self.preprocess_image(screenshot_path)                        
                                elements.append(image)
                                self.selector_map[len(elements) - 1] = selector
                        except Exception as e:
                            print(f"Error processing element with selector {selector}: {e}")
        except Exception as e:
            print(f"Error processing {link}: {e}")
            
        return np.array(elements)
    
    def custom_infer(self, predictions, predicted_classes): 
        prediction_results = []

        for idx, prediction in enumerate(predictions["output_0"]):
            selector = self.selector_map.get(idx)
            
            if selector:
                prediction_results.append({
                    "selector": selector,
                    "prediction": int(predicted_classes[idx])
                })
                if int(predicted_classes[idx]) == 0:  # Low contrast
                    self.driver.execute_script(
                        "arguments[0].style.border = '3px solid red';",
                        self.driver.find_element(By.XPATH, selector)
                    )
        self.driver.save_screenshot(FINAL_SCREENSHOT_PATH)
        return prediction_results

    def close_driver(self):
        """Close the web driver after processing."""
        self.driver.quit()
        
    def cleanup(self):
        os.remove(SCREENSHOT_PATH)
        try:
            for filename in os.listdir(OUTPUT_DIR):
                file_path = os.path.join(OUTPUT_DIR, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"Removed file: {file_path}")
            # print("All files removed successfully.")
        except Exception as e:
            print(f"Error: {e}")
