import os
import re

import yaml

import utils
from model.error import InvalidConfigError


class Rb2svConfig:
    required_args = ["bag_path", "topic_pairs", "project_type"]
    all_args = [
        "bag_path",
        "project_dir",
        "project_type",
        "topic_pairs",
        "pose_tag_color",
    ]

    def __init__(self, yaml_file_path: str) -> None:
        with open(yaml_file_path) as f:
            config = yaml.safe_load(f)

        for k, v in config.items():
            if k != "topic_pairs":
                v = str(v)
            setattr(self, k, v)

        self.__parse()

    def __parse(self):
        # Check if all required args are provided
        for p in self.required_args:
            if not hasattr(self, p):
                raise InvalidConfigError(f"args {p} is required.")

        # setting default values
        if not hasattr(self, "project_dir"):
            setattr(
                self, "project_dir", f"./{os.path.basename(self.bag_path)}-supervisely"
            )
        if not hasattr(self, "pose_tag_color"):
            setattr(self, "pose_tag_color", "#ED68A1")  # hot pink

        # check config validity and parse them
        if not os.path.exists(self.bag_path):
            raise InvalidConfigError(f"{self.bag_path} does not exist.")

        if os.path.exists(self.project_dir):
            print(f"WARN: The output directory {self.project_dir} already exists.")
            utils.prompt_confirm(default=False)

        self.project_type = self.project_type.lower()
        if self.project_type not in ("images", "videos", "point_clouds"):
            raise InvalidConfigError(
                f"Only accepts the following project type: ['images', 'videos', 'point_clouds']"
            )

        for i, pair in enumerate(self.topic_pairs):
            self.topic_pairs[i] = self.__parse_topic_tuple(pair)

        self.__is_hex_color(self.pose_tag_color)

    def __is_hex_color(self, value: str):
        # Regex for matching hex color codes (3 or 6 digits, with optional #)
        if not re.fullmatch(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$", value):
            raise InvalidConfigError(f"{value} is not a valid hex color code")

    def __parse_topic_tuple(self, value: str) -> tuple[str, str]:
        try:
            vals = value.strip("()").split(",")
            return tuple([t.strip() for t in vals])
        except ValueError:
            raise InvalidConfigError(
                f"topic-pairs must be in format (topicA-img-type, topicB-tag-type)"
            )
