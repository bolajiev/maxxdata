# Modules and Packages

A **module** is a `.py` file. Import with `import module` or `from module import name`.

## Packages

A **package** is a folder with `__init__.py`. Use dotted imports: `from pkg.sub import util`.

## Standard layout

```text
myproject/
  mypackage/
    __init__.py
    core.py
```

## `if __name__ == "__main__"`

Runs code only when the file is executed directly, not when imported.

## Virtual environments

Isolate dependencies per project with `python -m venv .venv` then activate before `pip install`.
