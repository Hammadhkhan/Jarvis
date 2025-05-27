import cv2
import numpy as np
from PIL import Image
import os

SAMPLES_DIR = 'backend/auth/samples/'
TRAINER_DIR = 'backend/auth/trainer/'
TRAINER_FILE = os.path.join(TRAINER_DIR, 'trainer.yml')
CLASSIFIER_PATH = 'backend/auth/haarcascade_frontalface_default.xml' # Needed for get_images_and_labels

def get_images_and_labels(path, detector):
    imagePaths = [os.path.join(path, f) for f in os.listdir(path) if not f.startswith('.')] # Ignore hidden files
    faceSamples = []
    ids = []
    print(f"Found {len(imagePaths)} images in {path}.")

    for imagePath in imagePaths:
        try:
            gray_img = Image.open(imagePath).convert('L')  # convert it to grayscale
            img_arr = np.array(gray_img, 'uint8')  # creating an array

            # Correctly extract ID, assuming format like face.ID.sampleNum.jpg
            filename = os.path.split(imagePath)[-1]
            parts = filename.split(".")
            if len(parts) < 3:
                print(f"Warning: Skipping file {filename} due to unexpected filename format.")
                continue 
            
            id_str = parts[1]
            if not id_str.isdigit():
                print(f"Warning: Skipping file {filename}, expected numeric ID but got {id_str}.")
                continue
            
            id = int(id_str)
            
            # It's generally better to use the already processed images (cropped faces)
            # rather than running detectMultiScale again here if samples are pre-cropped.
            # However, the original script runs detectMultiScale, so we replicate that.
            # If samples are already cropped faces, this detector step might be redundant or only serve as validation.
            faces = detector.detectMultiScale(img_arr)

            for (x, y, w, h) in faces:
                faceSamples.append(img_arr[y:y+h, x:x+w])
                ids.append(id)
        except Exception as e:
            print(f"Error processing image {imagePath}: {e}")

    if not faceSamples:
        print("No face samples found or processed. Check image paths and content.")
    return faceSamples, ids

def train_face_model():
    print("Initializing face model training...")

    if not os.path.exists(CLASSIFIER_PATH):
        print(f"Error: Haar Cascade classifier not found at {CLASSIFIER_PATH}")
        return False
    
    detector = cv2.CascadeClassifier(CLASSIFIER_PATH)
    recognizer = cv2.face.LBPHFaceRecognizer_create()

    print(f"Fetching images and labels from {SAMPLES_DIR}...")
    if not os.path.exists(SAMPLES_DIR) or not os.listdir(SAMPLES_DIR):
        print(f"Error: Samples directory {SAMPLES_DIR} is empty or does not exist.")
        return False
        
    faces, ids = get_images_and_labels(SAMPLES_DIR, detector)

    if not faces or not ids:
        print("No faces found to train. Aborting training.")
        return False
    
    print(f"Training model with {len(faces)} face samples...")
    try:
        recognizer.train(faces, np.array(ids))
        
        # Ensure trainer directory exists
        os.makedirs(TRAINER_DIR, exist_ok=True)
        recognizer.write(TRAINER_FILE)
        print(f"Model trained and saved to {TRAINER_FILE}")
        return True
    except Exception as e:
        print(f"Error during model training or saving: {e}")
        return False

if __name__ == '__main__':
    # Example of how to run (for testing this script directly)
    print("Attempting to train face model directly...")
    # Adjust paths if running directly from backend/auth
    # This direct run part is mostly for testing the script itself.
    current_dir = os.getcwd()
    if current_dir.endswith(os.path.join('backend', 'auth')):
        print("INFO: [Direct Run] Adjusting paths for direct execution from backend/auth.")
        project_root_from_direct_run = os.path.dirname(os.path.dirname(current_dir))
        
        global CLASSIFIER_PATH, SAMPLES_DIR, TRAINER_DIR, TRAINER_FILE
        CLASSIFIER_PATH = os.path.join(project_root_from_direct_run, 'backend', 'auth', 'haarcascade_frontalface_default.xml')
        SAMPLES_DIR = os.path.join(project_root_from_direct_run, 'backend', 'auth', 'samples')
        TRAINER_DIR = os.path.join(project_root_from_direct_run, 'backend', 'auth', 'trainer')
        TRAINER_FILE = os.path.join(TRAINER_DIR, 'trainer.yml')
        print(f"DEBUG: [Direct Run] Adjusted CLASSIFIER_PATH: {CLASSIFIER_PATH}")
        print(f"DEBUG: [Direct Run] Adjusted SAMPLES_DIR: {SAMPLES_DIR}")
        print(f"DEBUG: [Direct Run] Adjusted TRAINER_DIR: {TRAINER_DIR}")
        print(f"DEBUG: [Direct Run] Adjusted TRAINER_FILE: {TRAINER_FILE}")

    if train_face_model():
        print("Face model training test successful.")
    else:
        print("Face model training test failed.")
