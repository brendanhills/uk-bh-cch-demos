---
name: colab
description: >-
  Create, edit, and execute Colab (.ipynb) notebooks. Covers creating notebooks,
  listing cells, reading/updating cell content, adding new cells, deleting
  cells, and executing notebooks on Colab runtimes. Supports creating Colab URLs
  for visualization, starting local and Borg runtime servers for execution, and
  managing iterative execution sessions with persistent context.
---

# Colab Skill

Create and edit Colab Notebook (`.ipynb`) files without manual JSON
manipulation. Execute Python code and Colab Notebook (`.ipynb`) files on Colab
runtimes.

## When to Use

-   Create, edit, or retrieve information from Colab Notebook (`.ipynb`) files.
-   Executing standalone Python code or notebooks to visualize data, train
    models, or run scripts.
-   Iterative code execution that requires persistent context (state/variables)
    across steps.
-   Creating Colab URLs for notebooks so the user can review results.

## Notebook Formats

Colab supports two main file formats:

1.  **.ipynb**: The standard Jupyter Notebook format (JSON). It preserves
    outputs and is fully self-contained.
2.  **_nb.py**: Pure Python files with cell delimiters (`# %%`). They are much
    easier to handle in merge conflicts and work better with standard Python
    tools (linting, type checking).

It is recommended to use `_nb.py` files for iteration and storage where keeping
the outputs of the cells is not necessary. If saving and sharing outputs is an
essential part of the task, `.ipynb` is preferred.

## CLI Usage (recommended)

> [!IMPORTANT] **This skill targets the CLI (`$COLAB` / `colab_tool_cli`).**
> Direct or legacy Colab MCP tool calls (e.g., `execute`, `get_colab_link`
> prefixed with `colab/`) are out of scope and may cause schema mismatches.

Prefer using the pre-built binary (available on all gLinux machines):

```bash
COLAB=/google/bin/releases/gemini-agents-colab/colab_tool_cli
```

Alternatively, install via apt (the `colab_tool_cli` binary will be available
directly on PATH):

```bash
sudo glinux-add-repo -b gemini-agents-colab stable
sudo apt update && sudo apt install -y gemini-agents-colab
```

Use `--version` to check the build date. To verify the exact build CL: `binfs ls
/google/bin/releases/gemini-agents-colab`.

If you modify the CLI source code, build from source:

```bash
blaze build //learning/gemini/agents/clis/colab:colab_tool_cli
COLAB=blaze-bin/learning/gemini/agents/clis/colab/colab_tool_cli
```

## CLI Commands

<!-- mdformat off(preserve table) -->
| Command    | Subcommand         | Description                                                    | Supported Flags |
|------------|--------------------|----------------------------------------------------------------|-----------------|
| `notebook` | `create`           | Creation of a new .ipynb notebook.                             | `filepath`      |
|            | `list_cells`       | Listing of cells in an .ipynb notebook.                        | `filepath`      |
|            | `get`              | Retrieval of content of a specific cell in an .ipynb notebook. | `filepath`, `cell_index` |
|            | `update`           | Update of content of a specific cell in an .ipynb notebook.    | `filepath`, `cell_index`, `content` |
|            | `add`              | Addition of a new cell to an .ipynb notebook.                  | `filepath`, `cell_type`, `content`, `position` |
|            | `delete`           | Deletion of a cell from an .ipynb notebook.                    | `filepath`, `cell_index` |
|            | `get_colab_link`   | Retrieval of a Colab link from notebook JSON or filepath.      | `notebook_json`, `filepath`, `connect_local`, `session_id` |
| `runtime`  | `fetch`            | Fetching of execute service runtimes.                          |                 |
|            | `fetch_borg_types` | Fetching of supported Borg runtime types that can be started with `start_borg` subcommand.  |                 |
|            | `start_borg`       | Starts a new Colab runtime on Borg.                            | `runtime_type`, `replace_existing`  |
|            | `watch_borg`       | Polls a Borg runtime status until ready and emits a trigger when the creation is complete.  |`server_address` |
| `execute`  |                    | Execution of code and notebooks in Colab.                      | `server_address`, `code`, `notebook_json`, `filepath`, `session_id`, `cell_ids`, `timeout_sec`, `output_format`, `inplace`, `template_params` |
| `session`  | `open`             | Opening of an execute session.                                 | `server_address`, `kernel_name` |
|            | `close`            | Closing of an execute session.                                 | `server_address`, `session_id` |
|            | `get`              | Check active status of a session.                              | `server_address`, `session_id` |
|            | `interrupt`        | Interrupt an ongoing cell execution in a session.              | `server_address`, `session_id` |
| `kernelspec`| `create`          | Creates a new kernelspec by building a colab_binary.           | `server_address`, `notebook_id`, `additional_dep_targets`, `colab_binary_target`, `source_uri` |
|             | `watch`           | Polls a kernel spec build operation and emits a trigger when the creation is complete.      | `server_address`, `operation_name` |
|             | `list`            | Lists all available kernelspecs. Includes the default and any created kernelspecs.          | `server_address` |
<!-- mdformat on -->

### Set up variables

```bash
NB="/path/to/notebook.ipynb"
```

### Adding Cells

```bash
# Add markdown cell
$COLAB notebook add --filepath=$NB --cell_type=markdown --content="## Section Title"

# Add code cell (default type)
$COLAB notebook add --filepath=$NB --content="print('hello')"

# Insert at specific position
$COLAB notebook add --filepath=$NB --position=0 --content="# First cell"
```

### Updating Cells

> [!NOTE] Newly created notebooks contain 0 cells (empty), so cell index `0`
> does not exist yet. Use `$COLAB notebook add` to insert the first cell before
> attempting to update cell 0.

```bash
# Recommended: Update cell 0 using the --content flag (to avoid heredoc execution errors)
$COLAB notebook update --filepath=$NB --cell_index=0 --content="print('new cell content')"

# Update cell 0 with new content
$COLAB notebook update --filepath=$NB --cell_index=0 << 'EOF'
# Updated Title
New content here
EOF
```

### Other Operations

```bash
# List cells
$COLAB notebook list_cells --filepath=$NB

# Get cell content
$COLAB notebook get --filepath=$NB --cell_index=0

# Delete cell
$COLAB notebook delete --filepath=$NB --cell_index=2
```

For details on how to construct a notebook, see
[notebook_creation.md](references/notebook_creation.md).

### Executing Code and Notebooks

If you need to execute code or a notebook and do not have the address of a
runtime, you can check for available Borg and local runtimes using:

```bash
$COLAB runtime fetch
```

If you are explicitly asked to start a new runtime or if you ran `runtime fetch`
command and no runtimes are available for the user's execution you can follow
detailed instructions on starting local or Borg runtimes at
[runtime_management.md](references/runtime_management.md).

#### Recommended: Execution with Session Management (Default)

Unless specified otherwise by the user, you **MUST** use sessions. You can
assume that the user will want to iterate on the execution results, so
maintaining state between executions is needed. If a session is not provided by
the user, you can open and use one as shown below:

> [!IMPORTANT] Do NOT close the session until the user explicitly confirms they
> are done with their work. Kernel state (Python variables, functions, etc.) is
> lost once the session is closed. Once a task has completed you can ask the
> user if they'd like to close the session to free up resources on their
> runtime.

```bash
# 1. Open a session
SESSION_ID=$($COLAB session open --server_address=$SERVER_ADDRESS | awk '{print $NF}')

# 2. Execute code in the session (illustrating state persistence)
$COLAB execute --server_address=$SERVER_ADDRESS --session_id=$SESSION_ID --code="x = 100"
$COLAB execute --server_address=$SERVER_ADDRESS --session_id=$SESSION_ID --code="print(x * 2)" # Outputs 200

# 3. Execute a notebook in the session
$COLAB execute --server_address=$SERVER_ADDRESS --session_id=$SESSION_ID --notebook_json='{"nbformat": 4, "nbformat_minor": 5, "metadata": {}, "cells": [{"cell_type": "code", "execution_count": null, "id": "cellid", "metadata": {}, "outputs": [], "source": ["print(123)"]}]}'

# 4. Execute a notebook from a file in the session
$COLAB execute --server_address=$SERVER_ADDRESS --session_id=$SESSION_ID --filepath='/path/to/notebook.ipynb'

# 5. Check if session is active (active means the session is open, it does not imply whether it is blocked with a prior execution request)
$COLAB session get --server_address=$SERVER_ADDRESS --session_id=$SESSION_ID # Outputs Session session-123 is active.

# 6. (Optional) Interrupt ongoing execution in the session (use this command if you think the session is stuck or unresponsive; the session will be available for use after successful interruption)
$COLAB session interrupt --server_address=$SERVER_ADDRESS --session_id=$SESSION_ID

# 7. Close the session ONLY after explicitly confirming the user no longer needs the session.
$COLAB session close --server_address=$SERVER_ADDRESS --session_id=$SESSION_ID
```

#### One-off Execution (Without Session)

If you do not need to persist state between executions, you can run commands
without a session. Note that variables will not be shared between separate
`execute` calls.

```bash
# Execute standalone Python code (no state persisted)
$COLAB execute --server_address=$SERVER_ADDRESS --code="print('Hello')"
```

### Executing specific cells

Colab notebook cells are independent and not all cells need to be executed if
they are not relevant for the task. You can specify `cell_ids` to trigger their
execution based on the order determined by the notebook. Combine it with a
runtime session for easier iteration on specific cells.

**Constraints:**

-   **Code cells only**: `--cell_ids` only supports code cells. Executing
    markdown/raw cells will fail.

**Finding Cell IDs:**

-   Standalone field in `nbformat` 4.5+ (`"id": "..."`); in `metadata` for older
    versions (`"metadata": {"id": "..."}`).

```bash
# Execute only the cell with id cellid456 in a session
$COLAB execute --server_address=$SERVER_ADDRESS --session_id=$SESSION_ID --cell_ids=cellid456 --notebook_json='{"nbformat": 4, "nbformat_minor": 5, "metadata": {}, "cells": [{"cell_type": "code", "execution_count": null, "id": "cellid123", "metadata": {}, "outputs": [], "source": ["print(123)"]}, {"cell_type": "code", "execution_count": null, "id": "cellid456", "metadata": {}, "outputs": [], "source": ["print(456)"]}]}'
```

You can combine both cell IDs and sessions to maintain state across multiple
executions while running specific cells.

### Executing long-running notebooks

Some notebook cells take longer to execute than the default timeout of 600
seconds. If you expect that a notebook or a code snippet would need more time
for execution, you can specify it through the `timeout_sec` parameter.

```bash
$COLAB execute --server_address=$SERVER_ADDRESS --session_id=$SESSION_ID --timeout_sec=1500 --filepath='/path/to/long_running_notebook.ipynb'
```

```bash
$COLAB execute --server_address=$SERVER_ADDRESS --session_id=$SESSION_ID --timeout_sec=1000 --code="import sample_library" --code="" --code="sample_library.long_running_fn()"
```

### Using `_nb.py` file for execution

You can pass a `_nb.py` file directly to the `--filepath` flag. The CLI will
automatically handle it by executing it as Python code.

```bash
$COLAB execute --server_address=$SERVER_ADDRESS --session_id=$SESSION_ID --filepath='/path/to/notebook_nb.py'
```

The `--cell_ids` flag is not supported when executing `_nb.py` files.

### Using `template_params` for parameterization

You can pass template parameters as a JSON string to override template variables
in the script or notebook. See more about template notebooks at
go/colab/templates:

```bash
$COLAB execute --server_address=$SERVER_ADDRESS --session_id=$SESSION_ID --filepath='/path/to/notebook_nb.py' \
  --template_params='{"PARAM_NAME": "value"}'
```

### Handling the Output from Execution

Format of execution results can be controlled by `--output_format`:

<!-- mdformat off(preserve table) -->
| Value           | Description   |
|-----------------|---------------|
| `markdown` | **(default)** Markdown converted cells including both inputs and outputs. |
| `markdown_outputs_only` | Markdown converted cell output. |
| `notebook_json` | The raw executed notebook as a JSON string. |
<!-- mdformat on -->

Both markdown formats prepend an H2 header that links to the executed notebook
in the Colab UI. When `--inplace` is used with a path that Colab can serve
directly the header link points at `--filepath`, otherwise, the notebook is
written to a per-user CNS directory with a 1 week TTL.

Image outputs (e.g. matplotlib plots, PNG/JPEG/SVG `display_data`) are also
persisted to that same per-user CNS directory and are inlined in the markdown
body as `cnsviewer.corp.google.com` URLs so they render in markdown viewers.

The `notebook_json` format returns only the raw notebook JSON and does not
upload to CNS or attach a header.

Using `--inplace` updates the notebook in `--filepath` with the resulting
notebook JSON while also returning the desired output as specified in
`--output_format`.

```bash
# Default: get markdown with both inputs and outputs.
$COLAB execute --server_address=$SERVER_ADDRESS --session_id=$SESSION_ID --code="print(42)"

# Get markdown output directly without inputs (most token-efficient for text-only results)
$COLAB execute --server_address=$SERVER_ADDRESS --session_id=$SESSION_ID \
  --output_format=markdown_outputs_only --code="print(42)"

# Get raw notebook JSON
$COLAB execute --server_address=$SERVER_ADDRESS --session_id=$SESSION_ID \
  --output_format=notebook_json --code="print(42)"
```

The Colab link in the header of the markdown output has the form
`http://colab.corp.google.com<notebook_path_in_cns>`. You can extract the CNS
path from that link and read the notebook contents directly with `fileutil`:

```bash
fileutil cat "<notebook_path_in_cns>"
```

### Getting Colab Links to visualize notebooks in the Colab UI

```bash
# Get Colab link using a filepath
$COLAB notebook get_colab_link --filepath=$NB

# Get Colab link using notebook JSON
$COLAB notebook get_colab_link --notebook_json='{"nbformat": 4, "nbformat_minor": 5, "metadata": {}, "cells": [{"cell_type": "code", "execution_count": null, "id": "cellid", "metadata": {}, "outputs": [], "source": ["print(123)"]}]}'
```

#### Connect to local Runtime

Optionally, when a local runtime is used, include the connect_local flag to
automatically connect to the local runtime when viewing the notebook in the
Colab UI.

#### Connect to active execution session via Colab UI

Optionally, include the session ID to automatically connect to the execution
session when viewing the notebook in the Colab UI. This allows users to use and
explore the same Python state in the Colab UI that has been previously executed
on this session.

## Manage dependencies

> [!IMPORTANT] Do NOT attempt to use `pip` or other package managers as those do
> not work in Google3. Use custom kernelspecs instead.

If execute-based invocations are failing due to `ModuleNotFound` or
`ImportError` exceptions, you may want to create a new kernelspec with a custom
set of dependencies. A kernelspec is a template of a kernel binary from which
you can create multiple sessions that use that kernelspec binary. This supports
including any previously missing/unavailable Python dependencies such that
future sessions don't encounter the import-related exceptions.

For detailed instructions on how to create, build, monitor, and use a custom
kernelspec with custom dependencies, see
[dependency_management.md](references/dependency_management.md).

## Key Flags

<!-- mdformat off(preserve table) -->
| Flag               | Description                                             |
| ------------------ | ------------------------------------------------------- |
| `--filepath`       | Path to notebook file.                                  |
| `--cell_index`     | 0-based cell index (for `notebook get/update/delete`).  |
| `--content`        | Content to write to the cell (for `notebook add/update`). |
| `--cell_type`      | code (default), markdown, raw (for `notebook add`).     |
| `--position`       | Insert position, default: append (for `notebook add`).  |
| `--server_address` | Server address (BNS for Borg or local e.g. `localhost:8000`). |
| `--code`           | Python code to execute (for `execute`). Repeatable; values are joined with newlines. |
| `--notebook_json`  | Notebook JSON for `execute` or `notebook get_colab_link`. |
| `--session_id`     | ID for a persistent session (for `execute`, `session close`, or `notebook get_colab_link`). |
| `--cell_ids`       | Cell IDs to execute (for `execute`).                    |
| `--timeout_sec`    | Execution deadline in seconds (for `execute`).          |
| `--output_format`  | Output format for `execute`: `markdown` (default), `markdown_outputs_only`, `notebook_json`. |
| `--inplace`        | Save executed notebook to provided path (for `execute`). |
| `--template_params` | JSON string of template parameters (for `execute`). |
| `--connect_local`  | Whether to automatically connect to a local runtime in the Colab UI (for `notebook get_colab_link`). |
| `--notebook_id`     | Client created ID representing the notebook/workload (for `kernelspec create`).  See [dependency_management](references/dependency_managament.md) for choosing these values. |
| `--additional_dep_targets` | Additional dependency targets to build into the kernel (for `kernelspec create`). |
| `--colab_binary_target` | The colab_binary target to build (for `kernelspec create`). |
| `--source_uri`     | The source URI to build from (for `kernelspec create`). |
<!-- mdformat on -->

## Reporting Issues

Report bugs or improvements for this skill at
[Agent Skill: colab](http://b/hotlists/7300567). See the `skill_issue` skill for
instructions on filing and triaging skill bugs.
