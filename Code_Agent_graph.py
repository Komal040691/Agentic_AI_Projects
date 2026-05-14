# =============================================================================
# Code Explainer Agent -- A LangGraph Learning Project
# =============================================================================

import sys
import operator
import json
from typing import Annotated

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

from pydantic import BaseModel
try:
    from langchain_openai import ChatOpenAI
except ImportError as exc:
    raise SystemExit(
        "Missing required package 'langchain-openai'. Install dependencies with: pip install -r requirements.txt"
    ) from exc
from langgraph.graph import StateGraph, START, END

sys.stdout.reconfigure(encoding="utf-8")
if load_dotenv is not None:
    load_dotenv()


# ---------------------------------------------------

# Define State

# ---------------------------------------------------

class CodeState(BaseModel):
    code: str = ""
    review_type: str = ""
    explanation: str = ""
    risk: str = ""
    comments: str = ""
    final_output: str = ""
    messages: Annotated[list[str], operator.add] = []

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# ---------------------------------------------------

# Specialist Node 1 - Explain Code

# ---------------------------------------------------

def explain_code_plain_english(state: CodeState) -> dict:
    response = llm.invoke(
        f"You are an expert programming tutor. "
        f"A user code snippet: '{state.code}'."
        f"Explain the following code in simple English for a beginner."
       )
    return {
        "messages": [f"[explanation] {response.content}"]
    }
 

# ---------------------------------------------------
# Specialist Node 2 - Identify Code Risks
# ---------------------------------------------------
def identify_code_risks(state: CodeState) -> dict:
    response = llm.invoke(
   f"""Analyze the following {state.code} code.
    Identify:
    1. Possible bugs
    2. Edge cases
    3. Performance concerns
    4. Unclear or confusing parts
    """)
    return {
        "risks": response.content,
        "messages": [f"[risks] verified"]
    }

# ==========================================================
# Specialist Node 3 - Add Inline Comments
# ==========================================================
def add_code_comments(state: CodeState) -> dict:
    response = llm.invoke(
   f"""Explain the following {state.code} code in simple terms for beginners.
       Add clear and beginner-friendly inline comments to the code below.
       Return only the commented code.
    
    """)
    return {
        "comments": response.content,
        "messages": [f"[comments] added"]
    }


# ==========================================================
# Decision Node
# ==========================================================
def decision_node(state: CodeState) -> dict:
    response = llm.invoke(
    f"""Based on the code review analysis {state.code}, analyze if the following code:
    If the code is short and straightforward, return:simple
    If the code is complex, contains loops, conditions, classes,
    or appears to need review, return:deep
    Return only one word: simple or deep
    """)
    decision_content = response.content
    if isinstance(decision_content, list):
        decision_content = " ".join(str(item) for item in decision_content)
    elif isinstance(decision_content, dict):
        decision_content = " ".join(str(value) for value in decision_content.values())

    decision = str(decision_content).strip().lower()

    if "deep" in decision:
        return {"review_type": "deep"}

    return {"review_type": "simple"}

# ==========================================================
# Router Function
# ==========================================================
def router(state: CodeState) -> str:
    return state.review_type or "simple"


# ==========================================================
# Final Node - Simple Code Explanation
# ==========================================================
def simple_code_explanation(state: CodeState) -> dict:
    response = llm.invoke(
        f"You are an expert programming tutor. "
        f"Explain the following code in simple English for a beginner: '{state.code}'"
    )
    final_output = f"Simple Code Explanation:\n{response.content}"
    return {"final_output": final_output}


# ==========================================================
# Final Node - Deep Code Review
# ==========================================================
def deep_code_review(state: CodeState) -> dict:
    # Get explanation
    explanation_response = llm.invoke(
        f"You are an expert programming tutor. "
        f"Explain the following code in detail: '{state.code}'"
    )

    # Get risks
    risks_response = llm.invoke(
        f"""Analyze the following code for potential issues:
        Code: {state.code}
        Identify:
        1. Possible bugs
        2. Edge cases
        3. Performance concerns
        4. Security issues
        5. Best practices violations
        """
    )

    # Get comments
    comments_response = llm.invoke(
        f"""Add clear and comprehensive inline comments to the following code:
        Code: {state.code}
        Return only the commented code with detailed explanations.
        """
    )

    final_output = f"""Deep Code Review:

Code Explanation:
{explanation_response.content}

Identified Risks and Issues:
{risks_response.content}

Commented Code:
{comments_response.content}
"""

    return {"final_output": final_output}  
   

# ==========================================================
# Build LangGraph
# ==========================================================
graph = StateGraph(CodeState)
graph.add_node("decision", decision_node)
graph.add_node("simple_code_explanation", simple_code_explanation)
graph.add_node("deep_code_review", deep_code_review)

# Entry point decision
graph.add_edge(START, "decision")

graph.add_conditional_edges(
    "decision",
    router,
    {
        "simple": "simple_code_explanation",
        "deep": "deep_code_review"
    }
)

graph.add_edge("simple_code_explanation", END)
graph.add_edge("deep_code_review", END)

app = graph.compile()

def run_code_review(code_snippet: str) -> str:
    print("=" * 55)
    print("  Code Explainer Agent")
    print(f"  You said: \"{code_snippet}\"")
    print("=" * 55)


    result = app.invoke({
        "code": code_snippet,
        "messages": [],
    })


    print("\n" + "=" * 55)
    print("  FINAL SUGGESTION")
    print("=" * 55)
    print(f"\n{result['final_output']}")

    print("\n" + "-" * 55)
    print("  MESSAGE LOG")
    print("-" * 55)
    for msg in result["messages"]:
        print(f"  {msg}")

    return result['final_output']


if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("  CODE EXPLAINER AGENT")
    print("=" * 55)
    print("\n  Tell me the code you'd like me to explain and I'll break it down for you.")
    print("  Type 'quit' to exit.\n")

    while True:
        code_snippet = input("  Enter the code you'd like me to explain: > ").strip()

        if code_snippet.lower() in ("quit", "exit", "q"):
            print("\n  Take care of yourself. Goodbye!\n")
            break

        if not code_snippet:
            continue

        run_code_review(code_snippet)
        print("\n")



