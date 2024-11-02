# RB2SV
rb2sv is a tool for extracting data from ROS bags and converting it to the Supervisely format.

# Requirements
**Environments**<br>
1. Python **^3.10**
2. **ROS2** installed
3. [**Poetry**](https://python-poetry.org/docs/) installed

Install Python Package Dependencies with the following command:
```bash
poetry install
```

# Supported Topic Types
- **Image Type**
    - sensor_msgs/msg/Image
    - sensor_msgs/msg/CompressedImage

- **Tag Type**
    - geometry_msgs/msg/PoseStamped

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

See `examples/example_config.yaml` for configuration format.<br>

The output directory name is default to `./{rosbag-name}-supervisely`.<br>
The generated project structure will be like:
```
{rosbag-name}-supervisely/
├── meta.json
└── {topic-name-1}/
│   ├── ann/
│   │   ├── img1.jpeg.json
│   │   ├── img2.jpeg.json
│   │   ├── img3.jpeg.json
│   ... ...
│
│   ├── img/
│   │   ├── img1.jpeg
│   │   ├── img2.jpeg
│   │   ├── img3.jpeg
│   ... ...
│
│   └── meta/
├── {topic-name-2}/
├── {topic-name-3}/
...

└── {topic-name-N}/
```

## Options
- `-h`, `--help`: Show this help message and exit
- `-q`, `--quiet`: No logging during the conversion.
- `-c`, `--config-file-path`: Required. The tool configuration.