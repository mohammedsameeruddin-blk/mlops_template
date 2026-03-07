from pathlib import Path
from typing import List, Optional
from benedict import benedict


class ProjectDiscovery:
    def __init__(self, project_path: Path):
        self.project_path = Path(project_path)
        self.src_path = self.project_path / "src"

    # Core project detection
    def get_project_root(self) -> Optional[Path]:
        """
        Returns src/<project_name> if valid, else None
        """
        if not self.src_path.exists():
            return None

        for d in self.src_path.iterdir():
            if (
                d.is_dir()
                and (d / "config.toml").exists()
                and (d / "pipeline_configs").exists()
            ):
                return d

        return None

    def is_valid_project(self) -> bool:
        return self.get_project_root() is not None

    # Dataset discovery
    def get_datasets(self) -> List[str]:
        project = self.get_project_root()
        if project is None:
            return []

        datasets = set()

        training_dir = project / "pipeline_configs" / "training"
        inference_dir = project / "pipeline_configs" / "inference"
        retraining_dir = project / "pipeline_configs" / "retraining"

        def collect_from_pipeline_dir(pipeline_dir: Path) -> None:
            for yml_file in pipeline_dir.glob("*.yml"):
                if yml_file.name == "data.yml":
                    try:
                        yml_data = benedict.from_yaml(str(yml_file))
                    except Exception:
                        continue

                    actions = yml_data.get("actions", [])
                    if not isinstance(actions, list):
                        continue

                    for action in actions:
                        if not isinstance(action, dict):
                            continue

                        dataset_name = str(action.get("name", "")).strip()
                        if dataset_name.endswith("_extraction"):
                            dataset_name = dataset_name[: -len("_extraction")]

                        if dataset_name:
                            datasets.add(dataset_name)
                else:
                    continue

        if training_dir.exists():
            collect_from_pipeline_dir(training_dir)

        if inference_dir.exists():
            collect_from_pipeline_dir(inference_dir)

        if retraining_dir.exists():
            collect_from_pipeline_dir(retraining_dir)

        return sorted(datasets)
    
    # Model discovery
    def get_models(self) -> List[str]:
        project_root = self.get_project_root()
        if project_root is None:
            return []

        models_dir = project_root / "models"
        if not models_dir.exists():
            return []

        models = []

        for d in models_dir.iterdir():
            if not d.is_dir():
                continue

            # minimal validity check
            if (d / "training").exists() and (d / "inference").exists():
                models.append(d.name)

        return sorted(models)

