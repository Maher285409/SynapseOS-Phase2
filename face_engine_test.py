import cv2
from face_engine import FaceEngine


# Create face recognition engine
face = FaceEngine("faces/Maher1")

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Camera could not be opened.")
    exit()

print("\nFace Engine Test")
print("Look at the camera.")
print("Press Q to quit.\n")


while True:

    ret, frame = cap.read()

    if not ret:
        break

    frame = cv2.flip(frame, 1)

    # Check face
    recognized = face.recognize(frame)

    if recognized:

        status = "VERIFIED"
        color = (0, 255, 0)

    else:

        status = "UNKNOWN"
        color = (0, 0, 255)

    cv2.putText(
        frame,
        f"FACE: {status}",
        (20, 45),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        color,
        2
    )

    cv2.imshow(
        "SynapseOS - Face Engine Test",
        frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


cap.release()
cv2.destroyAllWindows()