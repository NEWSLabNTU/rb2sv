"""
rb2sv.py

Main class definition of the module rb2sv.
"""

import os
import json

import cv2
import numpy as np
import rosbag2_py
from rclpy.serialization import deserialize_message
from sensor_msgs.msg import Image, CompressedImage

from . import utils


class rb2sv:

    __type_dict = {}
    __supported_types = ["sensor_msgs/msg/CompressedImage", "sensor_msgs/msg/Image"]
    __convertible_topics = set()

    def __init__(self, bag_path: str, project_dir: str, logging=True) -> None:
        self.logging = logging
        self.project_dir = project_dir

        # Prepare the reader
        self.reader = rosbag2_py.SequentialReader()
        storage_options = rosbag2_py.StorageOptions(uri=bag_path, storage_id="sqlite3")
        converter_options = rosbag2_py.ConverterOptions(
            input_serialization_format="cdr", output_serialization_format="cdr"
        )
        self.reader.open(storage_options, converter_options)
        topic_filter = rosbag2_py.StorageFilter(topics=list(self.__convertible_topics))
        self.reader.set_filter(topic_filter)

        # Get all topics
        topics_and_types = self.reader.get_all_topics_and_types()
        self.__log("Topics and Message Types found:")
        for topic in topics_and_types:
            self.__log(f"- Topic: {topic.name}, Type: {topic.type}")
            self.__type_dict[topic.name] = topic.type
            if topic.type in self.__supported_types:
                self.__convertible_topics.add(topic.name)
        self.__log(
            "The messages of these topics will be converted:",
            *self.__convertible_topics,
        )

    def __log(self, *args, **kargs):
        if self.logging:
            print(*args, **kargs)

    def __construct_project_structure(self):
        """
        Construct the directory structure based on supervisely format
        """
        for topic in self.__convertible_topics:
            topic = topic.strip("/").replace("/", "-")
            os.makedirs(os.path.join(self.project_dir, topic, "ann"), exist_ok=True)
            os.makedirs(os.path.join(self.project_dir, topic, "img"), exist_ok=True)
            os.makedirs(os.path.join(self.project_dir, topic, "meta"), exist_ok=True)

    def __construct_project_meta(self):
        """
        Create the meta.json file for project's meta.
        """
        meta = {
            "classes": [],
            "tags": [
                {"name": "PoseStamped", "color": "#ED68A1", "value_type": "any_string"}
            ],
            "projectType": "images",
        }
        with open(os.path.join(self.project_dir, "meta.json"), "w") as f:
            json.dump(meta, f)

    def read_into_project(self):
        """
        Dispatching function to store various msg types into project file
        by calling corresponding reading function
        """
        self.__construct_project_structure()
        self.__construct_project_meta()

        while self.reader.has_next():
            (topic_name, data, timestamp) = self.reader.read_next()
            match self.__type_dict[topic_name]:
                case "sensor_msgs/msg/CompressedImage":
                    self.__read_images((topic_name, data, timestamp), compressed=True)
                case "sensor_msgs/msg/Image":
                    self.__read_images((topic_name, data, timestamp), compressed=False)
                case _:
                    pass

    def __read_images(self, record, compressed: bool):
        """
        Read messages of image type and create individual annotation json file.

        compressed=True for sensor_msgs/msg/CompressedImage,
        compressed=False for sensor_msgs/msg/Image
        """
        (topic_name, data, timestamp) = record

        img_name = str(timestamp) + ".jpeg"
        img_path = utils.construct_file_path(
            self.project_dir, topic_name, "img", img_name
        )
        self.__log(f"Transfering {img_path}")

        # Deserialize the data and store the image
        if compressed:
            deserialized_msg = deserialize_message(data, CompressedImage)
            img = cv2.imdecode(
                np.frombuffer(deserialized_msg.data, np.uint8), cv2.IMREAD_COLOR
            )
        else:
            deserialized_msg = deserialize_message(data, Image)
            img = np.frombuffer(deserialized_msg.data, np.uint8).reshape(
                deserialized_msg.height, deserialized_msg.width, -1
            )
        cv2.imwrite(img_path, img, [cv2.IMWRITE_JPEG_QUALITY, 100])

        # Prepare annotation file
        annotation = {
            "description": topic_name,
            "name": img_name,
            "size": {"width": img.shape[1], "height": img.shape[0]},
            "tags": [],
            "objects": [],
        }
        ann_path = utils.construct_file_path(
            self.project_dir, topic_name, "ann", img_name + ".json"
        )
        with open(ann_path, "w") as j:
            json.dump(annotation, j)
