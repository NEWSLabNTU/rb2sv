import os
import re
import argparse

import utils


class Rb2svConfig:

    def __init__(self) -> None:
        parser = argparse.ArgumentParser(description="Configuration of rb2sv")

        # path to the rosbag to be converted
        parser.add_argument(
            "-b",
            "--bag-path",
            type=str,
            required=True,
            help="The path to the rosbag directory you want to convert.",
        )

        # path to the project(output) directory, default: ./{bag name}-supervisely
        parser.add_argument(
            "-p",
            "--project-dir",
            type=str,
            help="The output directory of the converted data.",
        )

        # project type
        parser.add_argument(
            "--project-type",
            type=str,
            choices=["images"],
            default="images",
            help="The project type of the supervisely dataset. Can be one of ['images', 'videos', 'point_clouds'].",
        )

        # logging or not
        parser.add_argument(
            "-q",
            "--quiet",
            action="store_true",
            help="No logging during the conversion.",
        )

        # color for pose tag
        parser.add_argument(
            "--pose-tag-color",
            type=self.__is_hex_color,
            default="#ED68A1",
            help="The hex color code of the pose tag.",
        )

        self.parser = parser

    def parse(self):
        args = self.parser.parse_args()
        if args.project_dir is None:
            args.project_dir = f"./{os.path.basename(args.bag_path)}-supervisely"
        self.args = args

        self.__check_config()
        return args

    def __is_hex_color(self, value: str) -> str:
        # Regex for matching hex color codes (3 or 6 digits, with optional #)
        if not re.fullmatch(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$", value):
            raise argparse.ArgumentTypeError(f"{value} is not a valid hex color code")
        return value

    def __check_config(self):
        """
        Check the validity of the configuration.
        """
        # check if the output directory exists
        if os.path.exists(self.args.project_dir):
            print(f"WARN: The output directory {self.args.project_dir} already exists.")
            utils.prompt_confirm(default=False)
