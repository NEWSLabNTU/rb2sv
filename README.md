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

# Usage
## Syntax
```bash
poetry run poe rb2sv [-h] -b BAG_PATH [-p PROJECT_DIR] [--project-type {images}] [-q] [--pose-tag-color POSE_TAG_COLOR]
```
e.g. To convert a rosbag into supervisely format:
```bash
poetry run poe rb2sv -b "/path/to/rosbag"
```
And the output directory name is default to `./{rosbag-name}-supervisely`.<br>
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
- `-b BAG_PATH`, `--bag-path BAG_PATH`: The path to the rosbag directory you want to convert.
- `-p PROJECT_DIR`, `--project-dir PROJECT_DIR`: The output directory of the converted data. The default is `./{rosbag-name}-supervisely`.
- `--project-type`: The project type of the supervisely dataset. Can be one of ['images', 'videos', 'point_clouds']. The default is 'images'.
- `-q`, `--quiet`: No logging during the conversion.
- `--pose-tag-color POSE_TAG_COLOR`: The hex color code of the pose tag. The default is '#ED68A1'(Hot Pink).
