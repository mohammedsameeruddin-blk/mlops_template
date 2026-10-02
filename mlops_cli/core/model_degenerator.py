import shutil
from pathlib import Path
from ruamel.yaml import YAML


class ModelFileDegenerator:
    def __init__(self, project_root: Path):
        """
        project_root = src/<project_name>
        """
        self.project_root = project_root
        self.project_name = project_root.name

        self.training_dir = project_root / "pipeline_configs" / "training"
        self.inference_dir = project_root / "pipeline_configs" / "inference"
        self.retraining_dir = project_root / "pipeline_configs" / "retraining"
        self.drift_monitoring_dir = (
            project_root / "pipeline_configs" / "drift_monitoring"
        )

        self.repo_root = project_root.parents[1]
        self.workflow_dir = self.repo_root / "workflow_jobs"
        self.training_job = self.workflow_dir / f"wf_{self.project_name}_training.yml"
        self.inference_job = self.workflow_dir / f"wf_{self.project_name}_inference.yml"
        self.retraining_job = (
            self.workflow_dir / f"wf_{self.project_name}_retraining.yml"
        )
        self.drift_monitoring_job = (
            self.workflow_dir / f"wf_{self.project_name}_drift_monitoring.yml"
        )

        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.indent(mapping=2, sequence=4, offset=2)
        self.yaml.width = 4096

    def degenerate(self, model_name: str) -> tuple[list[Path], list[Path]]:
        removed_files = []
        updated_workflow_files = []

        # Remove model config directories
        for stage_dir in (
            self.training_dir,
            self.inference_dir,
            self.retraining_dir,
            self.drift_monitoring_dir,
        ):
            model_dir = stage_dir / model_name
            if model_dir.exists():
                for f in model_dir.iterdir():
                    removed_files.append(f)
                shutil.rmtree(model_dir)

        self._update_evaluate_yml(model_name)

        # Update workflow files
        if self.training_job.exists():
            self._remove_from_job(
                self.training_job,
                "training",
                f"{model_name}_training",
                "--models_registered",
                model_name,
            )
            updated_workflow_files.append(self.training_job)

        if self.inference_job.exists():
            self._remove_from_job(
                self.inference_job,
                "inference",
                f"{model_name}_inference",
                "--models_used",
                model_name,
            )
            updated_workflow_files.append(self.inference_job)

        if self.retraining_job.exists():
            self._remove_from_job(
                self.retraining_job,
                "retraining",
                f"{model_name}_retraining",
                "--models_registered",
                model_name,
            )
            updated_workflow_files.append(self.retraining_job)

        if self.drift_monitoring_job.exists():
            self._remove_from_job(
                self.drift_monitoring_job,
                "drift_monitoring",
                f"{model_name}_drift_detection",
                None,
                None,
            )
            updated_workflow_files.append(self.drift_monitoring_job)

        return removed_files, updated_workflow_files

    def _update_evaluate_yml(self, model_name: str) -> None:
        evaluate_yml = self.drift_monitoring_dir / "evaluate.yml"
        if not evaluate_yml.exists():
            return
        with evaluate_yml.open(encoding="utf-8") as f:
            data = self.yaml.load(f)
        models: list = data["actions"][0]["functions"]["kwargs"]["models"]
        models[:] = [m for m in models if m != model_name]
        with evaluate_yml.open("w", encoding="utf-8") as f:
            self.yaml.dump(data, f)

    def _remove_from_job(
        self,
        job_path: Path,
        job_key: str,
        task_key: str,
        param_name: str | None = None,
        model_name: str | None = None,
    ) -> None:
        with job_path.open() as f:
            data = self.yaml.load(f)

        tasks = data["resources"]["jobs"][job_key]["tasks"]

        # nothing to remove
        if not any(t["task_key"] == task_key for t in tasks):
            return

        # remove the model task
        tasks[:] = [t for t in tasks if t["task_key"] != task_key]

        # remove from end_setup depends_on and model param
        end_task = next((t for t in tasks if t["task_key"] == "end_setup"), None)
        if end_task:
            end_task["depends_on"] = [
                d
                for d in end_task.get("depends_on", [])
                if d.get("task_key") != task_key
            ]
            self._remove_model_param(end_task, param_name, model_name)

        with job_path.open("w") as f:
            self.yaml.dump(data, f)

    def _remove_model_param(
        self, end_task, param_name: str | None, model_name: str | None
    ) -> None:
        params = end_task["spark_python_task"]["parameters"]

        for i, p in enumerate(params):
            if param_name is not None and p == param_name:
                current = params[i + 1].strip("'")
                models = [
                    m.strip()
                    for m in current.split(",")
                    if m.strip() and (model_name is None or m.strip() != model_name)
                ]
                params[i + 1] = ",".join(models)
                break
