from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from ruamel.yaml import YAML


class ModelFileGenerator:
    def __init__(self, project_root: Path):
        """
        project_root = src/<project_name>
        """
        self.project_root = project_root
        self.training_dir = project_root / "pipeline_configs" / "training"
        self.inference_dir = project_root / "pipeline_configs" / "inference"
        self.retraining_dir = project_root / "pipeline_configs" / "retraining"
        self.drift_monitoring_dir = (
            project_root / "pipeline_configs" / "drift_monitoring"
        )

        self.project_name = project_root.name

        self.templates_dir = Path(__file__).resolve().parents[1] / "templates" / "model"

        self.train_env = Environment(
            loader=FileSystemLoader(self.templates_dir / "training")
        )
        self.infer_env = Environment(
            loader=FileSystemLoader(self.templates_dir / "inference")
        )
        self.retrain_env = Environment(
            loader=FileSystemLoader(self.templates_dir / "retraining")
        )
        self.drift_monitor_env = Environment(
            loader=FileSystemLoader(self.templates_dir / "drift_monitoring")
        )

        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.indent(mapping=2, sequence=4, offset=2)
        self.yaml.width = 4096

    def generate(self, model: str) -> list[Path]:
        train_model_dir = self.training_dir / model
        inference_model_dir = self.inference_dir / model
        retrain_model_dir = self.retraining_dir / model
        drift_monitoring_model_dir = self.drift_monitoring_dir / model

        if train_model_dir.exists():
            raise FileExistsError(f"Model '{model}' already exists")
        else:
            train_model_dir.mkdir(parents=True)

        if inference_model_dir.exists():
            raise FileExistsError(f"Model '{model}' already exists")
        else:
            inference_model_dir.mkdir(parents=True)

        if retrain_model_dir.exists():
            raise FileExistsError(f"Model '{model}' already exists")
        else:
            retrain_model_dir.mkdir(parents=True)
        if drift_monitoring_model_dir.exists():
            raise FileExistsError(f"Model '{model}' already exists")
        else:
            drift_monitoring_model_dir.mkdir(parents=True)

        context = {"project": self.project_name, "model": model}

        created_files = []

        ## Training pipeline
        for template_name in self.train_env.list_templates():
            if not template_name.endswith(".jinja"):
                continue

            output_path = train_model_dir / template_name.replace(".jinja", "")
            created_files.append(
                self._render(template_name, output_path, context, self.train_env)
            )

        ## Inference pipeline
        for template_name in self.infer_env.list_templates():
            if not template_name.endswith(".jinja"):
                continue

            output_path = inference_model_dir / template_name.replace(".jinja", "")
            created_files.append(
                self._render(template_name, output_path, context, self.infer_env)
            )

        ## Retraining pipeline
        for template_name in self.retrain_env.list_templates():
            if not template_name.endswith(".jinja"):
                continue

            output_path = retrain_model_dir / template_name.replace(".jinja", "")
            created_files.append(
                self._render(template_name, output_path, context, self.retrain_env)
            )

        ## Drift Monitoring pipeline
        for template_name in self.drift_monitor_env.list_templates():
            if not template_name.endswith(".jinja"):
                continue

            output_path = drift_monitoring_model_dir / template_name.replace(
                ".jinja", ""
            )
            created_files.append(
                self._render(
                    template_name, output_path, context, self.drift_monitor_env
                )
            )

        self._ensure_data_yml()
        created_files.append(self._update_evaluate_yml(model))

        return created_files

    def _ensure_data_yml(self) -> None:
        data_yml = self.drift_monitoring_dir / "data.yml"
        if data_yml.exists():
            return
        content = (
            "# Drift detection — data loading is handled directly by DriftOrchestrator via Spark table reads.\n"
            "# This file is intentionally minimal; it records the stage and audit table for traceability.\n\n"
            "version: '1.0'\n"
            "stage: drift_monitoring\n"
            "file: data.yml\n"
            'audit_table: "{{ env.AUDIT_TARGET_CATALOG }}.{{ env.AUDIT_TARGET_SCHEMA }}.{{ env.AUDIT_TARGET_TABLE }}"\n'
            "actions: []\n"
        )
        data_yml.write_text(content, encoding="utf-8")

    def _update_evaluate_yml(self, model: str) -> Path:
        evaluate_yml = self.drift_monitoring_dir / "evaluate.yml"

        if not evaluate_yml.exists():
            raise FileNotFoundError(f"{evaluate_yml} does not exist")
            # content = (
            #     "# Drift evaluation — aggregates per-model results and optionally triggers retraining.\n\n"
            #     "version: '1.0'\n"
            #     "stage: drift_monitoring\n"
            #     "file: evaluate.yml\n"
            #     'audit_table: "{{ env.AUDIT_TARGET_CATALOG }}.{{ env.AUDIT_TARGET_SCHEMA }}.{{ env.AUDIT_TARGET_TABLE }}"\n'
            #     "actions:\n"
            #     "  - name: evaluate_drift\n"
            #     "    enable: true\n"
            #     "    functions:\n"
            #     f"      class_path: {self.project_name}.common.drift.drift_utils:DriftEvaluator\n"
            #     "      kwargs:\n"
            #     f"        project_name: {self.project_name}\n"
            #     "        process_name: drift_evaluation\n"
            #     f'        drift_results_table: "{{{{ env.MODEL_CATALOG_SCHEMA }}}}.{self.project_name}_drift_results"\n'
            #     "        models:\n"
            #     f"          - {model}\n"
            #     "        auto_trigger:\n"
            #     "          enable: false\n"
            #     "          retraining_job_id: null\n"
            #     "          min_drifted_models: 1\n"
            # )
            # evaluate_yml.write_text(content, encoding="utf-8")
        else:
            with evaluate_yml.open(encoding="utf-8") as f:
                data = self.yaml.load(f)
            models: list = data["actions"][0]["functions"]["kwargs"]["models"]
            if model not in models:
                models.append(model)
            with evaluate_yml.open("w", encoding="utf-8") as f:
                self.yaml.dump(data, f)

        return evaluate_yml

    def _render(
        self, template_name: str, output_path: Path, context: dict, env: Environment
    ) -> Path:
        template = env.get_template(template_name)
        content = template.render(**context)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")

        return output_path
