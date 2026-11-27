import cv2
import os
import json
import numpy as np

# ==========================================
# SETTINGS
# ==========================================

FACE_FOLDER = "faces"
MODEL_FILE = "face_model.yml"
LABEL_FILE = "face_labels.json"

CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"

# ==========================================
# FACE DETECTOR
# ==========================================

face_detector = cv2.CascadeClassifier(CASCADE_PATH)

if face_detector.empty():
    print("ERROR: Could not load face detector.")
    exit()

# ==========================================
# CHECK FOLDERS
# ==========================================

if not os.path.isdir(FACE_FOLDER):
    print("ERROR: faces folder not found.")
    exit()

faces = []
labels = []
label_map = {}

print("\n========================================")
print("       SYNAPSEOS FACE TRAINING")
print("========================================\n")

members = sorted(
    name
    for name in os.listdir(FACE_FOLDER)
    if os.path.isdir(os.path.join(FACE_FOLDER, name))
)

if not members:
    print("ERROR: No member folders found.")
    exit()

# ==========================================
# LOAD ALL MEMBERS' PHOTOS
# ==========================================

for label, member_name in enumerate(members, start=1):

    member_folder = os.path.join(FACE_FOLDER, member_name)
    label_map[str(label)] = member_name

    member_count = 0

    print(f"\nProcessing: {member_name}")

    for filename in os.listdir(member_folder):

        if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        path = os.path.join(member_folder, filename)
        image = cv2.imread(path)

        if image is None:
            print(f"[SKIP] Could not read: {filename}")
            continue

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        detected = face_detector.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80)
        )

        if len(detected) == 0:
            print(f"[SKIP] No face found: {filename}")
            continue

        # Select the largest detected face
        x, y, w, h = max(detected, key=lambda face: face[2] * face[3])

        face = gray[y : y + h, x : x + w]
        face = cv2.resize(face, (200, 200))

        faces.append(face)
        labels.append(label)

        member_count += 1
        print(f"[OK] {filename}")

    print(f"Samples for {member_name}: {member_count}")

    if member_count == 0:
        print(f"\nERROR: No usable samples for {member_name}.")
        print("Training stopped.")
        exit()

# ==========================================
# TRAIN MODEL
# ==========================================

if len(faces) == 0:
    print("ERROR: No usable face images found.")
    exit()

print(f"\nTraining with {len(faces)} samples...")

recognizer = cv2.face.LBPHFaceRecognizer_create(
    radius=1, neighbors=8, grid_x=8, grid_y=8
)

recognizer.train(faces, np.array(labels))
recognizer.write(MODEL_FILE)

# ==========================================
# SAVE MEMBER NAMES
# ==========================================

with open(LABEL_FILE, "w", encoding="utf-8") as file:
    json.dump(label_map, file, indent=4)

# ==========================================
# COMPLETION
# ==========================================

print("\n========================================")
print("FACE MODEL TRAINED SUCCESSFULLY!")
print(f"Total samples: {len(faces)}")
print(f"Registered members: {len(label_map)}")
print(f"Model saved: {MODEL_FILE}")
print(f"Names saved: {LABEL_FILE}")
print("========================================\n")

for label, name in label_map.items():
    print(f"Label {label}: {name}")
