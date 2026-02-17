# JVox JupyterLab Extension and AI Magics - Installation Guide

This guide assists you with the installation of all required components including ANTLR4, JupyterLab, [`jvox_ai_magics`](https://github.com/ProgrammingEduBVI/JupyterVox), and this extension (`jvox_jlab_ext`). Please follow each section carefully.

---

## 1. Prerequisites

- **Python:** >=3.7 recommended (v3.13.5 used for development)
- **Node.js:** v18.x or higher is recommended (for building JupyterLab extensions, v20.19.2 used for development)
- **pip** and **git** (should be available in your PATH)

---

## 2. Install Required Packages

Install [`pip` requirements](#required-python-packages) and system requirements for ANTLR4.

### Required Python Packages

```bash
pip install jupyterlab
```

### ANTLR4 (for Python)

Install ANTLR4 runtime for Python:

```bash
# install ANTLR4
pip install antlr4-tools
# download ANTLR4 Java pacakge
antlr4
# install Python run-time for ANTLR4
pip install antlr4-python3-runtime
```

Note that antlr4 v4.13.1 was used for development

---

## 3. Install `jvox_ai_magics`

[`jvox_ai_magics`](https://github.com/ProgrammingEduBVI/JupyterVox) is a package that provides JVox AI magic commands for Jupyter.

```bash
pip install -e jvox_ai_magics
```

Add the `jvox_ai_magics` to iPython extension list for autoloading

In iPython's configuration file (usually at `~/.ipython/profile_default/ipython_config.py`), add the following lines:

    ```python
    c.InteractiveShellApp.extensions = [
        'jvox_ai_magics'
    ]
    ```

Please see the README file in `jvox_ai_magics` for more information.

---

## 4. Install `jvox_jlab_ext` JupyterLab Extension

This extension enables screen reader and accessibility features in JupyterLab.

### A. Install the Python package (with/for development):

```bash
cd web_interface/jvox_jlab_ext
pip install -e .
```

### B. Install the JavaScript extension (with/for development):

```bash
# Required to identify the project for Yarn 3
touch yarn.lock
# Install package in development mode
pip install -e .
# Link your development version of the extension with JupyterLab
jupyter labextension develop . --overwrite
# Rebuild extension Typescript source after making changes
jlpm
jlpm run build
```

---

## 5. Verify the JVox Extension in JupyterLab

JupyterLab should automatically detect and enable the extension after install.

To manually verify:

```bash
jupyter labextension list
# Should show: jvox-jlab-ext enabled
jupyter server extension list
# Should show: jvox_jlab_ext imported
```
---

## 6. AI backend

### A. llama.cpp
This project was developed using the `llama-3.2-8B-instruct:FP8` model running with `llama.cpp`. By default, the llama.cpp server URL is set to `http://127.0.0.1:4590`. To specify a different URL for your `llama.cpp` server, set the following environment variable:

```bash
export LLAMA_CPP_URL=http://yourip:yourport
```

### B. Gemini
JupyterVox currently only supports Gemini API. Using Gemini requires modifying Python code at the moment. It also requires setting the Gemini API key,

```bash
export GEMINI_API_KEY=your_api
```
Support for other LLMs and GUI configuration will be added in the future.

---

## 7. Launch JupyterLab

JupyterVox requires a configuration file to specify logging parameters.
An example configuration file, `jvox_config.toml`, is provided in this repository. To allow JupyterVox to locate and use your configuration file, please set the following environment variable to the path of your `jvox_config.toml`:

```bash
export JVOX_CONFIG_FILE=path/to/jvox_config.toml
```

Start JupyterLab as usual:

```bash
jupyter lab
```

You should now see JVox features enabled.

---

## 7. Troubleshooting

- If you do not see JVox UI or features, restart JupyterLab and confirm the extension is enabled.
- For developer debugging, run `jupyter lab --dev-mode` and check browser console/logs.

---

## 8. Uninstallation

To remove the extension:

```bash
# Server extension must be manually disabled in develop mode
jupyter server extension disable jvox_jlab_ext
pip uninstall jvox_jlab_ext
```
In development mode, you will also need to remove the symlink created by `jupyter labextension develop`
command. To find its location, you can run `jupyter labextension list` to figure out where the `labextensions`
folder is located. Then you can remove the symlink named `jvox-jlab-ext` within that folder. Please find more information for uninstallation in the README file of jvox_jlab_ext.

To remove `jvox_ai_magics`:

```bash
pip uninstall jvox_ai_magics
```


---

For more details, issues, or to contribute, please visit the [JVox GitHub Repository](https://github.com/ProgrammingEduBVI/JupyterVox).