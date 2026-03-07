from pathlib import Path
from tempfile import NamedTemporaryFile
from jinja2 import Environment, FileSystemLoader
from benedict import benedict


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

        updated_files: list[Path] = []

        ## Training pipeline
        # data.yml
        train_env = Environment(loader=FileSystemLoader(self.templates_dir / "training"))
        train_data_yml = self._render(
            template_name="data.yml.jinja",
            context=context,
            env=train_env
        )
        train_file = self.training_dir / "data.yml"
        self._merge_rendered_actions_into_file(train_file, train_data_yml)
        updated_files.append(train_file)

        ## Inference pipeline
        # data.yml
        infer_env = Environment(loader=FileSystemLoader(self.templates_dir / "inference"))
        infer_data_yml = self._render(
            template_name="data.yml.jinja",
            context=context,
            env=infer_env
        )
        infer_file = self.inference_dir / "data.yml"
        self._merge_rendered_actions_into_file(infer_file, infer_data_yml)
        updated_files.append(infer_file)

        return updated_files

    def _render(self, template_name: str, context: dict, env: Environment) -> str:
        template = env.get_template(template_name)
        content = template.render(**context)
        return content

    def _merge_rendered_actions_into_file(self, existing_yml_path: Path, rendered_content: str) -> None:
        if existing_yml_path.exists() and existing_yml_path.read_text(encoding="utf-8").strip():
            existing_data = benedict.from_yaml(str(existing_yml_path))
        else:
            raise ValueError(f"Expected existing YAML file at {existing_yml_path} with content, but it does not exist or is empty.")

        rendered_data = self._load_yaml_from_rendered_content(rendered_content)

        existing_actions = existing_data.get("actions", [])
        if not isinstance(existing_actions, list):
            existing_actions = []

        new_actions = rendered_data.get("actions", [])
        if not isinstance(new_actions, list):
            new_actions = []

        existing_data["actions"] = [*existing_actions, *new_actions]
        existing_data.to_yaml(filepath=str(existing_yml_path))

    def _load_yaml_from_rendered_content(self, rendered_content: str) -> benedict:
        with NamedTemporaryFile(mode="w", suffix=".yml", encoding="utf-8", delete=False) as temp_file:
            temp_file.write(rendered_content)
            temp_file_path = Path(temp_file.name)

        try:
            return benedict.from_yaml(str(temp_file_path))
        finally:
            temp_file_path.unlink(missing_ok=True)