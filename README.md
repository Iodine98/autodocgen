# autodocgen

## Documentation

1. Install as dependency in Poetry by adding the following line to `pyproject.toml`

```toml
autodocgen = { git = "" }
```

1. Create a `.env` file that contains your `OPENAI_KEY`
```env
OPENAI_KEY=<your OpenAI key>
```
2. Call the ASTAnalyzer and ensure that the `model_name` is correct. 

The default values are below
```python
ASTAnalyzer(
    self,
    model_name="text-davinci-003",
    model_kwargs: dict = None,
    method_visitor: MethodVisitor = MethodVisitor(),
    prepend_prompt: str = "Write Pydoc for the function below and only return the PyDoc:\n\n",
    **kwargs)
```

