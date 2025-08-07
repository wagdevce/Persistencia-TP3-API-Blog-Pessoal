import logging
import yaml
import os


base_dir = os.path.dirname(os.path.abspath(__file__))


config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "config.yml"))


with open(config_path, "r") as f:
    config = yaml.safe_load(f)


log_level = getattr(logging, config["logging"]["level"].upper(), logging.INFO)


logging.basicConfig(
    level=log_level,
    format=config["logging"]["format"],
    handlers=[
        logging.FileHandler(config["logging"]["file"]),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
