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
from interfaces.image import ImageConverter
from utils.bidict_filtered import BidictWithNoneFilter
from interfaces.pose_stamped import PoseStampedConverter
from interfaces.point_cloud_2 import PointCloudConverter


class Rb2sv:

    __type_dict = {}
    __support_types = {
        "content": {
            "images": ["sensor_msgs/msg/CompressedImage", "sensor_msgs/msg/Image"],
            "point_clouds": ["sensor_msgs/msg/PointCloud2"],
        },
        "tag": ["geometry_msgs/msg/PoseStamped"],
    }

    def __init__(self, args) -> None:
        self.args = config.Rb2svConfig(args.config_file_path, args.quiet)

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
        self.image_converter = ImageConverter(args=self.args)
        self.pos_converter = PoseStampedConverter(self.args, self.topic_pairs)
        self.pcd_converter = PointCloudConverter(self.args)

    def __check_topics_validity(self):
        """
        Check if there are more than one supported image topic in
        the rosbag.

        If there is not only one image topic and one tag topic, and
        if the user doesn't specify the topic he wants to convert and
        the corresponding tag topic, then we require the user to specify it clearly.
        """
        topics_and_types = self.reader.get_all_topics_and_types()
        for topic in topics_and_types:
            self.__type_dict[topic.name] = topic.type

        assert self.args.topic_pairs is not None, "topic-pairs must be provided"
        topic_pairs = BidictWithNoneFilter(
            {img_top: tag_top for (img_top, tag_top) in self.args.topic_pairs}
        )

        all_topics_in_bag = self.__type_dict.keys()
        for content_topic, tag_topic in topic_pairs.items():
            if self.args.project_type == "point_clouds":
                assert (
                    tag_topic == ""
                ), "Does not support tags for Point Cloud projects now."

            assert (
                content_topic in all_topics_in_bag
            ), f"{content_topic} not found in rosbag."
            assert (
                self.__type_dict[content_topic]
                in self.__support_types["content"][self.args.project_type]
            ), f"{self.__type_dict[content_topic]} is not a supported content type for {self.args.project_type} project"

            if tag_topic != "":
                assert (
                    tag_topic in all_topics_in_bag
                ), f"{tag_topic} not found in rosbag."
                assert (
                    self.__type_dict[tag_topic] in self.__support_types["tag"]
                ), f"{self.__type_dict[tag_topic]} is not a supported tag type"

        print("Content topics to be converted:", *[t for t in topic_pairs.keys()])
        print(
            "Tag topics to be converted:",
            *[t for t in topic_pairs.values()],
        )
        print()
        self.topic_pairs = topic_pairs
        return

    def __construct_project_structure(self):
        """
        Construct the directory structure based on supervisely format
        """
        project_dir = self.args.project_dir
        topic_dirs = [t.strip("/").replace("/", "-") for t in self.topic_pairs.keys()]

        if self.args.project_type == "images":
            for topic in topic_dirs:
                for d in ("ann", "img", "meta"):
                    os.makedirs(os.path.join(project_dir, topic, d), exist_ok=True)
        elif self.args.project_type == "point_clouds":
            for topic in topic_dirs:
                os.makedirs(
                    os.path.join(project_dir, topic, "pointcloud"), exist_ok=True
                )

    def __construct_project_meta(self):
        """
        Create the meta.json file for project's meta.
        """
        tags = []
        for t in self.topic_pairs.values():
            if t is not None:
                tags.append(
                    {
                        "name": t.split("/")[-1],
                        "color": util.random_color(),
                        "value_type": "any_string",
                    }
                )

        meta = {
            "classes": [],
            "tags": tags,
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
                case "sensor_msgs/msg/PointCloud2":
                    self.pcd_converter.convert((topic_name, data, timestamp))
                case _:
                    pass

        print(f"Successfully convert the rosbag to {self.args.project_dir}")
