#!/usr/bin/env python3
"""
Cluely - Proactive Context-Aware AI Desktop Assistant

A lightweight real-time desktop assistant that continuously listens for speech,
watches your screen, and generates intelligent contextual responses.
"""

import time
import sys
import signal
import threading
import logging
from typing import Dict, Any

# Import Cluely modules
from audio.audio_listener import listen_and_transcribe, test_microphone
from vision.screen_capture import get_screen_text, test_screen_capture
from vision.visual_parser import get_active_app, detect_app_context, test_visual_parser
from brain.router import should_respond, get_response_priority
from brain.prompt_builder import build_prompt
from brain.response_executor import show_response, show_error
from llm.local_llm_runner import initialize_llm, run_llm, test_llm
from utils.tools import (
    setup_logging, config, performance_monitor, 
    validate_environment, check_permissions, format_response_type
)

class CluelyApp:
    """Main Cluely application class"""
    
    def __init__(self):
        self.running = False
        self.audio_thread = None
        self.vision_thread = None
        self.last_screen_capture = time.time()
        self.last_audio_check = time.time()
        
        # Configuration from utils
        self.listen_duration = config.get("audio.listen_duration", 5)
        self.capture_interval = config.get("vision.capture_interval", 10)
        self.max_tokens = config.get("llm.max_tokens", 150)
        self.use_local_llm = config.get("llm.use_local", True)
        
        print("🧠 Cluely AI Desktop Assistant")
        print("=" * 40)
    
    def initialize(self) -> bool:
        """Initialize all Cluely components"""
        
        print("🔧 Initializing Cluely...")
        
        # Set up logging
        setup_logging()
        
        # Validate environment
        print("✅ Checking environment...")
        issues = validate_environment()
        if issues:
            print("❌ Environment issues found:")
            for issue in issues:
                print(f"  - {issue}")
            print("\nPlease fix these issues before running Cluely.")
            return False
        
        # Check permissions
        print("🔑 Checking permissions...")
        permissions = check_permissions()
        missing_permissions = [p for p, granted in permissions.items() if not granted]
        if missing_permissions:
            print(f"⚠️ Missing permissions: {missing_permissions}")
            print("Please grant required permissions in System Preferences > Security & Privacy")
        
        # Test components
        print("🧪 Testing components...")
        
        # Test microphone
        if not test_microphone():
            print("❌ Microphone test failed")
            return False
        
        # Test screen capture
        if not test_screen_capture():
            print("❌ Screen capture test failed")
            return False
        
        # Test visual parser
        if not test_visual_parser():
            print("❌ Visual parser test failed")
            return False
        
        # Initialize LLM
        print("🧠 Initializing LLM...")
        if not initialize_llm(use_local=self.use_local_llm):
            print("⚠️ Failed to initialize local LLM, trying OpenAI...")
            if not initialize_llm(use_local=False):
                print("❌ Failed to initialize any LLM")
                return False
        
        # Test LLM
        if not test_llm():
            print("❌ LLM test failed")
            return False
        
        print("✅ All components initialized successfully!")
        return True
    
    def start(self):
        """Start the main Cluely loop"""
        
        if not self.initialize():
            print("❌ Initialization failed. Exiting.")
            return
        
        print("\n🚀 Starting Cluely...")
        print("🎙️ Listening for audio...")
        print("👁️ Watching screen...")
        print("🧠 AI ready to assist...")
        print("\nPress Ctrl+C to stop")
        print("=" * 40)
        
        self.running = True
        
        # Set up signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        
        try:
            # Start main loop
            self.main_loop()
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()
    
    def main_loop(self):
        """Main application loop"""
        
        while self.running:
            try:
                # Get current context
                current_time = time.time()
                
                # Audio processing (every loop iteration)
                audio_text = self._process_audio()
                
                # Vision processing (every capture_interval seconds)
                screen_text, app = self._process_vision(current_time)
                
                # Decision making and response
                if audio_text.strip():  # Only process if we heard something
                    self._process_response(audio_text, screen_text, app)
                
                # Brief pause to prevent excessive CPU usage
                time.sleep(0.1)
                
            except Exception as e:
                logging.error(f"Error in main loop: {e}")
                time.sleep(1)  # Longer pause on error
    
    @performance_monitor.time_function("audio_processing_time")
    def _process_audio(self) -> str:
        """Process audio input"""
        try:
            return listen_and_transcribe(seconds=self.listen_duration)
        except Exception as e:
            logging.error(f"Audio processing error: {e}")
            return ""
    
    @performance_monitor.time_function("vision_processing_time")
    def _process_vision(self, current_time: float) -> tuple:
        """Process vision input"""
        try:
            # Only capture screen periodically to save resources
            if current_time - self.last_screen_capture >= self.capture_interval:
                screen_text, _ = get_screen_text()
                app = get_active_app()
                self.last_screen_capture = current_time
                
                # Cache the results
                self._cached_screen_text = screen_text
                self._cached_app = app
                
                return screen_text, app
            else:
                # Use cached results
                return getattr(self, '_cached_screen_text', ''), getattr(self, '_cached_app', 'Unknown')
                
        except Exception as e:
            logging.error(f"Vision processing error: {e}")
            return "", "Unknown"
    
    @performance_monitor.time_function("total_response_time")
    def _process_response(self, audio_text: str, screen_text: str, app: str):
        """Process and generate response"""
        try:
            # Check if we should respond
            if should_respond(audio_text, screen_text, app):
                print(f"\n🎯 Triggered by: '{audio_text}'")
                
                # Get response priority
                priority = get_response_priority(audio_text, app)
                
                # Build prompt
                prompt = build_prompt(audio_text, screen_text, app)
                
                # Generate LLM response (with timing)
                start_time = time.time()
                response = run_llm(prompt, max_tokens=self.max_tokens)
                end_time = time.time()
                
                # Log LLM timing manually
                llm_time = end_time - start_time
                performance_monitor.metrics["llm_response_time"].append(llm_time)
                if len(performance_monitor.metrics["llm_response_time"]) > 100:
                    performance_monitor.metrics["llm_response_time"] = performance_monitor.metrics["llm_response_time"][-100:]
                
                if response and not response.startswith("❌"):
                    # Determine response type for UI
                    response_type = self._determine_response_type(audio_text, app)
                    
                    # Show response
                    auto_dismiss = 0 if priority == "high" else config.get("ui.auto_dismiss_time", 10)
                    show_response(response, response_type=response_type, auto_dismiss=auto_dismiss)
                    
                    # Log the interaction
                    logging.info(f"Response generated: {response[:100]}...")
                else:
                    show_error(f"Failed to generate response: {response}")
                    
        except Exception as e:
            logging.error(f"Response processing error: {e}")
            show_error(f"Processing error: {str(e)}")
    
    def _determine_response_type(self, audio_text: str, app: str) -> str:
        """Determine the type of response for UI display"""
        
        audio_lower = audio_text.lower()
        app_lower = app.lower()
        
        # Check for specific patterns
        if "remind" in audio_lower:
            return "reminder"
        elif any(word in audio_lower for word in ["tweet", "post", "share"]) and "twitter" in app_lower:
            return "social_media"
        elif "summarize" in audio_lower or "summary" in audio_lower:
            return "summary"
        elif any(word in audio_lower for word in ["what", "how", "why", "when", "where"]):
            return "question"
        elif "email" in audio_lower or app_lower in ["mail", "gmail", "outlook"]:
            return "communication"
        elif app_lower in ["word", "docs", "notion", "obsidian"]:
            return "writing"
        elif app_lower in ["chrome", "safari", "firefox"]:
            return "web_browsing"
        elif app_lower in ["vscode", "cursor", "xcode", "terminal"]:
            return "development"
        elif any(word in audio_lower for word in ["idea", "brainstorm", "creative"]):
            return "creative"
        else:
            return "suggestion"
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\n🛑 Shutting down Cluely...")
        self.running = False
    
    def stop(self):
        """Stop the application"""
        self.running = False
        print("👋 Cluely stopped. Goodbye!")
        
        # Print performance report
        report = performance_monitor.get_performance_report()
        if report:
            print("\n📊 Performance Report:")
            for category, metrics in report.items():
                print(f"  {category}: {metrics['average']:.3f}s avg ({metrics['count']} calls)")

def run_tests():
    """Run comprehensive tests of all components"""
    print("🧪 Running Cluely Tests")
    print("=" * 40)
    
    tests = [
        ("Environment", lambda: len(validate_environment()) == 0),
        ("Microphone", test_microphone),
        ("Screen Capture", test_screen_capture),
        ("Visual Parser", test_visual_parser),
        ("LLM", test_llm)
    ]
    
    passed = 0
    for test_name, test_func in tests:
        print(f"Testing {test_name}...")
        try:
            if test_func():
                print(f"✅ {test_name} test passed")
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test error: {e}")
    
    print(f"\n📊 Test Results: {passed}/{len(tests)} passed")
    return passed == len(tests)

def main():
    """Main entry point"""
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            run_tests()
            return
        elif sys.argv[1] == "config":
            print("📝 Current Configuration:")
            import json
            print(json.dumps(config.config, indent=2))
            return
        elif sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("Cluely - AI Desktop Assistant")
            print("\nUsage:")
            print("  python main.py        # Run Cluely")
            print("  python main.py test   # Run tests")
            print("  python main.py config # Show configuration")
            return
    
    # Create and start the app
    app = CluelyApp()
    app.start()

if __name__ == "__main__":
    main() 