### Description

Create bindings for zig -> python. 

When installing from pip, uses ziglang python package that contains zig to compile the source locally.

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
