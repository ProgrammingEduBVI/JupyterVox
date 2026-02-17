# JVox AI Magics

This package provides an IPython extension that adds custom AI-powered cell magics for Python code generation. It is independent of JupyterLab or Notebook extensions and works wherever IPython magics are supported.

## Installation

Install this package in your Python environment:

```bash
pip install -e .
```

## Loading the Extension

To load the extension in a Jupyter Notebook or JupyterLab session, run the following in a cell:

```python
%load_ext jvox_ai_magics
```

## Usage

After loading, use the magic in a code cell:

```python
%%jvoxAI
# Your prompt or description here
```

The AI will generate Python code based on your prompt and automatically insert a new code cell with the generated code.

## Automatic Loading on Startup

To automatically load the extension in every session, add it to your IPython profile configuration:

1. Find your IPython profile location by running:
    ```bash
    ipython locate profile
    ```
2. The typical location is `~/.ipython/profile_default`.
3. In the profile directory, create or edit the file `ipython_config.py`.
4. Add the following lines:

    ```python
    c.InteractiveShellApp.extensions = [
        'jvox_ai_magics'
    ]
    ```

This will ensure `jvox_ai_magics` is loaded automatically for every IPython/Jupyter session.

## Notes

- This extension currently does not provide a JupyterLab or Jupyter Notebook custom UI. It adds magics for code generation only.

For further questions or integration help, please refer to [the main project README](https://github.com/ProgrammingEduBVI/JupyterVox).
