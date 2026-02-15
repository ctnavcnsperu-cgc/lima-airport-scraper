# Plan de Desarrollo: Scraping Lima Airport a Google Sheets

Este documento detalla los pasos para desarrollar el sistema de extracción de datos de vuelos del Aeropuerto Jorge Chávez (LAP) y su sincronización automática con Google Sheets mediante Google Colab.

## 🎯 Objetivo
Extraer información en tiempo real de vuelos (Salidas/Llegadas) desde la web oficial de Lima Airport y almacenarla de forma estructurada en una hoja de Google Sheets denominada **"Lima Airport Data"**.

---

## 🛠️ Requisitos Técnico
- **Plataforma**: Google Colab (Entorno de ejecución de Python en la nube).
- **Librerías principales**: `requests`, `pandas`, `gspread`, `google-auth`.
- **Almacenamiento**: Google Sheets API.

---

## 🚀 Fases del Desarrollo

### Fase 1: Entorno y Autenticación
1. **Configuración de Colab**: Instalación de dependencias necesarias.
2. **Autenticación nativa**: Uso de `google.colab.auth` para vincular la cuenta de Google sin necesidad de archivos de credenciales externos.
3. **Inicialización de Clientes**: Configurar el acceso a Google Drive y Google Sheets.

### Fase 2: Infraestructura en Google Sheets
1. **Creación del Archivo**: Crear por código el libro `Lima Airport Data`.
2. **Configuración de Pestañas**: Crear la pestaña `Data` y eliminar hojas por defecto.
3. **Encabezados**: Definir la fila de títulos basado en la captura de referencia:
   - Fecha, Hora Prog., Nueva Hora, Destino, Vuelo, Aerolínea, Puerta, Check-in, Estado.

### Fase 3: Ingeniería de Extracción (Scraping)
1. **Detección de Endpoints**: Identificar las URLs de los servicios JSON que alimentan la web de LAP.
2. **Manejo de Cabeceras (Headers)**: Simular un navegador real para evitar bloqueos por seguridad.
3. **Parsing de Datos**: Limpiar el JSON para convertirlo en una tabla de Python (Dataframe).

### Fase 4: Sincronización de Datos
1. **Lógica de Actualización**:
   - Comparar datos nuevos con existentes.
   - Limpiar la hoja e insertar la data fresca.
2. **Formateo Condicional**: (Opcional) Aplicar colores a los estados (ej. Morado para "Embarque Finalizado").

### Fase 5: Automatización
1. **Bucle de Ejecución**: Implementar un ciclo que repita el proceso cada X minutos (ej. 15 min).
2. **Timestamp de Control**: Añadir una celda con la última hora de actualización exitosa.

---

## 📋 Estructura de Datos Esperada
| Campo | Origen | Descripción |
| :--- | :--- | :--- |
| **Fecha** | Web | Fecha del vuelo (DD/MM/YYYY) |
| **Hora Prog.** | Web | Horario original de salida/llegada |
| **Nueva Hora** | Web | Horario reprogramado (si aplica) |
| **Destino** | Web | Ciudad de origen o destino |
| **Vuelo** | Web | Código alfanumérico del vuelo |
| **Aerolínea** | Web | Nombre de la compañía aérea |
| **Puerta** | Web | Puerta de embarque asignada |
| **Check-in** | Web | Mostradores asignados |
| **Estado** | Web | Estado actual (Confirmado, Finalizado, etc.) |

---

## 🧘 Mantra de Desarrollo
**PAZ INTERIOR** - Paso a paso, siguiendo las instrucciones y validando cada fase.
