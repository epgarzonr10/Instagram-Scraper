# 📊 Instagram Scraper + Dashboard
 
Scraper de posts de Instagram con visualización en HTML.
 
---
 
## Estructura del proyecto
 
```
proyecto/
├── venv/
├── main.py          # Scraper principal
├── cookies.env      # Cookies de sesión (no subir a git)
├── .gitignore
├── posts.json       # Datos generados por el scraper
└── index.html       # Dashboard de visualización
```
 
---
 
## Requisitos
 
- Python 3.10+
- Google Chrome instalado
- Playwright

## Entorno virtual (recomendado)

Se recomienda crear un entorno virtual para instalar las dependencias sin afectar el sistema global:

```bash
python -m venv venv
```

Actívalo según tu sistema operativo:

```bash
# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

Una vez activado, instala las dependencias normalmente con `pip`.


```bash
pip install playwright python-dotenv
playwright install chromium
```

---

## Configuración
 
Crea el archivo `cookies.env` con tus cookies de sesión de Instagram:
 
```env
CSRFTOKEN=tu_valor
DS_USER_ID=tu_valor
SESSIONID=tu_valor
MID=tu_valor
IG_DID=tu_valor
RUR=tu_valor
```
 
> ⚠️ Nunca subas `cookies.env` a GitHub. Ya está en `.gitignore`.
 
Para obtener las cookies: abre Instagram en Chrome → F12 → Application → Cookies → `instagram.com`.
 
---
 
## Uso
 
### 1. Ejecutar el scraper
 
Edita en `main.py` el usuario y cantidad de posts:
 
```python
INSTAGRAM_USER = "nombre_de_usuario"
MAX_POSTS = 10
```
 
Luego corre:
 
```bash
python main.py
```
 
Genera `posts.json` con los datos de cada post.
 
### 2. Ver el dashboard
 
```bash
python -m http.server 8080
```
 
Abre en el navegador: [http://localhost:8080](http://localhost:8080)
 
---
 
## Datos que extrae
 
| Campo | Descripción |
|---|---|
| `link` | URL del post o reel |
| `tipo` | `post` o `reel` |
| `fecha` | Fecha de publicación |
| `likes` | Número de likes |
| `comentarios` | Número de comentarios |
| `descripcion` | Caption del post |
 
---
 
## Cómo funciona el scraper
 
### Análisis de las solicitudes web
 
Instagram no expone una API pública para obtener datos de posts. Para acceder a la información se analizó cómo el navegador autentica y mantiene una sesión activa con la plataforma. Instagram utiliza un conjunto de cookies de sesión que identifican al usuario y autorizan cada solicitud. Las más críticas son `SESSIONID` (identifica la sesión activa) y `CSRFTOKEN` (token de seguridad contra falsificación de solicitudes). El scraper extrae estas cookies desde un navegador real y las inyecta en el contexto de Playwright antes de hacer cualquier navegación, logrando así que Instagram trate las solicitudes como si vinieran de un usuario legítimo.
 
Una vez autenticado, el scraper navega al perfil objetivo y extrae los links de los posts directamente del DOM. Luego entra a cada post individualmente y lee el contenido de la etiqueta `<meta name="description">`, que Instagram genera con los datos del post (likes, comentarios, fecha y caption) sin necesidad de llamadas adicionales a la API.
 
### Estrategia para minimizar bloqueos
 
Instagram detecta comportamiento automatizado principalmente por la velocidad y regularidad de las solicitudes. Para reducir este riesgo se implementaron las siguientes medidas:
 
**Tiempos de espera aleatorios** — en lugar de pausas fijas, el scraper espera intervalos variables entre cada acción: entre 1.2 y 3.0 segundos antes de navegar a un post, entre 2.0 y 5.0 segundos tras cargar la página, y pausas más largas de entre 6.0 y 12.0 segundos cada 3 posts. Esto imita el ritmo irregular de un usuario humano.
 
**Orden cronológico de acceso** — los posts se procesan del más antiguo al más reciente (invirtiendo el orden en que Instagram los muestra). Esto evita el patrón mecánico de "primero al último" que suelen seguir los bots.
 
**Detección de bloqueos** — el scraper verifica en cada paso si Instagram redirigió a la página de login o mostró un mensaje de bloqueo temporal ("Try again later"), y detiene la ejecución en ese caso en lugar de seguir acumulando errores.
 
**User-agent real** — el contexto del navegador declara un User-Agent de Chrome en Windows, que es el más común en la web, para no levantar sospechas por cabeceras inusuales.
 
---
 
## Dashboard (index.html)
 
El archivo `index.html` es un dashboard estático que visualiza los datos generados por el scraper. Se abre en el navegador y carga el archivo `posts.json` directamente.
 
Muestra un resumen con tarjetas de estadísticas en la parte superior: total de publicaciones, likes acumulados, comentarios totales, cantidad de reels y cantidad de fotos. Debajo presenta una tabla con cada post, incluyendo su tipo (reel o foto con badge de color), fecha, likes, comentarios, caption truncado con tooltip al pasar el cursor, y un enlace directo a la publicación en Instagram.
 
Los números se formatean automáticamente en K y M para mayor legibilidad. El dashboard no requiere ninguna dependencia externa ni servidor de backend, solo necesita correr bajo un servidor local para poder leer el `posts.json`.
 
---
 
## Notas
 
- El scraper usa cookies reales, por lo que simula una sesión activa.
- Instagram puede bloquear si se hacen demasiadas peticiones seguidas. 
- Los datos se sobreescriben en `posts.json` cada vez que se corre el script.