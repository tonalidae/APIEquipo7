import streamlit as st
import requests
from PIL import Image, ImageDraw, ImageFont
import io
import os
from streamlit_cropper import st_cropper

# 1. Custom CSS
def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"No se encontró el archivo de estilos: {file_name}")

local_css("style.css")

# 2. Sidebar with Language and Model Selection
translations = {
    'Español': {
        'title': 'Análisis de Expresiones Faciales',
        'upload_image': 'Cargar tu imagen aquí:',
        'analyze_button': 'Analizar imagen',
        'feedback_title': 'Expresión detectada',
        'submit_feedback': 'Enviar retroalimentación',
        'select_model': 'Seleccionar modelo:',
        'ethical_disclaimer': 'Aviso: Al cargar o capturar una imagen, confirmas que tienes los derechos para hacerlo y que la imagen no viola ninguna política de privacidad. Las imágenes no se almacenarán en el servidor.',
        'documentation_title': 'Documentación',
        'documentation_content': """
            # Documentación de la Aplicación

            Esta aplicación utiliza modelos de aprendizaje automático para analizar expresiones faciales en imágenes.

            ## Cómo usar la aplicación

            1. **Cargar una imagen**: Puedes subir una imagen desde tu dispositivo o tomar una foto usando tu cámara.
            2. **Seleccionar el modelo**: Elige entre los modelos disponibles para el análisis.
            3. **Analizar la imagen**: Haz clic en 'Analizar imagen' para obtener la predicción.
            4. **Proporcionar retroalimentación**: Indica si la predicción es correcta y proporciona comentarios adicionales si lo deseas.

            ## Acerca de los modelos

            Los modelos disponibles han sido entrenados en diferentes conjuntos de datos y pueden variar en precisión y velocidad.

            ## Privacidad y Ética

            Las imágenes no se almacenan en el servidor y solo se utilizan para el análisis durante la sesión actual. Consulta el aviso ético para más detalles.
        """,
    },
    'English': {
        'title': 'Facial Expression Analysis',
        'upload_image': 'Upload your image here:',
        'analyze_button': 'Analyze Image',
        'feedback_title': 'Detected Expression',
        'submit_feedback': 'Submit Feedback',
        'select_model': 'Select Model:',
        'ethical_disclaimer': 'Disclaimer: By uploading or capturing an image, you confirm that you have the rights to do so and that the image does not violate any privacy policies. The images will not be stored on the server.',
        'documentation_title': 'Documentation',
        'documentation_content': """
            # Application Documentation

            This application uses machine learning models to analyze facial expressions in images.

            ## How to Use the Application

            1. **Upload an image**: You can upload an image from your device or take a photo using your camera.
            2. **Select the model**: Choose from the available models for analysis.
            3. **Analyze the image**: Click 'Analyze Image' to get the prediction.
            4. **Provide feedback**: Indicate if the prediction is correct and provide additional comments if desired.

            ## About the Models

            The available models have been trained on different datasets and may vary in accuracy and speed.

            ## Privacy and Ethics

            Images are not stored on the server and are only used for analysis during the current session. See the ethical disclaimer for more details.
        """,
    }
}

with st.sidebar:
    logo_path = 'logo7.jpg'
    if os.path.exists(logo_path):
        st.image(logo_path, width=200)
    else:
        st.warning("Logo no encontrado. Por favor, añade 'logo7.jpg' al directorio del proyecto.")
    selected_language = st.selectbox("Idioma / Language", ["Español", "English"])
    texts = translations[selected_language]

    # Model selection
    model_options = ['Modelo A', 'Modelo B'] if selected_language == 'Español' else ['Model A', 'Model B']
    selected_model = st.selectbox(texts['select_model'], model_options)

# 3. Main Title
st.title(texts['title'])

# 4. Tabs for Navigation
tab_names = ["Cargar Imagen", "Imágenes de Muestra", "Documentación"] if selected_language == 'Español' else ["Upload Image", "Sample Images", "Documentation"]
tab1, tab2, tab3 = st.tabs(tab_names)

# 5. Sample Images Mapping
class_to_idx = {
    0: 'Enojo' if selected_language == 'Español' else 'Anger',
    1: 'Desprecio' if selected_language == 'Español' else 'Contempt',
    2: 'Desagrado' if selected_language == 'Español' else 'Disgust',
    3: 'Miedo' if selected_language == 'Español' else 'Fear',
    4: 'Felicidad' if selected_language == 'Español' else 'Happiness',
    5: 'Neutral' if selected_language == 'Español' else 'Neutral',
    6: 'Tristeza' if selected_language == 'Español' else 'Sadness',
    7: 'Sorpresa' if selected_language == 'Español' else 'Surprise'
}

if selected_language == 'Español':
    sample_images = {
        'Felicidad': 'felicidad.png',
        'Tristeza': 'tristeza.png',
        'Sorpresa': 'sorpresa.png',
        'Enojo': 'enojo.png',
        'Miedo': 'miedo.png',
        'Desagrado': 'asco.png',
        'Desprecio': 'desprecio.png',
        'Neutral': 'neutral.png'
    }
else:
    sample_images = {
        'Happiness': 'felicidad.png',
        'Sadness': 'tristeza.png',
        'Surprise': 'sorpresa.png',
        'Anger': 'enojo.png',
        'Fear': 'miedo.png',
        'Disgust': 'asco.png',
        'Contempt': 'desprecio.png',
        'Neutral': 'neutral.png'
    }

def load_sample_image(img_name):
    image_path = os.path.join('samples', img_name)
    if not os.path.exists(image_path):
        st.error(f"Sample image not found: {image_path}")
        return None
    try:
        return Image.open(image_path)
    except IOError:
        st.error(f"Could not open image: {image_path}")
        return None

# 6. Handle Tabs
with tab1:
    uploaded_file = st.file_uploader(texts['upload_image'], type=["jpg", "jpeg", "png"], help="Sube una imagen en formato JPG o PNG.")
    img_file_buffer = st.camera_input("Tomar una foto" if selected_language == 'Español' else "Take a photo")
    st.info(texts['ethical_disclaimer'])

with tab2:
    sample_label = 'O seleccionar una imagen de ejemplo:' if selected_language == 'Español' else 'Or select a sample image:'
    selected_sample = st.selectbox(sample_label, ['Ninguna'] + list(sample_images.keys()) if selected_language == 'Español' else ['None'] + list(sample_images.keys()))

with tab3:
    st.markdown(texts['documentation_content'])

# 7. Display Selected Image
image = None

if selected_sample != 'None' and selected_sample != 'Ninguna':
    image = load_sample_image(sample_images[selected_sample])
    if image:
        st.image(image, caption='Imagen de ejemplo seleccionada' if selected_language == 'Español' else 'Sample Image', use_column_width=True)

elif uploaded_file is not None or img_file_buffer is not None:
    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption='Imagen cargada' if selected_language == 'Español' else 'Uploaded Image', use_column_width=True)
        except IOError:
            st.error("El archivo cargado no es una imagen válida." if selected_language == 'Español' else "The uploaded file is not a valid image.")
            image = None
    elif img_file_buffer is not None:
        try:
            image = Image.open(img_file_buffer)
            st.image(image, caption='Imagen capturada' if selected_language == 'Español' else 'Captured Image', use_column_width=True)
        except IOError:
            st.error("La foto tomada no es una imagen válida." if selected_language == 'Español' else "The captured photo is not a valid image.")
            image = None
else:
    st.info("Por favor, carga una imagen, toma una foto o selecciona una imagen de ejemplo." if selected_language == 'Español' else "Please upload an image, take a photo, or select a sample image.")

# 8. Image Cropping
if image is not None:
    st.subheader("Editar Imagen" if selected_language == 'Español' else "Edit Image")
    cropped_image = st_cropper(image, realtime_update=True, box_color='red', aspect_ratio=None)
    if cropped_image:
        st.image(cropped_image, caption='Imagen recortada' if selected_language == 'Español' else 'Cropped Image', use_column_width=True)
        image = cropped_image

    # 9. Analyze Image
    model_mapping = {
        'Modelo A': 'model_a',
        'Modelo B': 'model_b',
        'Model A': 'model_a',
        'Model B': 'model_b'
    }
    model_id = model_mapping[selected_model]
    API_URL = "https://1e53-186-154-39-104.ngrok-free.app/sentiment/image/"

    if st.button(texts['analyze_button']):
        with st.spinner('Analizando la imagen...' if selected_language == 'Español' else 'Analyzing image...'):
            # Prepare data for API
            buf = io.BytesIO()
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            image.save(buf, format='JPEG')
            byte_image = buf.getvalue()
            files = {'file': ('image.jpg', byte_image, 'image/jpeg')}
            data = {'model': model_id}

            # Send POST request to API
            try:
                response = requests.post(API_URL, files=files, data=data)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                st.error(f"Error: {e}")
            else:
                results = response.json()
                expression_index = int(results.get('expresion', -1))
                expresion = class_to_idx.get(expression_index, 'Desconocida' if selected_language == 'Español' else 'Unknown')

                # Display Detected Expression
                st.markdown(f"### **{texts['feedback_title']}:** {expresion}")

                # Feedback Mechanism
                st.subheader(texts['feedback_title'])
                feedback_options = ('Sí', 'No') if selected_language == 'Español' else ('Yes', 'No')
                feedback = st.radio("", feedback_options)
                if feedback == 'No':
                    correct_expression = st.selectbox('Seleccione la expresión correcta:' if selected_language == 'Español' else 'Select the correct expression:', list(sample_images.keys()))
                    comments = st.text_area("Comentarios adicionales:" if selected_language == 'Español' else "Additional comments:")
                    if st.button(texts['submit_feedback']):
                        st.success("Gracias por tu retroalimentación." if selected_language == 'Español' else "Thank you for your feedback.")
                elif feedback == 'Sí':
                    st.success("¡Gracias por confirmar la predicción!" if selected_language == 'Español' else "Thank you for confirming the prediction!")

                # Option to Download Annotated Image
                st.download_button(
                    label="Descargar imagen" if selected_language == 'Español' else "Download Image",
                    data=byte_image,
                    file_name='imagen_analizada.jpg' if selected_language == 'Español' else 'analyzed_image.jpg',
                    mime='image/jpeg'
                )

                # Add to Session History
                if 'history' not in st.session_state:
                    st.session_state['history'] = []
                st.session_state['history'].append({'image': image, 'expresion': expresion})

                # Display Session History
                if st.session_state['history']:
                    st.subheader("Historial de análisis" if selected_language == 'Español' else "Analysis History")
                    for idx, entry in enumerate(st.session_state['history']):
                        st.image(entry['image'], caption=f"Análisis {idx+1}: {entry['expresion']}" if selected_language == 'Español' else f"Analysis {idx+1}: {entry['expresion']}", use_column_width=True)

else:
    st.warning("Por favor, proporciona una imagen para analizar." if selected_language == 'Español' else "Please provide an image to analyze.")

# 10. Educational Content
with st.expander("Información sobre las expresiones faciales" if selected_language == 'Español' else "Information about facial expressions"):
    st.write("""
        **Felicidad**: Una sonrisa amplia con ojos brillantes indica felicidad.

        **Tristeza**: Comisuras de los labios hacia abajo y ojos caídos muestran tristeza.

        **Sorpresa**: Ojos abiertos y cejas levantadas reflejan sorpresa.

        **Enojo**: Ceño fruncido y mandíbula tensa señalan enojo.

        **Miedo**: Ojos muy abiertos y boca abierta indican miedo.

        **Desprecio**: Un lado de la boca levantado muestra desprecio.

        **Desagrado**: Arrugas en la nariz y boca torcida reflejan desagrado.

        **Neutral**: Expresión facial sin emociones marcadas.
    """ if selected_language == 'Español' else """
        **Happiness**: A broad smile with bright eyes indicates happiness.

        **Sadness**: Downturned corners of the mouth and drooping eyes show sadness.

        **Surprise**: Wide-open eyes and raised eyebrows reflect surprise.

        **Anger**: Frowning and a tense jaw signal anger.

        **Fear**: Very wide-open eyes and an open mouth indicate fear.

        **Contempt**: One side of the mouth raised shows contempt.

        **Disgust**: Wrinkled nose and twisted mouth reflect disgust.

        **Neutral**: Facial expression without marked emotions.
    """)
