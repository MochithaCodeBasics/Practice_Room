description = """
A retail company stores daily transaction data in a text file. Each line in the file
represents a single transaction containing the product name and the sale amount.

The finance team wants a summary report that shows the total sales amount per product.

You are given a text file named `sales.txt` containing transaction records.
Each line in the file follows the format:

    <product_name>,<amount>

Your task is to read the file and generate a sales summary using a dictionary.

### Requirements
- Define a function named `generate_sales_summary(file_path)`
- Open and read the file at `file_path`
- Use a dictionary where:
  - key   -> product name (string)
  - value -> total sales amount (float)
- Accumulate sales amounts for products that appear multiple times
- Return the final result as a dictionary
- Round each total to **2 decimal places**

### Example

If a file contains:
Apple,10
Banana,5.5
Apple,2.25

Output:
{"Apple": 12.25, "Banana": 5.5}
"""

hint = """
Focus on reading the file line by line and splitting each line by a comma.
Use a dictionary to accumulate totals per product.
Remember to convert amounts to float and round totals at the end.
"""

inital_sample_code = """
# Write your solution here

# Create a function named:
# generate_sales_summary(file_path)

# It should return a dictionary:
# { product_name: total_sales_amount }
"""

def get_description():
    return description

def get_hint():
    return hint

def get_inital_sample_code():
    return inital_sample_code
