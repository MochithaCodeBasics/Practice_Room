description = """
Agentic AI systems are designed to take actions, not just generate text.
A core capability of an AI agent is the ability to call external tools
to accomplish tasks.

In this exercise, you will build a simple agent that:
- Uses an LLM to decide when to call a tool
- Invokes a **Calculator** tool to perform arithmetic operations
- Returns the final response after tool usage

A helper function `get_llm()` is already available in the environment.
By default, it is configured to use an open-source model.
If you want to use a Groq-hosted open-source model, add your `GROQ_API_KEY`
in a `.env` file. You may also modify `get_llm()` in `questions/_env.py`
to use any other LLM and update `requirements.txt` accordingly.

### Your Task
- Use `get_llm()` to obtain the LLM
- Define a `calculator` tool function that can evaluate arithmetic expressions
- Create an agent that uses this tool to answer math questions
- Return the final agent response as a string

### Example
Query: "What is 3 + 5?"
Expected: The agent should use the calculator tool and return a response containing "8"

### Function Signature
simple_tool_agent(query: str) -> str
"""

hint = """
Define a calculator tool using the `@tool` decorator and bind it to the LLM to handle arithmetic queries.
"""

initial_sample_code = """
from langchain_core.prompts import PromptTemplate

def simple_tool_agent(query: str):
    llm = get_llm()
    # Write your code here
"""

def get_description():
    return description

def get_hint():
    return hint

def get_initial_sample_code():
    return initial_sample_code