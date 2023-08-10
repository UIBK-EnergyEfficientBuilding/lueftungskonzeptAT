
# Setup dev venv

```
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

# setup dev env with conda

```
conda install -c conda-forge flask
conda install -c conda-forge numpy
conda install -c conda-forge scipy
conda install -c conda-forge flask-restx
```

# Run dev system
```
FLASK_DEBUG=1 python -m flask --app lueftungstool/__init__.py run
```
or use vscode run and debug, open http://127.0.0.1:5000/api/doc with your browser for the rest api documentation.

# Build an run container image

```
docker build -t lueftungstool:latest .
docker run --rm -p 8000:8000 lueftungstool:latest
```
open http://127.0.0.1:8000/api/doc with your browser for the rest api documentation.
