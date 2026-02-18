# ==============================================================================
# CONFIGURACIÓN DEL PROYECTO LIMA AIRPORT ALERT BOT
# ==============================================================================

import os

# 1. CONFIGURACIÓN DE RUTAS Y ARCHIVOS
SUBSCRIBERS_FILE = 'suscriptores.txt'
SENT_ALERTS_FILE = 'alertas_enviadas.txt'
GITHUB_DATA_REPO = "ctnavcnsperu-cgc/lima-airport-data"
TELEGRAM_ADMIN_ID = os.environ.get('TELEGRAM_ADMIN_ID')

# 2. URLs DEL AEROPUERTO
URL_SALIDAS = "https://www.lima-airport.com/pasajeros/vuelos?day=today&adi=departures"
URL_LLEGADAS = "https://www.lima-airport.com/pasajeros/vuelos?day=today&adi=arrivals"

# 3. LISTA DE DESTINOS DOMÉSTICOS (PERÚ)
DESTINOS_PERU = [
    "AREQUIPA", "AYACUCHO", "CAJAMARCA", "CHACHAPOYAS", "CHICLAYO", "CUSCO", 
    "HUANUCO", "ANTA - HUARAZ", "IQUITOS", "JAUJA", "JAEN", 
    "JULIACA", "MAZAMARI", "PIURA", "PUCALLPA", "PUERTO MALDONADO", "TACNA", 
    "TALARA", "TARAPOTO", "TRUJILLO", "TUMBES", "YURIMAGUAS", "ILO", "PISCO",
    "TINGO MARIA", "ANDAHUAYLAS", "NUEVO MUNDO"
]

# 4. DICCIONARIO MAESTRO DE AEROLÍNEAS (IATA CODES)
AEROLINEAS = {
    "LA": "LATAM Airlines",
    "H2": "Sky Airline",
    "SKY": "Sky Airline",
    "CC": "LATAM Airlines",
    "LP": "LATAM Airlines Peru",
    "XL": "LATAM Airlines Ecuador",
    "4C": "LATAM Airlines Colombia",
    "AV": "Avianca",
    "A0": "Avianca Peru",
    "2K": "Avianca Ecuador",
    "CM": "Copa Airlines",
    "AA": "American Airlines",
    "DL": "Delta Air Lines",
    "UA": "United Airlines",
    "AC": "Air Canada",
    "AM": "Aeroméxico",
    "IB": "Iberia",
    "UX": "Air Europa",
    "AF": "Air France",
    "KL": "KLM",
    "AR": "Aerolíneas Argentinas",
    "JA": "JetSmart",
    "JZ": "JetSmart",
    "VV": "Viva Air",
    "P9": "Peruvian Airlines",
    "2I": "Star Peru",
    "L5": "Atlas Air",
    "M0": "Aero Mongolia",
    "V0": "Conviasa",
    "QL": "LASER Airlines",
    "R7": "Aserca Airlines",
    "Z8": "Amaszonas",
    "OB": "Boliviana de Aviación",
    "H8": "Latin American Wings",
    "NK": "Spirit Airlines",
    "B6": "JetBlue",
    "F9": "Frontier Airlines",
    "WN": "Southwest Airlines", 
    "AT": "Royal Air Maroc",
    "LH": "Lufthansa", 
    "LX": "Swiss International Air Lines",
    "OS": "Austrian Airlines",
    "SN": "Brussels Airlines",
    "TK": "Turkish Airlines",
    "TP": "TAP Air Portugal",
    "VS": "Virgin Atlantic",
    "BA": "British Airways",
    "AZ": "ITA Airways",
    "KE": "Korean Air",
    "NH": "All Nippon Airways",
    "JL": "Japan Airlines",
    "CX": "Cathay Pacific",
    "QF": "Qantas",
    "NZ": "Air New Zealand",
    "EK": "Emirates",
    "QR": "Qatar Airways",
    "EY": "Etihad Airways",
    "AI": "Air India",
    "SA": "South African Airways",
    "ET": "Ethiopian Airlines",
    "MS": "EgyptAir"
}
