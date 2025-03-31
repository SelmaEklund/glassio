import os
import cv2
import mediapipe as mp
import numpy as np
from sklearn import svm
from sklearn.preprocessing import StandardScaler
import joblib
from feature_engineer_mp import extract_geometric_features_from_mp

dataset_path = "faces/"
classes = os.listdir(dataset_path)

mp_face_mesh = mp.solutions.face_mesh

X = []
y = []

with mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True) as face_mesh:
    for label in classes:
        folder = os.path.join(dataset_path, label)
        if not os.path.isdir(folder):
            continue

        for filename in os.listdir(folder):
            if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                continue

            img_path = os.path.join(folder, filename)
            print(f"Reading: {img_path}")
            image = cv2.imread(img_path)
            if image is None:
                print(f"Failed to read image: {img_path}")
                continue

            results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            if not results.multi_face_landmarks:
                print(f"No face detected in {img_path}")
                continue

            landmarks = results.multi_face_landmarks[0]
            features = extract_geometric_features_from_mp(landmarks, image.shape)

            X.append(features)
            y.append(label)

print(f"Total samples collected: {len(X)}")

if len(X) == 0:
    print("No valid training data found. Exiting.")
else:
    print("Normalizing features and training SVM model (RBF kernel)...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    clf = svm.SVC(kernel='rbf')
    clf.fit(X_scaled, y)

    joblib.dump((clf, scaler), "model.pkl")
    print("Model saved as model.pkl")
