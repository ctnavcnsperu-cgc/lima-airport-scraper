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

def parse_historial_vuelos(solo_hoy=False):
    """Lee alertas_enviadas.txt y genera la lista de vuelos para el dashboard o el historial completo"""
    vuelos_result = []
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
            
        fecha = partes[0]
        # Filtrar si se solicita solo hoy
        if solo_hoy and fecha != hoy_str:
            continue

        hora = "--:--"
        vuelo = ""
        ciudad = ""
        sentido = ""

        # Detección inteligente de formato (con o sin hora)
        if ":" in partes[1] and len(partes[1]) == 5:
            hora = partes[1]
            vuelo = partes[2]
            ciudad = partes[3]
            sentido = partes[4] if len(partes) > 4 else "DESCONOCIDO"
        else:
            hora = "--:--"
            vuelo = partes[1]
            ciudad = partes[2]
            sentido = partes[3] if len(partes) > 3 else "DESCONOCIDO"

        # Identificar Aerolínea
        airline = "AEROLÍNEA"
        if len(vuelo) >= 2:
            code = vuelo[:2].upper()
            if code in config.AEROLINEAS:
                airline = config.AEROLINEAS[code]
            else:
                code3 = vuelo[:3].upper()
                if code3 in config.AEROLINEAS:
                    airline = config.AEROLINEAS[code3]

        vuelos_result.append({
            'tipo': sentido,
            'fecha': fecha,
            'hora_prog': hora,
            'hora_real': "",
            'ciudad': ciudad,
            'vuelo': vuelo,
            'aerolinea': airline,
            'estado': "CANCELADO"
        })
    
    return vuelos_result

def ejecutar_ciclo_completo():
    hora_actual = obtener_hora_peru().strftime('%H:%M:%S')
    print(f"[{hora_actual}] 🚀 Iniciando ciclo de vigilancia (Hora Perú)...")

    try:
        # 1. Sincronizar datos (Viene de main.py)
        main.sync_from_private_repo()

        # 2. Procesar suscripciones nuevas (Viene de main.py)
        main.process_telegram_updates()

        # 3. Escanear vuelos cancelados (Viene de main.py)
        vuelos_recientes = []
        vuelos_recientes.extend(main.scan_for_cancelled_flights("SALIDAS"))
        vuelos_recientes.extend(main.scan_for_cancelled_flights("LLEGADAS"))

        # 4. ENVIAR ALERTAS A TELEGRAM
        if vuelos_recientes:
            main.send_cancellation_alerts(vuelos_recientes)
        else:
            print("✅ No se detectaron cancelaciones nuevas para Telegram.")

        # 5. GENERAR DATOS PARA EL MAPA (SOLO HOY)
        vuelos_hoy = parse_historial_vuelos(solo_hoy=True)
        datos_dashboard = {
            "ultima_sincronizacion": obtener_hora_peru().strftime("%d/%m/%Y %H:%M:%S"),
            "conteo": len(vuelos_hoy),
            "vuelos": vuelos_hoy
        }
        with open("vuelos_dashboard.json", "w", encoding='utf-8') as f:
            json.dump(datos_dashboard, f, ensure_ascii=False, indent=4)
        print(f"📁 Dashboard (Mapa) actualizado: {len(vuelos_hoy)} vuelos de hoy.")

        # 6. GENERAR DATOS HISTÓRICOS (TODO EL ARCHIVO)
        vuelos_totales = parse_historial_vuelos(solo_hoy=False)
        datos_historial = {
            "ultima_sincronizacion": obtener_hora_peru().strftime("%d/%m/%Y %H:%M:%S"),
            "conteo": len(vuelos_totales),
            "vuelos": vuelos_totales
        }
        with open("vuelos_history.json", "w", encoding='utf-8') as f:
            json.dump(datos_historial, f, ensure_ascii=False, indent=4)
        print(f"📁 Historial consolidado generado: {len(vuelos_totales)} alertas totales.")

        # 7. Sincronizar cambios de vuelta al repo privado
        main.sync_to_private_repo()

        print(f"[{obtener_hora_peru().strftime('%H:%M:%S')}] ✨ Ciclo completado con éxito.")

    except Exception as e:
        print(f"❌ Error en el Dashboard Manager: {e}")

if __name__ == "__main__":
    ejecutar_ciclo_completo()
