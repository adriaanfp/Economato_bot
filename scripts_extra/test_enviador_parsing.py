import re

def parsear(item_texto):
    match = re.search(r"^(.*?)\s*\((.*?)\)$", item_texto)
    if match:
        return match.group(1).strip()
    else:
        return item_texto

print("--- Testing Regex Logic ---")
test_cases = [
    "Tomate Pera (5kg)",
    "Tomates (3 cajas)",
    "Leche Semidesnatada Puleva",
    "Huevos XL (2 docenas)",
    "Solomillo de Ternera"
]

for t in test_cases:
    res = parsear(t)
    print(f"'{t}' -> '{res}'")
