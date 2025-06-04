import pygetwindow as gw
import logging
import re

def get_active_app():
    """
    Get the currently active application/window
    
    Returns:
        str: Name of active application
    """
    try:
        # Try to get active window - handle different pygetwindow versions
        try:
            active_window = gw.getActiveWindow()
        except:
            # Fallback for different API versions
            windows = gw.getAllWindows() if hasattr(gw, 'getAllWindows') else []
            active_window = windows[0] if windows else None
        
        if active_window and hasattr(active_window, 'title'):
            # Get title and ensure it's a string
            title_attr = active_window.title
            if callable(title_attr):
                app_name = str(title_attr())  # Call method if it's callable
            else:
                app_name = str(title_attr)  # Convert to string if it's a property
            
            # Clean and parse app name
            parsed_name = parse_app_name(app_name)
            print(f"🖥️ Active app: {parsed_name}")
            
            return parsed_name
        else:
            print("🖥️ No active window detected")
            return "Unknown"
            
    except Exception as e:
        logging.error(f"Error getting active app: {e}")
        return "Unknown"

def parse_app_name(window_title):
    """
    Parse and clean application name from window title
    
    Args:
        window_title (str): Raw window title
    
    Returns:
        str: Cleaned application name
    """
    if not window_title:
        return "Unknown"
    
    # Common app patterns
    app_patterns = {
        r'.*Twitter.*': 'Twitter',
        r'.*Chrome.*': 'Chrome',
        r'.*Safari.*': 'Safari', 
        r'.*Firefox.*': 'Firefox',
        r'.*Slack.*': 'Slack',
        r'.*Discord.*': 'Discord',
        r'.*Zoom.*': 'Zoom',
        r'.*Microsoft Word.*': 'Word',
        r'.*Microsoft Excel.*': 'Excel',
        r'.*PowerPoint.*': 'PowerPoint',
        r'.*Notion.*': 'Notion',
        r'.*Obsidian.*': 'Obsidian',
        r'.*VS Code.*': 'VS Code',
        r'.*Cursor.*': 'Cursor',
        r'.*Terminal.*': 'Terminal',
        r'.*iTerm.*': 'Terminal',
        r'.*Finder.*': 'Finder',
        r'.*Mail.*': 'Mail',
        r'.*Messages.*': 'Messages',
        r'.*Calendar.*': 'Calendar',
        r'.*Notes.*': 'Notes',
    }
    
    # Check against patterns
    for pattern, app_name in app_patterns.items():
        if re.match(pattern, window_title, re.IGNORECASE):
            return app_name
    
    # If no pattern matches, extract first word or clean title
    cleaned_title = window_title.split(' - ')[0].split(' | ')[0]
    
    # Remove common suffixes
    suffixes_to_remove = ['.app', '.exe', ' (Beta)', ' (Alpha)']
    for suffix in suffixes_to_remove:
        cleaned_title = cleaned_title.replace(suffix, '')
    
    return cleaned_title.strip() or "Unknown"

def get_window_list():
    """
    Get list of all open windows
    
    Returns:
        list: List of window titles
    """
    try:
        # Handle different pygetwindow API versions
        if hasattr(gw, 'getAllWindows'):
            windows = gw.getAllWindows()
        elif hasattr(gw, 'getWindowsWithTitle'):
            # Fallback method
            windows = []
            try:
                # Try to get all windows with any title
                all_titles = gw.getWindowsWithTitle('')
                windows.extend(all_titles)
            except:
                pass
        else:
            windows = []
        
        window_titles = []
        for w in windows:
            if hasattr(w, 'title') and w.title and str(w.title).strip():
                window_titles.append(str(w.title))
        
        print(f"🪟 Found {len(window_titles)} windows")
        return window_titles
        
    except Exception as e:
        logging.error(f"Error getting window list: {e}")
        return []

def detect_app_context(app_name, window_title):
    """
    Detect specific context within an application
    
    Args:
        app_name (str): Name of the application
        window_title (str): Full window title
    
    Returns:
        dict: Context information
    """
    context = {
        'app': app_name,
        'context_type': 'general',
        'details': {}
    }
    
    try:
        app_lower = app_name.lower()
        title_lower = window_title.lower()
        
        # Twitter/X context
        if 'twitter' in app_lower or 'x.com' in title_lower:
            context['context_type'] = 'social_media'
            context['details']['platform'] = 'Twitter'
            
            if 'compose' in title_lower or 'tweet' in title_lower:
                context['details']['action'] = 'composing'
            elif 'home' in title_lower or 'timeline' in title_lower:
                context['details']['action'] = 'browsing'
        
        # Browser context
        elif app_lower in ['chrome', 'safari', 'firefox']:
            context['context_type'] = 'web_browsing'
            context['details']['browser'] = app_name
            
            # Try to extract domain from title
            if ' - ' in window_title:
                parts = window_title.split(' - ')
                if len(parts) >= 2:
                    context['details']['page'] = parts[0]
                    context['details']['domain'] = parts[-1]
        
        # Communication apps
        elif app_lower in ['slack', 'discord', 'messages', 'mail']:
            context['context_type'] = 'communication'
            context['details']['platform'] = app_name
        
        # Productivity apps
        elif app_lower in ['word', 'excel', 'powerpoint', 'notion', 'obsidian']:
            context['context_type'] = 'productivity'
            context['details']['tool'] = app_name
        
        # Development apps
        elif app_lower in ['vs code', 'cursor', 'terminal', 'xcode']:
            context['context_type'] = 'development'
            context['details']['tool'] = app_name
        
        print(f"🔍 App context: {context['context_type']} in {app_name}")
        
        return context
        
    except Exception as e:
        logging.error(f"Error detecting app context: {e}")
        return context

def test_visual_parser():
    """Test visual parser functionality"""
    print("🔍 Testing visual parser...")
    try:
        app = get_active_app()
        windows = get_window_list()
        
        if app != "Unknown":
            print("✅ Visual parser working")
            print(f"🖥️ Active app: {app}")
            print(f"🪟 Total windows: {len(windows)}")
            return True
        else:
            print("⚠️ Visual parser working but no active window")
            return True
            
    except Exception as e:
        print(f"❌ Visual parser test failed: {e}")
        return False 