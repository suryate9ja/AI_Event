from ultralytics import YOLO
import os
import torch

def download_models():
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    # Download YOLO face detection model
    print("Downloading YOLO face detection model...")
    try:
        # First download the base YOLOv8n model
        model = YOLO('yolov8n.pt')
        
        # Save it to our models directory
        model_path = os.path.join('models', 'yolov8n-face.pt')
        torch.save(model.state_dict(), model_path)
        
        print("✅ Models downloaded successfully!")
        print(f"Model saved to: {model_path}")
    except Exception as e:
        print(f"❌ Error downloading models: {str(e)}")
        raise

if __name__ == "__main__":
    download_models() 