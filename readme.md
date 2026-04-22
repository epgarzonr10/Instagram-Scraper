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
 
## Notas
 
- El scraper usa cookies reales, por lo que simula una sesión activa.
- Instagram puede bloquear si se hacen demasiadas peticiones seguidas. Se recomienda no superar 20–30 posts por ejecución.
- Los datos se sobreescriben en `posts.json` cada vez que se corre el script.