# MLOps CLI Tool

CLI tool for managing MLOps projects — add and remove datasets and models.

## Installation

```bash
pip install -e .
```

Or as a project dependency (uv):

```bash
# pyproject.toml
"mlops-cli @ git+https://github.com/<org>/mlops_template.git@<branch>"
```

After updating the version, refresh the lock and sync:

```bash
uv lock --upgrade-package mlops-cli
uv sync
```

---

## Commands

### `add-dataset`

Adds a new dataset to an existing MLOps project. Updates the pipeline config files (`data.yml`, `preprocess.yml`, `featurization.yml`, `splitter.yml` / `prepare_input.yml`) across the training, inference, and retraining pipelines.

```bash
mlops-cli add-dataset /path/to/project --dataset-name <name>
```

| Option | Short | Required | Description |
|---|---|---|---|
| `--dataset-name` | `-d` | Yes | Name of the new dataset |

---

### `remove-dataset`

Removes an existing dataset from an MLOps project. Strips the corresponding actions and feature entries from all pipeline config files across training, inference, and retraining.

```bash
mlops-cli remove-dataset /path/to/project --dataset-name <name>
```

| Option | Short | Required | Description |
|---|---|---|---|
| `--dataset-name` | `-d` | Yes | Name of the dataset to remove |

---

### `add-model`

Adds a new model to an existing MLOps project. Creates pipeline config files under `training/`, `inference/`, and `retraining/` subdirectories, and inserts the corresponding tasks into all three workflow job YAML files.

```bash
mlops-cli add-model /path/to/project --model-name <name>
```

| Option | Short | Required | Description |
|---|---|---|---|
| `--model-name` | `-m` | Yes | Name of the new model |

**Creates:**
- `pipeline_configs/training/<model>/train.yml`
- `pipeline_configs/inference/<model>/inference.yml`
- `pipeline_configs/retraining/<model>/train.yml`

**Updates:**
- `workflow_jobs/wf_<project>_training.yml`
- `workflow_jobs/wf_<project>_inference.yml`
- `workflow_jobs/wf_<project>_retraining.yml`

---

### `remove-model`

Removes an existing model from an MLOps project. Deletes the model's pipeline config directories and removes the corresponding tasks (and their `end_setup` dependencies) from all three workflow job YAML files.

```bash
mlops-cli remove-model /path/to/project --model-name <name>
```

| Option | Short | Required | Description |
|---|---|---|---|
| `--model-name` | `-m` | Yes | Name of the model to remove |

**Removes:**
- `pipeline_configs/training/<model>/`
- `pipeline_configs/inference/<model>/`
- `pipeline_configs/retraining/<model>/`

**Updates:**
- `workflow_jobs/wf_<project>_training.yml`
- `workflow_jobs/wf_<project>_inference.yml`
- `workflow_jobs/wf_<project>_retraining.yml`

---

## Naming Rules

Dataset and model names must contain only letters, numbers, dashes (`-`), and underscores (`_`).
