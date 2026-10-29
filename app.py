import os
import time
import json
import glob
from PIL import Image
import streamlit as st
from bokeh.models import CustomJS
from bokeh.models.widgets import Button
from streamlit_bokeh_events import streamlit_bokeh_events
import paho.mqtt.client as paho

# Configuración de la página
st.set_page_config(
    page_title="Control por Voz MQTT",
    page_icon="🎙️",
    layout="centered"
)

# Estilos visuales
st.markdown("""
<style>
    .status-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Configuración Broker MQTT
broker = "broker.mqttdashboard.com"
port = 1883
topic_voice = "voice_ctrl"

def send_mqtt_voice(text_command):
    """Publica la transcripción de voz al broker MQTT."""
    try:
        try:
            client = paho.Client(paho.CallbackAPIVersion.VERSION1, "STREAMLIT-VOICE")
        except AttributeError:
            client = paho.Client("STREAMLIT-VOICE")

        client.connect(broker, port, keepalive=60)
        payload = json.dumps({"Act1": text_command.strip()})
        client.publish(topic_voice, payload)
        client.disconnect()
        return True
    except Exception as e:
        st.error(f"Error al enviar mensaje MQTT: {e}")
        return False

# Encabezado
st.title("🎙️ Interfaces Multimodales")
st.caption("Control por reconocimiento de voz y telemando MQTT")

st.divider()

col_img, col_ctrl = st.columns([1, 2], vertical_alignment="center")

with col_img:
    if os.path.exists("voice_ctrl.jpg"):
        image = Image.open("voice_ctrl.jpg")
        st.image(image, use_container_width=True)
    else:
        st.markdown("<h3>🗣️</h3>", unsafe_allow_html=True)

with col_ctrl:
    st.subheader("Instrucciones")
    st.write("1. Presiona el botón **'Iniciar Escucha'**.")
    st.write("2. Habla con claridad hacia el micrófono.")
    st.write("3. El comando se procesará y enviará al instante.")

st.divider()

# Botón Bokeh para Web Speech API
stt_button = Button(label="🎤 Iniciar Escucha", width=260, button_type="success")

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'es-ES';

    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
"""))

# Captura de evento Bokeh en Streamlit
result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen_voice",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

# Procesamiento de la voz capturada
if result and "GET_TEXT" in result:
    spoken_text = result.get("GET_TEXT")
    
    st.success("¡Voz capturada con éxito!")
