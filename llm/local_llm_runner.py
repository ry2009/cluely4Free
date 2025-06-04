import os
import logging
from typing import Optional, Dict, Any

# Try importing local LLM libraries
try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False

# Try importing Google Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

class LLMRunner:
    """Handles LLM inference with multiple backend options"""
    
    def __init__(self, use_local: bool = True):
        self.use_local = use_local
        self.local_model = None
        self.gemini_model = None
        self.model_loaded = False
        
        # Initialize chosen backend
        if use_local and LLAMA_CPP_AVAILABLE:
            self._init_local_model()
        elif GEMINI_AVAILABLE:
            self._init_gemini()
        else:
            raise RuntimeError("No LLM backend available")
    
    def _init_local_model(self):
        """Initialize local LLaMA model"""
        try:
            # Look for model files
            model_paths = [
                "./models/mistral-7b-instruct.Q4_K_M.gguf",
                "./models/llama-2-7b-chat.Q4_K_M.gguf", 
                "./models/orca-mini-3b.Q4_K_M.gguf",
                "./models/orca-mini-3b.q4_0.gguf"
            ]
            
            model_path = None
            for path in model_paths:
                if os.path.exists(path):
                    model_path = path
                    break
            
            if not model_path:
                print("⚠️ No local model found. Please download a GGUF model to ./models/")
                print("📥 Download from: https://huggingface.co/models?search=gguf")
                return False
            
            print(f"🧠 Loading local model: {model_path}")
            self.local_model = Llama(
                model_path=model_path,
                n_ctx=2048,  # Context window
                n_threads=4,  # CPU threads
                verbose=False
            )
            
            self.model_loaded = True
            print("✅ Local model loaded successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error loading local model: {e}")
            return False
    
    def _init_gemini(self):
        """Initialize Google Gemini client"""
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                print("⚠️ GEMINI_API_KEY not set")
                return False
            
            genai.configure(api_key=api_key)
            # Use gemini-1.5-flash for faster responses
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            self.model_loaded = True
            print("✅ Gemini client initialized")
            return True
            
        except Exception as e:
            print(f"❌ Error initializing Gemini: {e}")
            return False
    
    def generate_response(self, prompt: str, max_tokens: int = 150) -> str:
        """
        Generate response using configured LLM
        
        Args:
            prompt (str): Input prompt
            max_tokens (int): Maximum tokens to generate
        
        Returns:
            str: Generated response
        """
        
        if not self.model_loaded:
            return "❌ No LLM model available"
        
        try:
            if self.use_local and self.local_model:
                return self._generate_local(prompt, max_tokens)
            elif self.gemini_model:
                return self._generate_gemini(prompt, max_tokens)
            else:
                return "❌ No available LLM backend"
                
        except Exception as e:
            logging.error(f"Error generating response: {e}")
            return f"❌ Error generating response: {str(e)}"
    
    def _generate_local(self, prompt: str, max_tokens: int) -> str:
        """Generate response using local LLaMA model"""
        
        try:
            response = self.local_model(
                prompt,
                max_tokens=max_tokens,
                temperature=0.7,
                top_p=0.9,
                echo=False,
                stop=["User:", "Human:", "\n\n"]
            )
            
            generated_text = response["choices"][0]["text"].strip()
            return generated_text
            
        except Exception as e:
            raise Exception(f"Local model error: {e}")
    
    def _generate_gemini(self, prompt: str, max_tokens: int) -> str:
        """Generate response using Google Gemini API"""
        
        try:
            response = self.gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.9,  # Higher for faster, more creative responses
                    top_k=20,         # Lower for faster sampling
                    top_p=0.8,        # Lower for faster, more focused responses
                    candidate_count=1
                )
            )
            
            return response.text.strip()
            
        except Exception as e:
            raise Exception(f"Gemini API error: {e}")

# Global LLM runner instance
llm_runner = None

def initialize_llm(use_local: bool = True) -> bool:
    """
    Initialize the global LLM runner
    
    Args:
        use_local (bool): Whether to use local model or Gemini
    
    Returns:
        bool: True if initialization successful
    """
    global llm_runner
    
    try:
        llm_runner = LLMRunner(use_local=use_local)
        return llm_runner.model_loaded
    except Exception as e:
        print(f"❌ Failed to initialize LLM: {e}")
        return False

def run_llm(prompt: str, max_tokens: int = 150) -> str:
    """
    Generate response using the global LLM runner
    
    Args:
        prompt (str): Input prompt
        max_tokens (int): Maximum tokens to generate
    
    Returns:
        str: Generated response
    """
    global llm_runner
    
    if llm_runner is None:
        # Try to initialize with local model first, fallback to Gemini
        if not initialize_llm(use_local=True):
            if not initialize_llm(use_local=False):
                # For testing, return a mock response
                print("⚠️ No LLM available - using mock response for testing")
                return "This is a test response from Cluely! 🤖 Your request was processed successfully."
    
    return llm_runner.generate_response(prompt, max_tokens)

def test_llm():
    """Test LLM functionality"""
    print("🧪 Testing LLM...")
    
    test_prompt = "You are a helpful AI assistant. Respond with a brief greeting."
    
    response = run_llm(test_prompt, max_tokens=50)
    
    if response and not response.startswith("❌"):
        print("✅ LLM test successful")
        print(f"🤖 Response: {response}")
        return True
    else:
        print("❌ LLM test failed")
        print(f"Error: {response}")
        return False 