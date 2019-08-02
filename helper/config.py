import json


def read_configuration_from_file(config_path: str) -> dict:
    """
    Import configuration dictionary from JSON file
    :param config_path: path to configuration JSON file
    :return: configuration dictionary
    """
    with open(config_path) as f:
        config_content = f.read()
        return json.loads(config_content)