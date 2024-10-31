import streamlit as st
import requests
from PIL import Image, ImageDraw, ImageFont
import io
import os  # Añadido
import base64
from streamlit_cropper import st_cropper
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# 1. Custom CSS
def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"No se encontró el archivo de estilos: {file_name}")

local_css("style.css")

# 2. Sidebar with Language Selection
translations = {
    'Español': {
        'title': 'Análisis de Expresiones Faciales',
        'upload_image': 'Cargar tu imagen aquí:',
        'analyze_button': 'Analizar imagen',
        'feedback_title': '¿Es correcta la predicción?',
        'submit_feedback': 'Enviar retroalimentación',
        # Agrega más traducciones según sea necesario
    },
    'English': {
        'title': 'Facial Expression Analysis',
        'upload_image': 'Upload your image here:',
        'analyze_button': 'Analyze Image',
        'feedback_title': 'Is the prediction correct?',
        'submit_feedback': 'Submit Feedback',
        # Agrega más traducciones según sean necesarias
    }
}

with st.sidebar:
    logo_path = 'logo.png'
    if os.path.exists(logo_path):
        st.image(logo_path, width=200)
    else:
        st.warning("Logo no encontrado. Por favor, añade 'logo.png' al directorio del proyecto.")
    selected_language = st.selectbox("Idioma / Language", ["Español", "English"])

texts = translations[selected_language]

# 3. Main Title
st.title(texts['title'])

# 4. Tabs for Navigation
tab_names = ["Cargar Imagen", "Captura de Cámara", "Imágenes de Muestra"] if selected_language == 'Español' else ["Upload Image", "Camera Capture", "Sample Images"]
tab1, tab2, tab3 = st.tabs(tab_names)

# 5. Sample Images Mapping
class_to_idx = {
    0: 'enojo',
    1: 'desprecio',
    2: 'desagrado',
    3: 'miedo',
    4: 'felicidad',
    5: 'neutral',
    6: 'tristeza',
    7: 'sorpresa'
}

sample_images = {
    'Felicidad': 'felicidad.png',
    'Tristeza': 'tristeza.png',
    'Sorpresa': 'sorpresa.png',
    'Enojo': 'enojo.png',
    'Miedo': 'miedo.png',
    'Asco': 'asco.png',
    'Desprecio': 'desprecio.png',
    'Neutral': 'neutral.png'
}

def load_sample_image(img_name):
    image_path = os.path.join('samples', img_name)
    if not os.path.exists(image_path):
        st.error(f"Imagen de muestra no encontrada: {image_path}")
        return None
    try:
        return Image.open(image_path)
    except IOError:
        st.error(f"No se pudo abrir la imagen: {image_path}")
        return None


# 7. Manejo de Diferentes Tabs
with tab1:
    uploaded_file = st.file_uploader(texts['upload_image'], type=["jpg", "jpeg", "png"], help="Sube una imagen en formato JPG o PNG.")

with tab2:
    img_file_buffer = st.camera_input("Tomar una foto")

with tab3:
    sample_label = 'O seleccionar una imagen de ejemplo:' if selected_language == 'Español' else 'Or select a sample image:'
    selected_sample = st.selectbox(sample_label, ['Ninguna'] + list(sample_images.keys()), label_visibility='visible')

# 8. Mostrar la Imagen Seleccionada
if selected_sample != 'Ninguna':
    image = load_sample_image(sample_images[selected_sample])
    if image:
        st.image(image, caption='Imagen de ejemplo seleccionada', use_column_width=True)

elif img_file_buffer is not None:
    try:
        image = Image.open(img_file_buffer)
        st.image(image, caption='Imagen capturada', use_column_width=True)
    except IOError:
        st.error("La foto tomada no es una imagen válida.")
        image = None
elif uploaded_file is not None:
    try:
        image = Image.open(uploaded_file)
        st.image(image, caption='Imagen cargada', use_column_width=True)
    except IOError:
        st.error("El archivo cargado no es una imagen válida.")
        image = None
else:
    image = None
    st.info("Por favor, carga una imagen, toma una foto o selecciona una imagen de ejemplo.")

# 9. Recortar Imagen (Funcionalidad Avanzada)
if image is not None:
    st.subheader("Editar Imagen")
    cropped_image = st_cropper(image, realtime_update=True, box_color='red', aspect_ratio=None)
    if cropped_image:
        st.image(cropped_image, caption='Imagen recortada', use_column_width=True)
        image = cropped_image

    # 10. Analizar Imagen
    API_URL = "http://localhost:8000/sentiment/image/"

    if st.button(texts['analyze_button']):
        with st.spinner('Analizando la imagen...'):
            # Preparar los datos para enviar a la API
            buf = io.BytesIO()
            if image.mode == 'RGBA':
                image = image.convert('RGB')  # Convertir a RGB si está en RGBA
                save_format = 'JPEG'
                mime_type = 'image/jpeg'
                file_extension = 'jpg'
            else:
                save_format = 'PNG' if image.format == 'PNG' else 'JPEG'
                mime_type = 'image/png' if save_format == 'PNG' else 'image/jpeg'
                file_extension = 'png' if save_format == 'PNG' else 'jpg'
            image.save(buf, format=save_format)
            byte_image = buf.getvalue()
            files = {'file': (f'image.{file_extension}', byte_image, mime_type)}

            # Hacer la solicitud POST a la API
            try:
                response = requests.post(API_URL, files=files)
                response.raise_for_status()
            except requests.exceptions.HTTPError as http_err:
                st.error(f"Error HTTP: {http_err}")
            except requests.exceptions.ConnectionError:
                st.error("No se pudo conectar con el servidor. Por favor, verifica tu conexión a internet o intenta más tarde.")
            except requests.exceptions.Timeout:
                st.error("La solicitud ha expirado. Por favor, intenta nuevamente.")
            except requests.exceptions.RequestException as e:
                st.error(f"Error inesperado: {e}")
            else:
                results = response.json()
                
                # Mostrar la respuesta completa para depuración
                st.write("Respuesta de la API:", results)

                # Suponiendo que la API devuelve 'expresion', 'confidences' y 'boxes'
                expresion = class_to_idx.get(int(results.get('expresion', -1)), 'Desconocida')
                confidences = results.get('confidences', {})
                boxes = results.get('boxes', [])

                # Mostrar la Expresión Detectada
                st.markdown(f"### **Expresión detectada:** {expresion}")

                # Mostrar las Confidencias en un Gráfico de Barras si están Disponibles
                if confidences:
                    confidences_mapped = {class_to_idx.get(int(k), 'Desconocida'): v for k, v in confidences.items()}
                    st.bar_chart(data=confidences_mapped)

                # Anotar la Imagen con las Predicciones si Hay Cajas
                if boxes:
                    annotated_image = image.copy()
                    draw = ImageDraw.Draw(annotated_image)
                    font = ImageFont.load_default()
                    for box in boxes:
                        bbox = box.get('box')  # Asegúrate de que la clave sea correcta
                        expr = class_to_idx.get(int(box.get('expresion', -1)), 'Desconocida')
                        confidence = box.get('confidence', 0)
                        if bbox:
                            draw.rectangle(bbox, outline='red', width=2)
                            text = f"{expr} ({confidence*100:.1f}%)"
                            text_size = draw.textsize(text, font=font)
                            text_position = (bbox[0], bbox[1] - text_size[1]) if bbox[1] - text_size[1] > 0 else (bbox[0], bbox[1])
                            draw.rectangle([text_position, (bbox[0] + text_size[0], bbox[1])], fill='red')
                            draw.text(text_position, text, fill='white', font=font)
                    st.image(annotated_image, caption='Resultado con anotaciones', use_column_width=True)
                else:
                    st.warning("No se detectaron rostros en la imagen.")

                # Mecanismo de Retroalimentación
                st.subheader(texts['feedback_title'])
                feedback = st.radio("", ('Seleccione una opción', 'Sí', 'No'), label_visibility='visible', index=0)
                if feedback == 'No':
                    correct_expression = st.selectbox('Seleccione la expresión correcta:', list(class_to_idx.values()), label_visibility='visible')
                    comments = st.text_area("Comentarios adicionales:", label_visibility='visible')
                    if st.button(texts['submit_feedback']):
                        # Aquí podrías enviar esta información a tu backend para mejorar el modelo
                        # Por ahora, simplemente mostramos un mensaje de éxito
                        st.success("Gracias por tu retroalimentación.")
                elif feedback == 'Sí':
                    st.success("¡Gracias por confirmar la predicción!")
                # No hacer nada si 'Seleccione una opción' está seleccionado

                # Opción para Descargar la Imagen Anotada
                buf = io.BytesIO()
                if boxes:
                    annotated_image.save(buf, format=save_format)
                else:
                    image.save(buf, format=save_format)
                byte_im = buf.getvalue()
                st.download_button(
                    label="Descargar imagen",
                    data=byte_im,
                    file_name=f'imagen_analizada.{file_extension}',
                    mime=mime_type
                )

                # Compartir en Twitter
                share_text = f"Detecté una expresión de {expresion} usando la app de Análisis de Expresiones Faciales."
                share_url = f"https://twitter.com/intent/tweet?text={share_text}"
                st.markdown(f"[Compartir en Twitter]({share_url})")

                # Agregar al Historial de Sesiones
                if 'history' not in st.session_state:
                    st.session_state['history'] = []
                st.session_state['history'].append({'image': image, 'expresion': expresion})

                # Mostrar el Historial de Sesiones
                if st.session_state['history']:
                    st.subheader("Historial de análisis")
                    for idx, entry in enumerate(st.session_state['history']):
                        st.image(entry['image'], caption=f"Análisis {idx+1}: {entry['expresion']}", use_column_width=True)

else:
    st.warning("Por favor, proporciona una imagen para analizar.")

# 11. Contenido Educativo
with st.expander("Información sobre las expresiones faciales"):
    st.write("""
        **Felicidad**: Una sonrisa amplia con ojos brillantes indica felicidad.
        
        **Tristeza**: Comisuras de los labios hacia abajo y ojos caídos muestran tristeza.
        
        **Sorpresa**: Ojos abiertos y cejas levantadas reflejan sorpresa.
        
        **Enojo**: Ceño fruncido y mandíbula tensa señalan enojo.
        
        **Miedo**: Ojos muy abiertos y boca abierta indican miedo.
        
        **Desprecio**: Un lado de la boca levantado muestra desprecio.
        
        **Desagrado**: Arrugas en la nariz y boca torcida reflejan desagrado.
        
        **Neutral**: Expresión facial sin emociones marcadas.
    """)