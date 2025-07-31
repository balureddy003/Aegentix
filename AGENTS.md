This repository is a Python package that also contains a Gatsby-based frontend.

## Testing and Linting

Use **ruff** for formatting and linting and **pytest** for running the tests. The
configured tasks in `pyproject.toml` show the expected commands:

```bash
ruff format
ruff check
pytest -n 0 --cov=autogenstudio --cov-report=term-missing
```

You must run these commands before every commit that modifies repository files.

## Frontend

The `frontend/` folder contains a Gatsby UI. See `frontend/README.md` for
instructions. Use `yarn start` for local development and `yarn build` to build
production assets.
