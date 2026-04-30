import os
import logging
from threading import Thread
from flask import Flask, request, render_template_string
from transformers import MarianMTModel, MarianTokenizer
import torch
import pykakasi
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from rich.status import Status
from rich.table import Table

# --- CONFIGURACIÓN GLOBAL ---
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
logging.getLogger("werkzeug").setLevel(logging.ERROR) # Silenciar logs de Flask
MODELS_DIR = os.path.expanduser("~/modelos_ia")
os.makedirs(MODELS_DIR, exist_ok=True)
os.environ["TRANSFORMERS_CACHE"] = MODELS_DIR

console = Console()
kks = pykakasi.kakasi()

# --- MOTOR DE INTELIGENCIA ARTIFICIAL ---
class TraductorIA:
    def __init__(self):
        self.modelos = {}

    def obtener_romaji(self, texto):
        resultado = kks.convert(texto)
        return " ".join([item['hepburn'] for item in resultado]).capitalize()

    def cargar_modelo(self, src_lang):
        if src_lang in self.modelos:
            return self.modelos[src_lang]
        
        nombre_modelo = f"Helsinki-NLP/opus-mt-{src_lang}-es"
        try:
            tokenizer = MarianTokenizer.from_pretrained(nombre_modelo)
            modelo = MarianMTModel.from_pretrained(nombre_modelo)
            self.modelos[src_lang] = (tokenizer, modelo)
            return tokenizer, modelo
        except Exception as e:
            return None, None

    def traducir(self, texto, src_lang):
        tokenizer, modelo = self.cargar_modelo(src_lang)
        if not modelo:
            return None, "Error al cargar el modelo."

        inputs = tokenizer(texto, return_tensors="pt", padding=True)
        with torch.no_grad():
            tokens = modelo.generate(**inputs)
        traduccion = tokenizer.decode(tokens[0], skip_special_tokens=True)
        
        romaji = self.obtener_romaji(texto) if src_lang == "ja" else None
        return traduccion, romaji

motor_ia = TraductorIA()

# --- SERVIDOR WEB (FLASK) ---
app = Flask(__name__)

HTML_TEMPLATE = """
<!-- (Mismo HTML que te di en el script anterior, mantenlo idéntico aquí) -->
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IA Translator Offline</title>
    <style>
        body { font-family: system-ui, sans-serif; background: #f8fafc; color: #1e293b; padding: 15px; }
        .container { max-width: 500px; margin: auto; background: white; padding: 20px; border-radius: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        select, textarea, button { width: 100%; border-radius: 8px; border: 1px solid #ccc; padding: 10px; margin-top: 10px; box-sizing: border-box; }
        button { background: #2563eb; color: white; border: none; font-weight: bold; cursor: pointer; }
        .result { margin-top: 20px; padding: 15px; background: #f1f5f9; border-left: 5px solid #2563eb; }
    </style>
</head>
<body>
    <div class="container">
        <h2 style="text-align:center; color:#2563eb;">Traductor IA</h2>
        <form method="POST">
            <select name="src">
                <option value="en">Inglés</option><option value="ru">Ruso</option><option value="ja">Japonés</option>
            </select>
            <textarea name="text" required placeholder="Texto..."></textarea>
            <button type="submit">Traducir</button>
        </form>
        {% if translation %}
        <div class="result">
            {% if romaji %}<i>{{ romaji }}</i><br><br>{% endif %}
            <strong>{{ translation }}</strong>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    data = {"translation": None, "romaji": None}
    if request.method == "POST":
        src = request.form.get("src")
        text = request.form.get("text")
        with console.status(f"[bold cyan]Servidor procesando petición ({src})..."):
            data["translation"], data["romaji"] = motor_ia.traducir(text, src)
    return render_template_string(HTML_TEMPLATE, **data)

def iniciar_servidor_web():
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

# --- INTERFAZ DE TERMINAL (CLI) ---
def mostrar_banner():
    console.clear()
    banner = """
 ╔════════════════════════════════════════════════════╗
 ║  ████████╗██████╗  █████╗ ███╗   ██╗███████╗       ║
 ║  ╚══██╔══╝██╔══██╗██╔══██╗████╗  ██║██╔════╝       ║
 ║     ██║   ██████╔╝███████║██╔██╗ ██║███████╗       ║
 ║     ██║   ██╔══██╗██╔══██║██║╚██╗██║╚════██║       ║
 ║     ██║   ██║  ██║██║  ██║██║ ╚████║███████║       ║
 ║     ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝       ║
 ║      Offline Neural Translation Engine v1.0        ║
 ╚════════════════════════════════════════════════════╝
    """
    console.print(Text(banner, style="bold blue"))

def menu_principal():
    mostrar_banner()
    console.print(Panel.fit("Seleccione el modo de operación", style="cyan"))
    
    table = Table(show_header=False, box=None)
    table.add_row("[bold green]1.[/]", "Iniciar Servidor Web (Acceso desde el navegador)")
    table.add_row("[bold yellow]2.[/]", "Modo Consola (Traducir aquí mismo)")
    table.add_row("[bold red]3.[/]", "Salir del sistema")
    console.print(table)
    
    opcion = Prompt.ask("\n[bold cyan]>[/] Opción", choices=["1", "2", "3"], default="1")
    return opcion

def modo_consola():
    mostrar_banner()
    console.print("[bold yellow]Modo Consola Activo.[/] (Escribe 'volver' para salir al menú)\n")
    idioma = Prompt.ask("[bold cyan]Idioma origen[/] (en, ja, ru, fr)", default="en").lower()
    
    while True:
        texto = Prompt.ask(f"\n[bold green]Texto ({idioma})[/]")
        if texto.lower() == 'volver':
            break
            
        with Status(f"[bold magenta]Traduciendo con modelo neuronal...", spinner="dots"):
            traduccion, romaji = motor_ia.traducir(texto, idioma)
            
        if traduccion:
            console.print(Panel(
                f"[bold blue]Traducción:[/] {traduccion}\n" + 
                (f"[bold cyan]Romaji:[/] {romaji}" if romaji else ""),
                title="Resultado", border_style="green"
            ))

# --- PUNTO DE ENTRADA ---
if __name__ == "__main__":
    while True:
        opcion = menu_principal()
        
        if opcion == "1":
            mostrar_banner()
            console.print(Panel(
                "🌐 [bold green]Servidor Web Iniciado[/]\n"
                "Abre el navegador en tu teléfono y ve a:\n"
                "[bold underline cyan]http://localhost:5000[/]\n\n"
                "[dim]Presiona Ctrl+C para detener el servidor.[/]",
                border_style="green"
            ))
            try:
                iniciar_servidor_web()
            except KeyboardInterrupt:
                console.print("\n[bold red]Servidor detenido.[/]")
                
        elif opcion == "2":
            modo_consola()
            
        elif opcion == "3":
            console.print("[bold red]Cerrando motor de IA... ¡Hasta pronto![/]")
            break