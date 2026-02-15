# 🚀 Plan de Preparación para GitHub

Sigue esta lista de verificación para dejar tu proyecto **client-scraper-desktop** listo para publicar.

## 1. Documentación y Archivos Base 📄
- [x] **Crear `README.md`**: Ya tienes un borrador. Asegúrate de que esté actualizado con las últimas funciones (Enriquecimiento masivo, Búsqueda profunda).
- [x] **Crear `LICENSE`**: Agrega un archivo llamado `LICENSE` (sin extensión) con el texto de la licencia MIT (recomendada para open source).
- [x] **Crear `.gitignore`**: Vital para no subir archivos basura, perfiles de navegador pesados o datos privados.
- [x] **Crear `requirements.txt`**: Generado con las dependencias básicas (`selenium`, `webdriver-manager`).

## 2. Limpieza y Seguridad 🔒
- [x] **Revisar Datos Sensibles**: Asegúrate de que no haya contraseñas, emails personales hardcodeados o claves API reales en el código (`lead_app.py`).
- [x] **Verificar `selenium_profile`**: Asegúrate de que la carpeta de perfil de Chrome NO se suba (esto se maneja con el `.gitignore`).

## 3. Código y Estructura 🛠️
- [x] **Comentarios**: Revisa `lead_app.py` y agrega comentarios explicativos en las funciones complejas (como la lógica de scroll o los selectores XPath).
- [ ] **Limpieza de Logs**: Verifica que los `print` o logs de consola sean útiles y no "ruido" de depuración.

## 4. Publicación en GitHub 🐙
- [ ] **Crear Repositorio**: Ve a GitHub.com -> New Repository. Sugerencia de nombre: `client-scraper-desktop`.
- [ ] **Inicializar Git**: Ejecutar `git init` en la carpeta.
- [ ] **Primer Commit**: Subir los archivos limpios.

---

### 📝 Contenido sugerido para `.gitignore`
Crea un archivo llamado `.gitignore` en la raíz del proyecto y pega esto:
```text
# Python
__pycache__/
*.pyc
*.pyo
*.pyd
venv/

# Selenium / Chrome
selenium_profile/
chromedriver.exe
*.log

# Datos recolectados (Opcional: para no subir tus leads)
fichas_leads/*.json
```

### 📝 Contenido sugerido para `requirements.txt`
Crea un archivo llamado `requirements.txt` y pega esto:
```text
selenium
webdriver-manager
```