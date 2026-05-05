"""
===========================================================================
 EMAIL HUMANIZER -- A Beginner's LangChain Single-Agent Project
===========================================================================

 WHAT THIS PROJECT TEACHES YOU:
   1. How LangChain works (chains, prompts, LLMs, tools, agents)
   2. How to build a SINGLE AGENT that uses tools
   3. How to connect LangChain to OpenAI
   4. How prompt templates shape LLM output
   5. How an agent "thinks" using a tool-calling loop

 HOW LANGCHAIN WORKS (the big picture):
   LangChain is a framework that makes it easy to build LLM-powered apps.

     [User Input] --> [Prompt Template] --> [LLM (GPT)] --> [Output]

   - Prompt Template : A reusable template with placeholders (like a form)
   - LLM            : The AI model that generates text (OpenAI GPT)
   - Output         : The generated response

 WHAT IS AN AGENT?
   An agent is an LLM that can USE TOOLS and DECIDE what to do next.
   Unlike a simple chain (input -> LLM -> output), an agent can:
     1. Think about what it needs to do
     2. Pick a tool to use
     3. Use the tool and see the result
     4. Decide if it needs more steps or if it's done

   This is the tool-calling loop:
     THINK -> ACT -> OBSERVE -> THINK -> ... -> FINAL ANSWER

 HOW THIS PROJECT FLOWS:
   1. User provides an email idea (e.g., "thank my team for Q4 results")
   2. Agent calls draft_email tool   -> creates a formal email draft
   3. Agent calls humanize_email tool -> rewrites it to sound natural
   4. Agent returns the final humanized email to the user

 KEY LANGCHAIN COMPONENTS USED:
   - ChatOpenAI      : LLM wrapper that sends prompts to OpenAI's GPT API
   - PromptTemplate  : Template with {placeholders} filled before sending to LLM
   - @tool decorator : Turns a Python function into a tool the agent can call
   - create_agent    : Wires LLM + tools + system prompt into a runnable agent

 SETUP:
   1. pip install -r requirements.txt
   2. Copy .env.example to .env and add your OpenAI API key
   3. python email_humanizer.py

 See langchain_tutorial.md for a full beginner's guide to LangChain.
 See architecture_diagram.drawio for a visual diagram of this project.
===========================================================================
"""

from dis import code_info
import logging
import sys
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("EmailHumanizer")

logger.info("Starting Email Humanizer Agent...")

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key or api_key.startswith("sk-your"):
    logger.error("OPENAI_API_KEY not set! Copy .env.example to .env and add your key.")
    sys.exit(1)

logger.info("API key loaded successfully")
logger.info("All LangChain components imported")
logger.info("Initializing the LLM (OpenAI GPT)...")

llm = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0.8,
    verbose=True,
)

logger.info("LLM initialized: model=gpt-4.1-mini, temperature=0.7")
logger.info("Defining agent tools...")


@tool
def explain_code(idea: str) -> str:
    """
    create paragraph-style instrcuctions from a raw code snippet (any language) or block of code (any language).
    use this tool FIRST when the user provides a code snippet or block of code. Input should be the raw code snippet or block of code.
    Explain what the code does in simple, plain English — no jargon, suitable for a beginner
    returns a paragraph-style plain English explanation.

    """
    logger.info(f"[Tool: code_analyze] Received idea: '{idea}'")

    explain_code_prompt = PromptTemplate(
        input_variables=["idea"],
        template="""You are a professional code analyst specializing in teaching beginners.
        Given the following idea, write aparagraph-style plain English explanation of what the code does, suitable for a beginner.

Code Snippet: {idea}

Instructions:
- Input will be a raw code snippet.
- Explain what it does in simple, plain English.
- Avoid technical jargon or complex terms.
- Write the explanation as a clear, short paragraph.

Return ONLY the explanation in paragraph form, nothing else.""",
    )

    formatted_prompt = explain_code_prompt.format(idea=idea)
    logger.info("[Tool: explain_code] Sending prompt to LLM...")

    response = llm.invoke(formatted_prompt)

    logger.info("[Tool: explain_code] Explanation created successfully!")
    return response.content


@tool
def add_inline_comments(draft: str) -> str:
    """
    Rewrite the given code by adding simple and helpful inline comments, focusing only on important or significant lines, 
    without changing how the code works,to make it easier for beginners to understand what each part does.
    Use this tool SECOND, after the explain_code tool has created a plain English explanation. Input should be the original code snippet.
    Returns a version of the code with beginner-friendly inline comments added to key lines, without changing the original code logic or structure.
    
    """
    logger.info("[Tool: add_inline_comments] Humanizing the code explanation...")

    add_inline_comments_prompt = PromptTemplate(
        input_variables=["draft"],
        template="""

        You are a professional code explainer who adds simple, clear inline comments to key lines of the given code without changing it, 
        keeping explanations beginner-friendly and easy to understand.

        Take this code snippet draft and add inline comments to explain what each part does in simple, plain English.

    Rules:
    - Treat the code as something you are explaining to a beginner seeing it for the first time
    - Focus on what each important line is doing, not just what it is
    - Write short, clear inline comments directly next to the relevant code lines
    - Keep explanations simple, natural, and easy to understand
    - Dont change the original code logic or structure in any way
    - Avoid complex terminology; prefer everyday words instead
    - Make sure comments add clarity without making the code cluttered or hard to read

Code Snippet:
{draft}

Return ONLY the humanized code explanation, nothing else.""",
    )

    formatted_prompt = add_inline_comments_prompt.format(draft=draft)
    logger.info("[Tool: add_inline_comments] Sending to LLM for inline comment addition...")

    response = llm.invoke(formatted_prompt)

    logger.info("[Tool: add_inline_comments] Inline comments added successfully!")
    return response.content


tools = [explain_code, add_inline_comments]
logger.info(f"Tools registered: {[t.name for t in tools]}")
logger.info("Creating the agent...") 

SYSTEM_PROMPT = """You are a code explanation assistant. Your job is to act as a patient coding tutor who helps beginners understand any code by explaining it in simple,
 clear language and adding helpful inline comments without changing the original code.

When the user gives you a code snippet, follow these steps:
1. First, use the explain_code tool to create a structured explanation.
2. Then, use the add_inline_comments tool to add inline comments in the code.
3. Return the final humanized explanation to the user.

Always use both tools in order: explain first, then add inline comments."""

agent_graph = create_agent(
    model=llm,
    tools=tools,
    system_prompt=SYSTEM_PROMPT,
    debug=True,
)

logger.info("Agent created and ready to run!")


def run_code_explainer(code_idea: str) -> str:
    """
    Main function to run the code explainer agent.

    Args:
        code_idea: A brief description of the code snippet you want to explain.
                    Example: "a = 5
                              b = 3
                              sum = a + b
                              print(sum)"

    Returns:
        A humanized, natural-sounding explanation of the code with inline comments.
    """
    logger.info("=" * 60)
    logger.info(f"USER'S CODE IDEA: {code_idea}")
    logger.info("=" * 60)
    logger.info("Agent is now thinking... watch the tool-calling loop below!")
    logger.info("-" * 60)

    result = agent_graph.invoke(
        {"messages": [HumanMessage(content=code_idea)]}
    )

    final_code_explanation = result["messages"][-1].content

    logger.info("-" * 60)
    logger.info("Agent finished! Here's your simplified code explanation:")
    logger.info("=" * 60)

    return final_code_explanation


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  CODE EXPLAINER AGENT")
    print("  Powered by LangChain + OpenAI")
    print("=" * 60)
    print("\nDescribe the code snippet you want explained, and the agent will")
    print("create a simplified explanation for you.\n")
    print("Type 'quit' to exit.\n")

    while True:
        code_idea = input("Your code snippet: ").strip()

        if not code_idea:
            print("Please enter a code snippet.\n")
            continue

        if code_idea.lower() in ("quit", "exit", "q"):
            print("\nGoodbye! Happy coding!")
            break

        try:
            simple_code_explanation = run_code_explainer(code_idea)

            print("\n" + "=" * 60)
            print("YOUR SIMPLIFIED CODE EXPLANATION:")
            print("=" * 60)
            print(simple_code_explanation)
            print("=" * 60 + "\n")

        except Exception as e:
            logger.error(f"Something went wrong: {e}")
            print(f"\nError: {e}")
            print("Please check your API key and try again.\n")
# This block runs only when the script is executed directly (not imported as a module)
if __name__ == "__main__":
    # Print a welcome banner to the console
    print("\n" + "=" * 60)
    print("  CODE EXPLAINER AGENT")
    print("  Powered by LangChain + OpenAI")
    print("=" * 60)
    # Give the user instructions on what to do
    print("\nPaste a code snippet, and the agent will explain it")
    print("in simple, beginner-friendly terms.\n")
    print("Type 'quit' to exit.\n")

    # Start an infinite loop to accept multiple code snippets from the user
    while True:
        # Prompt the user to enter a code snippet and remove extra whitespace
        code_idea = input("Your code snippet: ").strip()

        # Check if the user provided an empty input
        if not code_idea:
            print("Please enter a code snippet.\n")
            # Skip to the next iteration if input is empty
            continue

        # Check if the user wants to exit the program
        if code_idea.lower() in ("quit", "exit", "q"):
            print("\nGoodbye! Happy coding!")
            # Break out of the loop to end the program
            break

        # Try to run the code explanation (this can fail if there's an API error)
        try:
            # Call the main function to analyze the code snippet
            simple_code_explanation = run_code_explainer(code_idea)

            # Print a visual separator to clearly show the result
            print("\n" + "=" * 60)
            print("YOUR SIMPLIFIED CODE EXPLANATION:")
            print("=" * 60)
            # Print the explanation generated by the agent
            print(simple_code_explanation)
            print("=" * 60 + "\n")

        # If something goes wrong, catch the error and display it to the user
        except Exception as e:
            # Log the error in the system logs
            logger.error(f"Something went wrong: {e}")
            # Display the error message to the user