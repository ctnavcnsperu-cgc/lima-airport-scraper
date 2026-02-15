# 🚀 Guía de Subida a GitHub - Lima Airport Scraper

Este archivo contiene los comandos necesarios para vincular tu carpeta local con el repositorio de GitHub y activar la automatización.

## 🛠️ Requisitos Previos
1. Tener creado el repositorio **privado** en GitHub llamado `lima-airport-scraper`.
2. Tener configurado el Secret `GCP_SERVICE_ACCOUNT_KEY` en GitHub (con el contenido del JSON).

---

## 💻 Comandos para la Terminal (PowerShell o CMD)

Ejecuta estos comandos uno por uno dentro de la carpeta `d:\CELSO HOJAS DE RUTA\lima airport`:

### 1. Preparar los archivos
Este comando "atrapa" todos los archivos nuevos y carpetas (incluida `.github`).
```powershell
git add .
```

### 2. Crear el paquete (Commit)
Le damos un nombre a esta actualización.
```powershell
git commit -m "Primera subida: Scraper automático 9AM-6PM"
```

### 3. Renombrar rama principal
GitHub usa por defecto el nombre `main`.
```powershell
git branch -M main
```

### 4. Vincular con tu repositorio en la nube
**⚠️ NOTA IMPORTANTE:** Reemplaza `TU_USUARIO` por tu nombre de usuario de GitHub en el siguiente comando.
```powershell
git remote add origin https://github.com/TU_USUARIO/lima-airport-scraper.git
```

### 5. Subir los archivos
Aquí se te pedirá iniciar sesión si es la primera vez.
```powershell
git push -u origin main
```

---

## ✅ ¿Qué pasará después?
Una vez que el comando `git push` termine con éxito:
1. Ve a la pestaña **Actions** en tu repositorio de GitHub.
2. Verás un flujo llamado **"Lima Airport Flight Scraper"**.
3. El robot se activará solo a las 9:00 AM, pero puedes probarlo de inmediato haciendo clic en **"Run workflow"** (el botón gris a la derecha).
