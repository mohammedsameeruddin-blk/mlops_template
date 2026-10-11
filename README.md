# MLOps CLI Tool

CLI tool for managing MLOps projects - add and remove datasets and models.

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

Adds a new model to an existing MLOps project. Creates pipeline config files under `training/`, `inference/`, `retraining/`, `drift_monitoring/`, `serving/`, and `promotion/` subdirectories, appends the model to `drift_monitoring/evaluate.yml`, and inserts the corresponding tasks into all workflow job YAML files that exist.

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
- `pipeline_configs/drift_monitoring/<model>/drift.yml`
- `pipeline_configs/serving/<model>/serving.yml`
- `pipeline_configs/promotion/<model>/promotion.yml`

**Updates:**
- `pipeline_configs/drift_monitoring/evaluate.yml` - appends model to `models:` list
- `workflow_jobs/wf_<project>_training.yml`
- `workflow_jobs/wf_<project>_inference.yml`
- `workflow_jobs/wf_<project>_retraining.yml`
- `workflow_jobs/wf_<project>_drift_monitoring.yml`
- `workflow_jobs/wf_<project>_serving.yml`
- `workflow_jobs/wf_<project>_promotion.yml`

> `pipeline_configs/drift_monitoring/data.yml` is created on the first model add if it does not already exist.

---

### `remove-model`

Removes an existing model from an MLOps project. Deletes the model's pipeline config directories, removes the model from `drift_monitoring/evaluate.yml`, and strips the corresponding tasks from all workflow job YAML files that exist.

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
- `pipeline_configs/drift_monitoring/<model>/`
- `pipeline_configs/serving/<model>/`
- `pipeline_configs/promotion/<model>/`

**Updates:**
- `pipeline_configs/drift_monitoring/evaluate.yml` - removes model from `models:` list
- `workflow_jobs/wf_<project>_training.yml`
- `workflow_jobs/wf_<project>_inference.yml`
- `workflow_jobs/wf_<project>_retraining.yml`
- `workflow_jobs/wf_<project>_drift_monitoring.yml`
- `workflow_jobs/wf_<project>_serving.yml`
- `workflow_jobs/wf_<project>_promotion.yml`

---

## Naming Rules

Dataset and model names must contain only letters, numbers, dashes (`-`), and underscores (`_`).
