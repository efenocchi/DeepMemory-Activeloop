# pylint: disable=locally-disabled, multiple-statements, fixme, line-too-long, missing-function-docstring

import yaml


def get_resources_file():
    with open("resources.yaml", "r", encoding="utf-8") as file:
        yaml_file = yaml.load(file, Loader=yaml.FullLoader)
    return yaml_file
