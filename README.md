# autodocgen

## Installing from PyPI

> Note: this package has not been published to PyPI yet. Once it is
> published (see [#4](https://github.com/Iodine98/autodocgen/issues/4)),
> it will become installable via:

```sh
pip install autodocgen
```

## Documentation

### Installation

1. Install as dependency in Poetry by adding the following line to `pyproject.toml`

```toml
autodocgen = { git = "https://github.com/Iodine98/autodocgen.git" }
```

1. Create a `.env` file that contains your `OPENAI_KEY`
```env
OPENAI_KEY=<your OpenAI key>
```

### Usage

`autodocgen` also installs a command-line script of the same name that can be run
directly from a terminal, without having to call the library from Python:

```shell
autodocgen <path> [-i] [-s SUFFIX] [--disable_tqdm]
```

Arguments:

- `path` (required): path to a single Python file or to a directory. When a directory
  is given, every `.py` file in it (and its subdirectories) is processed, except for
  `__init__.py` files.
- `-i`, `--overwrite`, `--inplace`: overwrite the original file(s) in place with the
  generated docstrings injected. When omitted, a new file is written instead and the
  original file is left untouched.
- `-s SUFFIX`, `--suffix SUFFIX`: the suffix appended to the stem of the output file
  name when *not* overwriting in place, e.g. `my_module.py` becomes `my_module_doc.py`
  by default. This option is ignored when `-i`/`--overwrite` is used, since the file
  is overwritten instead of written to a new path.
- `--disable_tqdm`: disable the progress bar shown while processing a directory.

Examples:

```shell
# Write documented output to my_module_doc.py, leaving my_module.py untouched
autodocgen my_module.py

# Overwrite my_module.py in place with the generated docstrings
autodocgen my_module.py -i

# Process every Python file in ./src, writing "<name>_annotated.py" siblings
autodocgen ./src -s _annotated

# Process a directory in place without showing a progress bar
autodocgen ./src -i --disable_tqdm
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

