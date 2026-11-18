
from textwrap import dedent

from app.tools.sandbox_tool import run_linter_tool


# Test 1: Properly formatted Python code
good_code = dedent("""
    def add_numbers(a, b):
        return a + b
""").strip() + "\n"


# Test 2: Poorly formatted Python code
bad_code = dedent("""
    def add_numbers(a,b):
     x= a+b
     return x
""").strip() + "\n"


print("\n========== TEST 1: GOOD CODE ==========")

result = run_linter_tool.invoke({
    "code_string": good_code
})

print(result)


print("\n========== TEST 2: BAD CODE ==========")

result = run_linter_tool.invoke({
    "code_string": bad_code
})

print(result)

# Test 3: Invalid Python syntax

syntax_error_code = """
def calculate_total(price, quantity)
    return price * quantity
"""

print("\n========== TEST 3: SYNTAX ERROR ==========")

result = run_linter_tool.invoke({
    "code_string": syntax_error_code
})

print(result)