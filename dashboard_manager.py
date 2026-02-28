# ==============================================================================
# DASHBOARD MANAGER - LIMA AIRPORT
# Este archivo coordina el Bot de Telegram y genera los datos para el Mapa.
# NO MODIFICA EL ARCHIVO main.py ORIGINAL.
# ==============================================================================

import os

# TRUCO PARA LOCAL: Configurar tokens ficticios si no existen para evitar errores al importar main
if not os.environ.get('TELEGRAM_BOT_TOKEN'):
    os.environ['TELEGRAM_BOT_TOKEN'] = 'DUMMY_TOKEN_FOR_LOCAL_TEST'
if not os.environ.get('DATA_REPO_TOKEN'):
    os.environ['DATA_REPO_TOKEN'] = 'DUMMY_TOKEN_FOR_LOCAL_TEST'

import main
import json
import os
from datetime import datetime, timedelta, timezone
import config

# Configurar Zona Horaria de Perú (UTC-5)
timezone_peru = timezone(timedelta(hours=-5))

def obtener_hora_peru():
    return datetime.now(timezone_peru)

def parse_historial_vuelos():
    """Lee alertas_enviadas.txt y genera la lista de vuelos del día para el dashboard"""
    vuelos_historial = []
    sent_alerts_file = main.SENT_ALERTS_FILE
    hoy_str = obtener_hora_peru().strftime("%d/%m/%Y")
    
    if not os.path.exists(sent_alerts_file):
        return []

    with open(sent_alerts_file, 'r', encoding='utf-8') as f:
        lineas = f.readlines()

    for linea in lineas:
        linea = linea.strip()
        if not linea or "_" not in linea:
            continue
            
        partes = linea.split("_")
        if len(partes) < 4:
            continue
            
        # Detección inteligente de campos
        fecha = partes[0]
        # Filtrar solo los de HOY de inmediato para ahorrar proceso
        if fecha != hoy_str:
            continue

        hora = "--:--"
        vuelo = ""
        ciudad = ""
        sentido = ""

        # Si tenemos la hora (ej: 14:15), buscamos la parte que tenga ":"
        if ":" in partes[1] and len(partes[1]) == 5:
            hora = partes[1]
            vuelo = partes[2]
            ciudad = partes[3]
            sentido = partes[4] if len(partes) > 4 else "DESCONOCIDO"
        else:
            # Formato viejo o sin hora
            hora = "--:--"
            vuelo = partes[1]
            ciudad = partes[2]
            sentido = partes[3] if len(partes) > 3 else "DESCONOCIDO"

        # Identificar Aerolínea por prefijo de vuelo
        airline = "AEROLÍNEA"
        if len(vuelo) >= 2:
            code = vuelo[:2].upper()
            if code in config.AEROLINEAS:
                airline = config.AEROLINEAS[code]
            else:
                code3 = vuelo[:3].upper()
                if code3 in config.AEROLINEAS:
                    airline = config.AEROLINEAS[code3]

        vuelos_historial.append({
            'tipo': sentido,
            'fecha': fecha,
            'hora_prog': "--:--", # En el historial no guardamos la hora, pero el mapa lo necesita
            'hora_real': "",
            'ciudad': ciudad,
            'vuelo': vuelo,
            'aerolinea': airline,
            'estado': "CANCELADO"
        })
    
    return vuelos_historial

def ejecutar_ciclo_completo():
    hora_actual = obtener_hora_peru().strftime('%H:%M:%S')
    print(f"[{hora_actual}] 🚀 Iniciando ciclo de vigilancia (Hora Perú)...")

    try:
        # 1. Sincronizar datos (Viene de main.py)
        main.sync_from_private_repo()

        # 2. Procesar suscripciones nuevas (Viene de main.py)
        main.process_telegram_updates()

        # 3. Escanear vuelos cancelados (Viene de main.py)
        # Recogemos los vuelos nuevos de este momento para enviarlos a Telegram
        vuelos_recientes = []
        vuelos_recientes.extend(main.scan_for_cancelled_flights("SALIDAS"))
        vuelos_recientes.extend(main.scan_for_cancelled_flights("LLEGADAS"))

        # 4. ENVIAR ALERTAS A TELEGRAM (CRÍTICO)
        # Esto es lo que hace sonar los celulares
        if vuelos_recientes:
            main.send_cancellation_alerts(vuelos_recientes)
        else:
            print("✅ Todo despejado: No se detectaron cancelaciones nuevas para Telegram.")

        # 5. GENERAR DATOS HISTÓRICOS PARA EL DASHBOARD
        # Leemos el archivo que el scraper acaba de actualizar
        vuelos_hoy = parse_historial_vuelos()
        
        datos_dashboard = {
            "ultima_sincronizacion": obtener_hora_peru().strftime("%d/%m/%Y %H:%M:%S"),
            "conteo": len(vuelos_hoy),
            "vuelos": vuelos_hoy
        }

        with open("vuelos_dashboard.json", "w", encoding='utf-8') as f:
            json.dump(datos_dashboard, f, ensure_ascii=False, indent=4)
        
        print(f"📁 Dashboard actualizado con HISTORIAL del día ({len(vuelos_hoy)} vuelos).")

        # 5. Sincronizar cambios de vuelta (Suscriptores y Alertas)
        main.sync_to_private_repo()

        print(f"[{obtener_hora_peru().strftime('%H:%M:%S')}] ✨ Ciclo completado con éxito.")

    except Exception as e:
        print(f"❌ Error en el Dashboard Manager: {e}")

if __name__ == "__main__":
    ejecutar_ciclo_completo()
