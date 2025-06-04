# 🤖 Cluely - AI Desktop Assistant

**A proactive, context-aware AI desktop assistant that continuously listens for speech, watches your screen, and generates intelligent responses.**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![OpenAI](https://img.shields.io/badge/AI-Google%20Gemini-green)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ Features

- 🎤 **Voice Recognition** - Powered by OpenAI Whisper for accurate speech-to-text
- 👁️ **Screen Awareness** - OCR-based screen reading and context understanding  
- 🧠 **Smart AI** - Google Gemini integration for intelligent responses
- ⚡ **Real-time Processing** - Fast response times with optimized inference
- 🎯 **Intent Detection** - Natural language understanding for various tasks
- 💬 **Interactive UI** - Beautiful popup windows with actionable responses
- 📊 **Chart Analysis** - Specialized understanding of data visualizations

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- macOS (tested) / Linux / Windows
- Google Gemini API key (free) or any other LLM API key / any local llm you can run
- Microphone access

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/ry2009/cluely4Free.git
cd cluely4Free
```

2. **Run the automated setup**
```bash
python setup.py
```

3. **Set your API key**
```bash
export GEMINI_API_KEY="your_api_key_here"
```

4. **Start Cluely**
```bash
python main.py
```

## 🎯 Usage Examples

### Voice Commands

- **"Hey Cluely, what's on my screen?"** - Analyzes current screen content
- **"Hey Cluely, explain this chart"** - Detailed chart and data analysis
- **"Hey Cluely, summarize this article"** - Web content summarization
- **"Hey Cluely, help me with this code"** - Programming assistance

### Supported Applications

- **Development**: VS Code, Cursor, Terminal, Xcode
- **Web Browsing**: Chrome, Safari, Firefox  
- **Writing**: Word, Google Docs, Notion, Obsidian
- **Communication**: Mail, Gmail, Outlook
- **Social Media**: Twitter/X, LinkedIn

## 🏗️ Architecture

```
cluely/
├── audio/           # Speech recognition & processing
├── vision/          # Screen capture & OCR
├── brain/           # Intent routing & prompt building
├── llm/             # AI model interfaces (Gemini, local models)
├── utils/           # Configuration & performance monitoring
└── main.py          # Application entry point
```

## 🔧 Configuration

Customize Cluely via `cluely_config.json`:

```json
{
  "audio": {
    "listen_duration": 3,
    "silence_threshold": 0.01
  },
  "llm": {
    "max_tokens": 1000,
    "temperature": 0.9
  },
  "ui": {
    "auto_dismiss_time": 15
  }
}
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python main.py test
```

Tests include:
- ✅ Environment validation
- ✅ Microphone functionality  
- ✅ Screen capture & OCR
- ✅ Visual parsing
- ✅ LLM connectivity

## 📈 Performance

- **Response Time**: ~3-4 seconds from speech to AI response
- **Audio Processing**: OpenAI Whisper (base model)
- **AI Inference**: Google Gemini 1.5 Flash (optimized for speed)
- **Screen Analysis**: Tesseract OCR with intelligent filtering

## 🔒 Privacy

- **Local Processing**: Audio and screen data processed locally
- **API Calls**: Only text prompts sent to Gemini (no audio/images)
- **No Storage**: No conversation history or personal data stored
- **Secure**: Environment variables for API keys

## 🛠️ Advanced Features

### Multi-Modal Understanding
- Context-aware responses based on active application
- Visual content analysis (charts, graphs, documents)
- Intelligent intent detection from natural speech

### Extensible Architecture
- Modular design for easy feature additions
- Support for multiple LLM backends
- Configurable response types and UI behaviors

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenAI Whisper](https://github.com/openai/whisper) for speech recognition
- [Google Gemini](https://ai.google.dev/) for AI inference
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) for screen text extraction

## 📞 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/ry2009/cluely4Free/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/ry2009/cluely4Free/discussions)
- 📧 **Email**: For private inquiries

---

**Made with suggestions from cluely to cursor directly & by [ry2009](https://github.com/ry2009)**

*Cluely - Your intelligent desktop companion* 
