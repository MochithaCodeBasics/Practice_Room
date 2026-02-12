# questions/_env.py
import pandas as pd
import random
import string
import re
import os
from collections import Counter
from langchain_groq import ChatGroq

def get_llm(provider=None, **kwargs):
    """
    Returns an LLM instance based on the specified provider or the DEFAULT_LLM_PROVIDER env var.
    Supported providers: 'groq', 'openai', 'anthropic'
    """
    provider = (provider or os.getenv("DEFAULT_LLM_PROVIDER", "groq")).lower().strip()
    
    # Common defaults
    temperature = kwargs.get("temperature", 0.0)

    try:
        if provider == "groq":
            from langchain_groq import ChatGroq
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                print("WARNING: GROQ_API_KEY not found in environment.")
                return None
            return ChatGroq(
                model=kwargs.get("model", "llama-3.3-70b-versatile"),
                temperature=temperature,
                groq_api_key=api_key
            )

        elif provider == "openai":
            from langchain_openai import ChatOpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("WARNING: OPENAI_API_KEY not found in environment.")
                return None
            return ChatOpenAI(
                model=kwargs.get("model", "gpt-4o-mini"),
                temperature=temperature,
                openai_api_key=api_key
            )

        elif provider == "anthropic":
            from langchain_anthropic import ChatAnthropic
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                print("WARNING: ANTHROPIC_API_KEY not found in environment.")
                return None
            return ChatAnthropic(
                model=kwargs.get("model", "claude-3-5-sonnet-latest"),
                temperature=temperature,
                anthropic_api_key=api_key
            )
            
    except ImportError as e:
        print(f"ERROR: Provider '{provider}' dependencies not installed. {e}")
        return None
        
    print(f"WARNING: Unsupported LLM provider: {provider}")
    return None

__all__ = ["pd", "random", "string", "re", "Counter", "get_llm"]
