1. This is an IPython extension, independent from JupyterLab or Notebook. I don't know how to integrate this into JupyterLab.

2. Install this package with "pip3 instal -e ."

3. To manually load it in Jupyter Lab/Notebook, in a cell, put "%load_ext jvox_ai_magics"

4. To use it, run "%jvoxAI" in a cell

5. To install automatically
    1) find the location of IPython profile, with bash command "ipython locate profile"
    2) the location is usually ~/.ipython/profile_default
    3) the profile directory (e.g., /.ipython/profile_default), create a file "ipython_config.py"
    4) in the file, add
        c.InteractiveShellApp.extensions = [
            'jvox_ai_magics'
        ]
