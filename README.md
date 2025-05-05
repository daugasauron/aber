### Description

Create bindings for zig -> python. 

When installing from pip, uses ziglang python package that contains zig to compile the source locally.

## Demo

```
(.venv) aber # python
>>> from aber import hello
>>> hello.zig_mult(3, 4)
12
```

```
export fn zig_mult(a: i32, b: i32) i32 {
    return a * b;
}
```

### install

```
pip install aber
```

### local dev

```
cd zig && python -m ziglang build && cd ..
```

```
python generate_bindings.py
```

#### Debug build step
```
pip install build
python -m build -s -w
```

#### Publish

```
poetry build -f sdist
poetry publish
```
