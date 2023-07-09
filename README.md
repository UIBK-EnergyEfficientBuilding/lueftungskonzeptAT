
# Setup dev venv

```
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

# Run dev system
```
cd lueftungstool
FLASK_DEBUG=1 python -m flask run
```
or use vscode run and debug, open http://127.0.0.1:5000/api/doc with your browser for the rest api documentation.
