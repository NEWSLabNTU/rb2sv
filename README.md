# RB2SV
rb2sv is a tool for extracting data from ROS bags and converting it to the Supervisely format.

## Support
rb2sv now supports converting a ros2 bag to the following project types with message types listed below:
- Supervisely **images** project type
    - `sensor_msgs/msg/Image `
    - `sensor_msgs/msg/CompressedImage `
- Supervisely **point_cloud_episodes** project type
    - `geometry_msgs/msg/PointCloud2`

For **images** project type, the following message type can be converted to tags:
- `sensor_msgs/msg/PoseStamped`

However, for **point_cloud_episodes** project type, rb2sv does not support adding tags currently.


# Requirements
**Environments**<br>
1. Python **^3.10**
2. **ROS2** installed
3. [**Poetry**](https://python-poetry.org/docs/) installed

Install Python package dependencies with the following command:
```bash
poetry install
```

# Usage
Clone the repo.
```bash
git clone https://github.com/NEWSLabNTU/rb2sv.git
cd rb2sv
```
**Source** the ROS2 setup script before you start.
```bash
source /opt/ros/$ROS_DISTRO/setup.bash
```

## Syntax
```bash
poetry run poe rb2sv [-h] [-q] -c TOOL_CONFIG.yaml
# e.g. poetry run poe rb2sv -c ./examples/example_config.yaml
```
- `-c`, `--config-file-path`: Required. The path to the configuration file.
- `-q`, `--quiet`: No logging during the conversion.
- `-h`, `--help`: Show this help message and exit

### Format for the configuration file
The config file should be a yaml file with following keys:
- `bag_path`: Required. The path to the ros2 bag directory you want to convert.
- `project_dir`: Optional. The output directory.
- `project_type`: Required. Supports only `images` or `point_cloud_episodes` now.
- `topic_pairs`: Required. An array of pairs of `(content-topic, tag-topic)` to be converted.

See [example_config.yaml](examples/example_config.yaml) for example configuration.<br>

The output directory name is default to `./{rosbag-name}-supervisely`. Each topic specified in the configuration yaml file would be treated as a dataset in the converted supervisely project.
