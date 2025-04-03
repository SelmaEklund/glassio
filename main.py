from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from predict import predict_face_shape
from glasses_overlay import generate_overlay_images
import base64
import os

app = FastAPI()

# Allow access from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        # Save uploaded image to disk
        contents = await file.read()
        temp_path = "temp_input.jpg"
        with open(temp_path, "wb") as f:
            f.write(contents)

        # Predict face shape
        face_shape = predict_face_shape(temp_path)

        # Generate 3 overlays for that shape
        overlay_bytes = generate_overlay_images(temp_path, face_shape)

        # Convert overlays to base64
        base64_images = []
        for img_bytes in overlay_bytes:
            encoded = base64.b64encode(img_bytes).decode("utf-8")
            base64_images.append(encoded)

        # Return everything in one response
        return {
            "face_shape": face_shape,
            "images": base64_images
        }

    except Exception as e:
        return {"error": str(e)}



"""
import os
import cv2
from predict import predict_face_shape
from glasses_overlay import overlay_glasses
from glasses_recommend import recommend_glasses

print("Welcome to Glassio — Face Shape Identifier & Glasses Recommender")
print("Type the name of the face image you'd like to test (e.g., selma.jpeg)")
print("Type 'q' or 'quit' anytime to exit.\n")

while True:
    image_path = input("Enter face image filename: ").strip()

    if image_path.lower() in ['q', 'quit']:
        print("Exiting Glassio. Bye!")
        break

    if not os.path.exists(image_path):
        print(f"Image '{image_path}' not found.")
        continue

    try:
        # Step 1: Predict face shape
        face_shape = predict_face_shape(image_path)
        print(f"\nPredicted face shape: {face_shape}")

        # Step 2: Recommend glasses
        options = recommend_glasses(face_shape)
        print("\nRecommended glasses styles:")
        for i, rec in enumerate(options, 1):
            print(f"{i}. {rec}")
        print("4. Exit glasses preview")

        # Step 3: Load image and landmarks
        image = cv2.imread(image_path)
        landmarks = predict_face_shape(image_path, return_landmarks=True)

        while True:
            print("\nSelect glasses style:")
            print("1 - Style 1")
            print("2 - Style 2")
            print("3 - Style 3")
            print("4 - Go back and try a new face image")
            choice = input("Your choice: ").strip()

            if choice == '4':
                cv2.destroyAllWindows()
                print("\nBack to face image selection.\n")
                break

            if choice not in ['1', '2', '3']:
                print("Invalid choice. Choose 1, 2, 3, or 4.")
                continue

            glasses_path = f"glasses/{face_shape.lower()}/{choice}.png"
            if not os.path.exists(glasses_path):
                print(f"Glasses image not found: {glasses_path}")
                continue

            # Step 4: Overlay and show
            cv2.destroyAllWindows()  # Smooth transition by clearing previous display
            result = overlay_glasses(image.copy(), landmarks, glasses_path)
            cv2.imshow("With Glasses", result)
            cv2.waitKey(1)  # small delay to show image window

    except Exception as e:
        print(f"Error during prediction or overlay: {e}")
"""