"""
sv2rb.py

This program transform a supervisely-format folder to a ros2 bag. 
"""

import os
import cv2
from rclpy.node import Node
from rclpy.serialization import serialize_message
from cv_bridge import CvBridge
import rosbag2_py._storage
import rosbag2_py
from rosbag2_py import SequentialWriter, StorageOptions, ConverterOptions


class Sv2rb(Node):
    def __init__(self, image_folder: str, bag_path: str):
        super().__init__("image_folder_to_bag")

        # Initialize the writer
        self.writer = SequentialWriter()
        storage_options = StorageOptions(
            uri=bag_path, storage_id="sqlite3"  # Use 'mcap' for modern format
        )
        converter_options = ConverterOptions(
            input_serialization_format="cdr", output_serialization_format="cdr"
        )
        self.writer.open(storage_options, converter_options)

        # Register the topic
        topic_info = rosbag2_py._storage.TopicMetadata(
            name="/camera/image_raw",
            type="sensor_msgs/msg/Image",
            serialization_format="cdr",
        )
        self.writer.create_topic(topic_info)

        self.image_folder = image_folder
        self.bridge = CvBridge()

    def write_images_to_bag(self):
        # Get a sorted list of image files in the folder
        image_files = sorted(
            [
                f
                for f in os.listdir(self.image_folder)
                if f.endswith((".png", ".jpg", ".jpeg"))
            ]
        )

        if not image_files:
            self.get_logger().warn("No images found in the folder!")
            return

        for i, image_file in enumerate(image_files):
            # Full path to the image
            image_path = os.path.join(self.image_folder, image_file)

            # Load the image using OpenCV
            img = cv2.imread(image_path)

            if img is None:
                self.get_logger().warn(f"Failed to load image: {image_path}")
                continue

            # Convert OpenCV image to ROS 2 Image message
            image_msg = self.bridge.cv2_to_imgmsg(img, encoding="bgr8")

            sec, nanosec = self.get_clock().now().seconds_nanoseconds()
            image_msg.header.stamp.sec = sec
            image_msg.header.stamp.nanosec = nanosec

            # Write the message to the bag
            self.writer.write(
                "/camera/image_raw",
                serialize_message(image_msg),
                int(str(sec) + str(nanosec)),
            )
            self.get_logger().info(f"Wrote {image_file} to the bag")

    def close_bag(self):
        self.get_logger().info("Bag file successfully written and closed!")


# def main():
#     rclpy.init()
#     image_folder = "./out/out-compressed/img"  # Path to your images folder
#     bag_path = "output_bag"  # Name for your ROS 2 bag file

#     # Create the node
#     node = ImageFolderToBag(image_folder=image_folder, bag_path=bag_path)

#     try:
#         # Write images to bag
#         node.write_images_to_bag()
#     finally:
#         # Close the bag and shutdown ROS
#         node.close_bag()
#         rclpy.shutdown()
