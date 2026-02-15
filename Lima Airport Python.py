# ==============================================================================
# PROYECTO: LIMA AIRPORT FLIGHT DATA SCRAPER (SINGLE CELL VERSION - MASTER VALIDATOR)
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. INSTALACIÓN DE COMPONENTES DE SISTEMA
# ------------------------------------------------------------------------------
print("📦 Instalando Google Chrome y dependencias (Motor Master)...")

# Instalamos Google Chrome Stable
!wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
!apt-get install -y ./google-chrome-stable_current_amd64.deb -q

# Librerías necesarias
!pip install --upgrade gspread requests==2.32.4 pandas==2.2.2 google-auth-oauthlib beautifulsoup4 selenium -q

import gspread
import pandas as pd
import requests
import time
import os
import re
from datetime import datetime, timedelta, timezone
from google.colab import auth, drive
from google.auth import default
from googleapiclient.discovery import build
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 2. AUTENTICACIÓN
print("🔐 Iniciando autenticación...")
auth.authenticate_user()
creds, _ = default()
gc = gspread.authorize(creds)

# ------------------------------------------------------------------------------
# 2. CONFIGURACIÓN DE INFRAESTRUCTURA (FASE 2)
# ------------------------------------------------------------------------------
SHEET_NAME = "Lima Airport Data"
WORKSHEET_NAME = "Data"

# DICCIONARIO MAESTRO DE DESTINOS (PERÚ)
DESTINOS_PERU = [
    "AREQUIPA", "AYACUCHO", "CAJAMARCA", "CHACHAPOYAS", "CHICLAYO", "CUSCO", 
    "HUANUCO", "ANTA - HUARAZ", "IQUITOS", "JAUJA", "JAEN", 
    "JULIACA", "MAZAMARI", "PIURA", "PUCALLPA", "PUERTO MALDONADO", "TACNA", 
    "TALARA", "TARAPOTO", "TRUJILLO", "TUMBES", "YURIMAGUAS", "ILO", "PISCO",
    "TINGO MARIA", "ANDAHUAYLAS", "NUEVO MUNDO"
]

def setup_google_sheet():
    print("📂 Montando Google Drive...")
    drive.mount('/content/drive', force_remount=True)
    drive_service = build('drive', 'v3', credentials=creds)
    
    print("🔍 Buscando carpeta y hoja...")
    q_folder = "(name = 'lima airport' or name = 'LIMA AIRPORT') and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    folders = drive_service.files().list(q=q_folder, fields='files(id)').execute().get('files', [])
    folder_id = folders[0]['id'] if folders else None

    q_sheet = f"name = '{SHEET_NAME}' and mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false"
    sheets = drive_service.files().list(q=q_sheet, fields='files(id)').execute().get('files', [])
    
    if sheets:
        sh = gc.open_by_key(sheets[0]['id'])
    else:
        sh = gc.create(SHEET_NAME)
        if folder_id:
            drive_service.files().update(fileId=sh.id, addParents=folder_id, removeParents='root').execute()

    try:
        worksheet = sh.worksheet(WORKSHEET_NAME)
    except:
        worksheet = sh.add_worksheet(title=WORKSHEET_NAME, rows="2000", cols="15")
        try: sh.del_worksheet(sh.worksheet('Sheet1'))
        except: pass

    headers = ["Fecha", "Hora Prog.", "Nueva Hora", "Destino", "Vuelo", "Aerolínea", "Puerta", "Check-in", "Estado", "Última Actualización"]
    worksheet.clear()
    worksheet.append_row(headers)
    worksheet.format("A1:J1", {"backgroundColor": {"red": 0.0, "green": 0.1, "blue": 0.3}, "textFormat": {"foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}, "bold": True}})
    worksheet.freeze(rows=1)
    return worksheet

# ------------------------------------------------------------------------------
# 3. FUNCIONES DE SCRAPING (FASE 3 - MASTER VALIDATOR)
# ------------------------------------------------------------------------------
def clean_destination_and_flight(text):
    text = text.upper().strip()
    
    # Limpieza de "HOMOLOGADO" y normalización de espacios
    text = text.replace("HOMOLOGADO", " ").strip()
    text = re.sub(r'\s+', ' ', text)
    found_dest = "DESCONOCIDO"
    found_flight = "---"

    # 1. Identificar el Destino usando la Master List (Coincidencia Difusa)
    for d in DESTINOS_PERU:
        # Si el texto empieza con la ciudad o si la ciudad empieza con el texto (para casos truncados como CHICLAY)
        if text.startswith(d) or d.startswith(text[:6]):
            found_dest = d
            # Lo que sobra del texto original es el vuelo (limpiando posibles restos de la ciudad)
            # Removemos la parte de la ciudad del texto para aislar el vuelo
            potential_flight = text.replace(found_dest, "").replace(found_dest[:6], "").strip()
            # Si quedó vacío, probamos con regex para sacarlo del texto original
            if not potential_flight:
                match = re.search(r'([A-Z0-9]{2,3}\s*[0-9]{1,5})$', text)
                found_flight = match.group(0) if match else "---"
            else:
                found_flight = potential_flight
            break
    
    if found_dest == "DESCONOCIDO":
        # Fallback si no está en la lista (Vuelos internacionales o nuevos)
        match = re.search(r'([A-Z\s.-]+?)\s*([A-Z0-9]{2,3}\s*[0-9]{1,5})$', text)
        if match:
            found_dest, found_flight = match.group(1).strip(), match.group(2).strip()
        else:
            found_dest = text

    return found_dest, found_flight

def get_flight_data(vuelo_tipo="salidas"):
    print(f"📡 Iniciando extracción de {vuelo_tipo.upper()}...")
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        url = f"https://www.lima-airport.com/pasajeros/vuelos?adi={'departures' if vuelo_tipo == 'salidas' else 'arrivals'}"
        driver.get(url)
        
        wait = WebDriverWait(driver, 60)
        wait.until(EC.presence_of_element_located((By.XPATH, "//tr[td]")))
        
        for _ in range(8):
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(3)
        
        rows = driver.find_elements(By.XPATH, "//tr[td]")
        flights_list = []
        peru_now = datetime.now(timezone(timedelta(hours=-5)))
        now_str = peru_now.strftime("%H:%M:%S")
        fecha_today = peru_now.strftime("%d/%m/%Y")

        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            texts = [c.get_attribute("textContent").strip() for c in cells]
            if not texts or len(texts) < 2: continue

            # 1. TIEMPOS (Paso a paso: Limpieza de horas)
            h_prog, h_real = "", ""
            time_text = texts[0].replace("N/A", "").strip()
            if len(time_text) >= 10: 
                h_prog, h_real = time_text[:5], time_text[5:10]
            elif len(time_text) >= 5:
                h_prog = time_text[:5]
            else:
                h_prog = time_text if time_text else ""

            # 2. IDENTIFICACIÓN DE COLUMNAS (Mantra: Validación de estructura)
            # Usamos índices relativos al final para mayor estabilidad
            num_cols = len(texts)
            check_in, puerta, estado = "", "", ""
            
            if num_cols >= 6:
                # Estructura estándar: [..., Check-in, Puerta, Estado]
                estado = texts[-1]
                puerta = texts[-2]
                check_in = texts[-3]
                
                # Determinamos si el Destino y Vuelo están juntos o separados
                if num_cols >= 7:
                    # Caso: [Hora, Destino, Vuelo, Aerolínea, Check-in, Puerta, Estado]
                    raw_dest_vuelo = f"{texts[1]} {texts[2]}"
                else:
                    # Caso: [Hora, Destino/Vuelo, Aerolínea, Check-in, Puerta, Estado]
                    raw_dest_vuelo = texts[1]
            else:
                # Fallback para tablas minimalistas
                raw_dest_vuelo = texts[1]
                estado = texts[2] if num_cols > 2 else ""

            # 3. LIMPIEZA MAESTRA (Destino, Vuelo y Homologación)
            destino, vuelo = clean_destination_and_flight(raw_dest_vuelo)

            # 4. AEROLÍNEA (Desde logo)
            airline = "AEROLÍNEA"
            try:
                img = row.find_element(By.TAG_NAME, "img")
                airline = img.get_attribute("title") or img.get_attribute("alt") or airline
            except: pass

            data_row = [fecha_today, h_prog, h_real, destino, vuelo, airline, puerta, check_in, estado, now_str]
            if vuelo != "": flights_list.append(data_row)

        driver.quit()
        aqp = [f for f in flights_list if "AREQUIPA" in f[3]]
        print(f"📊 Total: {len(flights_list)} | ✈️ Arequipa Validados: {len(aqp)}")
        return flights_list
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'driver' in locals(): driver.quit()
        return []

def sync_to_sheets(ws, data):
    if not data: return
    print(f"♻️ Sincronizando datos limpios...")
    try: ws.delete_rows(2, 3000)
    except: pass
    ws.append_rows(data, value_input_option="USER_ENTERED")
    print("✨ ¡Proceso completado con éxito!")

# ------------------------------------------------------------------------------
# 4. EJECUCIÓN
# ------------------------------------------------------------------------------
try:
    ws_data = setup_google_sheet()
    data_vuelos = get_flight_data("salidas")
    sync_to_sheets(ws_data, data_vuelos)
except Exception as e:
    print(f"\n⚠️ Fallo: {e}")
