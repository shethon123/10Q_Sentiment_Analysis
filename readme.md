# Setup & Installation

## Prerequisites

### 1. Python Dependencies

Install the required packages:

```bash
pip install edgartools transformers openai ollama python-dotenv
```

Install PyTorch with the correct version for your system by visiting the official selector:
👉 https://pytorch.org/get-started/locally/

Choose your OS, package manager, and CUDA version, then run the generated command. Example for CPU-only:

```bash
pip install torch torchvision torchaudio
```

Example for CUDA 12.1:

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

---

### 2. Environment Variables

Copy or create a `.env` file in the project root and set your OpenAI API key:

```
OPENAI_API_KEY=your_openai_api_key_here
```

> ⚠️ **Required:** The app will not work without a valid `OPENAI_API_KEY` in `.env`.

---

### 3. Ollama

Install Ollama from https://ollama.com and then pull the required model:

```bash
ollama pull gemma4:latest
```

Make sure the Ollama service is running before starting the app.

---

## Running the App

```bash
python cli.py
```
