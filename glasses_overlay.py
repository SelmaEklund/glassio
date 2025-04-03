"""
import cv2
import numpy as np
import os

def overlay_glasses(image, landmarks, glasses_img_path):
    h, w, _ = image.shape
    coords = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks.landmark]

    left_eye = coords[33]
    right_eye = coords[263]
    nose = coords[168]

    eye_width = np.linalg.norm(np.array(right_eye) - np.array(left_eye))
    center = tuple(np.mean([left_eye, right_eye], axis=0).astype(int))
    angle = np.degrees(np.arctan2(right_eye[1] - left_eye[1], right_eye[0] - left_eye[0]))

    if not os.path.exists(glasses_img_path):
        raise FileNotFoundError(f"Missing glasses image: {glasses_img_path}")

    glasses = cv2.imread(glasses_img_path, cv2.IMREAD_UNCHANGED)
    if glasses is None or glasses.shape[2] != 4:
        raise ValueError("Invalid or non-transparent glasses image.")

    scale = eye_width / glasses.shape[1] * 1.8 #size
    new_w = int(glasses.shape[1] * scale)
    new_h = int(glasses.shape[0] * scale)
    resized = cv2.resize(glasses, (new_w, new_h), interpolation=cv2.INTER_AREA)

    M = cv2.getRotationMatrix2D((new_w // 2, new_h // 2), angle, 1)
    rotated = cv2.warpAffine(resized, M, (new_w, new_h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

    #placement on nose
    x, y = center[0] - new_w // 2, center[1] - new_h // 2 + int(0.2 * new_h)

    for i in range(new_h):
        for j in range(new_w):
            if 0 <= y + i < h and 0 <= x + j < w:
                alpha = rotated[i, j, 3] / 255.0
                image[y + i, x + j] = (1 - alpha) * image[y + i, x + j] + alpha * rotated[i, j, :3]

    return image
"""
import cv2
import numpy as np
import os

def generate_overlay_images(image_path: str, face_shape: str) -> list:
    # Define the paths for glasses images based on face shape
    shape_to_glasses = {
        "round": ["glasses/round/1.png", "glasses/round/2.png", "glasses/round/3.png"],
        "square": ["glasses/square/1.png", "glasses/square/2.png", "glasses/square/3.png"],
        "oval": ["glasses/oval/1.png", "glasses/oval/2.png", "glasses/oval/3.png"],
        "diamond": ["glasses/diamond/1.png", "glasses/diamond/2.png", "glasses/diamond/3.png"],
        "default": ["glasses/default/1.png", "glasses/default/2.png", "glasses/default/3.png"]
    }

    # Get the correct glasses paths based on face shape
    glasses_paths = shape_to_glasses.get(face_shape.lower(), shape_to_glasses["default"])
    images = []

    # Read the face image
    image = cv2.imread(image_path)
    h, w = image.shape[:2]
    center = (w // 2, h // 2)
    left_eye = (int(w * 0.35), int(h * 0.4))
    right_eye = (int(w * 0.65), int(h * 0.4))
    eye_width = right_eye[0] - left_eye[0]
    angle = np.degrees(np.arctan2(right_eye[1] - left_eye[1], right_eye[0] - left_eye[0]))

    # Loop through each glasses image path
    for glasses_img_path in glasses_paths:
        glasses = cv2.imread(glasses_img_path, cv2.IMREAD_UNCHANGED)

        # Skip if glasses image is invalid or doesn't have transparency (alpha channel)
        if glasses is None or glasses.shape[2] != 4:
            continue  # Skip invalid images

        # Calculate the size and apply scaling to fit the glasses to the user's face
        scale = eye_width / glasses.shape[1] * 1.8
        new_w = int(glasses.shape[1] * scale)
        new_h = int(glasses.shape[0] * scale)
        resized = cv2.resize(glasses, (new_w, new_h), interpolation=cv2.INTER_AREA)

        # Rotate glasses based on the angle of the user's face
        M = cv2.getRotationMatrix2D((new_w // 2, new_h // 2), angle, 1)
        rotated = cv2.warpAffine(resized, M, (new_w, new_h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

        # Calculate the position to place the glasses over the eyes
        x, y = center[0] - new_w // 2, center[1] - new_h // 2 + int(0.2 * new_h)
        blended = image.copy()

        # Overlay the glasses onto the face image
        for i in range(new_h):
            for j in range(new_w):
                if 0 <= y + i < h and 0 <= x + j < w:
                    alpha = rotated[i, j, 3] / 255.0
                    blended[y + i, x + j] = (1 - alpha) * blended[y + i, x + j] + alpha * rotated[i, j, :3]

        # Encode the blended image to PNG format and append as bytes
        _, buffer = cv2.imencode(".png", blended)
        images.append(buffer.tobytes())

    return images
