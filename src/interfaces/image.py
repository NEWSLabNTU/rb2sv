import json

import cv2
import numpy as np
from sensor_msgs.msg import Image, CompressedImage
from rclpy.serialization import deserialize_message

import utils.util as util
from interfaces.base_converter import BaseConverter


class ImageConverter(BaseConverter):
    def __init__(self, args) -> None:
        super().__init__(args)

    def convert(self, record, compressed: bool):
        """
        Read messages of image type and create individual annotation json file.

        record: a single entry obtained from SequentialReader.read_next()
        compressed=True for sensor_msgs/msg/CompressedImage,
        compressed=False for sensor_msgs/msg/Image
        """
        (topic_name, data, timestamp) = record

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

        img_name = (
            str(deserialized_msg.header.stamp.sec)
            + "-"
            + str(deserialized_msg.header.stamp.nanosec)
            + ".jpeg"
        )
        img_path = self.construct_img_path(topic_name, "img", img_name)
        self.log(f"Transfering {img_path}")
        cv2.imwrite(img_path, img, [cv2.IMWRITE_JPEG_QUALITY, 100])

        # Prepare annotation file
        annotation = {
            "description": topic_name,
            "name": img_name,
            "size": {"width": img.shape[1], "height": img.shape[0]},
            "tags": [],
            "objects": [],
        }
        ann_path = self.construct_img_path(topic_name, "ann", img_name + ".json")
        with open(ann_path, "w") as j:
            json.dump(annotation, j, indent=4)

    def construct_img_path(self, topic_name: str, file_type: str, file_name: str):
        """
        Construct the path to store the image
        """
        assert file_type in [
            "ann",
            "img",
            "meta",
        ], "file type should be one of ['ann', 'img', 'meta']"

        topic_name = util.parse_topic_name(topic_name)
        return self.args.project_dir / topic_name / file_type / file_name
