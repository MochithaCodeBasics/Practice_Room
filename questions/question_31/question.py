description = """
In real-world Generative AI systems, LLMs are often asked to return information
in a fixed, structured format so that it can be processed programmatically.

In this exercise, you will build a small GenAI utility that:
- Uses an LLM to extract structured information from unstructured text
- Forces the LLM to follow a strict output format using prompt engineering
- Parses the LLM response into a Python dictionary

A helper function `get_llm()` is already available in the environment.
By default, it is configured to use an open-source model.

### Your Task
- Use `get_llm()` to obtain the LLM
- Create a PromptTemplate that enforces the following output format:

Name: <name>
Amount: <amount>
Category: <category>

- Run the prompt using LangChain
- Parse the output and return a dictionary with:
  - `name` (str)
  - `amount` (int)
  - `category` (str)

### Function Signature
```python
def extract_financial_info(text: str) -> dict
```
"""

hint = """
Think of this as two steps:
1. Prompt the LLM to return structured text
2. Convert that structured text into Python data
"""

initial_sample_code = """from langchain_core.prompts import PromptTemplate

def extract_financial_info(text: str):
    '''
    Extracts financial information from text using an LLM.
    
    Args:
        text (str): The input text containing financial details.
        
    Returns:
        dict: A dictionary with keys 'name', 'amount', and 'category'.
    '''
    llm = get_llm()
    # Your code here
    pass

# ==========================================================
# Uncomment below to see the output
# ==========================================================
#if __name__ == "__main__":
#    sample_text = "John paid $4500 for office supplies"
#    print(extract_financial_info(sample_text))"""
