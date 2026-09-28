from pathlib import Path
from ruamel.yaml import YAML


class DatasetFileDegenerator:
    def __init__(self, project_root: Path):
        """
        project_root = src/<project_name>
        """
        self.project_root = project_root
        self.training_dir = project_root / "pipeline_configs" / "training"
        self.inference_dir = project_root / "pipeline_configs" / "inference"
        self.retraining_dir = project_root / "pipeline_configs" / "retraining"

        self.project_name = project_root.name

        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.indent(mapping=2, sequence=4, offset=2)
        self.yaml.width = 4096

    def degenerate(self, dataset_name: str) -> list[Path]:
        updated_files: list[Path] = []

        action_files = {
            "data.yml": f"{dataset_name}_extraction",
            "preprocess.yml": f"{dataset_name}_preprocessing",
            "featurization.yml": f"{dataset_name}_featurization",
        }

        pipelines = [
            (self.training_dir, "splitter.yml"),
            (self.inference_dir, "prepare_input.yml"),
            (self.retraining_dir, "splitter.yml"),
        ]

        for pipeline_dir, features_file in pipelines:
            for yml_file, action_name in action_files.items():
                path = pipeline_dir / yml_file
                if path.exists():
                    self._remove_action_from_file(path, action_name)
                    updated_files.append(path)

            path = pipeline_dir / features_file
            if path.exists():
                self._remove_feature_from_file(path, dataset_name)
                updated_files.append(path)

        return updated_files

    def _remove_action_from_file(self, yml_path: Path, action_name: str) -> None:
        with yml_path.open("r", encoding="utf-8") as f:
            data = self.yaml.load(f)

        actions = data.get("actions") or []
        data["actions"] = [a for a in actions if a.get("name") != action_name]

        with yml_path.open("w", encoding="utf-8") as f:
            self.yaml.dump(data, f)

    def _remove_feature_from_file(self, yml_path: Path, dataset_name: str) -> None:
        with yml_path.open("r", encoding="utf-8") as f:
            data = self.yaml.load(f)

        actions = data.get("actions") or []
        if not actions:
            return

        features = (
            actions[0]
            .get("functions", {})
            .get("kwargs", {})
            .get("inputs", {})
            .get("databricks_table", {})
            .get("features", {})
        )

        if features and dataset_name in features:
            del features[dataset_name]

        with yml_path.open("w", encoding="utf-8") as f:
            self.yaml.dump(data, f)
