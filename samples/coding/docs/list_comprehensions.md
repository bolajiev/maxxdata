# List Comprehensions

A compact way to build lists: `[expr for item in iterable if condition]`.

```python
squares = [x * x for x in range(10)]
evens = [x for x in range(20) if x % 2 == 0]
```

## Dict and set comprehensions

- Dict: `{k: v for k, v in pairs}`
- Set: `{x for x in items}`

## When to avoid

Prefer a plain loop when logic is long or has side effects; readability beats brevity.
