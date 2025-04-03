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
