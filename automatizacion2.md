# Plan Maestro de Automatización 2.0: Lima Airport Alert Bot

Este documento detalla la estrategia para escalar el bot de alertas, optimizar el uso de recursos de GitHub y garantizar la privacidad de los datos de los usuarios.

## 🎯 objetivos Principales
1.  **Recursos Ilimitados:** Migrar a repositorio público para obtener minutos gratuitos de GitHub Actions sin restricciones.
2.  **Privacidad Total:** Implementar un segundo repositorio privado para almacenar datos sensibles (suscriptores y alertas).
3.  **Monitoreo Total:** Escanear Salidas y Llegadas las 24 horas, cada 10 minutos.
4.  **Eficiencia:** Consolidar todo en un solo flujo de trabajo (Workflow) y un solo Cron-job.

---

## 🛠️ Fase 1: Arquitectura de Seguridad (Lo Primero)
Antes de hacer público el código, debemos preparar la "caja fuerte" para los datos.

1.  **Crear Repositorio Privado:** Crear un nuevo repositorio en GitHub (ej. `lima-airport-data`) que sea **PRIVADO**.
2.  **Generar PAT (Personal Access Token):** Crear un token en GitHub con permisos `repo` para que el script del repositorio público pueda escribir en el privado.
    *   **Pasos para crear el Token:**
        1.  Perfil -> **Settings** -> **Developer settings**.
        2.  **Personal access tokens** -> **Tokens (classic)**.
        3.  **Generate new token** -> **Generate new token (classic)**.
        4.  **Note:** `Lima Airport Data Access`.
        5.  **Expiration:** `90 days` o `No expiration`.
        6.  **Scopes:** Marcar la casilla completa de **`repo`**.
        7.  **Generate token** y COPIAR el código `ghp_...` (no se volverá a mostrar).
3.  **Configurar Secretos:** Agregar el nuevo token como un secreto en el repositorio principal (`DATA_REPO_TOKEN`).
4.  **Lógica de Sincronización:** Modificar el código para que al iniciar descargue los archivos `.txt` del repo privado y al terminar los suba actualizados.

---

## 🧠 Fase 2: Expansión de Lógica y Limpieza
Preparar el cerebro del bot para manejar más información de forma ordenada.

1.  **Modularización (`config.py`):**
    *   Mover el diccionario de `AEROLINEAS` y `DESTINOS_PERU`.
    *   Definir URLs de Salidas y Llegadas.
2.  **Generalización del Scraper:**
    *   Modificar `scan_for_cancelled_flights(tipo)` para que funcione con ambas URLs.
    *   Ajustar la captura de datos (Origen vs. Destino).
3.  **Mensajería Dinámica:**
    *   Adaptar el mensaje de Telegram: `🚨 SALIDA CANCELADA` vs `🚨 LLEGADA CANCELADA`.
4.  **Pruebas Locales:** Verificar que el bot detecta ambos tipos de vuelos y los procesa correctamente.

---

## 🚀 Fase 3: El Gran Salto (Producción)
Puesta en marcha del sistema 24/7.

1.  **Configuración del `.gitignore`:** Asegurar que los archivos locales `.txt`, `.json` y carpetas de `backups` nunca se suban al repo público.
2.  **Cambio de Visibilidad:** Cambiar el repositorio principal de **Privado** a **Público**.
3.  **Consolidación de Cron-job:** 
    *   Actualizar `Cron-job.org` para que apunte al nuevo flujo único.
    *   Configurar frecuencia a **cada 10 minutos**.
4.  **Monitoreo Inicial:** Supervisar las primeras ejecuciones en GitHub Actions para asegurar que el tiempo de ejecución sea óptimo y los archivos se guarden en el repo privado.

---

## 📝 Notas de Mantenimiento
*   **Repositorio Público:** Código, lógica y configuración no sensible.
*   **Repositorio Privado:** `suscriptores.txt` y `alertas_enviadas.txt`.
*   **GitHub Secrets:** `TELEGRAM_BOT_TOKEN` y `DATA_REPO_TOKEN`.

---
*Plan creado por Antigravity - 2026-02-17*
