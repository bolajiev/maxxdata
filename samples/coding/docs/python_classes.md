# Classes in Python

Classes bundle data and behavior. Define with `class Name:` and call with `Name()`.

```python
class Dog:
    def __init__(self, name):
        self.name = name

    def bark(self):
        return f"{self.name} says woof!"
```

## Inheritance

Subclass with `class Puppy(Dog):` and use `super()` to call parent methods.

## Special methods

`__str__` and `__repr__` control string display. `__len__` supports `len(obj)` when implemented.

## Dataclasses

For data-heavy objects, `@dataclass` reduces boilerplate (Python 3.7+).
