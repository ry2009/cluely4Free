# Models Directory

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
