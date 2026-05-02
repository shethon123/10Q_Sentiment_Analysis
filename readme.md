# Setup & Installation

## Prerequisites

### 1. Create a Python Virtual Environment

Create and activate a virtual environment before installing any dependencies:

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
```

> You should see `(.venv)` in your terminal prompt once activated. Run all subsequent commands inside this environment.

---

### 2. Python Dependencies

Install the required packages:

```bash
pip install edgartools transformers python-dotenv openai mcp anthropic uvicorn fastapi
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

### 3. Environment Variables

Copy or create a `.env` file in the project root and set your API keys:

```
LLM_PROVIDER=claude          # ollama | openai | claude
ANTHROPIC_API_KEY=your_key   # required if LLM_PROVIDER=claude
OPENAI_API_KEY=your_key      # required if LLM_PROVIDER=openai
OLLAMA_MODEL=gemma4:latest   # required if LLM_PROVIDER=ollama
```

> ⚠️ **Required:** The app will not work without valid credentials in `.env`.

---

### 4. Ollama (optional — only if using `LLM_PROVIDER=ollama`)

Install Ollama from https://ollama.com and then pull the required model:

```bash
ollama pull gemma4:latest
```

Make sure the Ollama service is running before starting the app.

---

## Running the CLI

```bash
python cli.py
```

## Running the Website

In one terminal, start the API server:
```bash
uvicorn api:app --reload
```

In another terminal, serve the frontend:
```bash
python Website/serve.py
```
