<<<<<<< HEAD
# Code Explainer - LangChain Single Agent Project

A beginner-friendly project that teaches you how to build a **single agent** using **LangChain + OpenAI**. The agent takes a code snippet and explains it in simple, plain English suitable for beginners.

## What You'll Learn

- How LangChain works (LLMs, prompts, tools, agents)
- How to create tools using the `@tool` decorator
- How an agent decides which tools to call and in what order
- How `PromptTemplate` shapes LLM output
- How the agent's tool-calling loop works (think -> act -> observe -> repeat)

## How It Works

```
User's code snippet
       |
       v
  [Agent thinks: "I need to analyze this code first"]
       |
       v
  [Tool: code_analyze] --> creates an initial explanation in plain English
       |
       v
  [Agent thinks: "Now I should make this explanation more natural"]
       |
       v
  [Tool: final_code_explanation] --> enhances it to sound conversational and warm with inline comments
       |
       v
  Final beginner-friendly code explanation returned to user
```

## Prerequisites

- Python 3.10 or higher
- An OpenAI API key ([get one here](https://platform.openai.com/api-keys))

## Setup

### 1. Clone the repository

```bash
#git clone https://github.com/NisargKadam/Langchain_sample_project.git
cd Langchain_sample_project_assignment
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

- **Windows (PowerShell):**
  ```powershell
  .venv\Scripts\Activate
  ```
- **macOS / Linux:**
  ```bash
  source .venv/bin/activate
  ```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your API key

Copy the example env file and add your real key:

```bash
cp .env.example .env
```

Open `.env` and replace the placeholder with your actual OpenAI API key:

```
OPENAI_API_KEY=sk-your-actual-key-here
```

## Run

```bash
python Code Explainer.py
```

You'll see an interactive prompt:

```
============================================================
  CODE EXPLAINER AGENT
  Powered by LangChain + OpenAI
============================================================

Paste a code snippet, and the agent will explain it
in simple, beginner-friendly terms.
```

Type 'quit' to exit.

Your code snippet:
```

Type your code snippet (e.g., `def add(a, b): return a + b`) and the agent will generate a beginner-friendly explanation. You'll also see detailed logs showing the agent's reasoning and tool calls.

## Example

**Input:**
```
def add(a, b): return a + b
```

**Output:**
```
This code defines a simple function called add that takes two numbers and returns their sum. Think of it like a calculator that only does addition - you give it two numbers, and it gives you back the total. For example, if you call add(3, 5), it would return 8. It's a basic building block that other parts of your program can use whenever they need to add two numbers together.
```

## Project Structure

```
.
├── Code Explainer.py   # Main agent code (fully commented)
├── requirements.txt     # Python dependencies
├── .env.example         # API key template
├── .gitignore           # Keeps secrets and venv out of git
└── README.md            # This file
```

## Tech Stack

- [LangChain](https://python.langchain.com/) - Framework for building LLM applications
- [OpenAI GPT-4o-mini](https://platform.openai.com/) - The LLM powering the agent
- [python-dotenv](https://pypi.org/project/python-dotenv/) - Environment variable management
