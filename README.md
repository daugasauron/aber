### install

```
pip install aber
python -m aber.hello
```

### local dev

```
cd zig && python -m ziglang build && cd ..
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
