from roboflow import Roboflow
rf = Roboflow(api_key="7KJd5zCuK5XRxFMfXlRv")
project = rf.workspace("gym-exercise-correction").project("bicep-curl")
dataset = project.version(1).download("coco")  # Use "coco" instead of "coco-keypoints"