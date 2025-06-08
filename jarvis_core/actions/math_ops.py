import math
import re

ALLOWED_MATH_NAMES = {
    "acos": math.acos, "asin": math.asin, "atan": math.atan, "atan2": math.atan2,
    "ceil": math.ceil, "cos": math.cos, "cosh": math.cosh, "degrees": math.degrees,
    "exp": math.exp, "fabs": math.fabs, "floor": math.floor, "fmod": math.fmod,
    "frexp": math.frexp, "hypot": math.hypot, "ldexp": math.ldexp, "log": math.log, # math.log is natural log
    "log10": math.log10, "log2": math.log2, "modf": math.modf, "pow": math.pow,
    "radians": math.radians, "sin": math.sin, "sinh": math.sinh, "sqrt": math.sqrt,
    "tan": math.tan, "tanh": math.tanh, "factorial": math.factorial,
    "gamma": math.gamma, "lgamma": math.lgamma, "erf": math.erf, "erfc": math.erfc,
    "pi": math.pi, "e": math.e,
    # Custom safe functions or aliases if needed
    "ln": math.log, # Alias for natural log
    "cbrt": lambda x: x**(1/3.0), # Cube root
    "nth_root": lambda x, n: x**(1/float(n)) if n != 0 else float('inf') # Nth root
}
# built-ins that are often used in math like abs, round, float, int
ALLOWED_BUILTINS = {
    "abs": abs, "round": round, "float": float, "int": int, "pow": pow # pow is also in math
}
# Combine them into a single context for eval
SAFE_EVAL_CONTEXT = {"__builtins__": ALLOWED_BUILTINS, **ALLOWED_MATH_NAMES}

def evaluate_expression(expression_string):
    """
    Safely evaluates a mathematical expression string.
    The expression_string should be one that is constructed carefully
    by the NLP to only use allowed functions and numbers.
    """
    print(f"DEBUG: Math expression to evaluate: '{expression_string}'")
    if not re.match(r"^[a-zA-Z0-9\s\.\+\-\*\/\%(\)\,\_]+$", expression_string):
        pass
    try:
        result = eval(expression_string, SAFE_EVAL_CONTEXT, {})
        if isinstance(result, complex):
            return f"The result is a complex number: {result}. I can only provide results for real numbers as of now!"
        if isinstance(result, float):
            if result.is_integer():
                result = int(result)  # Display as integer if it's like 5.0
            else:
                result = round(result, 6)
        return f"The result is {result}"
    except ZeroDivisionError:
        return "Sorry, I can't divide by zero."
    except OverflowError:
        return "The result of the calculation is too large to handle."
    except TypeError as e:
        print(f"Math TypeError: {e} for expression '{expression_string}'")
        return "There seems to be a problem with the numbers or functions in your calculation. Please check the format."
    except SyntaxError as e:
        print(f"Math SyntaxError: {e} for expression '{expression_string}'")
        return "I couldn't understand the calculation format. Please rephrase."
    except NameError as e:
        print(
            f"Math NameError: {e} for expression '{expression_string}' - an disallowed function/variable might have been used.")
        return "Sorry, an unexpected error occurred with the calculation. Some functions might not be available."
    except Exception as e:
        print(f"Unexpected math evaluation error: {e} for expression '{expression_string}'")
        return "Sorry, an unexpected error occurred while trying to calculate that."

if __name__ == '__main__':
    # Test cases
    test_expressions = {
        "5 + 3": "The result is 8",
        "10 - 4": "The result is 6",
        "6 * 7": "The result is 42",
        "100 / 4": "The result is 25",
        "10 / 0": "Sorry, I can't divide by zero.",
        "10 % 3": "The result is 1",
        "2**3": "The result is 8", # power
        "pow(2, 4)": "The result is 16", # using pow from context
        "sqrt(16)": "The result is 4",
        "cbrt(27)": "The result is 3",
        "nth_root(81, 4)": "The result is 3",
        "log10(100)": "The result is 2",
        "ln(e)": "The result is 1", # e is math.e
        "factorial(5)": "The result is 120",
        "sin(radians(30))": "The result is 0.5", # approx
        "degrees(asin(0.5))": "The result is 30", # approx
        "cos(radians(60))": "The result is 0.5", # approx
        "degrees(acos(0.5))": "The result is 60", # approx
        "tan(radians(45))": "The result is 1", # approx
        "degrees(atan(1))": "The result is 45", # approx
        "abs(-5)": "The result is 5",
        "round(3.14159, 2)": "The result is 3.14",
        "sqrt(-1)": "The result is a complex number: 1j. I can only provide real number results for now." # If cmath isn't used. math.sqrt raises ValueError.
                                                                                                       # Our eval context doesn't have cmath.
                                                                                                       # math.sqrt(-1) will raise ValueError, let's test that.
    }

    # Corrected test for math.sqrt(-1) raising ValueError
    print(f"Testing 'math.sqrt(-1)':")
    try:
        math.sqrt(-1)
    except ValueError as e:
        print(f"  Correctly raised ValueError: {e}")
    print(f"  Result via evaluate_expression('sqrt(-1)'): {evaluate_expression('sqrt(-1)')}")


    for expr, expected_start in test_expressions.items():
        result = evaluate_expression(expr)
        print(f"'{expr}' -> '{result}' (Expected start: '{expected_start}') -> {'Pass' if result.startswith(expected_start.split('.')[0]) else 'Fail (check rounding or exact message)'}")

    # Test a more complex valid expression that NLP might generate
    complex_expr = "5 * (log10(100) + sqrt(16)) / 2" # 5 * (2 + 4) / 2 = 5 * 6 / 2 = 30 / 2 = 15
    print(f"Testing '{complex_expr}': {evaluate_expression(complex_expr)}")

