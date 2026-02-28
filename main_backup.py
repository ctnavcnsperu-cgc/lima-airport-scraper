# ==============================================================================
# PROYECTO: LIMA AIRPORT FLIGHT DATA SCRAPER - GITHUB ACTIONS VERSION
# ==============================================================================

import gspread
import pandas as pd
import requests
import time
import os
import re
import json
from datetime import datetime, timedelta, timezone
from google.oauth2 import service_account
from googleapiclient.discovery import build
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ------------------------------------------------------------------------------
# 1. CONFIGURACIÓN DE AUTENTICACIÓN (GITHUB SECRETS)
# ------------------------------------------------------------------------------
print("🔐 Iniciando autenticación mediante GitHub Secrets...")

def get_google_creds():
    # Buscamos la llave en las variables de entorno de GitHub
    service_account_info = os.environ.get('GCP_SERVICE_ACCOUNT_KEY')
    
    if not service_account_info:
        raise Exception("❌ ERROR: No se encontró la variable 'GCP_SERVICE_ACCOUNT_KEY' en los Secrets de GitHub.")
    
    # Cargamos el JSON desde el string guardado en el Secret
    info = json.loads(service_account_info)
    
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    creds = service_account.Credentials.from_service_account_info(info, scopes=scopes)
    return creds

# Inicialización de clientes
try:
    creds = get_google_creds()
    gc = gspread.authorize(creds)
    drive_service = build('drive', 'v3', credentials=creds)
except Exception as e:
    print(f"❌ Error en autenticación: {e}")
    exit(1)

# ------------------------------------------------------------------------------
# 2. CONFIGURACIÓN DE INFRAESTRUCTURA
# ------------------------------------------------------------------------------
SHEET_NAME = "Lima Airport Data"
WORKSHEET_NAME = "Data"

# DICCIONARIO MAESTRO DE DESTINOS (PERÚ) - SIN TILDES Y EN MAYÚSCULAS
DESTINOS_PERU = [
    "AREQUIPA", "AYACUCHO", "CAJAMARCA", "CHACHAPOYAS", "CHICLAYO", "CUSCO", 
    "HUANUCO", "ANTA - HUARAZ", "IQUITOS", "JAUJA", "JAEN", 
    "JULIACA", "MAZAMARI", "PIURA", "PUCALLPA", "PUERTO MALDONADO", "TACNA", 
    "TALARA", "TARAPOTO", "TRUJILLO", "TUMBES", "YURIMAGUAS", "ILO", "PISCO",
    "TINGO MARIA", "ANDAHUAYLAS", "NUEVO MUNDO"
]

def setup_google_sheet():
    print("🔍 Buscando carpeta y hoja en Google Drive...")
    
    # Buscar carpeta 'lima airport'
    q_folder = "(name = 'lima airport' or name = 'LIMA AIRPORT') and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    folders = drive_service.files().list(q=q_folder, fields='files(id)').execute().get('files', [])
    folder_id = folders[0]['id'] if folders else None

    # Buscar la hoja de cálculo
    q_sheet = f"name = '{SHEET_NAME}' and mimeType = 'application/vnd.google-apps.spreadsheet' and trashed = false"
    sheets = drive_service.files().list(q=q_sheet, fields='files(id)').execute().get('files', [])
    
    if sheets:
        sh = gc.open_by_key(sheets[0]['id'])
        print(f"✅ Hoja encontrada: {SHEET_NAME}")
    else:
        print(f"📝 Creando nueva hoja: {SHEET_NAME}")
        sh = gc.create(SHEET_NAME)
        if folder_id:
            drive_service.files().update(fileId=sh.id, addParents=folder_id, removeParents='root').execute()
        
        # 🔑 COMPARTIR CON EL USUARIO (Para que aparezca en tu Drive)
        try:
            sh.share('ctnavcnsperu@gmail.com', perm_type='user', role='writer')
            print("👤 Hoja compartida con ctnavcnsperu@gmail.com")
        except Exception as e:
            print(f"⚠️ No se pudo compartir la hoja: {e}")

    try:
        worksheet = sh.worksheet(WORKSHEET_NAME)
    except:
        print(f"📝 Creando pestaña específica: {WORKSHEET_NAME}")
        worksheet = sh.add_worksheet(title=WORKSHEET_NAME, rows="2000", cols="15")
        try: sh.del_worksheet(sh.worksheet('Sheet1'))
        except: pass

    # Encabezados
    headers = ["Fecha", "Hora Prog.", "Nueva Hora", "Destino", "Vuelo", "Aerolínea", "Puerta", "Check-in", "Estado", "Última Actualización"]
    worksheet.clear()
    worksheet.append_row(headers)
    
    # Formato de cabecera (Azul oscuro, Texto blanco negrita)
    worksheet.format("A1:J1", {
        "backgroundColor": {"red": 0.0, "green": 0.1, "blue": 0.3}, 
        "textFormat": {"foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0}, "bold": True}
    })
    worksheet.freeze(rows=1)
    return worksheet

# ------------------------------------------------------------------------------
# 3. FUNCIONES DE SCRAPING
# ------------------------------------------------------------------------------
def clean_destination_and_flight(text):
    text = text.upper().strip()
    text = text.replace("HOMOLOGADO", " ").strip()
    text = re.sub(r'\s+', ' ', text)
    found_dest = "DESCONOCIDO"
    found_flight = "---"

    for d in DESTINOS_PERU:
        if text.startswith(d) or d.startswith(text[:6]):
            found_dest = d
            potential_flight = text.replace(found_dest, "").replace(found_dest[:6], "").strip()
            if not potential_flight:
                match = re.search(r'([A-Z0-9]{2,3}\s*[0-9]{1,5})$', text)
                found_flight = match.group(0) if match else "---"
            else:
                found_flight = potential_flight
            break
    
    if found_dest == "DESCONOCIDO":
        match = re.search(r'([A-Z\s.-]+?)\s*([A-Z0-9]{2,3}\s*[0-9]{1,5})$', text)
        if match:
            found_dest, found_flight = match.group(1).strip(), match.group(2).strip()
        else:
            found_dest = text

    return found_dest, found_flight

def get_flight_data(vuelo_tipo="salidas"):
    print(f"📡 Iniciando extracción de {vuelo_tipo.upper()}...")
    
    chrome_options = Options()
    chrome_options.add_argument('--headless') # Requerido para servidores
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')
    
    try:
        # Usamos service y webdriver-manager para asegurar la compatibilidad en GitHub
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        url = f"https://www.lima-airport.com/pasajeros/vuelos?adi={'departures' if vuelo_tipo == 'salidas' else 'arrivals'}"
        driver.get(url)
        
        wait = WebDriverWait(driver, 60)
        wait.until(EC.presence_of_element_located((By.XPATH, "//tr[td]")))
        
        # Scroll para cargar contenido dinámico
        for _ in range(8):
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(3)
        
        rows = driver.find_elements(By.XPATH, "//tr[td]")
        flights_list = []
        peru_now = datetime.now(timezone(timedelta(hours=-5))) # Hora Perú
        now_str = peru_now.strftime("%H:%M:%S")
        fecha_today = peru_now.strftime("%d/%m/%Y")

        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            texts = [c.get_attribute("textContent").strip() for c in cells]
            if not texts or len(texts) < 2: continue

            h_prog, h_real = "", ""
            time_text = texts[0].replace("N/A", "").strip()
            if len(time_text) >= 10: 
                h_prog, h_real = time_text[:5], time_text[5:10]
            elif len(time_text) >= 5:
                h_prog = time_text[:5]
            else:
                h_prog = time_text if time_text else ""

            num_cols = len(texts)
            check_in, puerta, estado = "", "", ""
            
            if num_cols >= 6:
                estado = texts[-1]
                puerta = texts[-2]
                check_in = texts[-3]
                
                if num_cols >= 7:
                    raw_dest_vuelo = f"{texts[1]} {texts[2]}"
                else:
                    raw_dest_vuelo = texts[1]
            else:
                raw_dest_vuelo = texts[1]
                estado = texts[2] if num_cols > 2 else ""

            destino, vuelo = clean_destination_and_flight(raw_dest_vuelo)

            airline = "AEROLÍNEA"
            try:
                img = row.find_element(By.TAG_NAME, "img")
                airline = img.get_attribute("title") or img.get_attribute("alt") or airline
            except: pass

            data_row = [fecha_today, h_prog, h_real, destino, vuelo, airline, puerta, check_in, estado, now_str]
            if vuelo != "": flights_list.append(data_row)

        driver.quit()
        print(f"📊 Total vuelos extraídos: {len(flights_list)}")
        return flights_list
    except Exception as e:
        print(f"❌ Error durante el scraping: {e}")
        if 'driver' in locals(): driver.quit()
        return []

def sync_to_sheets(ws, data):
    if not data: return
    print(f"♻️ Sincronizando {len(data)} filas con Google Sheets...")
    # Limpiamos datos antiguos (excepto cabecera)
    try: ws.delete_rows(2, 3000)
    except: pass
    ws.append_rows(data, value_input_option="USER_ENTERED")
    print("✨ ¡Sincronización completada!")

# ------------------------------------------------------------------------------
# 4. EJECUCIÓN PRINCIPAL
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        ws_data = setup_google_sheet()
        data_vuelos = get_flight_data("salidas")
        sync_to_sheets(ws_data, data_vuelos)
    except Exception as e:
        print(f"\n⚠️ El proceso falló: {e}")
