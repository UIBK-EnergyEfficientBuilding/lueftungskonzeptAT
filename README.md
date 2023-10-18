
# Setup dev venv

```
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

# setup dev env with conda

```
conda install -c conda-forge flask >=2, <3
conda install -c conda-forge numpy
conda install -c conda-forge scipy
conda install -c conda-forge flask-restx
```

# Run dev system
```
FLASK_DEBUG=1 python -m flask --app lueftungstool/__init__.py run
```
or use vscode run and debug, open http://127.0.0.1:5000/api/doc with your browser for the rest api documentation.

# Run tests

```
python -m unittest discover -v -s ./tests -p "test_*.py"
```
or use vscode run the tests.

# Build an run container image

amd64 build
```
docker buildx build --output=type=docker -t lueftungstool:latest --platform=linux/amd64 .
docker run --rm -p 8000:8000 lueftungstool:latest
```

arm64 build
```
docker buildx build --output=type=docker -t lueftungstool:latest --platform=linux/arm64/v8 .
DOCKER_DEFAULT_PLATFORM=linux/arm64/v8 docker run --rm -p 8000:8000 lueftungstool:latest
```

open http://127.0.0.1:8000/api/doc with your browser for the rest api documentation.
