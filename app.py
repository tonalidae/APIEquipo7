from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from keras.models import load_model
import numpy as np
import cv2
from PIL import Image
import io

# Load both models
model_a = load_model('modelo_affect_net.h5')
model_b = load_model('modelo_affect_net_20_epocas.h5')

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

def load_image(image: Image.Image):
    # Convert the image to a NumPy array
    img = np.array(image)
    img = cv2.resize(img, (96, 96))  # Resize to 96x96
    img = img / 255.0  # Normalize
    return img

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

        # Process the image
        img = load_image(image)
        img_array = np.expand_dims(img, axis=0)  # Add batch dimension

        # Select the model
        if model == 'model_a':
            predictions = model_a.predict(img_array)
        elif model == 'model_b':
            predictions = model_b.predict(img_array)
        else:
            raise HTTPException(status_code=400, detail="Invalid model selected")

        expresion = np.argmax(predictions, axis=1)[0]  # Get the class with highest probability

        # Return the result
        return {"expresion": int(expresion)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
