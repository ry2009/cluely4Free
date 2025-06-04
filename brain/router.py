import re
from typing import Dict, Any

def should_respond(audio_text: str, screen_text: str, app: str, context: Dict[str, Any] = None) -> bool:
    """
    Determine if the assistant should generate a response based on current context
    
    Args:
        audio_text (str): Transcribed speech from user
        screen_text (str): Text extracted from screen
        app (str): Currently active application
        context (dict): Additional context information
    
    Returns:
        bool: True if assistant should respond
    """
    
    if not audio_text.strip():
        return False  # No speech detected
    
    audio_lower = audio_text.lower().strip()
    app_lower = app.lower()
    
    # Direct trigger phrases
    direct_triggers = [
        "hey cluely", "cluely", "hey cluey", "cluey", 
        "hey chloe", "chloe", "hey clue", "clue",
        "suggest", "help me", "what should i",
        "generate", "create", "write", "compose"
    ]
    
    for trigger in direct_triggers:
        if trigger in audio_lower:
            print(f"🎯 Direct trigger detected: '{trigger}'")
            return True
    
    # Context-specific triggers
    context_triggers = check_context_triggers(audio_lower, app_lower, screen_text)
    if context_triggers:
        print(f"🎯 Context trigger detected: {context_triggers}")
        return True
    
    # Intent-based triggers
    intent_triggers = check_intent_triggers(audio_lower)
    if intent_triggers:
        print(f"🎯 Intent trigger detected: {intent_triggers}")
        return True
    
    return False

def check_context_triggers(audio_text: str, app: str, screen_text: str) -> str:
    """
    Check for context-specific trigger patterns
    
    Returns:
        str: Description of triggered context, or empty string if none
    """
    
    # Social media context
    if app in ['twitter', 'x.com'] or 'twitter' in screen_text.lower():
        social_triggers = [
            "tweet", "post", "share", "publish", 
            "what should i tweet", "tweet about this",
            "social media", "share this"
        ]
        
        for trigger in social_triggers:
            if trigger in audio_text:
                return f"social_media:{trigger}"
    
    # Email/Communication context
    if app in ['mail', 'gmail', 'outlook'] or any(word in screen_text.lower() for word in ['email', 'message', 'reply']):
        email_triggers = [
            "reply", "respond", "email", "message",
            "write back", "send", "compose"
        ]
        
        for trigger in email_triggers:
            if trigger in audio_text:
                return f"communication:{trigger}"
    
    # Document/Writing context
    if app in ['word', 'docs', 'notion', 'obsidian'] or any(word in screen_text.lower() for word in ['document', 'note', 'write']):
        writing_triggers = [
            "summarize", "summary", "rewrite", "edit",
            "improve", "polish", "draft", "outline"
        ]
        
        for trigger in writing_triggers:
            if trigger in audio_text:
                return f"writing:{trigger}"
    
    # Web browsing context
    if app in ['chrome', 'safari', 'firefox']:
        web_triggers = [
            "summarize this page", "what is this about",
            "explain this", "tldr", "summary"
        ]
        
        for trigger in web_triggers:
            if trigger in audio_text:
                return f"web_browsing:{trigger}"
    
    return ""

def check_intent_triggers(audio_text: str) -> str:
    """
    Check for intent-based triggers regardless of context
    
    Returns:
        str: Description of triggered intent, or empty string if none
    """
    
    # Reminder intent
    reminder_patterns = [
        r"remind me (?:to )?(.+)",
        r"don't forget (?:to )?(.+)",
        r"remember (?:to )?(.+)",
        r"note that (.+)",
        r"make a note (.+)"
    ]
    
    for pattern in reminder_patterns:
        match = re.search(pattern, audio_text, re.IGNORECASE)
        if match:
            return f"reminder:{match.group(1)}"
    
    # Question intent - MUCH more flexible patterns
    question_keywords = [
        "what", "how", "why", "when", "where", "who", "which",
        "explain", "tell me", "describe", "show me", "help me understand",
        "what's", "what is", "what are", "what does", "what do",
        "how does", "how do", "how can", "how should",
        "can you explain", "can you tell me", "can you show me",
        "what's this", "what's that", "what are these", "what are those",
        "tell me about", "explain this", "explain that",
        "what is this", "what is that", "what are these",
        "help me with", "help me understand"
    ]
    
    audio_lower = audio_text.lower()
    for keyword in question_keywords:
        if keyword in audio_lower:
            return "question"
    
    # Action intent
    action_patterns = [
        "copy this", "copy that", "select all",
        "open", "close", "save", "delete",
        "search for", "find", "look up"
    ]
    
    for pattern in action_patterns:
        if pattern in audio_text:
            return f"action:{pattern}"
    
    # Creative intent
    creative_patterns = [
        "brainstorm", "ideas", "creative", "inspiration",
        "alternatives", "options", "suggestions"
    ]
    
    for pattern in creative_patterns:
        if pattern in audio_text:
            return f"creative:{pattern}"
    
    return ""

def get_response_priority(audio_text: str, app: str, context: Dict[str, Any] = None) -> str:
    """
    Determine priority level for response
    
    Returns:
        str: Priority level (high, medium, low)
    """
    
    audio_lower = audio_text.lower()
    
    # High priority triggers
    high_priority = [
        "urgent", "important", "asap", "quickly",
        "help", "error", "problem", "issue"
    ]
    
    for trigger in high_priority:
        if trigger in audio_lower:
            return "high"
    
    # Medium priority (direct requests)
    medium_priority = [
        "please", "can you", "could you", "would you",
        "suggest", "recommend", "generate"
    ]
    
    for trigger in medium_priority:
        if trigger in audio_lower:
            return "medium"
    
    return "low"

def should_interrupt_current_task(audio_text: str, priority: str) -> bool:
    """
    Determine if current response should interrupt ongoing tasks
    
    Returns:
        bool: True if should interrupt
    """
    
    if priority == "high":
        return True
    
    interrupt_phrases = [
        "stop", "cancel", "never mind", "forget it",
        "wait", "hold on", "actually"
    ]
    
    audio_lower = audio_text.lower()
    for phrase in interrupt_phrases:
        if phrase in audio_lower:
            return True
    
    return False 