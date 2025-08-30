#!/bin/bash

# Smart Gemini Chatbot Setup Script (Miniconda)
echo "🐍 Setting up Smart Gemini Chatbot with Miniconda..."

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "❌ Conda is not installed. Please install Miniconda first:"
    echo "   https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

echo "✅ Conda detected"

# Environment name
ENV_NAME="chatbot-streamlit"

# Check if environment already exists
if conda info --envs | grep -q "$ENV_NAME"; then
    echo "⚠️  Environment '$ENV_NAME' already exists."
    read -p "Do you want to remove it and create a new one? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing existing environment..."
        conda env remove -n "$ENV_NAME" -y
    else
        echo "ℹ️  Using existing environment. Activating..."
        conda activate "$ENV_NAME"
        echo "📥 Installing/updating dependencies..."
        pip install -r requirements.txt
        echo ""
        echo "🎉 Setup complete!"
        echo ""
        echo "📋 To run the application:"
        echo "   conda activate $ENV_NAME"
        echo "   streamlit run streamlit_app.py"
        echo ""
        exit 0
    fi
fi

# Create conda environment with Python 3.9
echo "📦 Creating conda environment '$ENV_NAME' with Python 3.9..."
conda create -n "$ENV_NAME" python=3.9 -y

# Activate environment
echo "🔄 Activating environment..."
eval "$(conda shell.bash hook)"
conda activate "$ENV_NAME"

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Activate the conda environment:"
echo "   conda activate $ENV_NAME"
echo ""
echo "2. Run the application:"
echo "   streamlit run streamlit_app.py"
echo ""
echo "3. Open your browser and enter your Google AI API key"
echo ""
echo "🔑 Get your API key from: https://aistudio.google.com/"
echo ""
echo "📝 To deactivate the environment later:"
echo "   conda deactivate"
echo ""
echo "🗑️  To remove the environment:"
echo "   conda env remove -n $ENV_NAME"
echo ""
echo "Happy chatting! 💬"
