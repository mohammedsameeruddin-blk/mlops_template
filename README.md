# MLOps Template

A [Copier](https://copier.readthedocs.io/) scaffold that generates a production-ready MLOps project on **Databricks** with six fully wired pipeline types, MLflow tracking, Databricks Feature Store integration, Google Chat notifications, and a unified Delta-table audit trail.

---

## What Gets Generated

Running this template creates a Python package + Databricks Asset Bundle (DAB) project under `mlops_<project>/` containing:

| Workflow | Purpose |
|---|---|
| `wf_<project>_training` | End-to-end model training (extract → preprocess → featurize → split → train → register) |
| `wf_<project>_inference` | Batch inference (extract → preprocess → featurize → prepare input → score → write predictions) |
| `wf_<project>_retraining` | Same as training but triggered by drift; reads best params from the previous training run |
| `wf_<project>_serving` | Deploys a Databricks Model Serving endpoint (direct / blue-green / canary) |
| `wf_<project>_promotion` | Promotes the challenger endpoint version to champion |
| `wf_<project>_drift_monitoring` | Detects data drift, prediction drift, and data quality issues; optionally triggers retraining |

Each workflow logs every step to MLflow, writes an audit record to a Delta table, and sends a Google Chat notification on failure or completion.

---

## Prerequisites

| Tool | Version | Notes |
|---|---|---|
| Python | ≥ 3.10 | |
| [Copier](https://copier.readthedocs.io/) | ≥ 9 | `pip install copier` |
| [uv](https://docs.astral.sh/uv/) | latest | Used to build the project wheel (`uv build`) |
| [Databricks CLI](https://docs.databricks.com/en/dev-tools/cli/index.html) | ≥ 0.200 | Must be authenticated to your target workspace |
| DS Project wheel | — | Place the `.whl` file in `ds_backend/` before deploying |

---

## Scaffold a New Project

```bash
copier copy https://github.com/mohammedsameeruddin-blk/mlops_template <destination_directory>
```

Or to scaffold from a specific branch/revision:

```bash
copier copy --vcs-ref feature/project_template \
    https://github.com/mohammedsameeruddin-blk/mlops_template <destination_directory>
```

You will be prompted for the following values:

| Prompt | Example | Description |
|---|---|---|
| `project` | `fraud_detection` | MLOps project name. Used as the Python package name and Databricks bundle name. No `mlops_` prefix. |
| `model` | `transaction` | Model name within the project. Sets the model registry entry name and all model-specific config paths. |
| `dataset_keyword` | `transaction_data` | Dataset label used for preprocessing, featurization, and Feature Store table names. |
| `author_email` | `you@company.com` | Your email. Sets the DAB workspace root path for `dev` target. |
| `dev_host` | `https://adb-xxx.azuredatabricks.net` | Databricks workspace URL for development. |
| `qa_host` | `https://adb-yyy.azuredatabricks.net` | QA workspace URL. Defaults to `dev_host` if left blank. |
| `prod_host` | `https://adb-zzz.azuredatabricks.net` | Production workspace URL. Defaults to `dev_host` if left blank. |
| `ds_project` | `fraud_ds` | Name of the Data Science Python package. Must match the installed package name from the `ds_backend/` wheel. |

---

## Add a New Model to an Existing Project

To onboard a second model (e.g., `chargeback`) into the same project, run Copier again in the project directory:

```bash
copier update --vcs-ref feature/project_template --overwrite
```

Copier will re-prompt for `model` and `dataset_keyword`. Files marked `_skip_if_exists` in `copier.yml` (`databricks.yml`, `MANIFEST.in`, `pyproject.toml`) are left unchanged. New model-specific pipeline config YAMLs and workflow jobs are added.

---

## Post-Scaffold Setup

After scaffolding, complete these steps before deploying:

### 1. Fill in `config.toml`
Open `src/<project>/config.toml` and populate each environment section (`[dev]`, `[qa]`, `[prod]`) with your actual catalog/schema names, Volumes path, and Google Chat webhook URL. Every field that is left as `""` will cause a runtime error. See the inline comments in that file for what each field expects.

### 2. Set DS Project Class Paths
The pipeline config YAMLs under `src/<project>/pipeline_configs/` reference the Data Science project's Python classes via `class_path`. These are pre-filled for `train.yml` and `inference.yml` using the `ds_project` variable, but `preprocess.yml` and `featurization.yml` contain a `<data_science_module_file_path>` placeholder that must be replaced with the actual dotted Python path.

Look for every occurrence of `<data_science_module_file_path>` and replace it with the correct path, e.g.:
```
fraud_ds.preprocessing.pipeline:DataPreprocessor
```

### 3. Set Source Data Table (data.yml)
In `src/<project>/pipeline_configs/training/data.yml` (and the matching inference and retraining versions), replace `<catalog.schema.table>` with the fully qualified Databricks table name that holds your raw input data.

### 4. Review Cluster Variables
In `databricks.yml`, review the `spark_version`, `node_type_id`, `min_workers`, and `max_workers` variables and adjust them to match your compute requirements.

### 5. Place the DS Wheel
Drop the Data Science project `.whl` file into the `ds_backend/` directory. The DAB build step resolves it from `ds_backend/*.whl`.

### 6. Deploy
```bash
# Authenticate the CLI
databricks auth login --host https://adb-xxx.azuredatabricks.net

# Deploy to dev (default target)
databricks bundle deploy -t dev

# Run the training workflow
databricks bundle run wf_<project>_training -t dev
```

---

## Project Structure (Generated)

```
mlops_<project>/
├── databricks.yml              # DAB bundle root — cluster vars, targets, includes
├── pyproject.toml              # Python package definition & dependencies
├── ds_backend/                 # Drop the DS project .whl here before deploying
├── scripts/                    # Databricks Spark Python task entry points
│   ├── start_setup.py          # Creates MLflow experiment, sets up audit table
│   ├── data_extraction.py      # Reads source table, writes to MODEL_CATALOG_SCHEMA
│   ├── data_preprocessing.py   # Calls DS preprocessor class
│   ├── data_featurization.py   # Calls DS featurizer, writes to Feature Store (training)
│   ├── data_inference_featurization.py  # Same but transform-only (inference)
│   ├── train.py                # Hypertuning → evaluation → training → registration
│   ├── inference.py            # Batch scoring using @champion model
│   ├── deploy_serving.py       # Creates/updates Databricks serving endpoint
│   ├── promote_serving.py      # Promotes challenger → champion
│   ├── drift_detection.py      # Runs data / prediction / quality drift detectors
│   ├── drift_evaluation.py     # Aggregates results, optionally triggers retraining
│   └── end_setup.py            # Sends completion notification, cleans up output folder
├── src/<project>/
│   ├── config.toml             # Per-environment runtime config (FILL THIS IN)
│   ├── custom_actions/         # Add your own action classes here
│   ├── common/                 # Shared library (data, drift, serving, utils)
│   └── pipeline_configs/       # Action config YAMLs consumed by each script
│       ├── common/             # start.yml, end.yml
│       ├── training/           # data, preprocess, featurization, splitter, train
│       ├── inference/          # data, preprocess, featurization, prepare_input, inference
│       ├── retraining/         # mirrors training/
│       ├── serving/            # serving.yml (strategy, workload size)
│       ├── promotion/          # promotion.yml
│       └── drift_monitoring/   # drift.yml, evaluate.yml
└── workflow_jobs/
    ├── wf_<project>_training.yml
    ├── wf_<project>_inference.yml
    ├── wf_<project>_retraining.yml
    ├── wf_<project>_serving.yml
    ├── wf_<project>_promotion.yml
    └── wf_<project>_drift_monitoring.yml
```

---

## What the DS Team Needs to Implement

The template wires the full pipeline infrastructure. The Data Science team needs to implement these classes in the `ds_project` package:

| Class | Module Path | Called By |
|---|---|---|
| Preprocessor | `<ds_project>.preprocessing.<dataset>:DataPreprocessor` | `preprocess.yml` (training & inference) |
| Feature pipeline | `<ds_project>.featurization.<dataset>:FeaturePipeline` | `featurization.yml` (training & inference) |
| `HyperparameterTuner` | `<ds_project>.models.<model>.training.hypertuning.tuner` | `train.yml` |
| `ModelEvaluator` | `<ds_project>.models.<model>.training.evaluation.selector` | `train.yml` |
| `ModelTrainer` | `<ds_project>.models.<model>.training.train` | `train.yml` |
| `BatchScoring` | `<ds_project>.models.<model>.inference.scoring` | `inference.yml` |

Each class is loaded dynamically via the `class_path` field in the pipeline config YAML. The MLOps scaffold handles MLflow tracking, Feature Store writes, audit logging, and notifications — the DS classes only need to implement the business logic.

---

## Linting Jinja Templates

The repo includes `ruff_jinja.py`, a utility that strips Jinja syntax from `.py.jinja` files and runs Ruff on the resulting Python:

```bash
# Check all .py.jinja files
python ruff_jinja.py check

# Format all .py.jinja files
python ruff_jinja.py format
```

---

## Customising the Template

- **Add a custom action class**: Add a class to `src/<project>/custom_actions/__init__.py` and reference it via `class_path` in any pipeline config YAML. The class receives all `kwargs` from the YAML and must implement a `run()` method.
- **Change serving strategy**: Edit `src/<project>/pipeline_configs/serving/<model>/serving.yml` — options are `direct`, `blue_green`, or `canary`.
- **Enable drift auto-retraining**: Set `auto_trigger.enable: true` in `src/<project>/pipeline_configs/drift_monitoring/evaluate.yml`.
- **Schedule drift monitoring**: Uncomment and configure the `trigger` block in `workflow_jobs/wf_<project>_drift_monitoring.yml`.
