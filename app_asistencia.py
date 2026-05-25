import streamlit as st
import pandas as pd
import datetime
import cv2
import numpy as np

# Configuración de la página web
st.set_page_config(page_title="Control de Acceso - Expo Tech 2026", page_icon="🔒", layout="centered")

st.title("📷 Escáner de Asistencia — Expo Tech 2026")
st.write("Apunta la cámara del celular hacia el **Pase de Visitante** o **Pase de Estacionamiento**.")

# 1. Inicializar el estado de la aplicación (Base de datos temporal en la nube)
if 'asistentes' not in st.session_state:
    st.session_state.asistentes = []
if 'contador' not in st.session_state:
    st.session_state.contador = 0

# 2. Activar la cámara en cualquier celular (Android / iOS)
# Streamlit maneja automáticamente los permisos de la cámara del navegador
img_file_buffer = st.camera_input("Escanea un Pase")

if img_file_buffer is not None:
    # Leer la imagen capturada por el teléfono
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    
    # Convertir a escala de grises para el procesamiento
    gray = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2GRAY)
    
    # --- ALGORITMO DE RECONOCIMIENTO SIMPLIFICADO ---
    # Para entornos web móviles, el análisis de histograma de color verde o bordes del pase es el más efectivo.
    # Filtramos por el rango de color verde institucional del TESE/Expo Tech
    hsv = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2HSV)
    verde_bajo = np.array([35, 40, 40])
    verde_alto = np.array([85, 255, 255])
    mascara_verde = cv2.inRange(hsv, verde_bajo, verde_alto)
    pixeles_verdes = cv2.countNonZero(mascara_verde)
    
    # Si la cámara detecta una cantidad considerable del color verde característico de tus pases:
    if pixeles_verdes > 5000:  
        st.success("✅ ¡Pase Validado Exitosamente!")
        
        # Botón para confirmar el ingreso y evitar registros duplicados por error
        if st.button("Registrar Entrada"):
            st.session_state.contador += 1
            hora_registro = datetime.datetime.now().strftime("%H:%M:%S")
            
            # Guardamos los datos en la lista
            st.session_state.asistentes.append({
                "N° Registro": st.session_state.contador,
                "Hora de Acceso": hora_registro,
                "Estado": "Presente"
            })
            st.toast(f"Asistente #{st.session_state.contador} guardado.", icon="💾")
    else:
        st.warning("⚠️ No se reconoce el diseño del pase. Intenta enfocar mejor el color verde o el logo.")

# --- SECCIÓN DE CONTROL (Solo visible o útil para ti al finalizar) ---
st.write("---")
st.subheader("Métricas en Tiempo Real")
st.metric(label="Total de Usuarios que Entraron", value=st.session_state.contador)

if st.session_state.contador > 0:
    # Mostrar una vista previa de los últimos accesos en el celular
    df_asistencia = pd.DataFrame(st.session_state.asistentes)
    st.dataframe(df_asistencia.tail(5), use_container_width=True)
    
    # 3. Botón para Generar y Descargar el Excel al instante
    excel_data = df_asistencia.to_excel(index=False)
    
    st.download_button(
        label="📥 Finalizar Evento y Descargar Excel",
        data=df_asistencia.to_csv(index=False).encode('utf-8'), # Formato compatible directo en móviles
        file_name=f"Asistencia_ExpoTech_{datetime.date.today()}.csv",
        mime="text/csv",
    )
