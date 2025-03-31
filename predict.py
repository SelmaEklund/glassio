import cv2
import mediapipe as mp
import joblib
from feature_engineer_mp import extract_geometric_features_from_mp

mp_face_mesh = mp.solutions.face_mesh

def predict_face_shape(image_path, return_landmarks=False):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Could not load image at " + image_path)

    with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True) as face_mesh:
        results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        if not results.multi_face_landmarks:
            raise ValueError("No face detected in the image.")

        landmarks = results.multi_face_landmarks[0]
        features = extract_geometric_features_from_mp(landmarks, image.shape)

    model, scaler = joblib.load("model.pkl")
    features_scaled = scaler.transform([features])
    prediction = model.predict(features_scaled)[0]

    if return_landmarks:
        return landmarks
    return prediction
