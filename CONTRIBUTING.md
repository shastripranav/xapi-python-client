# Contributing to xapi-python-client

Thanks for your interest in contributing. This is an MIT-licensed Python xAPI client and contributions are welcome — particularly bug reports against real LRS implementations, additional verb definitions, and improvements to the typed statement models.

## How to Contribute

1. Fork the repository on GitHub.
2. Create a topic branch off `main`: `git checkout -b feat/statement-signing`.
3. Make your changes, add tests, and run the test suite locally.
4. Open a pull request against `main` describing the change and any LRS interop implications.

## Development setup

```bash
pip install -e ".[dev]"
```

The async client is the primary interface; the sync wrapper sits on top of it. If you're adding a new feature, please add it to the async client first.

## Code style

The project uses [ruff](https://docs.astral.sh/ruff/) for linting:

```bash
ruff check src/ tests/
```

## Testing

```bash
pytest -v
```

If you're adding support for a new verb or extension, please add a corresponding test in `tests/`. If you're fixing a bug specific to a particular LRS implementation, please include a fixture or mocked response that reproduces the original failure.

## Questions

Open an issue with the `question` label.
