import json
import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
import os
from math import hypot

# Your helper function
def angle_between(a, b, c):
    ax, ay = a
    bx, by = b
    cx, cy = c
    v1 = (ax - bx, ay - by)
    v2 = (cx - bx, cy - by)
    dot = v1[0] * v2[0] + v1[1] * v2[1]
    mag1 = hypot(v1[0], v1[1])
    mag2 = hypot(v2[0], v2[1])
    if mag1 * mag2 == 0:
        return 0.0
    cosang = max(-1.0, min(1.0, dot / (mag1 * mag2)))
    return np.degrees(np.arccos(cosang))

# Setup MediaPipe
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)


# Process all splits: train, test, valid
splits = ['train', 'test', 'valid']
features = []  # Store [avg_rom, avg_velocity, weight_kg] per image

for split in splits:
    print(f"\nProcessing split: {split}")
    ann_path = f'Bicep-curl-1/{split}/_annotations.coco.json'
    img_folder = f'Bicep-curl-1/{split}'
    if not os.path.exists(ann_path):
        print(f"Annotation file not found: {ann_path}")
        continue
    with open(ann_path, 'r') as f:
        data = json.load(f)
    for img_info in data['images']:
        img_path = os.path.join(img_folder, img_info['file_name'])
        image = cv2.imread(img_path)
        if image is None:
            print(f"Skipping {img_path} - not found")
            continue
        h, w = image.shape[:2]
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pose.process(img_rgb)
        if results.pose_landmarks:
            lm = results.pose_landmarks.landmark
            def xy(idx): return (int(lm[idx].x * w), int(lm[idx].y * h))
            # MediaPipe indices: Left=11(Shoulder),13(Elbow),15(Wrist); Right=12,14,16
            l_shoulder = xy(11)
            l_elbow = xy(13)
            l_wrist = xy(15)
            r_shoulder = xy(12)
            r_elbow = xy(14)
            r_wrist = xy(16)
            # Compute angles (ROM proxy)
            left_rom = angle_between(l_shoulder, l_elbow, l_wrist)
            right_rom = angle_between(r_shoulder, r_elbow, r_wrist)
            avg_rom = (left_rom + right_rom) / 2 if left_rom > 0 and right_rom > 0 else 0
            # Simulate velocity (static images: use 0 or small value)
            avg_velocity = 0.1  # Placeholder; adjust later with real data
            # Manual weight label (review image to decide: e.g., strained pose = 15kg)
            weight_kg = 10  # Default; manually adjust or batch-label later
            features.append([avg_rom, avg_velocity, weight_kg])
            print(f"Feature extracted for {img_path}: avg_rom={avg_rom:.2f}, avg_velocity={avg_velocity}, weight_kg={weight_kg}")
        else:
            print(f"No pose detected in {img_path}")

print(f"\nTotal features extracted: {len(features)}")


# --- Update weight_kg in training_data.csv based on avg_rom thresholds ---

import_path = 'training_data.csv'
# Always write the extracted features to CSV, overwriting any existing file
df = pd.DataFrame(features, columns=['avg_rom', 'avg_velocity', 'weight_kg'])
df.to_csv(import_path, index=False)
print(f"Processed {len(features)} images. Saved to {import_path}!")

# Now update weight_kg column based on avg_rom thresholds
def assign_weight(avg_rom):
    if avg_rom < 60:
        return 15
    elif avg_rom > 90:
        return 5
    else:
        return 10
df['weight_kg'] = df['avg_rom'].apply(assign_weight)
df.to_csv(import_path, index=False)
print(f"Updated weight_kg in {import_path} based on avg_rom thresholds.")