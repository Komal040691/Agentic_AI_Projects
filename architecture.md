# Code Explainer Agent -- Architecture

## How It Works

```
User enters code snippet
        |
        v
  [decision_node] -- analyzes code complexity (simple vs deep)
        |
        +---> [explain_code_plain_english]   \
        |                                    |
        +---> [identify_code_risks]          +--> run in PARALLEL (for deep review)
        |                                    |
        +---> [add_code_comments]           /
        |
        v
  [router] -- routes based on decision_node result
        |
        +-- SIMPLE --> [simple_code_explanation] --> basic explanation
        |
        +-- DEEP --> [deep_code_review] --> comprehensive analysis
        |
        v
  [END] -- final output displayed to user
```

## State Flow

1. **Initial State**: User provides code snippet
2. **Decision Phase**: LLM assesses if code needs simple or deep review
3. **Parallel Analysis** (if deep): Three nodes run simultaneously:
   - Explain code in plain English
   - Identify potential bugs/risks
   - Add inline comments
4. **Final Review**: Combines all analyses into comprehensive report
5. **Output**: Displays either simple explanation or deep review

## Key Components

- **CodeState**: Pydantic model holding all data
- **Decision Node**: Routes to simple or deep review path
- **Parallel Nodes**: Analyze different aspects simultaneously
- **Conditional Edges**: Dynamic routing based on complexity
- **Annotated Messages**: Track execution flow with operator.add
        |
        +-- HIGH ----------> [deep_practice]  --> 10-15 min session
        |
        v
  Final output printed to user
```

## Interactive Mode

```
$ python mental_wellness_graph.py

  =======================================================
    MENTAL WELLNESS PRACTICE SUGGESTER
  =======================================================

    Tell me how you're feeling and I'll suggest a
    personalized wellness practice just for you.
    Type 'quit' to exit.

    How are you feeling? > I feel anxious and can't focus
    ...graph runs...
    YOUR PERSONALIZED PRACTICE
    ...

    How are you feeling? > quit
    Take care of yourself. Goodbye!
```

## Graph Structure (Detailed)

```
                    +-------+
                    | START |
                    +---+---+
                        |
                        v
            +-----------+-----------+
            |   understand_mood     |
            |                       |
            | Acknowledges feeling  |
            | Severity: MILD /      |
            |   MODERATE / HIGH     |
            +-----------+-----------+
                        |
           PARALLEL FAN-OUT (3 edges from one node)
          /             |              \
         v              v               v
+--------+---+ +-------+------+ +------+--------+
|  suggest   | |   suggest    | |   suggest     |
|  breathing | | mindfulness  | |   movement    |
|            | |              | |               |
| e.g. 4-7-8| | e.g. 5-4-3  | | e.g. child's  |
| breathing  | | -2-1 ground | | pose, neck    |
|            | |              | | rolls         |
+--------+---+ +-------+------+ +------+--------+
         \              |               /
          FAN-IN (all 3 must finish)
                        |
                        v
          +-------------+-------------+
          |     pick_best_practice    |
          |                           |
          | Reads all 3 suggestions   |
          | Returns JSON:             |
          | {needs_deep_session,      |
          |  reason}                  |
          +-------------+-------------+
                        |
               CONDITIONAL EDGE
              route_after_decision()
                   /         \
      false       /           \      true
    (MILD/MOD)   /             \   (HIGH)
                v               v
    +-----------+--+   +-------+---------+
    | quick_       |   | deep_           |
    | practice     |   | practice        |
    |              |   |                 |
    | Under 5 min  |   | 10-15 min       |
    | Best single  |   | 3 phases:       |
    | technique,   |   |  1. Settle      |
    | numbered     |   |  2. Ground      |
    | steps        |   |  3. Release     |
    +-----------+--+   +-------+---------+
                \               /
                 \             /
                  v           v
                  +----+----+
                  |   END   |
                  +---------+
```

## State Fields

```
WellnessState
|
|-- user_feeling              <-- set by user input
|-- breathing_suggestion      <-- written by suggest_breathing
|-- mindfulness_suggestion    <-- written by suggest_mindfulness
|-- movement_suggestion       <-- written by suggest_movement
|-- needs_deep_session        <-- written by pick_best_practice
|-- practice_reason           <-- written by pick_best_practice
|-- final_suggestion          <-- written by quick_practice OR deep_practice
|-- messages                  <-- appended by ALL nodes (operator.add)
```

## LangGraph Concepts Used

| Concept | Where in Code | What It Does |
|---------|--------------|--------------|
| State (Pydantic) | `WellnessState` class | Typed data that flows through every node |
| Nodes | `understand_mood`, `suggest_*`, etc. | Functions that read state, do one job, return updates |
| Parallel Execution | 3 edges from `understand_mood` | LangGraph runs all 3 suggest nodes simultaneously |
| Fan-In | 3 edges into `pick_best_practice` | Waits for all parallel nodes to finish |
| Conditional Edge | `route_after_decision()` | Routes to quick or deep based on `needs_deep_session` |
| Graph Compilation | `graph.compile()` | Turns graph definition into runnable `app` |
| Invocation | `app.invoke({...})` | Runs the graph with initial state |
| Message Accumulation | `Annotated[list, operator.add]` | Parallel nodes append without overwriting |

## Tech Stack

| Component | Purpose |
|-----------|---------|
| LangGraph | Graph orchestration -- nodes, edges, parallel, conditional |
| LangChain | OpenAI LLM wrapper (ChatOpenAI) |
| OpenAI | gpt-4o-mini -- cheap, fast, good enough for demo |
| Pydantic | State validation and type safety |
| python-dotenv | Load OPENAI_API_KEY from .env |

## File Structure

```
LangGraph_AgentFramework/
|-- mental_wellness_graph.py    Main code (graph + interactive loop)
|-- architecture.md             This file
|-- architecture.drawio         Visual diagram (open with draw.io extension)
|-- requirements.txt            4 dependencies
|-- .env                        OPENAI_API_KEY (not committed)
|-- .env.example                Template for .env
|-- .gitignore                  Ignores .env, venv, __pycache__
```
