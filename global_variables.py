# pylint: disable=locally-disabled, multiple-statements, fixme, line-too-long, missing-function-docstring

from utils import get_resources_file


TYPE_LEGAL = "legal"
TYPE_FINANCE = "finance"
TYPE_BIOMEDICAL = "biomedical"

YAML_FILE = get_resources_file()
HUB_NAME = YAML_FILE["user_info"]["hub"]
TRAINED_CORPUS = None
DB_NAME = None
OUTPUT_TEXT_DEEP_MEMORY = None
OUTPUT_TEXT_WITHOUT_DEEP_MEMORY = None
DATASET_NAME_CHOSEN = None
