import toml
from importlib import resources
from benedict import benedict
from pathlib import Path
from jinja2 import Template


def load_project_config(
    project_name, env_name: str, which_file: str = "config.toml"
) -> dict:
    with resources.open_text(f"{project_name}", which_file) as fp:
        config = toml.load(fp)
    return config.get(env_name, {})


def render_yaml_from_jinja(yml_template_path: Path, context: dict) -> dict:
    content = yml_template_path.read_text(encoding="utf-8")
    rendered = Template(content).render(env=context)
    rendered = rendered.replace("\t", "  ")  # remove tabs, as YAML doesn't support them
    return benedict.from_yaml(rendered)


def load_task_config(
    project_name: str, model_name: str, stage_name: str, env_context: dict, which_file: str
) -> dict:
    # Read and render the Jinja-based YAML using env
    if which_file.startswith("start") or which_file.startswith("end"):
        stage_name = "common"
    yaml_path = resources.files(
        f"{project_name}.models.{model_name}.configs.{stage_name}"
    ) / which_file
    rendered_yaml_dict = render_yaml_from_jinja(yaml_path, context=env_context)
    return rendered_yaml_dict
