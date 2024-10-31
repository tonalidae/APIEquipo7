from fastapi import FastAPI, HTTPException, File, UploadFile
from keras.models import load_model
import numpy as np
import cv2
from PIL import Image
import io

# Cargar el modelo entrenado
#model = load_model('modelo_affect_net.h5')
model = load_model('modelo_affect_net_20_epocas.h5')

# Inicializar la API
app = FastAPI()

def load_image(image: Image.Image):
    # Convertir la imagen a un array de NumPy
    img = np.array(image)
    img = cv2.resize(img, (96, 96))  # Cambiar tamaño a 96x96
    img = img / 255.0  # Normalizar
    return img

# Nuevo endpoint para análisis de imágenes
@app.post("/sentiment/image/")
async def predict_sentiment_from_image(file: UploadFile = File(...)):
    try:
        # Leer la imagen desde el archivo
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert('RGB')

        # Cargar y procesar la imagen usando la función load_image
        img = load_image(image)
        img_array = np.expand_dims(img, axis=0)  # Agregar dimensión de batch

        # Realizar la predicción
        predictions = model.predict(img_array)
        expresion = np.argmax(predictions, axis=1)[0]  # Obtener la clase con mayor probabilidad

        # Devolver el resultado
        return {"expresion": int(expresion)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
