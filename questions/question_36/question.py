description = """
Some AI agents are designed to reason through a problem step-by-step
before producing a final answer. This is commonly used in planning,
multi-step decision making, and problem solving.

In this exercise, you will build a reasoning-style agent that:
- Uses an LLM to think through a problem
- Produces a final concise answer
- Separates reasoning from final output in the prompt design

A helper function `get_llm()` is already available in the environment.
By default, it is configured to use an open-source model.

### Your Task
- Use `get_llm()` to obtain the LLM
- Create a prompt that encourages step-by-step reasoning
- Extract and return only the final answer as a string

### Function Signature
```python
def reasoning_agent(question: str) -> str
```
"""

hint = """
Guide the model to think step-by-step, but return only the final answer.
"""

initial_sample_code = """from langchain_core.prompts import PromptTemplate

def reasoning_agent(question: str):
    '''
    An agent that reasons step-by-step before answering.
    
    Args:
        question (str): The user's question.
        
    Returns:
        str: The final answer.
    '''
    llm = get_llm()
    # Your code here
    pass

# ==========================================================
# Uncomment below to see the output
# ==========================================================
#if __name__ == "__main__":
#    print(reasoning_agent("If I have 3 apples and eat one, how many do I have?"))"""
