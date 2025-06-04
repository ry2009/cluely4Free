from typing import Dict, Any
import datetime

def build_prompt(audio_text: str, screen_text: str, app: str, context: Dict[str, Any] = None) -> str:
    """
    Build contextual prompt for the LLM based on current situation
    
    Args:
        audio_text (str): What the user said
        screen_text (str): Text visible on screen
        app (str): Currently active application
        context (dict): Additional context information
    
    Returns:
        str: Formatted prompt for LLM
    """
    
    # Get current time for context
    current_time = datetime.datetime.now().strftime("%I:%M %p")
    current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
    
    # Base system prompt
    system_prompt = f"""You are Cluely, a helpful and proactive desktop AI assistant. You understand context from what users say and what's visible on their screen.

Current Context:
- Time: {current_time}
- Date: {current_date}
- Active App: {app}
- User Said: "{audio_text}"

Response Guidelines:
- Be helpful, concise, and actionable (2-4 sentences max)
- Directly address what the user asked about
- Use information from the screen when relevant
- Provide specific suggestions or explanations
- Be conversational and friendly, not robotic
- If screen text is unclear, focus on the user's question

"""
    
    # Add context-specific instructions
    context_prompt = build_context_specific_prompt(app, audio_text, screen_text, context)
    
    # Add screen content if relevant
    screen_prompt = build_screen_content_prompt(screen_text, app)
    
    # Combine all parts
    full_prompt = system_prompt + context_prompt + screen_prompt
    
    return full_prompt

def build_context_specific_prompt(app: str, audio_text: str, screen_text: str, context: Dict[str, Any] = None) -> str:
    """
    Build app-specific prompt additions
    """
    
    app_lower = app.lower()
    audio_lower = audio_text.lower()
    
    # Social Media (Twitter/X)
    if 'twitter' in app_lower or 'x.com' in app_lower:
        if any(word in audio_lower for word in ['tweet', 'post', 'share']):
            return """
Context: User wants to create a tweet/post on Twitter/X.

Instructions:
- Suggest a compelling tweet based on screen content
- Keep it under 280 characters
- Make it engaging and authentic
- Include relevant hashtags if appropriate
- Consider current trends or topics visible on screen

"""
    
    # Email/Communication
    elif app_lower in ['mail', 'gmail', 'outlook'] or 'email' in audio_lower:
        return """
Context: User is working with email/messages.

Instructions:
- Help compose professional, clear communication
- Suggest appropriate tone based on context
- Offer template phrases if composing
- Suggest improvements if reviewing content

"""
    
    # Writing/Documentation
    elif app_lower in ['word', 'docs', 'notion', 'obsidian', 'pages']:
        if 'summarize' in audio_lower:
            return """
Context: User wants to summarize content.

Instructions:
- Provide a concise summary of visible text
- Highlight key points and main ideas
- Use bullet points if appropriate
- Keep summary to 2-3 sentences

"""
        else:
            return """
Context: User is writing or editing documents.

Instructions:
- Suggest improvements to writing
- Help with clarity and flow
- Offer alternative phrasings
- Assist with structure and organization

"""
    
    # Web Browsing
    elif app_lower in ['chrome', 'safari', 'firefox']:
        if any(word in audio_lower for word in ['chart', 'graph', 'data', 'visualization', 'plot']):
            return """
Context: User is asking about charts, graphs, or data visualizations on a web page.

Instructions:
- Focus on explaining the data and trends shown
- Identify the type of chart/graph if possible
- Explain what the data represents
- Point out key insights or patterns
- Explain axes, labels, and data points if visible
- If chart details are unclear, explain based on context

"""
        else:
            return """
Context: User is browsing the web.

Instructions:
- Help explain or summarize web content
- Suggest related topics or actions
- Offer to extract key information
- Provide context about what's being viewed

"""
    
    # Development/Coding
    elif app_lower in ['vscode', 'cursor', 'xcode', 'terminal']:
        return """
Context: User is coding or using development tools.

Instructions:
- Offer coding suggestions or explanations
- Help debug or improve code
- Suggest best practices
- Explain technical concepts if asked

"""
    
    # Default context
    return """
Context: General assistance needed.

Instructions:
- Provide helpful, relevant suggestions
- Consider the user's current activity
- Offer actionable next steps
- Be proactive but not intrusive

"""

def build_screen_content_prompt(screen_text: str, app: str) -> str:
    """
    Build prompt section for screen content
    """
    
    if not screen_text or len(screen_text.strip()) < 10:
        return "\nScreen Content: [No readable text detected]\n"
    
    # Truncate very long content
    if len(screen_text) > 1500:
        screen_text = screen_text[:1500] + "..."
    
    return f"""
Screen Content (what user is currently viewing):
"{screen_text}"

Based on this screen content and the user's request, provide your response:
"""

def build_reminder_prompt(reminder_text: str) -> str:
    """
    Build prompt for reminder functionality
    """
    
    return f"""You are Cluely, a desktop AI assistant. The user asked you to remind them about something.

User's reminder request: "{reminder_text}"

Create a helpful reminder message that:
- Clearly restates what they wanted to remember
- Is friendly and conversational
- Includes the current time for context
- Suggests any relevant next steps

Current time: {datetime.datetime.now().strftime("%I:%M %p")}

Reminder message:"""

def build_question_prompt(question: str, screen_text: str, app: str) -> str:
    """
    Build prompt for answering questions
    """
    
    context_info = ""
    if screen_text and len(screen_text.strip()) > 10:
        context_info = f"\n\nContext from screen:\n{screen_text}"
    
    return f"""You are Cluely, a helpful desktop AI assistant. The user asked a question while using {app}.

Question: "{question}"{context_info}

Provide a helpful, accurate answer that:
- Directly addresses their question
- Uses screen context if relevant
- Is concise but complete
- Offers additional help if appropriate

Answer:"""

def build_creative_prompt(creative_request: str, screen_text: str, app: str) -> str:
    """
    Build prompt for creative tasks (brainstorming, ideas, etc.)
    """
    
    context_info = ""
    if screen_text and len(screen_text.strip()) > 10:
        context_info = f"\n\nCurrent context:\n{screen_text}"
    
    return f"""You are Cluely, a creative AI assistant. The user needs help with brainstorming or creative thinking while using {app}.

Request: "{creative_request}"{context_info}

Provide creative, actionable suggestions that:
- Are relevant to their current context
- Offer 3-5 concrete ideas
- Are practical and achievable
- Spark further creativity

Ideas:"""

def optimize_prompt_length(prompt: str, max_tokens: int = 2000) -> str:
    """
    Optimize prompt length for LLM token limits
    """
    
    if len(prompt) <= max_tokens:
        return prompt
    
    # Try to truncate screen content first
    lines = prompt.split('\n')
    optimized_lines = []
    current_length = 0
    
    for line in lines:
        if current_length + len(line) > max_tokens:
            if 'Screen Content' in line:
                # Truncate this section
                remaining_space = max_tokens - current_length - 50
                if remaining_space > 100:
                    truncated_line = line[:remaining_space] + "...\""
                    optimized_lines.append(truncated_line)
                break
            else:
                optimized_lines.append(line)
                current_length += len(line)
        else:
            optimized_lines.append(line)
            current_length += len(line)
    
    return '\n'.join(optimized_lines) 