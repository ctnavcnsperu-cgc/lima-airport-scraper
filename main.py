# ==============================================================================
# PROYECTO: LIMA AIRPORT CANCELATION ALERTS - TELEGRAM BOT
# ==============================================================================

import os
import re
import time
import json
import requests
from datetime import datetime, timedelta, timezone
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ------------------------------------------------------------------------------
# 1. CONFIGURACIÓN DE TELEGRAM BOT
# ------------------------------------------------------------------------------
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
SUBSCRIBERS_FILE = 'suscriptores.txt'
SENT_ALERTS_FILE = 'alertas_enviadas.txt'

if not TELEGRAM_BOT_TOKEN:
    print("❌ ERROR: Variable TELEGRAM_BOT_TOKEN no encontrada en Secrets")
    exit(1)

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# ------------------------------------------------------------------------------
# 2. FUNCIONES DE TELEGRAM
# ------------------------------------------------------------------------------

def get_subscribers():
    """Lee la lista de usuarios suscritos"""
    if not os.path.exists(SUBSCRIBERS_FILE):
        return []
    with open(SUBSCRIBERS_FILE, 'r') as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def add_subscriber(chat_id):
    """Agrega un nuevo suscriptor"""
    subscribers = get_subscribers()
    if str(chat_id) not in subscribers:
        with open(SUBSCRIBERS_FILE, 'a') as f:
            f.write(f"{chat_id}\n")
        return True
    return False

def remove_subscriber(chat_id):
    """Elimina un suscriptor"""
    subscribers = get_subscribers()
    if str(chat_id) in subscribers:
        subscribers.remove(str(chat_id))
        with open(SUBSCRIBERS_FILE, 'w') as f:
            f.write('\n'.join(subscribers) + '\n')
        return True
    return False

def send_telegram_message(chat_id, text):
    """Envía un mensaje de Telegram a un chat específico"""
    try:
        url = f"{TELEGRAM_API_URL}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        response = requests.post(url, data=data, timeout=10)
        return response.json().get('ok', False)
    except Exception as e:
        print(f"⚠️ Error enviando mensaje a {chat_id}: {e}")
        return False

def process_telegram_updates():
    """Procesa mensajes nuevos de usuarios (suscripciones)"""
    try:
        url = f"{TELEGRAM_API_URL}/getUpdates"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if not data.get('ok'):
            return
        
        for update in data.get('result', []):
            message = update.get('message', {})
            chat_id = message.get('chat', {}).get('id')
            text = message.get('text', '').lower().strip()
            
            if not chat_id:
                continue
            
            if text == '/start':
                if add_subscriber(chat_id):
                    send_telegram_message(
                        chat_id,
                        "✅ <b>Suscripción activada</b>\n\n"
                        "Recibirás alertas automáticas cuando se detecten vuelos cancelados "
                        "en el Aeropuerto de Lima.\n\n"
                        "Comandos disponibles:\n"
                        "/start - Suscribirse a alertas\n"
                        "/stop - Cancelar suscripción"
                    )
                else:
                    send_telegram_message(chat_id, "ℹ️ Ya estabas suscrito a las alertas.")
            
            elif text == '/stop':
                if remove_subscriber(chat_id):
                    send_telegram_message(
                        chat_id,
                        "🔕 <b>Suscripción cancelada</b>\n\n"
                        "Ya no recibirás alertas. Escribe /start para volver a suscribirte."
                    )
                else:
                    send_telegram_message(chat_id, "ℹ️ No estabas suscrito.")
        
        # Limpiar updates procesados
        if data.get('result'):
            last_update_id = data['result'][-1]['update_id']
            requests.get(f"{TELEGRAM_API_URL}/getUpdates?offset={last_update_id + 1}", timeout=5)
    
    except Exception as e:
        print(f"⚠️ Error procesando updates de Telegram: {e}")

# ------------------------------------------------------------------------------
# 3. SISTEMA DE MEMORIA DE ALERTAS
# ------------------------------------------------------------------------------

def get_sent_alerts():
    """Lee las alertas ya enviadas"""
    if not os.path.exists(SENT_ALERTS_FILE):
        return set()
    with open(SENT_ALERTS_FILE, 'r') as f:
        return set(line.strip() for line in f.readlines())

def mark_alert_as_sent(flight_key):
    """Marca una alerta como enviada"""
    with open(SENT_ALERTS_FILE, 'a') as f:
        f.write(f"{flight_key}\n")

# ------------------------------------------------------------------------------
# 4. FUNCIONES DE SCRAPING
# ------------------------------------------------------------------------------

DESTINOS_PERU = [
    "AREQUIPA", "AYACUCHO", "CAJAMARCA", "CHACHAPOYAS", "CHICLAYO", "CUSCO", 
    "HUANUCO", "ANTA - HUARAZ", "IQUITOS", "JAUJA", "JAEN", 
    "JULIACA", "MAZAMARI", "PIURA", "PUCALLPA", "PUERTO MALDONADO", "TACNA", 
    "TALARA", "TARAPOTO", "TRUJILLO", "TUMBES", "YURIMAGUAS", "ILO", "PISCO",
    "TINGO MARIA", "ANDAHUAYLAS", "NUEVO MUNDO"
]

def clean_destination_and_flight(text):
    """Extrae destino y número de vuelo del texto combinado"""
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

def scan_for_cancelled_flights():
    """Escanea la web en busca de vuelos cancelados"""
    print("📡 Iniciando escaneo de vuelos cancelados...")
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    cancelled_flights = []
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        url = "https://www.lima-airport.com/pasajeros/vuelos?adi=departures"
        driver.get(url)
        
        wait = WebDriverWait(driver, 60)
        wait.until(EC.presence_of_element_located((By.XPATH, "//tr[td]")))
        
        # Scroll optimizado (solo 3 veces para reducir tiempo)
        for _ in range(3):
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(2)
        
        rows = driver.find_elements(By.XPATH, "//tr[td]")
        peru_now = datetime.now(timezone(timedelta(hours=-5)))
        fecha_today = peru_now.strftime("%d/%m/%Y")
        
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            texts = [c.get_attribute("textContent").strip() for c in cells]
            
            if not texts or len(texts) < 2:
                continue
            
            # Buscar específicamente la palabra "CANCELADO" en el estado
            estado = texts[-1].upper().strip()
            print(f"DEBUG: Vuelo a {texts[1]} tiene estado -> '{estado}'")
            
            
            if "CONFIRMADO" not in estado:
                continue  # Saltar si no está cancelado
            
            # Extraer horarios
            h_prog, h_real = "", ""
            time_text = texts[0].replace("N/A", "").strip()
            if len(time_text) >= 10:
                h_prog, h_real = time_text[:5], time_text[5:10]
            elif len(time_text) >= 5:
                h_prog = time_text[:5]
            
            # Extraer otros datos
            num_cols = len(texts)
            check_in, puerta = "", ""
            
            if num_cols >= 6:
                puerta = texts[-2]
                check_in = texts[-3]
                raw_dest_vuelo = f"{texts[1]} {texts[2]}" if num_cols >= 7 else texts[1]
            else:
                raw_dest_vuelo = texts[1]
            
            destino, vuelo = clean_destination_and_flight(raw_dest_vuelo)
            
            # Extraer aerolínea
            airline = "AEROLÍNEA"
            try:
                img = row.find_element(By.TAG_NAME, "img")
                airline = img.get_attribute("title") or img.get_attribute("alt") or airline
            except:
                pass
            
            cancelled_flights.append({
                'fecha': fecha_today,
                'hora_prog': h_prog,
                'hora_real': h_real,
                'destino': destino,
                'vuelo': vuelo,
                'aerolinea': airline,
                'puerta': puerta,
                'checkin': check_in,
                'estado': estado
            })
        
        driver.quit()
        print(f"🔍 Vuelos cancelados encontrados: {len(cancelled_flights)}")
        return cancelled_flights
    
    except Exception as e:
        print(f"❌ Error durante el escaneo: {e}")
        if 'driver' in locals():
            driver.quit()
        return []

# ------------------------------------------------------------------------------
# 5. SISTEMA DE ALERTAS
# ------------------------------------------------------------------------------

def send_cancellation_alerts(cancelled_flights):
    """Envía alertas de vuelos cancelados a todos los suscriptores"""
    if not cancelled_flights:
        print("✅ No hay vuelos cancelados para alertar.")
        return
    
    subscribers = get_subscribers()
    
    if not subscribers:
        print("ℹ️ No hay suscriptores registrados.")
        return
    
    sent_alerts = get_sent_alerts()
    
    for flight in cancelled_flights:
        # Crear identificador único del vuelo
        flight_key = f"{flight['fecha']}_{flight['vuelo']}_{flight['destino']}"
        
        # Verificar si ya se envió esta alerta
        if flight_key in sent_alerts:
            print(f"⏭️ Alerta ya enviada para: {flight['vuelo']} - {flight['destino']}")
            continue
        
        # Construir mensaje
        message = (
            f"🚨 <b>VUELO CANCELADO</b>\n\n"
            f"📅 <b>Fecha:</b> {flight['fecha']}\n"
            f"✈️ <b>Vuelo:</b> {flight['vuelo']}\n"
            f"🌍 <b>Destino:</b> {flight['destino']}\n"
            f"🏢 <b>Aerolínea:</b> {flight['aerolinea']}\n"
            f"🕐 <b>Hora Prog.:</b> {flight['hora_prog']}\n"
        )
        
        if flight['hora_real']:
            message += f"🕑 <b>Nueva Hora:</b> {flight['hora_real']}\n"
        if flight['puerta']:
            message += f"🚪 <b>Puerta:</b> {flight['puerta']}\n"
        if flight['checkin']:
            message += f"🎫 <b>Check-in:</b> {flight['checkin']}\n"
        
        message += f"\n❌ <b>Estado:</b> {flight['estado']}"
        
        # Enviar a todos los suscriptores
        for chat_id in subscribers:
            send_telegram_message(chat_id, message)
        
        # Marcar como enviada
        mark_alert_as_sent(flight_key)
        print(f"✉️ Alerta enviada: {flight['vuelo']} - {flight['destino']}")

# ------------------------------------------------------------------------------
# 6. EJECUCIÓN PRINCIPAL
# ------------------------------------------------------------------------------

if __name__ == "__main__":
    try:
        print("🤖 Lima Airport Alert Bot - Iniciando...")
        
        # Procesar suscripciones nuevas
        print("📨 Procesando comandos de usuarios...")
        process_telegram_updates()
        
        # Escanear vuelos cancelados
        cancelled_flights = scan_for_cancelled_flights()
        
        # Enviar alertas
        send_cancellation_alerts(cancelled_flights)
        
        print("✨ Proceso completado con éxito.")
    
    except Exception as e:
        print(f"\n⚠️ El proceso falló: {e}")
