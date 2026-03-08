from pathlib import Path
from jinja2 import Environment, FileSystemLoader


class ModelFileGenerator:
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
            / "model"
        )

        self.train_env = Environment(loader=FileSystemLoader(self.templates_dir / "training"))
        self.infer_env = Environment(loader=FileSystemLoader(self.templates_dir / "inference"))
        # self.retrain_env = Environment(loader=FileSystemLoader(self.templates_dir / "retraining"))

    def generate(self, model: str) -> list[Path]:
        train_model_dir = self.training_dir / model
        inference_model_dir = self.inference_dir / model
        # retrain_model_dir = self.retraining_dir / model

        if train_model_dir.exists():
            raise FileExistsError(f"Model '{model}' already exists")
        else:
            train_model_dir.mkdir(parents=True)
        
        if inference_model_dir.exists():
            raise FileExistsError(f"Model '{model}' already exists")
        else:
            inference_model_dir.mkdir(parents=True)
        
        # if retrain_model_dir.exists():
        #     raise FileExistsError(f"Model '{model}' already exists")
        # else:
        #     retrain_model_dir.mkdir(parents=True)

        context = {
            "project": self.project_name,
            "model": model
        }

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
        
        # ## Retraining pipeline
        # for template_name in self.retrain_env.list_templates():
        #     if not template_name.endswith(".jinja"):
        #         continue
        #
        #     output_path = retrain_model_dir / template_name.replace(".jinja", "")
        #     created_files.append(
        #         self._render(template_name, output_path, context, self.retrain_env)
        #     )
        
        return created_files

    def _render(self, template_name: str, output_path: Path, context: dict, env: Environment) -> Path:
        template = env.get_template(template_name)
        content = template.render(**context)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")

        return output_path
