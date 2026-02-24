description = """
In multi-agent systems, a routing agent decides which specialized agent
should handle a given user request.

In this exercise, you will build a simple routing agent that:
- Uses an LLM to classify the user query
- Routes the query to the correct handler
- Returns the handler's response

A helper function `get_llm()` is already available in the environment.
By default, it is configured to use an open-source model.

### Your Task
- Use `get_llm()` to obtain the LLM
- Classify the query into predefined categories
- Call the appropriate handler function
- Return the final response

### Function Signature
```python
def routing_agent(query: str) -> str
```
"""

hint = """
Define two simple handler functions and ask the LLM to choose between them.
"""

initial_sample_code = """from langchain_core.prompts import PromptTemplate
import re

def math_agent(query: str) -> str:
    # Safe extraction of math part: looks for digits and operators
    matches = re.findall(r"[0-9+\-*/().]+", query)
    if not matches:
        return "Math agent: No math found"
    
    # Simple evaluation (use safe logic in production)
    try:
        expression = matches[0]
        result = eval(expression)
        return f"Math Agent: {result}"
    except:
        return "Math Agent: Error"

def general_agent(query: str) -> str:
    # Simple general agent
    return f"General Agent: I can help with general queries."

def routing_agent(query: str):
    '''
    Routes a query to the appropriate agent.
    
    Args:
        query (str): The user input query.
        
    Returns:
        str: The response from the selected agent.
    '''
    llm = get_llm()
    # Your code here
    pass

# ==========================================================
# Uncomment below to see the output
# ==========================================================
#if __name__ == "__main__":
#    print(routing_agent("What is 10 + 5?"))
#    print(routing_agent("Who is the president?"))"""
