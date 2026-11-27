import cv2
from deepface import DeepFace
import os

# ─────────────────────────────────────────────
# CHANGE THIS TO YOUR FOLDER NAME
# ─────────────────────────────────────────────
FACE_FOLDER = "faces/Maher1"

# Get all registered face images
registered_faces = []

for file in os.listdir(FACE_FOLDER):
    if file.lower().endswith((".jpg", ".jpeg", ".png")):
        registered_faces.append(
            os.path.join(FACE_FOLDER, file)
        )

if not registered_faces:
    print("ERROR: No registered face images found.")
    exit()

print(f"Found {len(registered_faces)} registered face images.")

# ─────────────────────────────────────────────
# CAMERA
# ─────────────────────────────────────────────
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Could not open camera.")
    exit()

print("\nSynapseOS Face Authentication")
print("Look at the camera.")
print("Press Q to quit.\n")

while True:

    ret, frame = cap.read()

    if not ret:
        break

    frame = cv2.flip(frame, 1)

    status = "CHECKING..."

    try:

        # Assume unknown until a match is found
        verified = False

        # Compare camera image with every registered image
        for registered_face in registered_faces:

            result = DeepFace.verify(
                img1_path=registered_face,
                img2_path=frame,
                model_name="Facenet512",
                enforce_detection=False
            )

            if result["verified"]:
                verified = True
                break

        if verified:
            status = "VERIFIED"
        else:
            status = "UNKNOWN"

    except Exception as e:

        status = "FACE ERROR"

    # ─────────────────────────────────────────
    # DISPLAY STATUS
    # ─────────────────────────────────────────

    if status == "VERIFIED":
        color = (0, 255, 0)

    elif status == "UNKNOWN":
        color = (0, 0, 255)

    else:
        color = (0, 255, 255)

    cv2.putText(
        frame,
        f"FACE: {status}",
        (20, 45),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        color,
        2
    )

    cv2.putText(
        frame,
        "Press Q to quit",
        (20, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )

    cv2.imshow(
        "SynapseOS - Face Authentication",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()