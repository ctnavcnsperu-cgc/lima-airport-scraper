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
from datetime import datetime

def ejecutar_ciclo_completo():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 Iniciando ciclo de vigilancia...")

    try:
        # 1. Sincronizar datos (Viene de main.py)
        # Descarga la lista de suscriptores y alertas ya enviadas
        main.sync_from_private_repo()

        # 2. Procesar suscripciones nuevas (Viene de main.py)
        # Revisa si hay nuevos usuarios que escribieron /start
        main.process_telegram_updates()

        # 3. Escanear vuelos cancelados (Viene de main.py)
        # Hace el raspado una sola vez para ahorrar tráfico
        vuelos_totales = []
        vuelos_totales.extend(main.scan_for_cancelled_flights("SALIDAS"))
        vuelos_totales.extend(main.scan_for_cancelled_flights("LLEGADAS"))

        # 4. Enviar Alertas por Telegram (Viene de main.py)
        # Solo enviará los que no se han enviado antes
        if vuelos_totales:
            main.send_cancellation_alerts(vuelos_totales)
        else:
            print("✅ Todo despejado: No se detectaron vuelos cancelados.")

        # 5. GENERAR DATOS PARA EL DASHBOARD (Nueva funcionalidad)
        # Preparamos el JSON que leerá el mapa de Leaflet
        datos_dashboard = {
            "ultima_sincronizacion": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "conteo": len(vuelos_totales),
            "vuelos": vuelos_totales
        }

        with open("vuelos_dashboard.json", "w", encoding='utf-8') as f:
            json.dump(datos_dashboard, f, ensure_ascii=False, indent=4)
        
        print("📁 Datos para el mapa actualizados en 'vuelos_dashboard.json'.")

        # 6. Sincronizar cambios de vuelta (Viene de main.py)
        # Sube los suscriptores y alertas enviadas a GitHub
        main.sync_to_private_repo()

        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✨ Ciclo completado con éxito.")

    except Exception as e:
        print(f"❌ Error en el Dashboard Manager: {e}")

if __name__ == "__main__":
    ejecutar_ciclo_completo()
