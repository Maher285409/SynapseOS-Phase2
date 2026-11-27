import cv2
import os
import time

name = input("Enter your name: ").strip()

if not name:
    print("Name cannot be empty.")
    exit()

folder = os.path.join("faces", name)
os.makedirs(folder, exist_ok=True)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("ERROR: Could not open camera.")
    exit()

print("\nFace registration started.")
print("Look at the camera.")
print("We will capture 10 samples.")
print("Keep your face visible and slowly change your angle/lighting.")
print("Press Q to cancel.\n")

count = 0
last_capture = 0

while True:
    ret, frame = cap.read()

    if not ret:
        break

    frame = cv2.flip(frame, 1)

    # Display instructions
    cv2.putText(
        frame,
        f"Samples: {count}/10",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

    cv2.putText(
        frame,
        "Move slightly between captures",
        (20, 75),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        2
    )

    cv2.imshow("SynapseOS - Face Registration", frame)

    # Automatically capture every ~1 second
    if time.time() - last_capture >= 1.0:
        filename = os.path.join(folder, f"face_{count + 1}.jpg")
        cv2.imwrite(filename, frame)

        count += 1
        last_capture = time.time()

        print(f"Captured sample {count}/10")

    if count >= 10:
        break

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

print("\nRegistration complete!")
print(f"Saved {count} face samples in: {folder}")