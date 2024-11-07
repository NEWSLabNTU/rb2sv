import os
import re

import yaml

import utils.util as util
from error import InvalidConfigError


class Rb2svConfig:
    required_args = ["bag_path", "topic_pairs", "project_type"]
    all_args = [
        "bag_path",
        "project_dir",
        "project_type",
        "topic_pairs",
    ]

    def __init__(self, yaml_file_path: str, quiet: bool) -> None:
        self.quiet = quiet

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

        # check config validity and parse them
        if not os.path.exists(self.bag_path):
            raise InvalidConfigError(f"{self.bag_path} does not exist.")

        if os.path.exists(self.project_dir):
            print(f"WARN: The output directory {self.project_dir} already exists.")
            util.prompt_confirm(default=False)

        self.project_type = self.project_type.lower()
        if self.project_type not in ("images", "point_clouds"):
            raise InvalidConfigError(
                f"Only accepts the following project type: ['images', 'point_clouds']"
            )

        for i, pair in enumerate(self.topic_pairs):
            self.topic_pairs[i] = self.__parse_topic_tuple(pair)

    def __parse_topic_tuple(self, value: str) -> tuple[str, str]:
        vals = value.strip("()").split(",")
        assert (
            len(vals) == 2
        ), "topic-pairs must be in format (topicA-content-type, topicB-tag-type), \
or (topicA-content-type,) if no tag topics are going to be converted."
        return tuple([t.strip() for t in vals])
