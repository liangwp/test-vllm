These steps are NOT required for running the project.  
These were the commands run during project initialization in order to get the
uv environment set up properly.

1. `cd` into the `ui` directory.
1. Set up venv environment with python 3.12.
    ```
    uv init --python 3.12
    ```
1. Install dependencies.
    ```
    uv add dash gunicorn
    ```
1. Directory now contains `.python-version`, `pyproject.toml` and `uv.lock`.
   These should be copied into the docker image in the `Dockerfile`.
   