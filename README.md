# 🌍 Offline Neural Translator CLI

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-Web%20UI-black?logo=flask)
![PyTorch](https://img.shields.io/badge/PyTorch-AI%20Engine-ee4c2c?logo=pytorch)
![License](https://img.shields.io/badge/license-MIT-green.svg)

Una herramienta de traducción automática neuronal (NMT) diseñada para funcionar **100% offline**. Utiliza los modelos de código abierto `Helsinki-NLP/opus-mt` de Hugging Face, encapsulados en una interfaz de terminal interactiva (CLI) rica en visuales y un servidor web local.

Ideal para funcionar como un microservicio local o integrarse como el motor de traducción en aplicaciones más grandes (como plataformas de aprendizaje de idiomas o pipelines de reconocimiento de texto multi-modal).

## ✨ Características

- **Privacidad Total:** Toda la inferencia se realiza localmente. Sin APIs de terceros, sin telemetría, sin necesidad de internet una vez descargado el modelo.
- **Interfaz Híbrida:** 
  - `CLI Mode`: Un panel interactivo y estilizado en la terminal (potenciado por `rich`).
  - `Web Mode`: Un servidor Flask ligero con diseño responsivo para móviles.
- **Soporte Romaji:** Conversión automática de caracteres japoneses a Romaji utilizando `pykakasi`.
- **Multiplataforma:** Optimizado para ejecutarse en PC (Windows/Linux/Mac) y en Android a través de Termux (Ubuntu proot-distro).

## 🚀 Instalación

### Opción A: Escritorio (PC)
1. Clona el repositorio:
   ```bash
   git clone [https://github.com/TU_USUARIO/offline-neural-translator.git](https://github.com/TU_USUARIO/offline-neural-translator.git)
   cd offline-neural-translator