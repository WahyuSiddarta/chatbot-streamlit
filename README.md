# Smart Gemini Chatbot 💬

An intelligent Streamlit-based chatbot that uses Google's Gemini models with dynamic model routing for optimal performance and cost efficiency.

## Features

- 🤖 **Smart Model Routing**: Automatically selects between `gemini-2.5-flash` and `gemini-2.5-flash-lite` based on query complexity
- 🔍 **Google Search Integration**: Grounded responses with citations
- 💻 **Code Execution**: Built-in code execution capabilities for programming queries
- 💬 **Context Preservation**: Maintains conversation context across model switches
- 📊 **Real-time Stats**: Shows model usage and complexity scoring
- 🎯 **Optimized Performance**: Uses lighter models for simple queries, powerful models for complex ones

## Model Selection Logic

The chatbot intelligently routes queries based on complexity scoring:

### Gemini-2.5-Flash (Complex queries)

- Mathematical problems and algorithms
- Programming and code analysis
- Technical explanations
- Research queries

### Gemini-2.5-Flash-Lite (Simple queries)

- General conversations
- Basic questions
- Simple information requests

## Installation

### Prerequisites

- Python 3.8 or higher
- Google AI API key (get one from [Google AI Studio](https://aistudio.google.com/))

### Setup with Python Virtual Environment

1. **Clone the repository**

   ```bash
   git clone https://github.com/WahyuSiddarta/chatbot-streamlit.git
   cd chatbot-streamlit
   ```

2. **Create and activate virtual environment**

   ```bash
   # Create virtual environment
   python -m venv .venv

   # Activate virtual environment
   # On macOS/Linux:
   source .venv/bin/activate

   # On Windows:
   .venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**

   ```bash
   streamlit run streamlit_app.py
   ```

5. **Enter your Google AI API Key**
   - Open the app in your browser (usually http://localhost:8501)
   - Enter your Google AI API key in the sidebar
   - Start chatting!

## Usage

1. **Start a conversation**: Type any message in the chat input
2. **Watch the smart routing**: The app will show which model is being used
3. **Model switching**: Complex queries automatically switch to more powerful models
4. **Context preservation**: Conversation context is maintained across model switches
5. **Reset conversation**: Use the "Reset Conversation" button to start fresh

## API Key Security

- The API key is entered directly in the Streamlit interface
- Keys are stored only in browser session (not saved permanently)
- Never commit API keys to version control

## Project Structure

```
chatbot-streamlit/
├── streamlit_app.py      # Main Streamlit application
├── main.py              # FastAPI backend (reference implementation)
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── .gitignore          # Git ignore rules
└── LICENSE             # License file
```

## Development

### Key Components

- **Model Routing**: Complexity-based algorithm selection
- **Chat Sessions**: WebSocket-like persistent connections
- **Context Management**: Cross-model conversation preservation
- **Enhanced Features**: Code execution, search grounding, citations

### Customization

You can modify the model routing logic by adjusting these constants in `streamlit_app.py`:

```python
MODEL_MEDIUM_TIER_THRESHOLD = 7  # Threshold for model switching
WEIGHT_HARD = 5                  # Weight for complex keywords
WEIGHT_MEDIUM = 3                # Weight for medium keywords
WEIGHT_SMALL = 2                 # Weight for simple indicators
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [Google Gemini API](https://ai.google.dev/)
- Inspired by intelligent model routing patterns

## Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/WahyuSiddarta/chatbot-streamlit/issues) page
2. Create a new issue if your problem isn't already reported
3. Provide details about your environment and the specific error

---

**Happy Chatting! 🚀**
