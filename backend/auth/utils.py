import os
import glob

SAMPLES_PATH = "backend/auth/samples/"
TRAINER_FILE_PATH = "backend/auth/trainer/trainer.yml"

def delete_existing_face_data():
    """
    Deletes all existing face sample images and the trained data file.
    """
    deleted_samples = False
    sample_files = glob.glob(SAMPLES_PATH + '*')
    
    if not sample_files:
        print("No existing face samples found to delete in " + SAMPLES_PATH)
    else:
        for filepath in sample_files:
            try:
                os.remove(filepath)
                print(f"Deleted sample: {filepath}")
                deleted_samples = True
            except OSError as e:
                print(f"Error deleting sample {filepath}: {e.strerror}")
        if not deleted_samples: # This case might be redundant due to the initial check
             print("No face samples were deleted (though files might have been listed).")


    deleted_trainer = False
    if os.path.exists(TRAINER_FILE_PATH):
        try:
            os.remove(TRAINER_FILE_PATH)
            print(f"Deleted trainer file: {TRAINER_FILE_PATH}")
            deleted_trainer = True
        except OSError as e:
            print(f"Error deleting trainer file {TRAINER_FILE_PATH}: {e.strerror}")
    else:
        print(f"Trainer file not found at {TRAINER_FILE_PATH}, no need to delete.")

    if not deleted_samples and not deleted_trainer and sample_files: # Only if sample_files was not empty but nothing got deleted
        # This condition might need refinement. The goal is to confirm if an action was taken.
        # If sample_files was empty and trainer was not found, initial messages cover this.
        # This is more for "files were there but couldn't be deleted" or "trainer was there but couldn't be deleted"
        # which are covered by try-except now.
        pass # The specific print statements above should suffice.

if __name__ == '__main__':
    # Example usage:
    # Before running this, you might want to create dummy files to test deletion:
    # os.makedirs(SAMPLES_PATH, exist_ok=True)
    # os.makedirs(os.path.dirname(TRAINER_FILE_PATH), exist_ok=True)
    # with open(SAMPLES_PATH + "sample1.jpg", "w") as f: f.write("dummy")
    # with open(TRAINER_FILE_PATH, "w") as f: f.write("dummy")
    
    print("Attempting to delete existing face data...")
    delete_existing_face_data()
    print("Deletion process finished.")
