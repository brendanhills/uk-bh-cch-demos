# Python Project

This is a new Python project.

## Setup

## Setup

1.  Initialize the project (if not already done):
    ```bash
    uv sync
    ```

## Running

Run the main script:
```bash
uv run src/main.py
```

## Testing

Run tests:
```bash
uv run pytest
```

## BigQuery Logging

The `bq_logging.py` script requires additional configuration.
1.  Open `bq_logging.py` and update the `PROJECT`, `BQ_URI`, and `MODEL` variables.
2.  Run the script:
    ```bash
    uv run bq_logging.py
    ```

