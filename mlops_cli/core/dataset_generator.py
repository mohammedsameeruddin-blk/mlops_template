from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from ruamel.yaml import YAML
from io import StringIO


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

        # YAML handler
        self.yaml = YAML()
        self.yaml.preserve_quotes = True

    def generate(self, dataset_name: str) -> list[Path]:
        context = {
            "dataset_keyword": dataset_name,
            "project": self.project_name,
        }

        updated_files: list[Path] = []

        ## Training pipeline
        train_env = Environment(loader=FileSystemLoader(self.templates_dir / "training"))
        training_files = ["data.yml.jinja", "preprocess.yml.jinja", "featurization.yml.jinja"]
        for jfile in training_files:
            rendered_content = self._render(
                template_name=jfile,
                context=context,
                env=train_env
            )

            target_file = self.training_dir / jfile.replace(".jinja", "")
            self._merge_rendered_actions_into_file(target_file, rendered_content)
            updated_files.append(target_file)

        ## Inference pipeline
        infer_env = Environment(loader=FileSystemLoader(self.templates_dir / "inference"))
        inference_files = ["data.yml.jinja", "preprocess.yml.jinja", "featurization.yml.jinja"]
        for jfile in inference_files:
            rendered_content = self._render(
                template_name=jfile,
                context=context,
                env=infer_env
            )

            target_file = self.inference_dir / jfile.replace(".jinja", "")
            self._merge_rendered_actions_into_file(target_file, rendered_content)
            updated_files.append(target_file)

        # ## Retraining pipeline
        # retrain_env = Environment(loader=FileSystemLoader(self.templates_dir / "retraining"))
        # retraining_files = ["data.yml.jinja", "preprocess.yml.jinja", "featurization.yml.jinja"]
        # for jfile in retraining_files:
        #     rendered_content = self._render(
        #         template_name=jfile,
        #         context=context,
        #         env=retrain_env
        #     )

        #     target_file = self.retraining_dir / jfile.replace(".jinja", "")
        #     self._merge_rendered_actions_into_file(target_file, rendered_content)
        #     updated_files.append(target_file)

        return updated_files

    def _render(self, template_name: str, context: dict, env: Environment) -> str:
        template = env.get_template(template_name)
        content = template.render(**context)
        return content

    def _merge_rendered_actions_into_file(self, existing_yml_path: Path, rendered_content: str) -> None:

        if not existing_yml_path.exists() or not existing_yml_path.read_text(encoding="utf-8").strip():
            raise ValueError(
                f"Expected existing YAML file at {existing_yml_path} with content, but it does not exist or is empty."
            )

        # Load existing YAML
        with existing_yml_path.open("r", encoding="utf-8") as f:
            existing_data = self.yaml.load(f)

        # Load rendered YAML from string
        rendered_data = self.yaml.load(StringIO(rendered_content))

        existing_actions = existing_data.get("actions", [])
        if existing_actions is None:
            existing_actions = []

        new_actions = rendered_data.get("actions", [])
        if new_actions is None:
            new_actions = []

        # Prevent duplicate actions
        existing_action_names = {action.get("name") for action in existing_actions}

        for action in new_actions:
            action_name = action.get("name")
            if action_name not in existing_action_names:
                existing_actions.append(action)

        existing_data["actions"] = existing_actions

        # Write back preserving YAML formatting
        with existing_yml_path.open("w", encoding="utf-8") as f:
            self.yaml.dump(existing_data, f)