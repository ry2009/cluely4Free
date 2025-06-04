import pyautogui
from PIL import Image
import pytesseract
import logging
import time
import re

def get_screen_text():
    """
    Capture screenshot and extract text using OCR
    
    Returns:
        tuple: (extracted_text, screenshot_image)
    """
    try:
        print("📸 Capturing screen...")
        
        # Take screenshot
        screenshot = pyautogui.screenshot()
        
        # Extract text using Tesseract OCR
        extracted_text = pytesseract.image_to_string(screenshot)
        
        # Clean up the text
        cleaned_text = clean_ocr_text(extracted_text)
        
        if cleaned_text.strip():
            print(f"👁️ Screen text preview: '{cleaned_text[:100]}...'")
        else:
            print("👁️ No readable text found on screen")
        
        return cleaned_text, screenshot
        
    except Exception as e:
        logging.error(f"Error capturing screen: {e}")
        return "", None

def get_screen_text_region(x, y, width, height):
    """
    Capture specific region of screen and extract text
    
    Args:
        x, y (int): Top-left coordinates
        width, height (int): Region dimensions
    
    Returns:
        str: Extracted text from region
    """
    try:
        # Capture specific region
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        
        # Extract text
        text = pytesseract.image_to_string(screenshot)
        return clean_ocr_text(text)
        
    except Exception as e:
        logging.error(f"Error capturing screen region: {e}")
        return ""

def clean_ocr_text(text):
    """
    Clean and format OCR extracted text
    
    Args:
        text (str): Raw OCR text
    
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace and line breaks
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Filter and clean lines
    cleaned_lines = []
    for line in lines:
        # Skip very short lines (likely OCR artifacts)
        if len(line) < 3:
            continue
            
        # Remove lines with excessive special characters
        special_char_ratio = len(re.findall(r'[^a-zA-Z0-9\s\-.,!?:;()[\]{}]', line)) / len(line)
        if special_char_ratio > 0.4:  # Skip lines with >40% special characters
            continue
        
        # Clean up common OCR errors
        line = re.sub(r'[^\w\s\-.,!?:;()[\]{}@#$%&*+=<>/\\|`~"\']+', ' ', line)  # Remove excessive symbols
        line = re.sub(r'\s+', ' ', line)  # Normalize whitespace
        line = line.strip()
        
        # Only keep lines with reasonable content
        if len(line) > 3 and any(c.isalnum() for c in line):
            cleaned_lines.append(line)
    
    # Join with single spaces
    cleaned_text = ' '.join(cleaned_lines)
    
    # Additional cleaning
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # Normalize all whitespace
    cleaned_text = cleaned_text.strip()
    
    # Limit length to prevent overwhelming the LLM
    if len(cleaned_text) > 1500:
        cleaned_text = cleaned_text[:1500] + "..."
    
    return cleaned_text

def save_screenshot(filename=None):
    """
    Save current screenshot to file
    
    Args:
        filename (str): Optional filename, defaults to timestamp
    
    Returns:
        str: Path to saved screenshot
    """
    try:
        if filename is None:
            timestamp = int(time.time())
            filename = f"screenshot_{timestamp}.png"
        
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        
        print(f"💾 Screenshot saved: {filename}")
        return filename
        
    except Exception as e:
        logging.error(f"Error saving screenshot: {e}")
        return None

def test_screen_capture():
    """Test screen capture functionality"""
    print("📸 Testing screen capture...")
    try:
        text, image = get_screen_text()
        
        if image is not None:
            print("✅ Screen capture working")
            print(f"📄 Sample text: '{text[:50]}...'")
            return True
        else:
            print("❌ Screen capture failed")
            return False
            
    except Exception as e:
        print(f"❌ Screen capture test failed: {e}")
        return False 