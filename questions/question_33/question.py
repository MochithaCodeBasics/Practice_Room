description = """
Before sending user input to an LLM, GenAI systems often normalize or refine
the input to make it clearer and more consistent.

In this exercise, you will simulate this preprocessing step using LangChain.

A helper function `get_llm()` is already available in the environment.
By default, it is configured to use an open-source model.

### Your Task
- Use `get_llm()` to obtain the LLM
- Create a PromptTemplate that asks the LLM to rephrase a question clearly
- Run the prompt using LangChain
- Return the refined question as a string

### Function Signature
```python
def refine_question(question: str) -> str
```
"""

hint = """
Focus on clarity and simplicity when rephrasing.
"""

initial_sample_code = """from langchain_core.prompts import PromptTemplate

def refine_question(question: str):
    '''
    Refines a user question for better clarity using an LLM.
    
    Args:
        question (str): The original user question.
        
    Returns:
        str: The refined version of the question.
    '''
    llm = get_llm()
    # Your code here
    pass

# ==========================================================
# Uncomment below to see the output
# ==========================================================
#if __name__ == "__main__":
#    sample_question = "Explain RAG"
#    print(refine_question(sample_question))"""
