description = """
LLMs can produce varied outputs unless they are guided carefully.
In production systems, prompt control is used to ensure consistent
and deterministic responses.

In this exercise, you will build a simple GenAI-based summarizer that:
- Uses an LLM via `get_llm()`
- Produces a concise, single-sentence summary
- Relies on prompt instructions rather than post-processing logic

A helper function `get_llm()` is already available in the environment.
By default, it is configured to use an open-source model.

### Your Task
- Use `get_llm()` to obtain the LLM
- Create a prompt that instructs the LLM to return exactly one sentence
- Run the prompt using LangChain
- Return the generated summary as a string

### Function Signature
```python
def generate_summary(text: str) -> str
```
"""

hint = """
Be very explicit in your prompt about output length and format.
"""

initial_sample_code = """from langchain_core.prompts import PromptTemplate

def generate_summary(text: str):
    '''
    Generates a single-sentence summary of the input text.
    
    Args:
        text (str): The input text to summarize.
        
    Returns:
        str: A single-sentence summary.
    '''
    llm = get_llm()
    # Your code here
    pass

# ==========================================================
# Uncomment below to see the output
# ==========================================================
#if __name__ == "__main__":
#    sample_text = "Revenue increased significantly. Expenses also rose. Profits declined."
#    print(generate_summary(sample_text))"""
