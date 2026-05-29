# 📚 Python Module Notes

## 🔹 Module 01: Variables & Data Types
### Key Concepts:
- **Variable Rules**: 
  - Start with letter/underscore
  - No spaces/hyphens in names
  - Error examples: `1var`, `player name`
- **Data Types**:
  - `str` (strings), `int` (integers), `float`, `bool`, `None`
  - Type errors: `str + int` (use `int()`/`float()` for conversion)
- **Examples**:
  ```python
  total_runs = 12000
  batting_average = total_runs / (total_innings - not_outs)
  ```
- **Common Errors**:
  - Type mismatch in calculations
  - Incorrect input handling (e.g., `int("abc")`)

---

## 🔹 Module 02: Strings & Text
### Key Concepts:
- **Basic Operations**:
  - Concatenation: `str + str` only
  - `len()` for length
  - Indexing/slicing: `str[0:5]`, `str[-1]`
- **String Methods**:
  - `str.upper()`, `str.lower()`, `str.strip()`
  - `str.find()`, `str.replace()`, `str.startswith()`
- **Whitespace Handling**:
  - `.strip()` vs `.lstrip()`/.rstrip()
- **Formatting**:
  - F-strings: `f"{var:.2f}"`
  - Multiline strings with triple quotes
- **Examples**:
  ```python
  username = "Rocking Star YASH"
  print(f"First 8 chars: {username[:8]}")  # 'Rocking '
  ```

---

## 🔹 Module 03: Conditional Logic
### Key Concepts:
- ** ATM Simulation**:
  - Multi-condition checks (PIN, amount limits, multiples of 100)
  - Error handling for invalid inputs
- **IF/ELSE IF/OTHER**:
  - Chained conditions with clear priorities
  - Example:
    ```python
    if pin_correct:
        # proceed
    elif amount < 100:
        print("min withdraw is 100")
    else:
        # final else
    ```
- **Best Practices**:
  - Validate inputs early
  - Use descriptive error messages

---

## 🔹 Module 04: Loops & Iteration
### Key Concepts:
- **Range Function**:
  - `range(start, end, step)`
  - Negative step for reverse iteration
- **Loop Examples**:
  ```python
  for char in "Pritam":
      print(char)  # P r i t a m
  ```
  ```python
  for i in range(1, 10, 2):
      print(i)  # 1 3 5 7 9
  ```
- **String Reversal**:
  - Using `char + reverse` pattern or slicing `str[::-1]`

---

## 🔹 Module 05: Lists & Tuples
### Key Concepts:
- **List Operations**:
  - `append()` (single item), `extend()` (multiple items), `remove()`, `pop()`
  - Slicing: `list[:3]`, `list[-2:]`
- **Memory Insights**:
  - Use `sys.getsizeof()` to check object size:
    ```python
    sys.getsizeof(["burger", 10, True])  # 152 bytes
    ```
- **Common Errors**:
  - Mistaking `append()` for `extend()`
  - Trying to remove non-existent items

---

## 🔹 Cross-Module Takeaways
1. **Error Prevention**:
   - Validate inputs before processing
   - Use type conversion carefully
2. **String/Number Handling**:
   - F-strings for clean formatting
   - `isdigit()` checks for numeric strings
3. **Data Structures**:
   - Prefer lists for mutable collections
   - Use tuples for immutable data