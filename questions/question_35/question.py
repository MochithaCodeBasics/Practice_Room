description = """
Retrieval-Augmented Generation (RAG) combines external knowledge with LLMs
to produce more accurate and grounded answers.

In this exercise, you will build a minimal RAG-style flow using LangChain.

A helper function `get_llm()` is already available in the environment.
By default, it is configured to use an open-source model.

### Your Task
- Use `get_llm()` to obtain the LLM
- Select relevant context from the provided documents
- Inject the context into the prompt
- Generate an answer based on the retrieved context

This is a simplified version of a real RAG pipeline.

### Function Signature
```python
def rag_answer(documents: list[str], question: str) -> str
```
"""

hint = """
First decide which document is relevant, then pass it as context to the LLM.
"""

initial_sample_code = """from langchain_core.prompts import PromptTemplate

def rag_answer(documents, question):
    '''
    Generates an answer using RAG (Retrieval-Augmented Generation).
    
    Args:
        documents (list[str]): A list of text documents for context.
        question (str): The user query to answer.
        
    Returns:
        str: The generated answer based on the context.
    '''
    llm = get_llm()
    # Your code here
    pass

# ==========================================================
# Uncomment below to see the output
# ==========================================================
#if __name__ == "__main__":
#    docs = ["RAG improves LLM accuracy by grounding responses", "Prompt engineering controls model output"]
#    query = "Why is RAG useful?"
#    print(rag_answer(docs, query))"""
