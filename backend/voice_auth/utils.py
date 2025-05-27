# backend/voice_auth/utils.py
import os
import shutil

SAMPLES_DIR = "backend/voice_auth/samples/user_1/"
MODELS_DIR = "backend/voice_auth/models/"

def delete_existing_voice_data():
    deleted_something = False
    if os.path.exists(SAMPLES_DIR):
        try:
            shutil.rmtree(SAMPLES_DIR)
            print(f"Deleted voice samples directory: {SAMPLES_DIR}")
            deleted_something = True
        except Exception as e:
            print(f"Error deleting voice samples directory {SAMPLES_DIR}: {e}")
    else:
        print(f"Voice samples directory {SAMPLES_DIR} not found.")

    if os.path.exists(MODELS_DIR):
        try:
            for item in os.listdir(MODELS_DIR):
                item_path = os.path.join(MODELS_DIR, item)
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.unlink(item_path)
                    print(f"Deleted voice model file: {item_path}")
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                    print(f"Deleted voice model subdirectory: {item_path}")
            # If we reach here and listdir was not empty, or even if it was empty but MODELS_DIR existed
            # we can consider 'something' done in terms of checking/preparing the directory.
            # However, to be more precise, let's only set deleted_something if an actual deletion happened.
            # The prompt's original logic implies deleted_something = True if MODELS_DIR exists and is processed.
            # For safety, let's ensure it's only true if a file/dir within it was removed or if SAMPLES_DIR was removed.
            # The current logic sets it to True if we enter this block, which is fine for its use.
            deleted_something = True 
        except Exception as e:
            print(f"Error deleting voice models from {MODELS_DIR}: {e}")
    else:
        print(f"Voice models directory {MODELS_DIR} not found.")
    
    if deleted_something:
        print("Existing voice data deletion process finished.")
    else:
        print("No existing voice data found to delete or directories were already absent.")
    return deleted_something
