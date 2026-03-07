from pathlib import Path
from jinja2 import Environment, FileSystemLoader


class DatasetFileGenerator:
    def __init__(self, project_root: Path):
        """
        project_root = src/<project_name>
        """
        self.project_root = project_root
        self.training_dir = project_root / "pipeline_configs" / "training"
        self.inference_dir = project_root / "pipeline_configs" / "inference"
        # self.retraining_dir = project_root / "pipeline_configs" / "retraining"

        self.project_name = project_root.name

        self.templates_dir = (
            Path(__file__).resolve().parents[1]
            / "templates"
            / "dataset"
        )
    
    def generate(self, dataset_name: str) -> list[Path]:
        context = {
            "dataset_keyword": dataset_name,
            "project": self.project_name,
        }

        ## Training pipeline
        # data.yml
        train_env = Environment(loader=FileSystemLoader(self.templates_dir / "training"))
        train_data_yml = self._render(
            template_name="data.yml.jinja",
            context=context,
            env=train_env
        )

        ## Inference pipeline
        # data.yml
        infer_env = Environment(loader=FileSystemLoader(self.templates_dir / "inference"))
        infer_data_yml = self._render(
            template_name="data.yml.jinja",
            context=context,
            env=infer_env
        )

        return [train_data_yml, infer_data_yml]

    def _render(self, template_name: str, context: dict, env: Environment) -> Path:
        template = env.get_template(template_name)
        content = template.render(**context)
        return content