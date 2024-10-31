# Utiliza una imagen base de Python 3.9 (también podrías usar otra versión compatible con Keras y FastAPI)
FROM python:3.9-slim

# Configura el directorio de trabajo
WORKDIR /app

# Copia los archivos de requerimientos (requirements.txt) si existen
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de los archivos de la aplicación en el contenedor
COPY . .

# Expone el puerto que usará la aplicación FastAPI
EXPOSE 8000

# Comando para ejecutar la API con Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
