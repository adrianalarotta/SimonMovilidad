# SETUP.md - Guía de Despliegue Local

## Requisitos

• **Python 3.10+**  
• **Node.js** y **Angular CLI**  

---

## Backend (Django)

### 1. Clona el repositorio

```bash
git clone https://github.com/adrianalarotta/SimonMovilidad.git
cd SimonMovilidad
```

### 2. Crea y activa entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate.bat  # Windows
```

### 3. Instala dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecuta migraciones y corre servidor

```bash
python manage.py migrate
python manage.py runserver
```

---

## Frontend (Angular)

### 1. Clona el frontend

```bash
git clone https://github.com/adrianalarotta/FrontSimonMovilidad.git
cd FrontSimonMovilidad
```

### 2. Instala dependencias

```bash
npm install
```

### 3. Corre la aplicación

```bash
ng serve
```

Luego accede a **`http://localhost:4200`**.

---

## Simulador de Dispositivos

### Requisitos: Python 3.10+

```bash
python simulador_websocket.py  # (ubicado en la carpeta del backend)
```

Este script conecta vía **WebSocket** y transmite datos simulados en tiempo real para **3 dispositivos diferentes**.

---

## Credenciales por defecto

*Puedes registrar en `/admin`:*

• **Usuario:** `admin`  
• **Password:** `admin123`  

---

## Endpoints clave

• **`/api/login`** - Devuelve **JWT** al autenticar  
• **`/api/ingest`** - Ingesta datos de sensores  
• **`/api/sensor-history`** - Histórico de ubicaciones/datos  
• **`/api/active-alerts`** - Lista de alertas activas  
• **`/ws/ubicacion/`** - **WebSocket** para actualizaciones en vivo  

---

## Test

### Ejecutar tests unitarios

```bash
python manage.py test
```