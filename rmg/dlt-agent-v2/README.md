# RMG DLT Analysis Agent

<!-- Optional: Add badges here for build status, code coverage, PyPI version, etc. -->
<!--
[![Build Status](https://travis-ci.org/your_username/rmg-dlt-agent.svg?branch=main)](https://travis-ci.org/your_username/rmg-dlt-agent)
[![Coverage Status](https://coveralls.io/repos/github/your_username/rmg-dlt-agent/badge.svg?branch=main)](https://coveralls.io/github/your_username/rmg-dlt-agent?branch=main)
[![PyPI version](https://badge.fury.io/py/rmg-dlt-agent.svg)](https://badge.fury.io/py/rmg-dlt-agent)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
-->

An Agentic AI solution to automate the analysis of non-compliant shipping cases for Royal Mail Group (RMG), replacing the manual Decision Logging Tool (DLT) process.

## Description

This project provides an Agent-based AI solution designed to automate the analysis of non-compliant shipping cases, such as items with incorrect weight or dimensions, for Royal Mail Group (RMG). The current manual process, reliant on the Decision Logging Tool (DLT), is often slow and inefficient given the high daily volume of cases.

The RMG DLT Analysis Agent aims to demonstrate how an AI solution can:
*   Understand specific business queries related to non-compliant cases.
*   Fetch and process relevant data.
*   Perform analysis on this data.
*   Surface actionable insights, enabling faster and more confident decision-making, particularly in identifying cases eligible for surcharges.

## Features

*   **Query Understanding:** Interprets natural language queries from users.
*   **Data Retrieval:** Fetches relevant case data for analysis.
*   **Data Analysis:** Applies logic to identify non-compliant cases based on various criteria (e.g., weight, dimensions, open duration).
*   **Actionable Insights:** Presents results, often in tabular form, to support decision-making (e.g., identifying surchargeable cases).
*   **Multi-step Agentic Architecture:** Utilizes a sophisticated agent design for robust processing.

## Installation

This project uses [Poetry](https://python-poetry.org/) for dependency management and packaging.

### Prerequisites

*   Python 3.13+
*   Poetry (for development and installation from source)
*   pip (for installing from PyPI if available)

### Using pip (if published to PyPI)

If the package is available on PyPI, you can install it via pip:

```bash
pip install rmg-dlt-agent
```

### Using Poetry (Recommended)

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your_username/rmg-dlt-agent.git
    cd rmg-dlt-agent
    ```

2.  **Install dependencies:**
    ```bash
    poetry install
    ```
    This will create a virtual environment and install all necessary dependencies as specified in `pyproject.toml` and `poetry.lock`.

    For a development installation (including dev dependencies):
    ```bash
    poetry install --with dev
    ```

## Usage

The agent is designed to process queries related to non-compliant shipping cases. Below is a conceptual example of how it might be used:

```python
from rmg_dlt_agent.analyzer import DLTAnalyzerAgent # Or your main agent class

# Initialize the agent
agent = DLTAnalyzerAgent()

# Example queries
query1 = "Which cases can be surcharged with high confidence?"
query2 = "Show high-priority cases that are overweight and unopened for more than 10 days."
query3 = "Identify items non-compliant due to weight that have been open for less than 7 days."

# Process a query
results = agent.process_query(query1)

# Display results (e.g., as a pandas DataFrame or formatted table)
if hasattr(results, 'to_markdown'): # Example for pandas DataFrame
    print(results.to_markdown(index=False))
else:
    print(results)

```

For more detailed examples, refer to the documentation or the `examples/` directory within this repository.

## Contributing

Contributions are welcome! Please read our `CONTRIBUTING.md` (if available) for details on our code of conduct, and the process for submitting pull requests to us.

## License

This project is licensed under the [NAME OF LICENSE] - see the `LICENSE.md` file for details. (e.g., MIT License)

## Acknowledgements (Optional)

*   Mention any individuals, teams, or projects that inspired or significantly contributed to this work.

## Contact (Optional)

*   Your Name / Team Name – @your_contact_method – your_email@example.com
*   Project Link: https://github.com/your_username/rmg-dlt-agent