import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
import subprocess
import pyautogui
from typing import Optional
import queue

class ResponseWindow:
    """Handles display of AI responses in popup windows"""
    
    def __init__(self):
        self.current_window = None
        self.auto_dismiss_timer = None
        self.ui_queue = queue.Queue()
        self.main_thread_id = threading.current_thread().ident
    
    def show_response(self, text: str, title: str = "Cluely Suggestion", 
                     auto_dismiss: int = 10, response_type: str = "suggestion"):
        """
        Display AI response in a popup window
        
        Args:
            text (str): Response text to display
            title (str): Window title
            auto_dismiss (int): Seconds before auto-dismissing (0 = no auto-dismiss)
            response_type (str): Type of response (suggestion, reminder, action, etc.)
        """
        
        # Check if we're on the main thread
        if threading.current_thread().ident == self.main_thread_id:
            # We're on main thread, create window directly
            self._create_window_safe(text, title, auto_dismiss, response_type)
        else:
            # We're on a background thread, use queue-based approach
            try:
                # For macOS compatibility, try a simpler console output first
                print(f"\n💬 {title}")
                print(f"🤖 {text}")
                print("=" * 50)
                
                # Try to create window using main thread scheduling
                self._schedule_window_creation(text, title, auto_dismiss, response_type)
                
            except Exception as e:
                print(f"⚠️ UI display error: {e}")
                # Fallback to console output
                print(f"\n💬 Cluely Response: {text}\n")
    
    def _schedule_window_creation(self, text: str, title: str, auto_dismiss: int, response_type: str):
        """Schedule window creation on main thread"""
        try:
            # Use a simple approach - create window in main event loop
            root = tk.Tk()
            root.withdraw()  # Hide the root window
            
            # Schedule the actual window creation
            root.after(100, lambda: self._create_window_delayed(root, text, title, auto_dismiss, response_type))
            
            # Run briefly to process the scheduled event
            root.after(1000, root.quit)  # Auto-quit after 1 second
            root.mainloop()
            
        except Exception as e:
            print(f"⚠️ Window scheduling failed: {e}")
            # Fallback to console
            print(f"💬 Cluely: {text}")
    
    def _create_window_delayed(self, root, text: str, title: str, auto_dismiss: int, response_type: str):
        """Create window with delay to ensure main thread execution"""
        try:
            root.deiconify()  # Show the root window
            self._create_window_safe(text, title, auto_dismiss, response_type, parent=root)
        except Exception as e:
            print(f"⚠️ Delayed window creation failed: {e}")
            print(f"💬 Cluely: {text}")
    
    def _create_window_safe(self, text: str, title: str, auto_dismiss: int, response_type: str, parent=None):
        """Create and display the popup window safely"""
        
        try:
            # Close existing window if open
            if self.current_window:
                try:
                    self.current_window.destroy()
                except:
                    pass
            
            # Create main window
            if parent:
                window = tk.Toplevel(parent)
            else:
                window = tk.Tk()
            
            self.current_window = window
            
            window.title(title)
            window.geometry("400x300")
            window.resizable(True, True)
            
            # Position window in top-right corner
            screen_width = window.winfo_screenwidth()
            window.geometry(f"400x300+{screen_width-420}+50")
            
            # Configure window properties
            window.attributes('-topmost', True)  # Keep on top
            
            try:
                window.attributes('-alpha', 0.95)    # Slight transparency
            except:
                pass  # Transparency might not be supported
            
            # Create UI based on response type
            self._create_ui(window, text, response_type)
            
            # Set up auto-dismiss if specified
            if auto_dismiss > 0:
                self.auto_dismiss_timer = window.after(
                    auto_dismiss * 1000, 
                    lambda: self._dismiss_window(window)
                )
            
            # Show window without starting mainloop (to avoid blocking)
            window.update()
            
        except Exception as e:
            print(f"Error creating response window: {e}")
            # Fallback to console output
            print(f"\n💬 {title}")
            print(f"🤖 {text}")
            print("=" * 50)
    
    def _create_ui(self, window: tk.Tk, text: str, response_type: str):
        """Create the UI elements for the response window"""
        
        # Main frame
        main_frame = ttk.Frame(window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        window.columnconfigure(0, weight=1)
        window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Header with icon and type
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(1, weight=1)
        
        # Icon based on response type
        icon = self._get_response_icon(response_type)
        icon_label = ttk.Label(header_frame, text=icon, font=("Arial", 16))
        icon_label.grid(row=0, column=0, padx=(0, 10))
        
        # Response type label
        type_label = ttk.Label(header_frame, text=response_type.title(), 
                              font=("Arial", 10, "bold"))
        type_label.grid(row=0, column=1, sticky=tk.W)
        
        # Close button
        close_btn = ttk.Button(header_frame, text="✕", width=3,
                              command=lambda: self._dismiss_window(window))
        close_btn.grid(row=0, column=2)
        
        # Main text area
        text_area = scrolledtext.ScrolledText(
            main_frame,
            wrap=tk.WORD,
            width=45,
            height=12,
            font=("Arial", 11),
            relief="flat",
            borderwidth=0,
            background="#f8f9fa"
        )
        text_area.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Insert text
        text_area.insert(tk.END, text)
        text_area.config(state=tk.DISABLED)  # Make read-only
        
        # Action buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
        
        # Action buttons based on response type
        self._create_action_buttons(button_frame, text, response_type, window)
    
    def _get_response_icon(self, response_type: str) -> str:
        """Get emoji icon for response type"""
        
        icons = {
            'suggestion': '💡',
            'reminder': '⏰',
            'question': '❓',
            'action': '⚡',
            'creative': '🎨',
            'social_media': '📱',
            'communication': '💬',
            'writing': '📝',
            'web_browsing': '🌐',
            'development': '💻',
            'summary': '📄',
            'default': '🤖'
        }
        
        return icons.get(response_type, icons['default'])
    
    def _create_action_buttons(self, parent: ttk.Frame, text: str, 
                             response_type: str, window: tk.Tk):
        """Create action buttons based on response type"""
        
        # Always include Copy and Dismiss buttons
        copy_btn = ttk.Button(parent, text="📋 Copy", 
                             command=lambda: self._copy_to_clipboard(text))
        copy_btn.grid(row=0, column=0, padx=(0, 5))
        
        dismiss_btn = ttk.Button(parent, text="Dismiss", 
                               command=lambda: self._dismiss_window(window))
        dismiss_btn.grid(row=0, column=1, padx=5)
        
        # Response-type specific buttons
        if response_type == 'social_media':
            # Button to help with posting
            post_btn = ttk.Button(parent, text="📤 Use This", 
                                command=lambda: self._handle_social_action(text, window))
            post_btn.grid(row=0, column=2, padx=5)
            
        elif response_type == 'reminder':
            # Button to set system reminder
            remind_btn = ttk.Button(parent, text="⏰ Set Reminder", 
                                  command=lambda: self._set_system_reminder(text))
            remind_btn.grid(row=0, column=2, padx=5)
            
        elif response_type == 'action':
            # Button to execute suggested action
            action_btn = ttk.Button(parent, text="▶️ Execute", 
                                  command=lambda: self._execute_action(text))
            action_btn.grid(row=0, column=2, padx=5)
    
    def _copy_to_clipboard(self, text: str):
        """Copy text to system clipboard"""
        try:
            # Use pyautogui to copy to clipboard
            import pyperclip
            pyperclip.copy(text)
            print("📋 Copied to clipboard")
        except ImportError:
            # Fallback to pbcopy on macOS
            try:
                subprocess.run(['pbcopy'], input=text.encode(), check=True)
                print("📋 Copied to clipboard")
            except Exception as e:
                print(f"Error copying to clipboard: {e}")
    
    def _dismiss_window(self, window: tk.Tk):
        """Dismiss the response window"""
        try:
            if self.auto_dismiss_timer:
                window.after_cancel(self.auto_dismiss_timer)
                self.auto_dismiss_timer = None
            
            window.destroy()
            self.current_window = None
            print("🗑️ Response window dismissed")
            
        except Exception as e:
            print(f"Error dismissing window: {e}")
    
    def _handle_social_action(self, text: str, window: tk.Tk):
        """Handle social media posting action"""
        # Copy text and close window
        self._copy_to_clipboard(text)
        self._dismiss_window(window)
        
        # Could add integration with social media APIs here
        print("📱 Social media text copied - ready to paste")
    
    def _set_system_reminder(self, text: str):
        """Set a system reminder (macOS specific)"""
        try:
            # Use macOS Reminders app
            applescript = f'''
            tell application "Reminders"
                tell list "Cluely"
                    make new reminder with properties {{name:"{text}"}}
                end tell
            end tell
            '''
            
            subprocess.run(['osascript', '-e', applescript], check=True)
            print("⏰ Reminder set in macOS Reminders app")
            
        except Exception as e:
            print(f"Error setting reminder: {e}")
            # Fallback - just copy to clipboard
            self._copy_to_clipboard(f"REMINDER: {text}")
    
    def _execute_action(self, text: str):
        """Execute suggested action"""
        # This would contain logic to execute various actions
        # For now, just copy the action text
        self._copy_to_clipboard(text)
        print(f"⚡ Action prepared: {text}")

# Global response window instance
response_window = ResponseWindow()

def show_response(text: str, response_type: str = "suggestion", 
                 title: str = "Cluely Suggestion", auto_dismiss: int = 10):
    """
    Convenience function to show AI response
    
    Args:
        text (str): Response text
        response_type (str): Type of response
        title (str): Window title
        auto_dismiss (int): Auto-dismiss timer in seconds
    """
    
    if not text or not text.strip():
        print("⚠️ No response text to display")
        return
    
    print(f"💬 Showing {response_type}: {text[:50]}...")
    response_window.show_response(text, title, auto_dismiss, response_type)

def show_reminder(reminder_text: str):
    """Show a reminder popup"""
    show_response(
        f"⏰ Reminder: {reminder_text}",
        response_type="reminder",
        title="Cluely Reminder",
        auto_dismiss=0  # Don't auto-dismiss reminders
    )

def show_error(error_text: str):
    """Show an error message"""
    show_response(
        f"❌ Error: {error_text}",
        response_type="error",
        title="Cluely Error",
        auto_dismiss=5
    )

def test_response_display():
    """Test the response display functionality"""
    print("🧪 Testing response display...")
    
    # Test different response types
    test_responses = [
        ("Here's a suggested tweet: 'Just discovered an amazing new productivity tip! #productivity #lifehack'", "social_media"),
        ("Remember to call mom at 3 PM today", "reminder"),
        ("Based on what's on your screen, you might want to copy that code snippet and save it for later reference.", "suggestion"),
        ("You asked about Python. Python is a versatile programming language known for its simplicity and readability.", "question")
    ]
    
    for i, (text, resp_type) in enumerate(test_responses):
        print(f"Testing response {i+1}: {resp_type}")
        show_response(text, resp_type, auto_dismiss=3)
        time.sleep(4)  # Wait between tests
    
    print("✅ Response display test completed") 