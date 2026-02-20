# 🤖 Contexto y Normas del Proyecto (Reglas para la IA)

**Instrucción Principal:** Lee este archivo al inicio de cada interacción para alinear tu comportamiento con las preferencias del usuario.

## 1. Estilo de Commits (Git) 📝
El formato obligatorio para los mensajes de commit es:
`[Keyword en Inglés]: [Descripción en Español (Pasado Impersonal)]`

**Keywords Permitidas:**
- `Feat`: Nuevas funcionalidades.
- `Fix`: Corrección de errores.
- `Refactor`: Cambios de código que no alteran la funcionalidad (limpieza, modularización).
- `Docs`: Cambios en documentación.
- `Style`: Cambios de formato (espacios, comas, etc).
- `Chore`: Tareas de mantenimiento (actualizar dependencias, scripts de build).

**Ejemplos Correctos:**
- `Refactor: Se movió la lógica de constantes a src/constants.py`
- `Feat: Se creó el módulo de utilidades`
- `Fix: Se corrigió el selector CSS del botón de búsqueda`

## 2. Flujo de Trabajo
- **Documentación:** Mantener siempre actualizados los archivos `.md` de planificación.
- **Modularidad:** Preferir funciones pequeñas y archivos separados por responsabilidad.
- **Exportar Lógica:** Encapsular funcionalidades en funciones o clases bien definidas para que el código sea más entendible, reutilizable y fácil de desacoplar.

## 3. Convenciones de Nombres (Naming) 🏷️
- **Idioma General:** Español.
- **Variables:** Usar español (`nombre_archivo`, `datos_cliente`), salvo términos técnicos globales donde el inglés sea más claro o estándar (`driver`, `callback`, `json`, `request`, `id`).
- **Funciones:** Usar español descriptivo para la lógica de negocio (`ejecutar_scraping`, `guardar_datos`, `calcular_total`).

### Específico para Python 🐍
- **Estilo:** `snake_case` para variables y funciones (ej: `mi_variable`). `CamelCase` para Clases (ej: `GestorDatos`).

### Otros Lenguajes 🌐
- **Regla General:** Respetar siempre las convenciones estándar de la comunidad de ese lenguaje (ej: `camelCase` en JavaScript, `PascalCase` en C#, etc.).

## 4. Preferencias de Interacción 🤝
- **Explicaciones:** Acompañar los cambios de código con una breve explicación del "por qué".
- **Seguridad (Git):** Sugerir siempre crear una nueva rama (`git checkout -b`) antes de implementar cambios grandes o experimentales.
- **Paso a Paso:** Preferir instrucciones granulares y listas de verificación (checklists) para tareas complejas.
- **Conservadurismo:** Si algo funciona bien, evitar refactorizarlo agresivamente a menos que sea parte de un plan acordado.
- **Planificación Proactiva:** Ante cambios grandes o nuevas funcionalidades complejas, sugerir generar primero un plan detallado con checklist.