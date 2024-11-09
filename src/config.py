from pathlib import Path

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
        self.raw_config = config

        # Check if all required args are provided
        for p in self.required_args:
            if p not in config.keys():
                raise InvalidConfigError(f"args {p} is required.")

        self.__parse()

    def __parse(self):
        self.bag_path = Path(self.raw_config["bag_path"])
        self.project_type = str(self.raw_config["project_type"])
        self.topic_pairs = self.raw_config["topic_pairs"]
        self.project_dir = (
            Path(self.raw_config["project_dir"])
            if "project_dir" in self.raw_config.keys()
            else Path(f"./{self.bag_path.name}-supervisely")
        )

        # check config validity and parse them
        if not self.bag_path.exists():
            raise InvalidConfigError(f"{self.bag_path} does not exist.")

        if self.project_dir.exists():
            print(f"WARN: The output directory {self.project_dir} already exists.")
            util.prompt_confirm(default=False)

        self.project_type = self.project_type.lower()
        if self.project_type not in ("images", "point_cloud_episodes"):
            raise InvalidConfigError(
                f"Only accepts the following project type: ['images', 'point_cloud_episodes']"
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
