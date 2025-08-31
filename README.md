# Smart Gemini Chatbot 💬

An intelligent Streamlit-based chatbot that uses Google's Gemini models with dynamic three-tier model routing for optimal performance and cost efficiency.

## Features

- 🤖 **Smart 3-Tier Model Routing**: Automatically selects between `gemini-2.5-pro`, `gemini-2.5-flash`, and `gemini-2.5-flash-lite` based on query complexity
- 🧠 **Model Thinking Display**: See the AI's decision-making process in real-time (toggleable)
- 🔍 **Google Search Integration**: Grounded responses with citations
- 💻 **Code Execution**: Built-in code execution capabilities for programming queries
- 💬 **Context Preservation**: Maintains conversation context across model switches
- 📊 **Real-time Stats**: Shows model usage, complexity scoring, and token counting
- ⚙️ **Advanced Parameter Tuning**: Temperature, top_p, and top_k optimization per model
- 🎯 **Optimized Performance**: Uses appropriate models for different complexity levels

## Model Selection Logic

The chatbot intelligently routes queries based on complexity scoring and conversation length:

### Gemini-2.5-Pro (Most Complex/Long Conversations)

- Very complex mathematical problems and advanced algorithms
- Research-level technical analysis and academic queries
- Long conversations (>3000 tokens)
- **Parameters**: Temperature=0.2, Top-p=0.8, Top-k=20 (focused & consistent)

### Gemini-2.5-Flash (Medium Complexity)

- Programming and code analysis
- Technical explanations and documentation
- Medium complexity problems
- **Parameters**: Temperature=0.7, Top-p=0.9, Top-k=40 (balanced)

### Gemini-2.5-Flash-Lite (Simple/Quick Queries)

- General conversations and casual chat
- Basic questions and simple information requests
- Short conversations and quick responses
- **Parameters**: Temperature=1.0, Top-p=0.95, Top-k=64 (creative & varied)

### Model Thinking Display 🧠

Toggle the **"Show Model Thinking Process"** to see:
- 🎯 Complexity analysis and scoring
- 🔢 Real-time token counting
- 🤖 Model selection reasoning
- ⚡ Context preservation during switches
- ⚙️ Parameter configuration details

## Installation

### Prerequisites

- Python 3.8 or higher (or Miniconda/Anaconda)
- Google AI API key (get one from [Google AI Studio](https://aistudio.google.com/))

### Option 1: Automated Setup with Python Virtual Environment

**Quick setup using the provided script:**

```bash
git clone https://github.com/WahyuSiddarta/chatbot-streamlit.git
cd chatbot-streamlit
./setup.sh
```

### Option 2: Automated Setup with Miniconda

**Quick setup using Miniconda (recommended for isolated environments):**

```bash
git clone https://github.com/WahyuSiddarta/chatbot-streamlit.git
cd chatbot-streamlit
./setup-conda.sh
```

> **Note**: If you don't have Miniconda installed, download it from [https://docs.conda.io/en/latest/miniconda.html](https://docs.conda.io/en/latest/miniconda.html)

### Option 3: Manual Setup with Python Virtual Environment

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

### Option 4: Manual Setup with Miniconda

1. **Clone the repository**

   ```bash
   git clone https://github.com/WahyuSiddarta/chatbot-streamlit.git
   cd chatbot-streamlit
   ```

2. **Create and activate conda environment**

   ```bash
   # Create conda environment with Python 3.9
   conda create -n chatbot-streamlit python=3.9 -y

   # Activate the environment
   conda activate chatbot-streamlit
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

6. **Environment management**

   ```bash
   # To deactivate the environment
   conda deactivate

   # To remove the environment (if needed)
   conda env remove -n chatbot-streamlit
   ```

## Usage

1. **Start a conversation**: Type any message in the chat input
2. **Watch the smart routing**: The app shows which model is being used and why
3. **Enable thinking mode**: Toggle "Show Model Thinking Process" to see AI decision-making
4. **Model switching**: Complex queries automatically switch to more powerful models
5. **Context preservation**: Conversation context is maintained across model switches
6. **Monitor performance**: View real-time complexity scores and token usage
7. **Reset conversation**: Use the "Reset Conversation" button to start fresh

## Model Thinking Features

When **"Show Model Thinking Process"** is enabled, you'll see:

- **🎯 Model Selection**: Real-time complexity analysis
- **📊 Complexity Score**: Weighted scoring based on keywords and patterns
- **🔢 Token Count**: Live token estimation using Gemini API
- **🤖 Selected Model**: Which model was chosen and the reasoning
- **⚡ Context Preservation**: When and how model switching occurs
- **⚙️ Parameters**: Temperature, top_p, top_k values for the selected model
- **🧠 Generation Status**: Progress updates during response generation

## API Key Security

- The API key is entered directly in the Streamlit interface
- Keys are stored only in browser session (not saved permanently)
- Never commit API keys to version control

## Project Structure

```
chatbot-streamlit/
├── streamlit_app.py      # Main Streamlit application
├── main.py              # FastAPI backend (reference implementation)
├── requirements.txt     # Python dependencies (streamlit + google-genai)
├── setup.sh             # Automated setup script (Python venv)
├── setup-conda.sh       # Automated setup script (Miniconda)
├── README.md           # This file
├── .gitignore          # Git ignore rules
└── LICENSE             # License file
```

## Development

### Key Components

- **3-Tier Model Routing**: Complexity-based algorithm selection (Pro/Flash/Lite)
- **Model Thinking Display**: Real-time AI decision visualization
- **Advanced Parameter Tuning**: Temperature, top_p, top_k optimization per model
- **Chat Sessions**: WebSocket-like persistent connections with context preservation
- **Token Management**: Real-time counting with API integration and fallbacks
- **Enhanced Features**: Code execution, search grounding, citations

### Customization

You can modify the model routing logic by adjusting these constants in `streamlit_app.py`:

```python
MODEL_MEDIUM_TIER_THRESHOLD = 7  # Threshold for Flash model
MODEL_HIGH_TIER_THRESHOLD = 15   # Threshold for Pro model  
MAX_CHAT_HISTORY = 10           # Context preservation limit

# Complexity weights
WEIGHT_HARD = 5                  # Weight for complex keywords
WEIGHT_MEDIUM = 3                # Weight for medium keywords  
WEIGHT_SMALL = 2                 # Weight for simple indicators

# Model parameters
TEMPERATURE_PRO = 0.2            # Pro model temperature (focused)
TEMPERATURE_FLASH = 0.7          # Flash model temperature (balanced)
TEMPERATURE_LITE = 1.0           # Lite model temperature (creative)

TOP_P_PRO = 0.8                  # Pro model top_p (focused sampling)
TOP_P_FLASH = 0.9                # Flash model top_p (balanced)
TOP_P_LITE = 0.95                # Lite model top_p (broad sampling)

TOP_K_PRO = 20                   # Pro model top_k (precise vocabulary)
TOP_K_FLASH = 40                 # Flash model top_k (balanced variety)
TOP_K_LITE = 64                  # Lite model top_k (diverse vocabulary)
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
