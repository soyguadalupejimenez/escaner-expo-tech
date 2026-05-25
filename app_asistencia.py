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
        
        # --- NUEVA FUNCIÓN: PREGUNTAR CUÁNTOS ASISTENTES SON ---
        # Crea un selector numérico del 1 al 50 que por defecto inicia en 1
        cantidad_personas = st.number_input(
            "¿Cuántos asistentes ingresan con este pase?", 
            min_value=1, 
            max_value=50, 
            value=1,
            step=1
        )
        
        # Botón para confirmar el bloque completo de personas
        if st.button("Registrar Entrada"):
            # Sumamos la cantidad seleccionada al contador global acumulado
            st.session_state.contador += cantidad_personas
            
            # --- ZONA HORARIA TIEMPO REAL (ECATEPEC / CDMX) ---
            zona_horaria_mexico = pytz.timezone('America/Mexico_City')
            hora_actual_mexico = datetime.datetime.now(zona_horaria_mexico)
            hora_registro = hora_actual_mexico.strftime("%H:%M:%S")
            fecha_registro = hora_actual_mexico.strftime("%Y-%m-%d")
            
            # Guardamos los datos en la lista incluyendo la columna de personas
            st.session_state.asistentes.append({
                "N° Registro": len(st.session_state.asistentes) + 1,
                "Fecha": fecha_registro,
                "Hora de Acceso": hora_registro,
                "Asistentes en este Pase": cantidad_personas,
                "Estado": "Presente"
            })
            st.toast(f"¡Se registraron {cantidad_personas} personas correctamente! 💾", icon="✅")
    else:
        st.warning("⚠️ No se reconoce el diseño del pase. Enfoca bien el color verde o el logo.")

# --- MÉTRICAS Y VISTA PREVIA ---
st.write("---")
st.subheader("Métricas en Tiempo Real")

# Ahora la métrica muestra el acumulado real de personas totales que han cruzado la puerta
st.metric(label="Total de Personas que Entraron", value=st.session_state.contador)

# Si ya hay registros, mostramos la tabla con la nueva columna y habilitamos la descarga
if len(st.session_state.asistentes) > 0:
    df_asistencia = pd.DataFrame(st.session_state.asistentes)
    
    st.write("### Vista previa de los últimos accesos:")
    # Mostramos la tabla completa en pantalla para control del staff
    st.dataframe(df_asistencia.tail(5), use_container_width=True)
    
    st.write("---")
    st.write("### ⬇️ Guardar Reporte Final")
    
    # Preparamos los datos en formato CSV compatible al 100% con Excel (con soporte de acentos)
    csv_data = df_asistencia.to_csv(index=False).encode('utf-8-sig')
    
    # Botón para descargar el reporte a tu dispositivo
    st.download_button(
        label="💾 Guardar lista de asistencia",
        data=csv_data,
        file_name=f"Asistencia_ExpoTech_Grupal_{datetime.date.today()}.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    st.info("💡 Al presionar el botón, el archivo CSV se guardará en tus 'Descargas' incluyendo el conteo exacto de integrantes por cada grupo registrado.")
