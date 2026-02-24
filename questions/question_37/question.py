description = """
Many AI agents break a user request into multiple steps before executing
a final task. This is known as task planning in agentic systems.

In this exercise, you will build a small task-planning agent that:
- Uses an LLM to generate a step-by-step plan
- Executes each step sequentially
- Returns the final combined result

A helper function `get_llm()` is already available in the environment.
By default, it is configured to use an open-source model.

### Your Task
- Use `get_llm()` to obtain the LLM
- Generate a simple step plan from the user request
- Simulate execution of each step
- Return the final result as a string

### Function Signature
```python
def task_planning_agent(request: str) -> str
```
"""

hint = """
Ask the model to output a numbered plan, then process each step in order.
Return the final plan as a numbered or bulleted list (one step per line).
Avoid debug text in the returned string.
"""

initial_sample_code = """from langchain_core.prompts import PromptTemplate

def task_planning_agent(request: str):
    '''
    An agent that creates and executes a multi-step plan.
    
    Args:
        request (str): The user's request (e.g., 'Plan a 3-step workout').
        
    Returns:
        str: The result of the executed plan.
    '''
    llm = get_llm()
    # Your code here
    pass

# ==========================================================
# Uncomment below to see the output
# ==========================================================
#if __name__ == "__main__":
#    print(task_planning_agent("Plan a 3-step morning routine"))"""
