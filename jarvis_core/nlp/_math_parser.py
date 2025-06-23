import spacy

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")


def parse_math_query(text):
    """
    A more robust, token-based parser for math queries.
    """
    op_map = {
        "plus": "+", "add": "+",
        "minus": "-", "subtract": "-", "less": "-",
        "times": "*", "multiplied by": "*", "x": "*",
        "divided by": "/", "over": "/",
        "power": "**", "raised to": "**"
    }
    func_map = {
        "square root": "sqrt", "sqrt": "sqrt",
        "cube root": "cbrt",
        "log": "log10", "logarithm": "log10",
        "natural log": "ln", "ln": "ln",
        "sine": "sin", "sin": "sin",
        "cosine": "cos", "cos": "cos",
        "tangent": "tan", "tan": "tan",
        "arcsine": "asin", "inverse sine": "asin",
        "arccosine": "acos", "inverse cosine": "acos",
        "arctangent": "atan", "inverse tangent": "atan",
        "factorial": "factorial"
    }
    trig_funcs = {"sin", "cos", "tan"}
    inv_trig_funcs = {"asin", "acos", "atan"}

    doc = nlp(text.lower())
    parts = []
    i = 0
    while i < len(doc):
        token = doc[i]

        # To handle numbers
        if token.like_num:
            parts.append(token.text)
        # To handle operators
        elif token.text in op_map:
            parts.append(op_map[token.text])
        # To handle multi-word functions like "square root"
        elif i + 1 < len(doc) and f"{token.text} {doc[i + 1].text}" in func_map:
            func = func_map[f"{token.text} {doc[i + 1].text}"]
            parts.append(func + "(")
            i += 1  # Skip next token
        # To handle single-word functions
        elif token.text in func_map:
            func = func_map[token.text]
            parts.append(func + "(")

        i += 1

    # Simple logic to balance parentheses
    expression = " ".join(parts)
    open_paren = expression.count('(')
    close_paren = expression.count(')')
    if open_paren > close_paren:
        expression += ' )' * (open_paren - close_paren)

    # Special handling for trig degrees
    final_expr = []
    tokens = expression.split()
    skip_next = False
    for i, token in enumerate(tokens):
        if skip_next:
            skip_next = False
            continue

        # Checking if a trig function needs radians() wrapper
        func_name = token.replace('(', '')
        if func_name in trig_funcs and i + 1 < len(tokens):
            final_expr.append(f"{func_name}(radians({tokens[i + 1]}))")
            skip_next = True  # Skip the number token as we've consumed it
        # Checking if an inverse trig function needs degrees() wrapper
        elif func_name in inv_trig_funcs and i + 1 < len(tokens):
            final_expr.append(f"degrees({func_name}({tokens[i + 1]}))")
            skip_next = True
        else:
            final_expr.append(token)

    return " ".join(final_expr).replace(" )", ")")