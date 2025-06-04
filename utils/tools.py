import time
import logging
import threading
from typing import Dict, Any, Callable, Optional
import json
import os

def setup_logging():
    """Set up logging configuration for Cluely"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('cluely.log'),
            logging.StreamHandler()
        ]
    )

def safe_execute(func: Callable, *args, **kwargs) -> Any:
    """
    Safely execute a function with error handling
    
    Args:
        func: Function to execute
        *args, **kwargs: Arguments for the function
    
    Returns:
        Function result or None if error occurred
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logging.error(f"Error executing {func.__name__}: {e}")
        return None

def debounce(wait_time: float):
    """
    Decorator to debounce function calls
    
    Args:
        wait_time (float): Time to wait between calls in seconds
    """
    def decorator(func):
        last_called = [0.0]
        
        def wrapper(*args, **kwargs):
            current_time = time.time()
            if current_time - last_called[0] >= wait_time:
                last_called[0] = current_time
                return func(*args, **kwargs)
            
        return wrapper
    return decorator

def throttle(max_calls: int, time_window: float):
    """
    Decorator to throttle function calls
    
    Args:
        max_calls (int): Maximum number of calls allowed
        time_window (float): Time window in seconds
    """
    def decorator(func):
        calls = []
        
        def wrapper(*args, **kwargs):
            now = time.time()
            # Remove old calls outside the time window
            calls[:] = [call_time for call_time in calls if now - call_time < time_window]
            
            if len(calls) < max_calls:
                calls.append(now)
                return func(*args, **kwargs)
            else:
                logging.warning(f"Function {func.__name__} throttled")
                return None
                
        return wrapper
    return decorator

class ConfigManager:
    """Manage configuration settings for Cluely"""
    
    def __init__(self, config_file: str = "cluely_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        default_config = {
            "audio": {
                "listen_duration": 5,
                "silence_threshold": 0.01,
                "model": "base"
            },
            "vision": {
                "capture_interval": 10,
                "max_text_length": 2000
            },
            "llm": {
                "use_local": True,
                "max_tokens": 150,
                "temperature": 0.7
            },
            "ui": {
                "auto_dismiss_time": 10,
                "window_position": "top-right",
                "transparency": 0.95
            },
            "triggers": {
                "direct_activation": ["hey cluely", "cluely"],
                "intent_threshold": 0.7
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                # Merge with defaults
                return {**default_config, **loaded_config}
            else:
                # Create default config file
                self.save_config(default_config)
                return default_config
        except Exception as e:
            logging.error(f"Error loading config: {e}")
            return default_config
    
    def save_config(self, config: Dict[str, Any] = None):
        """Save configuration to file"""
        try:
            config_to_save = config or self.config
            with open(self.config_file, 'w') as f:
                json.dump(config_to_save, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving config: {e}")
    
    def get(self, key_path: str, default=None):
        """Get configuration value using dot notation"""
        try:
            keys = key_path.split('.')
            value = self.config
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any):
        """Set configuration value using dot notation"""
        try:
            keys = key_path.split('.')
            config = self.config
            for key in keys[:-1]:
                if key not in config:
                    config[key] = {}
                config = config[key]
            config[keys[-1]] = value
            self.save_config()
        except Exception as e:
            logging.error(f"Error setting config {key_path}: {e}")

class PerformanceMonitor:
    """Monitor performance metrics for Cluely"""
    
    def __init__(self):
        self.metrics = {
            "audio_processing_time": [],
            "vision_processing_time": [],
            "llm_response_time": [],
            "total_response_time": []
        }
    
    def time_function(self, category: str):
        """Decorator to time function execution"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                
                execution_time = end_time - start_time
                self.metrics[category].append(execution_time)
                
                # Keep only last 100 measurements
                if len(self.metrics[category]) > 100:
                    self.metrics[category] = self.metrics[category][-100:]
                
                logging.debug(f"{func.__name__} took {execution_time:.3f}s")
                return result
            return wrapper
        return decorator
    
    def get_average_time(self, category: str) -> float:
        """Get average execution time for a category"""
        if category in self.metrics and self.metrics[category]:
            return sum(self.metrics[category]) / len(self.metrics[category])
        return 0.0
    
    def get_performance_report(self) -> Dict[str, float]:
        """Get performance report for all categories"""
        report = {}
        for category, times in self.metrics.items():
            if times:
                report[category] = {
                    "average": sum(times) / len(times),
                    "count": len(times),
                    "latest": times[-1] if times else 0
                }
        return report

def format_response_type(trigger_info: str) -> str:
    """
    Format trigger information into response type
    
    Args:
        trigger_info (str): Trigger information from router
    
    Returns:
        str: Formatted response type
    """
    if not trigger_info:
        return "suggestion"
    
    # Extract response type from trigger info
    if ":" in trigger_info:
        category, action = trigger_info.split(":", 1)
        
        type_mapping = {
            "social_media": "social_media",
            "communication": "communication",
            "writing": "writing",
            "web_browsing": "web_browsing",
            "development": "development",
            "reminder": "reminder",
            "question": "question",
            "action": "action",
            "creative": "creative"
        }
        
        return type_mapping.get(category, "suggestion")
    
    return "suggestion"

def clean_text_for_display(text: str, max_length: int = 500) -> str:
    """
    Clean and format text for display in UI
    
    Args:
        text (str): Raw text
        max_length (int): Maximum length for display
    
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    cleaned = " ".join(text.split())
    
    # Truncate if too long
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length-3] + "..."
    
    return cleaned

def check_permissions():
    """Check if required macOS permissions are granted"""
    permissions_status = {
        "microphone": False,
        "screen_recording": False,
        "accessibility": False
    }
    
    # These would need to be implemented with system-specific checks
    # For now, return True to allow testing
    return {
        "microphone": True,
        "screen_recording": True,
        "accessibility": True
    }

def validate_environment():
    """Validate that the environment is properly set up"""
    issues = []
    
    # Check Python version
    import sys
    if sys.version_info < (3, 8):
        issues.append("Python 3.8+ required")
    
    # Check required packages
    required_packages = [
        "whisper", "sounddevice", "PIL", "pytesseract", 
        "pyautogui", "pygetwindow", "numpy", "tkinter"
    ]
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            issues.append(f"Missing package: {package}")
    
    # Check tesseract installation
    try:
        import subprocess
        subprocess.run(["tesseract", "--version"], 
                      capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        issues.append("Tesseract OCR not installed")
    
    return issues

# Global instances
config = ConfigManager()
performance_monitor = PerformanceMonitor() 