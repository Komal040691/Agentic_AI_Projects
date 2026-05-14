# Code Explainer Agent -- Learn LangGraph Step by Step

A beginner-friendly project to learn the LangGraph framework by building an AI-powered code explanation and review system.

---

## Understanding LangGraph Through the Code Review Analogy

Before diving into code, let us understand how LangGraph works using the **Code Review** analogy.

Imagine a software development team where a developer submits code, and it goes through different reviewers: one checks for bugs, another adds documentation, and a lead reviewer decides if it needs deep review or just basic explanation.

LangGraph works the same way -- but instead of code files, we pass **data (state)** through **nodes (functions)** connected by **edges (arrows)**.

```
    THE CODE REVIEW ANALOGY FOR LANGGRAPH
    =====================================

    Think of LangGraph as a code review pipeline:

    +----------------------------------------------------------+
    |                                                          |
    |   CODE SUBMISSION = STATE (Pydantic Model)              |
    |   The code travels through the review process.           |
    |   Each reviewer adds their feedback.                     |
    |                                                          |
    |   +-------------+  +-------------+  +-------------+     |
    |   | Reviewer 1  |  | Reviewer 2  |  | Reviewer 3  |     |
    |   | (Explains)  |  | (Finds      |  | (Comments)  |     |
    |   |             |  |  Risks)     |  |             |     |
    |   +-------------+  +-------------+  +-------------+     |
    |                                                          |
    +----------------------------------------------------------+

    NODES = Review Stations (each does one job)
    EDGES = Workflow connections between stations
    PARALLEL NODES = Multiple reviewers working simultaneously
    CONDITIONAL EDGE = Lead reviewer deciding: "Simple or Deep review?"

    How data flows:

    [Code Submission]                       <-- START node
          |
          v
    +-----------+
    | Initial   |                            <-- Node 1: Decision
    | Assessment|                            (Is this simple or complex code?)
    +-----------+
          |
     _____|_____________________
    |            |              |
    v            v              v
  +-------+   +-------+   +-------+
  | Simple|   | Deep  |   | Deep  |         3 POSSIBLE PATHS
  |Review |   |Review |   |Review |         (Conditional routing)
  +-------+   +-------+   +-------+
    |            |              |
    |____________|______________|
                 |
                 v                               (Fan-In: All paths lead to END)
         +--------------+
         | Final Report |                    <-- END node
         +--------------+                    Combines all review results


    KEY LANGGRAPH CONCEPTS:
    -----------------------
    1. STATE    = The code submission itself (holds all data)
    2. NODE     = A review station (a function that does one thing)
    3. EDGE     = A workflow connection (connects one node to the next)
    4. CONDITIONAL EDGE = A decision point routing to different paths
    5. PARALLEL = Multiple stations could work at the same time
```

---

## Our Project: AI Code Explainer Agent

Now we apply the same pattern to a real use case. A developer enters code, the system analyzes its complexity, then either provides a simple explanation or performs a comprehensive deep review with risks and comments.

```
    CODE EXPLAINER AGENT -- GRAPH ARCHITECTURE
    ===========================================

              +-----------------+
              |     START       |
              +-------+---------+
                      |
              +-------v---------+
              |  decision_node  |     Developer enters code snippet.
              +-------+---------+     System assesses complexity.
                      |
          ____________|_______________
         |             |               |
         v             v               v
  +-----------+  +-----------+  +----------------+
  | explain_  |  | identify_ |  | add_code_      |    3 PARALLEL NODES (for deep review)
  | code_     |  | code_     |  | comments       |    (Fan-Out)
  | plain     |  | risks     |  |                |
  +-----------+  +-----------+  +----------------+    Each node analyzes different aspects.
         |             |               |              No conflicts.
         |_____________|_______________|              All write to state.
                       |
              +--------v---------+
              | deep_code_       |                    FAN-IN:
              | review           |                    Combines all analyses.
              +--------+---------+                    Generates final report.
                       |
                       v
                     [END]


    STATE FIELDS (Pydantic Model):
    ================================
    code           --> Input: the code snippet to analyze
    review_type    --> Filled by: decision_node ("simple" or "deep")
    explanation    --> Filled by: explain_code_plain_english (for deep review)
    risk           --> Filled by: identify_code_risks (for deep review)
    comments       --> Filled by: add_code_comments (for deep review)
    final_output   --> Filled by: simple_code_explanation OR deep_code_review
    messages       --> Accumulated by ALL nodes (uses operator.add)
```

---

## How LangGraph State Works

```
    HOW STATE FLOWS THROUGH THE GRAPH
    ===================================

    Initial State (before graph runs):
    +-----------------------------------+
    | code: "def hello(): print('Hi')"  |
    | review_type: ""                   |
    | explanation: ""                   |
    | risk: ""                          |
    | comments: ""                      |
    | final_output: ""                  |
    | messages: []                      |
    +-----------------------------------+
                    |
                    v
        [decision_node runs]
                    |
                    v
    After decision_node:
    +-----------------------------------+
    | review_type: "simple"             |  <-- decision made
    | messages: ["[decision] assessed"] |  <-- appended
    +-----------------------------------+
                    |
                    v
    After simple_code_explanation:
    +-----------------------------------+
    | final_output: "Simple Code..."    |  <-- final output
    +-----------------------------------+

    OR (if complex code):

    After decision_node:
    +-----------------------------------+
    | review_type: "deep"               |  <-- decision made
    +-----------------------------------+
                    |
        ____________|____________
       |            |            |
       v            v            v
    [3 parallel nodes run, each fills fields]
                    |
                    v
    After parallel nodes:
    +-----------------------------------+
    | explanation: "This function..."   |  <-- filled by explain_code_plain_english
    | risk: "No major bugs found..."    |  <-- filled by identify_code_risks
    | comments: "def hello():"          |  <-- filled by add_code_comments
    | messages: [..., explanation,      |  <-- all appended (operator.add)
    |            risk, comment msgs]    |
    +-----------------------------------+
                    |
                    v
    After deep_code_review:
    +-----------------------------------+
    | final_output: "Deep Code Review.."|  <-- combined report
    +-----------------------------------+
```

---

## Setup and Run

### Prerequisites
- Python 3.10 or higher
- An OpenAI API key

### Steps

```bash
# 1. Clone the repository
git clone <repository-url>
cd langgraph_framework_For_Code_Explainer_agent

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up your API key
# Create a .env file and add your OpenAI API key:
# OPENAI_API_KEY=your-api-key-here

# 5. Run the code explainer
python Code_Agent_graph.py
```

### Expected Output

```
============================================================
  CODE EXPLAINER AGENT
  You said: "def factorial(n): return n * factorial(n-1) if n > 1 else 1"
============================================================

--- [decision] Code complexity assessed ---

--- Making final assessment ---
Decision: DEEP -- Code contains recursion, needs detailed review

--- [Parallel] Explaining code in plain English ---
--- [Parallel] Identifying code risks ---
--- [Parallel] Adding inline comments ---

--- Generating deep code review ---

============================================================
  FINAL SUGGESTION
============================================================

Deep Code Review:

Code Explanation:
This is a recursive function that calculates the factorial of a number...

Identified Risks and Issues:
1. Stack overflow for large n values
2. No input validation
...

Commented Code:
def factorial(n):
    # Base case: factorial of 1 or 0 is 1
    if n <= 1:
        return 1
    # Recursive case: n! = n * (n-1)!
    else:
        return n * factorial(n-1)
```

---

## Code Walkthrough

| Step | What Happens | File Location |
|------|-------------|---------------|
| 1 | Define `CodeState` with Pydantic | `Code_Agent_graph.py` line 25 |
| 2 | Initialize OpenAI LLM | `Code_Agent_graph.py` line 32 |
| 3 | Define decision node | `Code_Agent_graph.py` line 95 |
| 4 | Define parallel analysis nodes | `Code_Agent_graph.py` lines 40-90 |
| 5 | Define final review nodes | `Code_Agent_graph.py` lines 125-180 |
| 6 | Build graph (add nodes + edges) | `Code_Agent_graph.py` lines 185-200 |
| 7 | Compile and run | `Code_Agent_graph.py` lines 205-280 |

---

## Key Takeaways for Beginners

1. **State is just a data class** -- Define what data your graph needs using Pydantic fields with defaults.

2. **Nodes are functions** -- Each node is a Python function that takes state and returns a dict of updates.

3. **Edges connect nodes** -- Use `add_edge()` for direct connections, `add_conditional_edges()` for routing logic.

4. **Parallel processing** -- LangGraph can run multiple nodes simultaneously when they don't depend on each other.

5. **Annotated lists with operators** -- Use `Annotated[list[str], operator.add]` to accumulate messages from multiple nodes.

6. **Conditional routing** -- Router functions return strings that determine which edge to follow.

7. **State is immutable** -- Each node receives the current state and returns updates, LangGraph merges them automatically.

8. **Messages track execution** -- Use a messages field to log what each node did for debugging.

---

## Architecture Diagram

```
Code Explainer Agent Architecture
==================================

[User Input: Code Snippet]
        |
        v
+-------------------+     +-------------------+
| decision_node     | --> | Assess Complexity |
| (Simple/Deep?)    |     | (LLM Analysis)    |
+-------------------+     +-------------------+
        |
        +-------------------+
        |                   |
    "simple"            "deep"
        |                   |
        v                   v
+-------------------+     +-------------------+
| simple_code_      |     | Parallel Analysis |
| explanation       |     | Nodes:            |
+-------------------+     | - explain_code    |
        |             |   | - identify_risks  |
        |             |   | - add_comments    |
        |             |   +-------------------+
        v             |         |
+-------------------+     |         v
| Final Output      |     | +-------------------+
| (Simple Review)   |     | | deep_code_review |
+-------------------+     | | (Combine Results) |
                          | +-------------------+
                          |         |
                          |         v
                          +-------------------+
                            | Final Output      |
                            | (Deep Review)     |
                            +-------------------+
```