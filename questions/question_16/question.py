description = """
Agentic AI systems are designed to take actions, not just generate text.
A core capability of an AI agent is the ability to call external tools
to accomplish tasks.

In this exercise, you will build a simple agent that:
- Uses an LLM to decide when to call a tool
- Invokes a Calculator tool to perform arithmetic operations
- Returns the final response after tool usage

A helper function `get_llm()` is already available in the environment.
By default, it is configured to use an open-source model.

### Your Task
- Use `get_llm()` to obtain the LLM
- Define a `calculator` tool function that can evaluate arithmetic expressions
- Create an agent that uses this tool to answer math questions
- Return the final agent response as a string

### Example
Query: "What is 3 + 5?"
Expected: The agent should use the calculator tool and return a response containing "8"

### Function Signature
```python
def simple_tool_agent(query: str) -> str
```
"""

hint = """
Define a calculator tool using the `@tool` decorator and bind it to the LLM to handle arithmetic queries.
"""

initial_sample_code = """from langchain_core.prompts import PromptTemplate

def simple_tool_agent(query: str):
    '''
    An agent that uses a calculator tool to answer questions.
    
    Args:
        query (str): The user query (e.g., 'What is 3 + 5?').
        
    Returns:
        str: The final answer from the agent.
    '''
    llm = get_llm()
    # Your code here
    pass

# ==========================================================
# Uncomment below to see the output
# ==========================================================
#if __name__ == "__main__":
#    print(simple_tool_agent("What is 3 + 5?"))"""
