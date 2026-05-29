# Python Functions

A function is a reusable block of code that runs when called. You define a function with the `def` keyword.

```python
def greet(name):
    return f"Hello, {name}!"
```

## Parameters and arguments

Parameters are names in the function definition; arguments are values passed when calling.

## Return values

Use `return` to send a value back to the caller. If there is no `return`, the function returns `None`.

## Scope

Variables created inside a function are local unless declared `global` (avoid globals in production code).

## Best practices

- Keep functions small and focused on one task.
- Use descriptive names like `calculate_total` instead of `f1`.
- Add type hints for clarity: `def add(a: int, b: int) -> int`.
