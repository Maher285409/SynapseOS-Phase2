
import cv2
import os


# =========================================================
# SETTINGS
# =========================================================

MODEL_FILE = "face_model.yml"

CASCADE_PATH = (
    cv2.data.haarcascades
    + "haarcascade_frontalface_default.xml"
)


# =========================================================
# CHECK MODEL
# =========================================================

if not os.path.exists(MODEL_FILE):

    print(
        "ERROR: face_model.yml not found."
    )

    print(
        "Run train_face.py first."
    )

    exit()


# =========================================================
# LOAD FACE DETECTOR
# =========================================================

face_detector = cv2.CascadeClassifier(
    CASCADE_PATH
)

if face_detector.empty():

    print(
        "ERROR: Face detector failed."
    )

    exit()


# =========================================================
# LOAD LBPH MODEL
# =========================================================

recognizer = (
    cv2.face.LBPHFaceRecognizer_create()
)

recognizer.read(
    MODEL_FILE
)


# =========================================================
# CAMERA
# =========================================================

cap = cv2.VideoCapture(0)

if not cap.isOpened():

    print(
        "ERROR: Could not open camera."
    )

    exit()


print("\n========================================")
print("      SYNAPSEOS FACE RECOGNITION")
print("========================================")
print("Look at the camera.")
print("Try different lighting and angles.")
print("Press Q to quit.\n")


# =========================================================
# MAIN LOOP
# =========================================================

while True:

    success, frame = cap.read()

    if not success:
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


    for x, y, w, h in faces:

        face = gray[
            y:y+h,
            x:x+w
        ]


        face = cv2.resize(
            face,
            (200, 200)
        )


        # =============================================
        # PREDICT
        # =============================================

        label, confidence = recognizer.predict(
            face
        )


        # LBPH confidence:
        # Lower = more similar
        #
        # We start with 70 as a reasonable
        # preliminary threshold.

        if confidence < 70:

            status = "VERIFIED"
            status_color = (0, 255, 0)

        else:

            status = "UNKNOWN"
            status_color = (0, 0, 255)


        # =============================================
        # DRAW
        # =============================================

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
            (x, y - 12),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            status_color,
            2
        )


        cv2.putText(
            frame,
            f"Confidence: {confidence:.1f}",
            (x, y + h + 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            1
        )


    cv2.imshow(
        "SynapseOS - Face Recognition",
        frame
    )


    if cv2.waitKey(1) & 0xFF == ord("q"):

        break


# =========================================================
# CLEANUP
# =========================================================

cap.release()

cv2.destroyAllWindows()

print("\nFace recognition test closed.")

