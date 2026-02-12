description = """
In real-world Generative AI systems, LLMs are often asked to return information
in a fixed, structured format so that it can be processed programmatically.

In this exercise, you will build a small GenAI utility that:
- Uses an LLM to extract structured information from unstructured text
- Forces the LLM to follow a strict output format using prompt engineering
- Parses the LLM response into a Python dictionary

A helper function `get_llm()` is already available in the environment.
Configure your API key in the environment settings to use a specific provider.

### Your Task
- Use `get_llm()` to obtain the LLM
- Create a PromptTemplate that enforces the following output format:

Name: <name>  
Amount: <amount>  
Category: <category>

- Run the prompt using LangChain
- Parse the output and return a dictionary with:
  - name (str)
  - amount (int)
  - category (str)

### Function Signature
extract_financial_info(text: str) -> dict
"""

hint = """
Think of this as two steps:
1. Prompt the LLM to return structured text
2. Convert that structured text into Python data
"""

initial_sample_code = """
from langchain_core.prompts import PromptTemplate

# get_llm() is already available in the environment

def extract_financial_info(text: str):
    llm = get_llm()
    # Write your code here
    
# To see the output, you can use:
# print(extract_financial_info("John paid 4500 for office supplies"))
"""


def get_description():
    return description

def get_hint():
    return hint

def get_initial_sample_code():
    return initial_sample_code