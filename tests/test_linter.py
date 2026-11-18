from app.tools.sandbox_tool import run_linter_tool

def test_linter_handles_valid_code():

    valid_code = (
        "def calculate_total(price, quantity):\n"
        "    total = price * quantity\n"
        "    return total\n"
    )

    result = run_linter_tool.invoke({
        "code_string": valid_code
    })

    assert "Flake8 exit code: 0" in result
    assert "Black exit code: 0" in result

    print("SUCCESS: Valid Python code passed both checks!")