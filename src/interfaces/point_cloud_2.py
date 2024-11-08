import os
import json
from pathlib import Path
from collections import defaultdict

import numpy as np
import open3d as o3d
from sensor_msgs_py import point_cloud2
from sensor_msgs.msg import PointCloud2
from rclpy.serialization import deserialize_message

import utils.util as util
from interfaces.base_converter import BaseConverter


class PointCloudConverter(BaseConverter):
    def __init__(self, args) -> None:
        self.frame_pcd_map_dict = defaultdict(dict)
        self.frame_pcd_map_cnt = defaultdict(int)
        super().__init__(args)

    def convert(self, record):
        """
        Convert the sensor_msgs/msg/PointCloud2 message type to .pcd file

        record: a single entry obtained from SequentialReader.read_next()
        """
        (topic_name, data, timestamp) = record
        deserialized_msg = deserialize_message(data, PointCloud2)
        pcd_name = (
            str(deserialized_msg.header.stamp.sec)
            + "-"
            + str(deserialized_msg.header.stamp.nanosec)
            + ".pcd"
        )
        pcd_path = self.construct_pcd_path(topic_name, pcd_name)
        self.log(f"Transfering {pcd_path}")

        # record to frame_pointcloud_map
        self.frame_pcd_map_dict[topic_name][
            str(self.frame_pcd_map_cnt[topic_name])
        ] = pcd_name
        self.frame_pcd_map_cnt[topic_name] += 1

        cloud_points = point_cloud2.read_points(
            deserialized_msg, field_names=["x", "y", "z"], skip_nans=True
        ).tolist()

        # type should be float64; otherwise o3d would not run successfully
        cloud_np = np.array(cloud_points, dtype=np.float64)
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(cloud_np)
        # o3d.visualization.draw_geometries([pcd])

        o3d.io.write_point_cloud(pcd_path, pcd)

    def construct_pcd_path(self, topic_name: str, file_name: str):
        """
        Construct the path to the point cloud file
        """
        topic_name = util.parse_topic_name(topic_name)
        return os.path.join(self.args.project_dir, topic_name, "pointcloud", file_name)

    def write_frame_pcd_mapjson(self, topic_name: str):
        json_path = (
            Path(self.args.project_dir)
            / util.parse_topic_name(topic_name)
            / "frame_pointcloud_map.json"
        )
        with open(json_path, "w") as f:
            json.dump(self.frame_pcd_map_dict[topic_name], f, indent=4)
