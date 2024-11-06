import json

from geometry_msgs.msg import PoseStamped
from rclpy.serialization import deserialize_message

from utils import util


class PoseStampedConverter:
    def __init__(self) -> None:
        self.prev_img_name = ""

    def convert(self, record):
        """
        Read msgs of geometry_msgs/msg/PoseStamped type and convert them to the tag of
        the corresponding image.

        record: a single entry obtained from SequentialReader.read_next()
        """
        (topic_name, data, timestamp) = record
        deserialized_msg = deserialize_message(data, PoseStamped)
        img_name = (
            str(deserialized_msg.header.stamp.sec)
            + "-"
            + str(deserialized_msg.header.stamp.nanosec)
            + ".jpeg"
        )
        if img_name == self.prev_img_name:
            return
        self.prev_img_name = img_name

        ann_path = util.construct_img_path(
            self.args.project_dir,
            self.topic_pairs.inv_filtered[topic_name],
            "ann",
            img_name + ".json",
        )

        px = util.scientific_to_decimal(deserialized_msg.pose.position.x)
        py = util.scientific_to_decimal(deserialized_msg.pose.position.y)
        pz = util.scientific_to_decimal(deserialized_msg.pose.position.z)
        ox = util.scientific_to_decimal(deserialized_msg.pose.orientation.x)
        oy = util.scientific_to_decimal(deserialized_msg.pose.orientation.y)
        oz = util.scientific_to_decimal(deserialized_msg.pose.orientation.z)
        ow = util.scientific_to_decimal(deserialized_msg.pose.orientation.w)
        tag = {
            "name": "PoseStamped",
            "value": f"({px}, {py}, {pz}, {ox}, {oy}, {oz}, {ow})",
        }

        with open(ann_path, "r+") as f:
            ann = json.load(f)
            assert "tags" in ann, f"Annotation file {ann_path} is mal-formed."
            ann["tags"].append(tag)

            f.seek(0)
            json.dump(ann, f, indent=4)
            f.truncate()
