#!/usr/bin/env python3
"""
Setup script for Cluely AI Desktop Assistant
"""

import os
import sys
import subprocess
import platform
import urllib.request

def check_system():
    """Check system requirements"""
    print("🔍 Checking system requirements...")
    
    # Check OS
    if platform.system() != "Darwin":
        print("❌ Cluely currently only supports macOS")
        return False
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    
    print("✅ System requirements met")
    return True

def install_homebrew_dependencies():
    """Install required Homebrew packages"""
    print("🍺 Installing Homebrew dependencies...")
    
    try:
        # Check if Homebrew is installed
        subprocess.run(["brew", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Homebrew not found. Please install Homebrew first:")
        print("  /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
        return False
    
    # Install tesseract
    try:
        print("📦 Installing tesseract...")
        subprocess.run(["brew", "install", "tesseract"], check=True)
        print("✅ Tesseract installed")
    except subprocess.CalledProcessError:
        print("⚠️ Failed to install tesseract via Homebrew")
        return False
    
    return True

def create_virtual_environment():
    """Create and activate virtual environment"""
    print("🐍 Setting up Python virtual environment...")
    
    venv_path = "cluely_env"
    
    try:
        # Create virtual environment
        subprocess.run([sys.executable, "-m", "venv", venv_path], check=True)
        print(f"✅ Virtual environment created: {venv_path}")
        
        # Instructions for activation
        print(f"\n📝 To activate the virtual environment:")
        print(f"  source {venv_path}/bin/activate")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False

def install_python_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    # Determine pip path
    if os.path.exists("cluely_env/bin/pip"):
        pip_path = "cluely_env/bin/pip"
    else:
        pip_path = "pip"
    
    try:
        # Upgrade pip
        subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True)
        
        # Install requirements
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
        
        print("✅ Python dependencies installed")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Python dependencies: {e}")
        return False

def create_models_directory():
    """Create models directory for local LLMs"""
    print("📁 Creating models directory...")
    
    models_dir = "models"
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
        print(f"✅ Created {models_dir} directory")
    else:
        print(f"✅ {models_dir} directory already exists")
    
    # Create README for models
    readme_content = """# Models Directory

This directory is for storing local GGUF model files.

## Recommended Models:

### Small/Fast (3-7B parameters):
- **Orca Mini 3B**: Good balance of speed and quality
  - Download: https://huggingface.co/microsoft/orca-mini-3b-gguf
  
- **Mistral 7B Instruct**: Higher quality, slightly slower
  - Download: https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.1-GGUF

### Larger/Better (13B+ parameters):
- **Llama 2 13B Chat**: Best quality, requires more RAM
  - Download: https://huggingface.co/meta-llama/Llama-2-13b-chat-gguf

## Installation:

1. Download a .gguf file from the links above
2. Place it in this `models/` directory
3. Update the model path in `llm/local_llm_runner.py` if needed

## Alternative: Use OpenAI API

If you prefer to use OpenAI instead of local models:

1. Set your API key:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

2. Cluely will automatically use OpenAI if no local model is found.
"""
    
    readme_path = os.path.join(models_dir, "README.md")
    with open(readme_path, "w") as f:
        f.write(readme_content)
    
    print(f"✅ Created {readme_path}")
    return True

def setup_permissions():
    """Guide user through macOS permissions setup"""
    print("🔐 Setting up macOS permissions...")
    print("\nCluely needs the following permissions to work:")
    print("1. 🎙️ Microphone access (for speech recognition)")
    print("2. 📸 Screen recording (for screenshot analysis)")
    print("3. ♿ Accessibility (for window detection)")
    print("\nTo grant these permissions:")
    print("1. Open System Preferences > Security & Privacy")
    print("2. Go to Privacy tab")
    print("3. Add Terminal/iTerm (or your terminal app) to:")
    print("   - Microphone")
    print("   - Screen Recording")
    print("   - Accessibility")
    print("\n⚠️ You may need to restart your terminal after granting permissions.")

def main():
    """Main setup function"""
    print("🧠 Cluely Setup Script")
    print("=" * 40)
    
    if not check_system():
        sys.exit(1)
    
    # Install Homebrew dependencies
    if not install_homebrew_dependencies():
        print("⚠️ Some dependencies may not be installed. Continue? (y/n): ", end="")
        if input().lower() != 'y':
            sys.exit(1)
    
    # Create virtual environment
    if not create_virtual_environment():
        sys.exit(1)
    
    # Install Python dependencies
    if not install_python_dependencies():
        sys.exit(1)
    
    # Create models directory
    create_models_directory()
    
    # Setup permissions guide
    setup_permissions()
    
    print("\n🎉 Setup complete!")
    print("\n🚀 Next steps:")
    print("1. Activate virtual environment:")
    print("   source cluely_env/bin/activate")
    print("\n2. Download a model (optional for local LLM):")
    print("   See models/README.md for download links")
    print("\n3. Set OpenAI API key (optional):")
    print("   export OPENAI_API_KEY='your-key-here'")
    print("\n4. Test the installation:")
    print("   python main.py test")
    print("\n5. Run Cluely:")
    print("   python main.py")

if __name__ == "__main__":
    main() 