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
calculate_marketing_probabilities(channel_probs, conversion_rates) -> dict
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

hint = """- P(Convert) = sum of P(Channel) x P(Convert|Channel) for all channels
- P(Channel|Convert) = P(Channel) x P(Convert|Channel) / P(Convert)
- P(at least 2 channels) = P(E∩S) + P(E∩W) + P(S∩W) - 2×P(E∩S∩W), since channel interactions are independent"""

initial_sample_code = """from itertools import combinations
def calculate_marketing_probabilities(channel_probs, conversion_rates):
    '''
    Calculate marketing channel probabilities using Bayes' theorem.

    Parameters:
        channel_probs: dict mapping channel names to interaction probabilities
            e.g., {'Email': 0.40, 'Social': 0.35, 'Website': 0.25}
        conversion_rates: dict mapping channel names to conversion rates
            e.g., {'Email': 0.12, 'Social': 0.08, 'Website': 0.15}

    Returns:
        dict with keys:
            - overall_conversion_prob: float (total probability of conversion)
            - bayes_results: dict with posterior probabilities per channel
            - at_least_two_channels_prob: float (probability of 2+ channel interactions)
    '''
    # Your code here
    pass

# ==========================================================
# Uncomment below to see the output
# ==========================================================
# if __name__ == "__main__":
#     channel_probs = {'Email': 0.40, 'Social': 0.35, 'Website': 0.25}
#     conversion_rates = {'Email': 0.12, 'Social': 0.08, 'Website': 0.15}
#     result = calculate_marketing_probabilities(channel_probs, conversion_rates)
#     print(result)"""
