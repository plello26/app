from pathlib import Path
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jinja2 import TemplateNotFound

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="RentalPricer App", version="1.0.0")

# Mount /static ONLY if the folder exists (prevents startup crash)
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Redirect home to dashboard
@app.get("/", include_in_schema=False)
def root_redirect():
    return RedirectResponse(url="/dashboard")

@app.get("/healthz")
def healthz():
    return {"ok": True}

INLINE_DASHBOARD = """<!doctype html>
<html><head><meta charset='utf-8'><title>{{ title }}</title></head>
<body><h1>{{ title }}</h1>
<p>Template 'dashboard.html' non trovato: uso fallback inline.</p>
<p><a href="/platforms">Vai alle piattaforme</a> — <a href="/docs">API Docs</a></p>
<h2>Upload CSV di prova</h2>
<form id='uploadForm'>
  <input type='file' id='file' name='file' accept='.csv' required />
  <button type='submit'>Carica</button>
</form>
<pre id='result' style='background:#f4f4f4;padding:10px;'></pre>
<script>
document.getElementById('uploadForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const fileInput = document.getElementById('file');
  if (!fileInput.files.length) return;
  const formData = new FormData();
  formData.append('file', fileInput.files[0]);
  const res = await fetch('/api/upload', { method: 'POST', body: formData });
  const json = await res.json();
  document.getElementById('result').textContent = JSON.stringify(json, null, 2);
});
</script>
</body></html>"""

INLINE_PLATFORMS = """<!doctype html>
<html><head><meta charset='utf-8'><title>{{ title }}</title></head>
<body><h1>{{ title }}</h1>
<p>Pagina piattaforme (fallback inline).</p>
<p><a href="/dashboard">Torna alla Dashboard</a></p>
</body></html>"""

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    try:
        return templates.TemplateResponse("dashboard.html", {"request": request, "title": "Dashboard"})
    except TemplateNotFound:
        return HTMLResponse(content=INLINE_DASHBOARD.replace("{{ title }}", "Dashboard"))

@app.get("/platforms", response_class=HTMLResponse)
def platforms(request: Request):
    try:
        return templates.TemplateResponse("platforms.html", {"request": request, "title": "Piattaforme"})
    except TemplateNotFound:
        return HTMLResponse(content=INLINE_PLATFORMS.replace("{{ title }}", "Piattaforme"))

@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    data = await file.read()
    return {"filename": file.filename, "size": len(data)}
