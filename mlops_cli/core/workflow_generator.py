from pathlib import Path
from ruamel.yaml import YAML


class WorkflowFileGenerator:

    def __init__(self, project_root: Path):
        """
        project_root = src/<project_name>
        """
        self.project_root = project_root
        self.project_name = project_root.name

        self.repo_root = project_root.parents[1]
        self.workflow_dir = self.repo_root / "workflow_jobs"
        self.training_job = self.workflow_dir / f"wf_{self.project_name}_training.yml"
        self.inference_job = self.workflow_dir / f"wf_{self.project_name}_inference.yml"
        # self.retraining_job = self.workflow_dir / f"wf_{self.project_name}_retraining.yml"

        # YAML handler
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.indent(mapping=2, sequence=4, offset=2)
        self.yaml.width = 4096

    def generate(self, model_name: str):

        updated = []

        if self.training_job.exists():
            self._update_training_job(model_name)
            updated.append(self.training_job)

        if self.inference_job.exists():
            self._update_inference_job(model_name)
            updated.append(self.inference_job)

        return updated

    def _update_training_job(self, model_name: str):

        with self.training_job.open() as f:
            data = self.yaml.load(f)

        tasks = data["resources"]["jobs"]["training"]["tasks"]

        new_task_key = f"{model_name}_training"

        # avoid duplicates
        if any(t["task_key"] == new_task_key for t in tasks):
            return

        split_task = next(t for t in tasks if t["task_key"] == "split_data")
        end_task = next(t for t in tasks if t["task_key"] == "end_setup")

        new_task = {
            "task_key": new_task_key,
            "depends_on": [{"task_key": "split_data"}],
            "environment_key": "default",
            "spark_python_task": {
                "python_file": "../scripts/train.py",
                "parameters": [
                    "--root_path",
                    "${workspace.root_path}",
                    "--runtime_env",
                    "${var.run_time_env}",
                    "--yml_task",
                    "train.yml",
                    "--project_name",
                    f"{self.project_name}",
                    "--model_name",
                    f"{model_name}",
                    "--stage_name",
                    "training",
                    "--task_key",
                    "{{task.name}}",
                    "--task_run_id",
                    "{{task.run_id}}",
                    "--job_name",
                    "{{job.name}}",
                    "--job_id",
                    "{{job.id}}",
                    "--job_run_id",
                    "{{job.run_id}}",
                    "--experiment_id",
                    "{{tasks.split_data.values.experiment_id}}",
                ],
            },
        }

        # insert before end_setup
        end_index = tasks.index(end_task)
        tasks.insert(end_index, new_task)

        # update end_setup dependency
        end_task["depends_on"].append({"task_key": new_task_key})

        with self.training_job.open("w") as f:
            self.yaml.dump(data, f)

    def _update_inference_job(self, model_name: str):

        with self.inference_job.open() as f:
            data = self.yaml.load(f)

        tasks = data["resources"]["jobs"]["inference"]["tasks"]

        new_task_key = f"{model_name}_inference"

        if any(t["task_key"] == new_task_key for t in tasks):
            return

        prepare_task = next(t for t in tasks if t["task_key"] == "prepare_input")
        end_task = next(t for t in tasks if t["task_key"] == "end_setup")

        new_task = {
            "task_key": new_task_key,
            "depends_on": [{"task_key": "prepare_input"}],
            "environment_key": "default",
            "spark_python_task": {
                "python_file": "../scripts/inference.py",
                "parameters": [
                    "--root_path",
                    "${workspace.root_path}",
                    "--runtime_env",
                    "${var.run_time_env}",
                    "--yml_task",
                    "inference.yml",
                    "--project_name",
                    f"{self.project_name}",
                    "--model_name",
                    f"{model_name}",
                    "--stage_name",
                    "inference",
                    "--task_key",
                    "{{task.name}}",
                    "--task_run_id",
                    "{{task.run_id}}",
                    "--job_name",
                    "{{job.name}}",
                    "--job_id",
                    "{{job.id}}",
                    "--job_run_id",
                    "{{job.run_id}}",
                    "--experiment_id",
                    "{{tasks.prepare_input.values.experiment_id}}",
                ],
            },
        }

        # insert before end_setup
        end_index = tasks.index(end_task)
        tasks.insert(end_index, new_task)

        # update end_setup dependency
        end_task["depends_on"].append({"task_key": new_task_key})

        with self.inference_job.open("w") as f:
            self.yaml.dump(data, f)
