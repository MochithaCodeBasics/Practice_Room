description = """
An e-commerce company tracks customer interactions across three channels: Email, Social Media, 
and Direct Website. Historical data shows:

**Channel Interaction Probabilities:**
- 40% of customers interact via Email
- 35% via Social Media  
- 25% via Direct Website

**Conversion Rates (given interaction with channel):**
- Email: 12%
- Social Media: 8%
- Direct Website: 15%

**Note:** Customers can interact with multiple channels independently.

### Task
Implement a function:
```python
calculate_marketing_probabilities() -> dict
```

### Requirements
Calculate the following:

1. **Overall Conversion Probability**: 
   The probability that a randomly selected customer converts (through any channel).
   Use the law of total probability.

2. **Bayes' Theorem Results**: 
   If a customer converted, what's the probability they came from each channel?
   Calculate for Email, Social Media, and Website.

3. **At Least Two Channels Probability**: 
   The probability that a customer interacts with at least 2 channels 
   (given channel interactions are independent).

### Return
A dictionary with the following structure:
```python
{
    'overall_conversion_prob': float,  # rounded to 2 decimals
    'bayes_results': {
        'Email': float,    # P(Email | Converted), rounded to 2 decimals
        'Social': float,   # P(Social | Converted), rounded to 2 decimals
        'Website': float   # P(Website | Converted), rounded to 2 decimals
    },
    'at_least_two_channels_prob': float  # rounded to 2 decimals
}
```
"""

hint = """
- P(Convert) = P(Email)×P(Convert|Email) + P(Social)×P(Convert|Social) + P(Website)×P(Convert|Website)
- P(Email|Convert) = P(Email)×P(Convert|Email) / P(Convert)
- P(at least 2 channels) = P(E∩S) + P(E∩W) + P(S∩W) − 2×P(E∩S∩W), since channel interactions are independent
"""

initial_sample_code = """def calculate_marketing_probabilities():
    \"\"\"
    Calculate marketing channel probabilities using Bayes' theorem.

    Returns:
        dict with keys:
            - overall_conversion_prob: float (total probability of conversion)
            - bayes_results: dict with Email, Social, Website posterior probabilities
            - at_least_two_channels_prob: float (probability of 2+ channel interactions)
    \"\"\"
    # Your code here
    pass

# ==========================================================
# Uncomment below to see the output
# ==========================================================
# if __name__ == "__main__":
#     result = calculate_marketing_probabilities()
#     print(result)
"""


def get_description():
    return description

def get_hint():
    return hint

def get_initial_sample_code():
    return initial_sample_code
