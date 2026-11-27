
import cv2
import os
import numpy as np


# =========================================================
# SETTINGS
# =========================================================

FACE_FOLDER = "faces/Maher1"

# OpenCV's built-in Haar Cascade face detector
CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"


# =========================================================
# LOAD FACE DETECTOR
# =========================================================

face_detector = cv2.CascadeClassifier(CASCADE_PATH)

if face_detector.empty():
    print("ERROR: Could not load face detector.")
    exit()


# =========================================================
# LOAD REGISTERED FACE SAMPLES
# =========================================================

registered_faces = []

if not os.path.exists(FACE_FOLDER):

    print(
        f"ERROR: Face folder not found: {FACE_FOLDER}"
    )

    exit()


for filename in os.listdir(FACE_FOLDER):

    if filename.lower().endswith(
        (".jpg", ".jpeg", ".png")
    ):

        path = os.path.join(
            FACE_FOLDER,
            filename
        )

        image = cv2.imread(path)

        if image is None:
            continue

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        faces = face_detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(80, 80)
        )

        if len(faces) > 0:

            # Use the largest detected face
            x, y, w, h = max(
                faces,
                key=lambda f: f[2] * f[3]
            )

            face = gray[
                y:y+h,
                x:x+w
            ]

            face = cv2.resize(
                face,
                (200, 200)
            )

            registered_faces.append(face)


print(
    f"[Face] Loaded {len(registered_faces)} "
    "face samples."
)


if len(registered_faces) == 0:

    print(
        "ERROR: No usable face samples found."
    )

    exit()


# =========================================================
# FACE COMPARISON
# =========================================================

def compare_face(face):

    """
    Compare the camera face against the
    registered face samples.

    Returns:
        True  = likely the registered user
        False = unknown
    """

    face = cv2.resize(
        face,
        (200, 200)
    )

    best_score = float("inf")

    for registered in registered_faces:

        # Histogram comparison
        hist1 = cv2.calcHist(
            [registered],
            [0],
            None,
            [256],
            [0, 256]
        )

        hist2 = cv2.calcHist(
            [face],
            [0],
            None,
            [256],
            [0, 256]
        )

        cv2.normalize(
            hist1,
            hist1
        )

        cv2.normalize(
            hist2,
            hist2
        )

        score = cv2.compareHist(
            hist1,
            hist2,
            cv2.HISTCMP_BHATTACHARYYA
        )

        best_score = min(
            best_score,
            score
        )


    # Lower score = more similar
    #
    # This is only a preliminary threshold.
    # We will calibrate it with your camera.

    return best_score < 0.35, best_score


# =========================================================
# CAMERA
# =========================================================

cap = cv2.VideoCapture(0)

if not cap.isOpened():

    print("ERROR: Could not open camera.")
    exit()


print("\n========================================")
print("       SYNAPSEOS FACE AUTH TEST")
print("========================================")
print("Look at the camera.")
print("Press Q to quit.\n")


# =========================================================
# MAIN LOOP
# =========================================================

while True:

    ok, frame = cap.read()

    if not ok:
        continue


    frame = cv2.flip(
        frame,
        1
    )


    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )


    faces = face_detector.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(100, 100)
    )


    status = "NO FACE"
    status_color = (180, 180, 180)


    if len(faces) > 0:

        # Choose largest face
        x, y, w, h = max(
            faces,
            key=lambda f: f[2] * f[3]
        )


        face = gray[
            y:y+h,
            x:x+w
        ]


        verified, score = compare_face(
            face
        )


        if verified:

            status = "VERIFIED"
            status_color = (0, 255, 0)

        else:

            status = "UNKNOWN"
            status_color = (0, 0, 255)


        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            status_color,
            2
        )


        cv2.putText(
            frame,
            f"FACE: {status}",
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            status_color,
            2
        )


        cv2.putText(
            frame,
            f"Score: {score:.3f}",
            (x, y + h + 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            1
        )


    else:

        cv2.putText(
            frame,
            "FACE: NO FACE",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            status_color,
            2
        )


    cv2.imshow(
        "SynapseOS - Face Authentication",
        frame
    )


    if (
        cv2.waitKey(1) & 0xFF
        == ord("q")
    ):

        break


# =========================================================
# CLEANUP
# =========================================================

cap.release()

cv2.destroyAllWindows()

print("\nFace authentication test closed.")
