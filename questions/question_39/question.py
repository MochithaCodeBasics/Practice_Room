description = """
In production, AI agents must be evaluated for both task success
and safety. Guardrails help ensure that agents do not produce
unsafe or irrelevant outputs.

In this exercise, you will build a simple evaluated agent that:
- Uses an LLM to answer a question
- Applies a safety or relevance check
- Returns either the answer or a fallback message

A helper function `get_llm()` is already available in the environment.
By default, it is configured to use an open-source model.

### Your Task
- Use `get_llm()` to obtain the LLM
- Generate an answer to the user query
- Apply a simple validation or guardrail check
- Return the final safe response

### Function Signature
```python
def evaluated_agent(query: str) -> str
```
"""

hint = """
Check the LLM response before returning it. If it fails validation, return a fallback message.
"""

initial_sample_code = """from langchain_core.prompts import PromptTemplate

def evaluated_agent(query: str):
    '''
    An agent that validates its output for safety.
    
    Args:
        query (str): The user input query.
        
    Returns:
        str: The safe response.
    '''
    llm = get_llm()
    # Your code here
    pass

# ==========================================================
# Uncomment below to see the output
# ==========================================================
#if __name__ == "__main__":
#    print(evaluated_agent("What is the capital of France?"))
#    print(evaluated_agent("How do I hack a bank?"))"""
