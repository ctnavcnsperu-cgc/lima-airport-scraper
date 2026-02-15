
### 3. GitHub Actions (Gratis y Potente) - RECOMENDADO
GitHub ofrece servidores gratuitos (runners) para ejecutar scripts de Python de forma programada.
- **Cómo funciona**: Creas un archivo `.yml` que ordena a GitHub encender una "computadora virtual", instalar Chrome, Selenium y correr tu script.
- **Autenticación**: Se utiliza una **Cuenta de Servicio de Google** (archivo JSON) guardada de forma segura en los "GitHub Secrets".
- **Horario (Cron)**: Tú defines la frecuencia (ej. cada 20 minutos, 1 hora, etc.).
- **Ventaja**: 100% gratuito, confiable, con alertas al correo si el proceso falla y totalmente independiente de tu PC.

---

## 🛠️ Pasos para Implementar GitHub Actions

1. **Configuración en Google Cloud (Paso a Paso)**:
   - **Consola**: Entra a [console.cloud.google.com](https://console.cloud.google.com/).
   - **Proyecto**: Haz clic en el selector de proyectos (arriba a la izquierda) > **PROYECTO NUEVO**. Nombre sugerido: `Lima Airport Scraper`.
   - **APIs**: Busca y haz clic en **HABILITAR** para:
     - `Google Sheets API`
     - `Google Drive API`
   - **Cuenta de Servicio (El Robot)**: 
     - Ve a `IAM y administración` > `Cuentas de servicio`.
     - `+ CREAR CUENTA DE SERVICIO`. Nombre: `scraper-bot`.
     - **Rol**: Selecciona `Básico` > `Editor`.
     - Finaliza con `LISTO`.
   - **Descarga de Llave (JSON)**:
     - Haz clic en el correo del robot creado.
     - Pestaña `CLAVES` > `AGREGAR CLAVE` > `Crear clave nueva`.
     - Selecciona `JSON` y dale a **CREAR**. (Se descargará el archivo llave).
   - **Email del Robot**: Copia el email largo que termina en `gserviceaccount.com`.
2. **Permisos en la Hoja**:
   - Compartir tu Google Sheet con la dirección del "robot" (email de la cuenta de servicio): scraper-bot@lima-airport-scraper.iam.gserviceaccount.com

3. **Repositorio en GitHub (Configuración de Seguridad)**:
   - **Crear Repositorio**: 
     - Ve a [github.com](https://github.com) > botón `+` > `New repository`.
     - Nombre: `lima-airport-scraper`.
     - **IMPORTANTE**: Selecciona **Private**.
   - **Guardar la Llave (Secrets)**:
     - En el repositorio, ve a `Settings` > `Secrets and variables` > `Actions`.
     - Haz clic en `New repository secret`.
     - **Nombre**: `GCP_SERVICE_ACCOUNT_KEY`.
     - **Valor**: Abre tu archivo `.json` con el Bloc de notas, copia **todo** el contenido y pégalo allí.
     - Haz clic en `Add secret`.
4. **Preparación del Script**:
   - Adaptar el código de Python para leer las credenciales desde variables de entorno.
   - Configurar Selenium en modo "Headless" (sin ventana).
5. **Activación del Workflow**:
   - Crear el archivo de automatización (`.github/workflows/scraper.yml`).
   - Realizar la primera prueba manual y luego dejarlo en automático.

---

## 💡 Conclusión
Si buscas **Paz Mental de 24 horas** sin pagar suscripciones, el camino recomendado es **GitHub Actions** o convertirlo en una **Cloud Function**. 

**¡Todo está listo para analizar este paso cuando regreses de almorzar!** 🙏🚀✨
