import numpy as np

# Accepts MediaPipe landmarks and image shape
def extract_geometric_features_from_mp(landmarks, image_shape):
    h, w, _ = image_shape
    coords = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks.landmark]

    # Jaw width: landmark 234 to 454
    jaw_width = np.linalg.norm(np.array(coords[234]) - np.array(coords[454]))

    # Forehead estimation: distance from midpoint of eyebrows (65/295) to top forehead (10)
    brow_mid = np.mean([coords[65], coords[295]], axis=0)
    forehead_height = np.linalg.norm(np.array(coords[10]) - brow_mid)

    # Face height: chin (152) to forehead (10)
    face_height = np.linalg.norm(np.array(coords[10]) - np.array(coords[152]))

    # Width to height ratio
    ratio = jaw_width / face_height if face_height != 0 else 0

    # Chin angle: between points 152, 234, 454
    a = np.array(coords[234]) - np.array(coords[152])
    b = np.array(coords[454]) - np.array(coords[152])
    angle = np.arccos(np.clip(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)), -1.0, 1.0))

    return np.array([jaw_width, forehead_height, face_height, ratio, np.degrees(angle)])
