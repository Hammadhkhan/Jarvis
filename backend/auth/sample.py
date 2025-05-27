import cv2
import os

# Ensure paths are relative to the project root or handled appropriately
# For simplicity in this refactoring, let's assume these paths are correct when called from main.py
# or adjust them if main.py is in a different root relative to backend/auth.
# For now, let's assume the script is run from a context where 'backend\auth\' is valid.
# A better approach might be to pass classifier_path and samples_dir as arguments to the function.

CLASSIFIER_PATH = 'backend/auth/haarcascade_frontalface_default.xml'
SAMPLES_DIR = 'backend/auth/samples/'
FACE_ID = "1" # Default user ID
NUM_SAMPLES = 50 # Number of samples to take

def collect_face_samples():
    print("Initializing face sample collection...") # For logging

    # Ensure samples directory exists
    os.makedirs(SAMPLES_DIR, exist_ok=True)

    # Check if classifier file exists
    if not os.path.exists(CLASSIFIER_PATH):
        print(f"Error: Haar Cascade classifier not found at {CLASSIFIER_PATH}")
        return False

    detector = cv2.CascadeClassifier(CLASSIFIER_PATH)
    
    # Try different camera indices if 0 fails
    cam = None
    for cam_idx in range(3): # Try 0, 1, 2
        cam = cv2.VideoCapture(cam_idx, cv2.CAP_DSHOW)
        if cam.isOpened():
            print(f"Camera opened successfully with index {cam_idx}.")
            break
        else:
            print(f"Failed to open camera with index {cam_idx}.")
            if cam: cam.release() # Release if opened but not to be used
    
    if cam is None or not cam.isOpened(): # Check after loop
        print("Error: Could not open webcam.")
        return False

    cam.set(3, 640)  # Set video FrameWidth
    cam.set(4, 480)  # Set video FrameHeight

    print(f"Taking {NUM_SAMPLES} samples for user ID {FACE_ID}. Look at the camera...")
    count = 0
    # user_interrupted = False # This variable is not used without cv2.waitKey handling

    while count < NUM_SAMPLES:
        ret, img = cam.read()
        if not ret:
            print("Failed to capture image from camera.")
            break # Exit if frame not read

        converted_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(converted_image, 1.3, 5)

        for (x, y, w, h) in faces:
            # cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2) # Not strictly needed for saving samples
            count += 1
            sample_path = os.path.join(SAMPLES_DIR, f"face.{FACE_ID}.{count}.jpg")
            cv2.imwrite(sample_path, converted_image[y:y+h, x:x+w])
            print(f"Saved sample {count}/{NUM_SAMPLES} to {sample_path}") # Log progress
            
            # cv2.imshow('image', img) # Removed: UI handled by Eel
            # if cv2.waitKey(100) & 0xff == 27: # Removed: No direct key input
            #     user_interrupted = True
            #     break
        if count >= NUM_SAMPLES: # Check moved here to break outer loop
            break
        # if user_interrupted: # This check is now effectively dead code
        #     break
    
    # if user_interrupted:
    #     print("Sample collection interrupted by user.")

    print(f"Sample collection finished. Total samples taken: {count}")
    cam.release()
    cv2.destroyAllWindows() # Still good to clean up cv2 windows if any were implicitly created

    if count >= NUM_SAMPLES:
        print("Successfully collected all samples.")
        return True
    else:
        print(f"Failed to collect enough samples. Got {count} out of {NUM_SAMPLES}.")
        return False

if __name__ == '__main__':
    # Example of how to run (for testing this script directly)
    print("Attempting to collect face samples directly...")
    # Need to adjust path if running directly from backend/auth
    # This direct run part is mostly for testing the script itself.
    
    # Heuristic to adjust paths if running script directly from backend/auth
    # This is a common pattern for making scripts runnable both directly and as modules.
    current_dir = os.getcwd()
    # Assuming backend/auth is part of the path when run directly
    if current_dir.endswith(os.path.join('backend', 'auth')):
        print("INFO: [Direct Run] Adjusting paths for direct execution from backend/auth.")
        # Go up two levels to get to project root, then reconstruct paths
        project_root_from_direct_run = os.path.dirname(os.path.dirname(current_dir))
        
        # Temporarily override global paths for direct testing
        global CLASSIFIER_PATH, SAMPLES_DIR
        CLASSIFIER_PATH = os.path.join(project_root_from_direct_run, 'backend', 'auth', 'haarcascade_frontalface_default.xml')
        SAMPLES_DIR = os.path.join(project_root_from_direct_run, 'backend', 'auth', 'samples')
        print(f"DEBUG: [Direct Run] Adjusted CLASSIFIER_PATH: {CLASSIFIER_PATH}")
        print(f"DEBUG: [Direct Run] Adjusted SAMPLES_DIR: {SAMPLES_DIR}")

    if collect_face_samples():
        print("Face sample collection test successful.")
    else:
        print("Face sample collection test failed.")
