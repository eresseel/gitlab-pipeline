# common-gitlab-pipeline

## Prepare developer environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

## Run test
```bash
python tests/main.py
flake8 ./tests/
pytest -v tests/
pytest -v tests/test_gitflow.py
pytest -v tests/test_git_settings.py::test_git_email
```
