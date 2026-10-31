# MLOps Template

A [Copier](https://copier.readthedocs.io/) template for bootstrapping MLOps projects at Blackstraw. It provides a standardised project scaffold covering data extraction, preprocessing, featurization, training, inference, serving, promotion, retraining, and drift monitoring — orchestrated via Databricks workflows.

## Requirements

- [Copier](https://copier.readthedocs.io/) v9+
- [uv](https://docs.astral.sh/uv/)

```bash
uv tool install copier
```

## Naming Convention

Your project directory **must** be named with a `mlops_` prefix:

```
mlops_<project_name>
```

Example: `mlops_store_sales`, `mlops_customer_churn`, `mlops_fraud_detection`

## Creating a New Project

Run this command from your workspace (the parent directory where you want the project to live):

```bash
copier copy git@github.com:mohammedsameeruddin-blk/mlops_template.git mlops_<project_name> --trust
```

Example:

```bash
copier copy git@github.com:mohammedsameeruddin-blk/mlops_template.git mlops_store_sales --trust
```

### Questions You Will Be Asked

| Question | Description | Example |
|---|---|---|
| `project` | MLOps project name (no `mlops_` prefix) | `store_sales` |
| `model` | Model name | `sales_forecast` |
| `dataset_keyword` | Dataset keyword for preprocessing and featurization | `oil_stores` |
| `author_email` | Your email address | `you@blackstraw.ai` |
| `dev_host` | Databricks DEV workspace URL | `https://adb-xxxx.azuredatabricks.net/` |
| `qa_host` | Databricks QA workspace URL (defaults to DEV) | `https://adb-xxxx.azuredatabricks.net/` |
| `prod_host` | Databricks PROD workspace URL (defaults to DEV) | `https://adb-xxxx.azuredatabricks.net/` |
| `ds_project` | DS project name this MLOps project depends on | `store_sales` |

### After Creation

```bash
cd mlops_<project_name>

# Install dependencies
uv sync

# Initialise git
git init
git checkout -b main
git add .
git commit -m "chore: initial project scaffold from template"
```

## Updating an Existing Project

When a new template version is released, run this from inside your project directory:

```bash
copier update --vcs-ref <version> --trust
```

Example:

```bash
copier update --vcs-ref v1.1.0 --trust
```

Then review and commit the changes:

```bash
git diff
git add .
git commit -m "chore: update project scaffold to <version>"
```

## Project Structure

```
mlops_<project_name>/
├── src/
│   └── <project>/
│       ├── common/
│       │   ├── data/
│       │   ├── drift/
│       │   ├── model/
│       │   ├── serving/
│       │   └── utils/
│       ├── custom_actions/
│       └── pipeline_configs/
│           ├── training/
│           ├── retraining/
│           ├── inference/
│           ├── serving/
│           ├── promotion/
│           └── drift_monitoring/
├── scripts/
│   ├── train.py
│   ├── inference.py
│   ├── data_preprocessing.py
│   ├── data_featurization.py
│   ├── deploy_serving.py
│   ├── promote_serving.py
│   ├── drift_detection.py
│   └── drift_evaluation.py
├── workflow_jobs/
│   ├── wf_<project>_training.yml
│   ├── wf_<project>_inference.yml
│   ├── wf_<project>_retraining.yml
│   ├── wf_<project>_serving.yml
│   ├── wf_<project>_promotion.yml
│   └── wf_<project>_drift_monitoring.yml
├── databricks.yml
├── pyproject.toml
├── README.md
└── .copier-answers.yml
```

## Template Versions

| Version | Notes |
|---|---|
| `v1.0.0` | Initial release — restructured template, naming validation, `copier update` support |
