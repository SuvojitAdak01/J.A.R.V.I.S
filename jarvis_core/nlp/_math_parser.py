import re

def parse_math_query(text):
    replacements = {
        # Powers & Roots (most specific first)
        r"the (\d+)(?:st|nd|rd|th) root of": r"nth_root(",  # e.g., the 4th root of
        r"cube root of": "cbrt(",
        r"square root of": "sqrt(",
        # Logarithms
        r"natural log of": "ln(",
        r"log of": "log10(",  # Default log to base 10
        # Trigonometry (with degrees handling)
        r"(?:sine|sin) of": "sin(radians(",
        r"(?:cosine|cos) of": "cos(radians(",
        r"(?:tangent|tan) of": "tan(radians(",
        r"(?:arcsine|inverse sine|asin) of": "degrees(asin(",
        r"(?:arccosine|inverse cosine|acos) of": "degrees(acos(",
        r"(?:arctangent|inverse tangent|atan) of": "degrees(atan(",
        # Other functions
        r"factorial of": "factorial(",
        # Basic arithmetic (words to symbols)
        r" plus ": " + ",
        r" minus ": " - ",
        r" times ": " * ",
        r" x ": " * ",
        r" multiplied by ": " * ",
        r" divided by ": " / ",
        r" modulus ": " % ",
        r" modulo ": " % ",
        # Powers (words to symbols)
        r" to the power of ": "**",
        r" squared": "**2",
        r" cubed": "**3",
        # Constants
        r"\bpi\b": "pi",
        r"\be\b": "e",
    }

    processed_text = text.lower()

    processed_text = re.sub(r'([\d\.]+) factorial', r'factorial(\1)', processed_text)

    # Handling phrases like "log base 2 of 8"
    log_base_match = re.search(r"log base ([\d\.]+) of ([\d\.]+)", processed_text)
    if log_base_match:
        base, number = log_base_match.groups()
        processed_text = processed_text.replace(log_base_match.group(0), f"log({number}, {base})")

    # Handling phrases like "the 4th root of 81"
    nth_root_match = re.search(r"the ([\d\.]+)(?:st|nd|rd|th) root of ([\d\.]+)", processed_text)
    if nth_root_match:
        root, number = nth_root_match.groups()
        processed_text = processed_text.replace(nth_root_match.group(0), f"nth_root({number}, {root})")

    for pattern, replacement in replacements.items():
        processed_text = re.sub(pattern, replacement, processed_text)

    processed_text = processed_text.replace(" degrees", ")")

    open_paren = processed_text.count('(')
    close_paren = processed_text.count(')')
    if open_paren > close_paren:
        processed_text += ')' * (open_paren - close_paren)

    # Clean up: remove words that are not part of the expression
    # Words like "what", "is", "calculate", "compute", "tell", "me", "the"
    cleanup_words = ["what's", "what is", "whats", "calculate", "compute", "the result of", "tell me", "of",
                     "how much is"]
    for word in cleanup_words:
        processed_text = processed_text.replace(word, "")

    final_expression = re.sub(r"[^a-z0-9\s\.\+\-\*\/\%\(\)\,]", "", processed_text).strip()

    return final_expression