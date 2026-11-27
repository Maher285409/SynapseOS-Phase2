import os
from deepface import DeepFace


class FaceEngine:

    def __init__(self, face_folder="faces/Maher1"):

        self.face_folder = "faces/Maher1"
        self.registered_faces = []

        if not os.path.exists(self.face_folder):
            raise RuntimeError(
                f"Face folder not found: {self.face_folder}"
            )

        for file in os.listdir(self.face_folder):

            if file.lower().endswith((".jpg", ".jpeg", ".png")):

                path = os.path.join(
                    self.face_folder,
                    file
                )

                self.registered_faces.append(path)

        print(
            f"[Face] Loaded {len(self.registered_faces)} "
            "registered face samples."
        )

        if not self.registered_faces:
            raise RuntimeError(
                "No registered face images found."
            )

    def recognize(self, frame):

        try:

            for registered_face in self.registered_faces:

                result = DeepFace.verify(
                    img1_path=registered_face,
                    img2_path=frame,
                    model_name="Facenet512",
                    detector_backend="opencv",
                    enforce_detection=False,
                    silent=True
                )

                if result["verified"]:
                    return True

            return False

        except Exception:

            return False