# Gestión de Privacidad y Difusión en Telegram

Al abrir en el chat de Telegram el bot `@LimaAirportAlertsBot`, cualquier persona puede ver las alertas. Como administrador, para mantener un control de esto, puedes utilizar un Canal o un Grupo para centralizar la difusión.

## Opciones de Control

### Opción A: El Canal de Telegram (Recomendada)
Un **Canal** es ideal para un sistema de difusión (broadcast). 
- **Solo el Bot publica**: Como administrador, el bot es el único que publica las alertas.
- **Limpio y oficial**: Los usuarios solo leen, no pueden escribir ni responder.
- **Privacidad**: Puedes hacerlo **Privado**, permitiendo el acceso solo a quienes tengan tu "Enlace de Invitación".
- **Anonimato**: Los miembros no pueden ver quiénes más están en el canal.

### Opción B: El Grupo de Telegram
Úsalo si buscas que los usuarios interactúen entre ellos sobre las alertas.
- **Privado**: También puede configurarse como privado.
- **Permisos**: Requiere que el Bot sea "Administrador" para enviar mensajes.

---

## Implementación Técnica

Para que el sistema funcione con un Grupo o Canal, necesitamos obtener su **Chat ID** (un número que suele empezar con un guion, ej: `-100123456789`).

### Pasos para el Control Total:

1. **Creación**: Crea el Canal o Grupo y añade al bot como **Administrador**.
2. **Obtención del ID**: Escribe un mensaje en el grupo/canal y utiliza herramientas como `@username_to_id_bot` para obtener el ID del chat.
3. **Limpieza de Suscriptores**: 
   - Ve al repositorio privado (`lima-airport-data`).
   - Edita el archivo `suscriptores.txt`.
   - **Borra todas las IDs individuales** y coloca únicamente la **ID de tu Grupo o Canal**.

## Gestión de Invitaciones Controladas

Para un control total sobre quién accede a las alertas, Telegram te ofrece estas herramientas:

*   **Enlaces con Aprobación**: Puedes configurar el enlace para que los usuarios no entren directamente, sino que envíen una solicitud que tú (o el dueño) deben "Aprobar" o "Rechazar".
*   **Enlaces de Uso Único**: Puedes generar enlaces que solo funcionen para una persona o que expiren en un tiempo determinado.
*   **Seguimiento**: Puedes crear enlaces con nombres (ej: "Invitación para Gerencia") para saber exactamente quién entró con cada uno.

### Estrategia de Acceso Híbrido (VIP vs. Clientes)

Puedes combinar métodos para mantener la elegancia con los jefes y el control con los externos:

1.  **Nivel VIP (Jefes y Socios) - "Entrada Directa":**
    *   **Acción**: El propietario los agrega manualmente (`Añadir suscriptores`).
    *   **Resultado**: El jefe entra **automáticamente** sin tener que pedir permiso ni usar enlaces. Es la forma más profesional para rangos altos.
2.  **Nivel Externo (Clientes y Personal) - "Acceso Controlado":**
    *   **Acción**: Se les envía un enlace que tiene activa la opción **"Solicitar aprobación"**.
    *   **Resultado**: El usuario solicita entrar y el propietario recibe una notificación para decidir si lo deja pasar.

---

## Entrega al Usuario Final (Traspaso de Propiedad)

Como desarrollador, puedes crear y configurar todo el sistema ("llave en mano") y luego transferir la propiedad a Celso Gutierrez:

1.  **Añadir al Cliente**: Agrégalo al canal y asígnalo como **Administrador** con todos los permisos activos.
2.  **Transferir Propiedad**: En la configuración de administrador del cliente, aparecerá la opción **"Transferir propiedad de canal"**. 
    *   ### Importante: Seguridad para el Traspaso
        Para que Telegram te permita transferir la propiedad del canal a **Celso Gutierrez**, el sistema exige cumplir con la **Regla de Seguridad de 7 días**:
        
        1. **¿Qué es la Verificación en 2 Pasos (2FA)?**  
           Es una contraseña adicional (aparte del código SMS) que tú mismo creas. Es la capa de seguridad más fuerte de Telegram. Sin esto, nadie puede ser "Dueño" legal de un canal corporativo.
        2. **¿Por qué esperar 7 días?**  
           Es un periodo de "enfriamiento". Si un hacker robara una cuenta hoy, no podría traspasar los canales de inmediato; el dueño original tiene 7 días para recuperar su cuenta y cancelar cualquier traspaso.
        3. **¿Cómo se activa?**  
           En el celular: `Ajustes` > `Privacidad y Seguridad` > `Verificación en dos pasos`. Crea una contraseña que no olvides y añade un correo de recuperación.
        
        *Nota: Si la activas hoy, el botón de "Transferir propiedad" aparecerá habilitado exactamente dentro de una semana.*
3.  **Roles Post-Entrega**:
    *   **Usuario Final**: Queda como **Propietario** (dueño legal).
    *   **Desarrollador**: Te quedas como **Administrador** (para dar soporte técnico y gestionar el Bot).
    *   **El Bot**: Sigue como **Administrador** (para enviar las alertas).

## "Modo Administrador Único" (Seguridad Extra)
Para evitar que personas desconocidas se suscriban al bot enviándole un mensaje privado, se puede modificar el código para que el bot ignore a cualquier usuario que no seas tú (basado en tu ID personal). De esta forma, tú decides quién entra al grupo y el bot solo envía alertas a ese espacio controlado.
