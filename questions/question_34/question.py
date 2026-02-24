description = """
Vector databases are commonly used for semantic search, but in early prototypes
or low-scale systems, LLMs themselves can assist in selecting relevant content.

In this exercise, you will use an LLM to choose the most relevant document
from a list based on a user query.

A helper function `get_llm()` is already available in the environment.
By default, it is configured to use an open-source model.

### Your Task
- Use `get_llm()` to obtain the LLM
- Provide the list of documents and the query to the LLM
- Ask the LLM to select the single most relevant document
- Return the selected document as a string

### Function Signature
```python
def semantic_search(documents: list[str], query: str) -> str
```
"""

hint = """
Provide all documents clearly in the prompt and ask the LLM to choose one.
"""

initial_sample_code = """from langchain_core.prompts import PromptTemplate

def semantic_search(documents, query):
    '''
    Selects the most relevant document for a query using an LLM.
    
    Args:
        documents (list[str]): A list of text documents.
        query (str): The search query.
        
    Returns:
        str: The selected document.
    '''
    llm = get_llm()
    # Your code here
    pass

# ==========================================================
# Uncomment below to see the output
# ==========================================================
#if __name__ == "__main__":
#    docs = ["AI is powerful", "Dogs are animals", "GenAI uses large language models"]
#    query = "language models"
#    print(semantic_search(docs, query))"""
