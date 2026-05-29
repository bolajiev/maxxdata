# Error Handling in Python

Use `try` / `except` to handle errors without crashing the program.

```python
try:
    value = int(user_input)
except ValueError:
    print("Please enter a valid integer.")
```

## Common exception types

- `ValueError`: invalid value for a type conversion or operation
- `TypeError`: operation on wrong type
- `FileNotFoundError`: missing file path
- `KeyError`: missing dictionary key

## Else and finally

- `else` runs if no exception occurred in `try`
- `finally` always runs (cleanup: close files, release resources)

## Raising exceptions

Use `raise ValueError("message")` to signal errors to callers.

## Logging vs print

Prefer the `logging` module over `print` in applications so you can control levels and destinations.
