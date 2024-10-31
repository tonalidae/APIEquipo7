from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from keras.models import load_model
import numpy as np
import cv2
from PIL import Image
import io
import torch
import torch.nn as nn
import torchvision.transforms as transforms

# Load Keras models
model_a = load_model('modelo_affect_net.h5')
model_b = load_model('modelo_affect_net_20_epocas.h5')

# Load the PyTorch model
class VITModel(nn.Module):
    def __init__(self, num_classes=8):
        super(VITModel, self).__init__()
        # Define your model architecture here
        # For example, if you used a pre-trained ViT model:
        # self.model = torchvision.models.vit_b_16(pretrained=False)
        # self.model.heads = nn.Linear(self.model.heads.in_features, num_classes)
        self.model = torch.load('VIT-modelo.pth', map_location=torch.device('cpu'))
    
    def forward(self, x):
        return self.model(x)

model_c = VITModel()
model_c.eval()  # Set the model to evaluation mode

# Initialize the API
app = FastAPI()

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:8000",
    "https://1e53-186-154-39-104.ngrok-free.app",
    # Add any other origins you need to allow
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Or use ["*"] to allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_image(image: Image.Image, target_size=(96, 96)):
    # Convert the image to a NumPy array
    img = np.array(image)
    img = cv2.resize(img, target_size)  # Resize
    img = img / 255.0  # Normalize
    return img

def preprocess_for_vit(image: Image.Image):
    # Define the preprocessing steps required for the ViT model
    preprocess = transforms.Compose([
        transforms.Resize((224, 224)),  # ViT models often use 224x224 images
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],  # Mean and std for ImageNet
            std=[0.229, 0.224, 0.225]
        ),
    ])
    return preprocess(image)

# Endpoint for image analysis
@app.post("/sentiment/image/")
async def predict_sentiment_from_image(
    file: UploadFile = File(...),
    model: str = Form(...)
):
    try:
        # Read the image from the file
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert('RGB')

        # Select the model
        if model == 'model_a':
            # Process the image
            img = load_image(image)
            img_array = np.expand_dims(img, axis=0)  # Add batch dimension

            predictions = model_a.predict(img_array)
            expresion = np.argmax(predictions, axis=1)[0]

        elif model == 'model_b':
            # Process the image
            img = load_image(image)
            img_array = np.expand_dims(img, axis=0)  # Add batch dimension

            predictions = model_b.predict(img_array)
            expresion = np.argmax(predictions, axis=1)[0]

        elif model == 'model_c':
            # Process the image for ViT model
            img_tensor = preprocess_for_vit(image)
            img_tensor = img_tensor.unsqueeze(0)  # Add batch dimension

            with torch.no_grad():
                outputs = model_c(img_tensor)
                _, predicted = torch.max(outputs, 1)
                expresion = predicted.item()

        else:
            raise HTTPException(status_code=400, detail="Invalid model selected")

        # Return the result
        return {"expresion": int(expresion)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
