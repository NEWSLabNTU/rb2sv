"""
rb2sv.py

Main class definition of the module rb2sv.
"""

import os
import json
from itertools import chain

import rosbag2_py

import config
import utils.util as util
from error import InvalidTopicError
from interfaces.image import ImageConverter
from utils.bidict_filtered import BidictWithNoneFilter
from interfaces.pose_stamped import PoseStampedConverter


class Rb2sv:

    __type_dict = {}
    __supported_image_types = [
        "sensor_msgs/msg/CompressedImage",
        "sensor_msgs/msg/Image",
    ]
    __supported_tag_types = ["geometry_msgs/msg/PoseStamped"]

    def __init__(self, args) -> None:
        self.quiet = args.quiet
        self.args = config.Rb2svConfig(args.config_file_path)

        # Prepare the reader
        self.reader = rosbag2_py.SequentialReader()
        storage_options = rosbag2_py.StorageOptions(
            uri=self.args.bag_path, storage_id="sqlite3"
        )
        converter_options = rosbag2_py.ConverterOptions(
            input_serialization_format="cdr", output_serialization_format="cdr"
        )
        self.reader.open(storage_options, converter_options)

        self.__check_topics_validity()

        # prompt the user to confirm
        util.prompt_confirm()

        # prepare interfaces converter
        self.image_converter = ImageConverter()
        self.pos_converter = PoseStampedConverter()

    def __check_topics_validity(self):
        """
        Check if there are more than one supported image topic in
        the rosbag.

        If there is not only one image topic and one tag topic, and
        if the user doesn't specify the topic he wants to convert and
        the corresponding tag topic, then we require the user to specify it clearly.
        """
        topics_and_types = self.reader.get_all_topics_and_types()
        topics_have_img_types = []
        topics_have_tag_types = []
        for topic in topics_and_types:
            self.__type_dict[topic.name] = topic.type
            if topic.type in self.__supported_image_types:
                topics_have_img_types.append(topic.name)
            if topic.type in self.__supported_tag_types:
                topics_have_tag_types.append(topic.name)

        print(
            "Found convertible topics having image types:",
            *topics_have_img_types if len(topics_have_img_types) > 0 else "None",
        )
        print(
            "Found convertible topics having tag types:",
            *topics_have_tag_types if len(topics_have_tag_types) > 0 else "None",
        )

        # if the user has provided topic-pair, check for validity
        assert self.args.topic_pairs is not None, "--topic-pairs must be provided"
        topic_pairs = BidictWithNoneFilter(
            {img_top: tag_top for (img_top, tag_top) in self.args.topic_pairs}
        )

        for img_topic, tag_topic in topic_pairs.items():
            if img_topic not in topics_have_img_types:
                raise InvalidTopicError(
                    f"{img_topic}'s message type is not a supported image type."
                )
            if tag_topic != "" and tag_topic not in topics_have_tag_types:
                raise InvalidTopicError(
                    f"{tag_topic}'s message type is not a supported tag type."
                )

        print("Topics with image type user specify:", *[t for t in topic_pairs.keys()])
        print(
            "Topics with tag type user specify:",
            *[t for t in topic_pairs.values()],
        )
        print()
        self.topic_pairs = topic_pairs
        return

    def __construct_project_structure(self):
        """
        Construct the directory structure based on supervisely format
        """
        topic_dirs = [t.strip("/").replace("/", "-") for t in self.topic_pairs.keys()]
        for topic in topic_dirs:
            os.makedirs(
                os.path.join(self.args.project_dir, topic, "ann"), exist_ok=True
            )
            os.makedirs(
                os.path.join(self.args.project_dir, topic, "img"), exist_ok=True
            )
            os.makedirs(
                os.path.join(self.args.project_dir, topic, "meta"), exist_ok=True
            )

    def __construct_project_meta(self):
        """
        Create the meta.json file for project's meta.
        """
        meta = {
            "classes": [],
            "tags": [
                {
                    "name": "PoseStamped",
                    "color": self.args.pose_tag_color,
                    "value_type": "any_string",
                }
            ],
            "projectType": self.args.project_type,
        }
        with open(os.path.join(self.args.project_dir, "meta.json"), "w") as f:
            json.dump(meta, f, indent=4)

    def read_into_project(self):
        """
        Dispatching function to store various msg types into project file
        by calling corresponding reading function
        """
        self.__construct_project_structure()
        self.__construct_project_meta()

        # contains all topics involved in the conversion process
        interested_topics = list(chain(*self.topic_pairs.items()))

        while self.reader.has_next():
            (topic_name, data, timestamp) = self.reader.read_next()
            if topic_name not in interested_topics:
                continue

            match self.__type_dict[topic_name]:
                case "sensor_msgs/msg/CompressedImage":
                    self.image_converter.convert(
                        (topic_name, data, timestamp), compressed=True
                    )
                case "sensor_msgs/msg/Image":
                    self.image_converter.convert(
                        (topic_name, data, timestamp), compressed=False
                    )
                case "geometry_msgs/msg/PoseStamped":
                    self.pos_converter.convert((topic_name, data, timestamp))
                case _:
                    pass

        print(f"Successfully convert the rosbag to {self.args.project_dir}")
