import streamlit as st
import pandas as pd
import datetime
import pytz  # Librería para la zona horaria exacta
import cv2
import numpy as np

# Configuración de la página web
st.set_page_config(page_title="Control de Acceso - Expo Tech 2026", page_icon="🔒", layout="centered")

st.title("📷 Escáner de Asistencia — Expo Tech 2026")
st.write("Apunta la cámara del celular hacia el **Pase de Visitante** o **Pase de Estacionamiento**.")

# 1. Inicializar el estado de la aplicación
if 'asistentes' not in st.session_state:
    st.session_state.asistentes = []
if 'contador' not in st.session_state:
    st.session_state.contador = 0

# 2. Activar la cámara en el teléfono
img_file_buffer = st.camera_input("Escanea un Pase")

if img_file_buffer is not None:
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
    
    # Algoritmo por reconocimiento del color verde institucional
    hsv = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2HSV)
    verde_bajo = np.array([35, 40, 40])
    verde_alto = np.array([85, 255, 255])
    mascara_verde = cv2.inRange(hsv, verde_bajo, verde_alto)
    pixeles_verdes = cv2.countNonZero(mascara_verde)
    
    if pixeles_verdes > 5000:  
        st.success("✅ ¡Pase Validado Exitosamente!")
        
        # --- PREGUNTA 1: TIPO DE ASISTENTE ---
        tipo_asistente = st.radio(
            "Seleccione el tipo de asistente:",
            ["Padre de Familia / Invitado", "Alumno"]
        )
        
        # Variables por defecto
        nombre_alumno = "N/A"
        grupo_alumno = "N/A"
        puede_registrar = True
        
        # --- LÓGICA CONDICIONAL DEPENDIENDO DEL ROL ---
        if tipo_asistente == "Padre de Familia / Invitado":
            # Si es Padre, mostramos el selector de cantidad (del 1 al 50)
            cantidad_personas = st.number_input(
                "¿Cuántas personas ingresan con este pase?", 
                min_value=1, max_value=50, value=1, step=1
            )
        else:
            # Si es Alumno, se fuerza a 1 automáticamente y no se le pregunta nada en pantalla
            cantidad_personas = 1
            
            st.info("📝 Por favor, introduce los datos del alumno para continuar.")
            nombre_alumno = st.text_input("Nombre Completo del Alumno:")
            grupo_alumno = st.text_input("Grupo (Ej. 4401, 4602):")
            
            # Bloquear registro si los campos están vacíos
            if not nombre_alumno or not grupo_alumno:
                puede_registrar = False
                st.warning("⚠️ Debes rellenar el Nombre y el Grupo para poder registrar al alumno.")
        
        # Botón para confirmar el acceso
        if st.button("Registrar Entrada", disabled=not puede_registrar):
            # Sumamos la cantidad calculada al contador global acumulado
            st.session_state.contador += cantidad_personas
            
            # --- ZONA HORARIA TIEMPO REAL (ECATEPEC / CDMX) ---
            zona_horaria_mexico = pytz.timezone('America/Mexico_City')
            hora_actual_mexico = datetime.datetime.now(zona_horaria_mexico)
            hora_registro = hora_actual_mexico.strftime("%H:%M:%S")
            fecha_registro = hora_actual_mexico.strftime("%Y-%m-%d")
            
            # Guardamos los datos en la lista
            st.session_state.asistentes.append({
                "N° Registro": len(st.session_state.asistentes) + 1,
                "Fecha": fecha_registro,
                "Hora de Acceso": hora_registro,
                "Tipo de Asistente": tipo_asistente,
                "Cantidad Personas": cantidad_personas,
                "Nombre Alumno": nombre_alumno,
                "Grupo": grupo_alumno,
                "Estado": "Presente"
            })
            st.toast(f"¡Registro #{len(st.session_state.asistentes)} guardado con éxito! 💾", icon="✅")
    else:
        st.warning("⚠️ No se reconoce el diseño del pase. Enfoca bien el color verde o el logo.")

# --- MÉTRICAS Y VISTA PREVIA ---
st.write("---")
st.subheader("Métricas en Tiempo Real")

st.metric(label="Total de Personas que Entraron", value=st.session_state.contador)

if len(st.session_state.asistentes) > 0:
    df_asistencia = pd.DataFrame(st.session_state.asistentes)
    
    st.write("### Vista previa de los últimos accesos:")
    st.dataframe(df_asistencia.tail(5), use_container_width=True)
    
    st.write("---")
    st.write("### ⬇️ Guardar Reporte Final")
    
    csv_data = df_asistencia.to_csv(index=False).encode('utf-8-sig')
    
    st.download_button(
        label="💾 Guardar lista de asistencia",
        data=csv_data,
        file_name=f"Asistencia_ExpoTech_Filtro_{datetime.date.today()}.csv",
        mime="text/csv",
        use_container_width=True
    )
