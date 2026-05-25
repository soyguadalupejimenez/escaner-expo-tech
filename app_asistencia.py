import streamlit as st
import pandas as pd
import datetime
import pytz  # Librería para la zona horaria exacta
import os

# Configuración de la página web
st.set_page_config(page_title="Control de Acceso - Expo Tech 2026", page_icon="🔒", layout="centered")

st.title("📝 Registro de Asistencia — Expo Tech 2026")
st.write("Selecciona el tipo de acceso para registrar a los visitantes en la entrada.")

# --- ARCHIVO DE RESPALDO LOCAL EN EL SERVIDOR ---
ARCHIVO_RESPALDO = "asistencia_respaldo.csv"

# Función para cargar los datos guardados previamente
def cargar_datos_respaldo():
    if os.path.exists(ARCHIVO_RESPALDO):
        try:
            return pd.read_csv(ARCHIVO_RESPALDO).to_dict(orient="records")
        except Exception:
            return []
    return []

# Función para guardar datos en tiempo real
def guardar_datos_respaldo(datos):
    df = pd.DataFrame(datos)
    df.to_csv(ARCHIVO_RESPALDO, index=False, encoding='utf-8-sig')

# 1. Inicializar el estado de la aplicación recuperando el respaldo si existe
if 'asistentes' not in st.session_state:
    st.session_state.asistentes = cargar_datos_respaldo()

# Recalcular el contador total sumando la columna de 'Cantidad Personas'
if 'contador' not in st.session_state:
    st.session_state.contador = sum(int(item["Cantidad Personas"]) for item in st.session_state.asistentes)

# --- FORMULARIO DIRECTO ---
st.write("### 📋 Datos de Ingreso")

# Pregunta 1: Tipo de Asistente
tipo_asistente = st.radio(
    "Seleccione el tipo de asistente:",
    ["Padre de Familia / Invitado", "Alumno"]
)

# Variables por defecto
nombre_alumno = "N/A"
grupo_alumno = "N/A"
puede_registrar = True

# Lógica condicional dependiendo del rol seleccionado
if tipo_asistente == "Padre de Familia / Invitado":
    cantidad_personas = st.number_input(
        "¿Cuántas personas ingresan?", 
        min_value=1, max_value=50, value=1, step=1
    )
else:
    cantidad_personas = 1
    st.info("📝 Por favor, introduce los datos del alumno para continuar.")
    nombre_alumno = st.text_input("Nombre Completo del Alumno:")
    grupo_alumno = st.text_input("Grupo (Ej. 4401, 4602):")
    
    # Bloquear registro si los campos obligatorios están vacíos
    if not nombre_alumno or not grupo_alumno:
        puede_registrar = False

# Botón para confirmar y registrar el acceso
if st.button("Registrar Entrada", disabled=not puede_registrar, use_container_width=True):
    # --- ZONA HORARIA TIEMPO REAL (ECATEPEC / CDMX) ---
    zona_horaria_mexico = pytz.timezone('America/Mexico_City')
    hora_actual_mexico = datetime.datetime.now(zona_horaria_mexico)
    hora_registro = hora_actual_mexico.strftime("%H:%M:%S")
    fecha_registro = hora_actual_mexico.strftime("%Y-%m-%d")
    
    # Construir el nuevo registro
    nuevo_registro = {
        "N° Registro": len(st.session_state.asistentes) + 1,
        "Fecha": fecha_registro,
        "Hora de Acceso": hora_registro,
        "Tipo de Asistente": tipo_asistente,
        "Cantidad Personas": cantidad_personas,
        "Nombre Alumno": nombre_alumno,
        "Grupo": grupo_alumno,
        "Estado": "Presente"
    }
    
    # Agregar a la lista en memoria y actualizar el contador global
    st.session_state.asistentes.append(nuevo_registro)
    st.session_state.contador += cantidad_personas
    
    # GUARDADO AUTOMÁTICO EN EL SERVIDOR
    guardar_datos_respaldo(st.session_state.asistentes)
    
    st.toast(f"¡Registro #{len(st.session_state.asistentes)} guardado automáticamente! 💾", icon="✅")
    
    # Forzar el refresco visual inmediato de Streamlit para vaciar los campos
    st.rerun()

# Si es alumno y faltan datos, mostrar la advertencia abajo del botón de registro
if tipo_asistente == "Alumno" and not puede_registrar:
    st.warning("⚠️ Debes rellenar el Nombre y el Grupo para poder registrar al alumno.")

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
        label="💾 Guardar lista de asistencia (Descargar a dispositivo)",
        data=csv_data,
        file_name=f"Asistencia_ExpoTech_Final_{datetime.date.today()}.csv",
        mime="text/csv",
        use_container_width=True
    )
