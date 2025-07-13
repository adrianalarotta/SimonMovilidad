# Design.md - Documento de Diseño del Proyecto

## Elección del Stack Tecnológico y Trade-offs

### Tecnologías Utilizadas

#### Backend: Django + Django REST Framework + Django Channels

**Motivo de elección:**

• **Dominio** del framework 
• Ecosistema maduro, robusto y bien documentado  
• Soporte directo para WebSockets mediante `Django Channels`  
• Rápido desarrollo de APIs RESTful con `DRF`  

**Trade-offs:**
• Puede ser más pesado comparado con microframeworks como FastAPI  
• WebSocket con Channels requiere una capa adicional de ASGI y configuración de capa de canales  

#### Base de Datos: SQLite

**Motivo de elección:**
• Simple, sin necesidad de configuración adicional para desarrollo local  
• Integrado naturalmente con Django  

**Trade-offs:**
• No apta para producción o concurrencia alta (PostgreSQL sería el reemplazo natural)  

#### Frontend: Angular + Leaflet + Chart.js

**Motivo de elección:**
• Angular permite estructura modular robusta  
• Leaflet permite visualización interactiva de mapas OpenStreetMap sin dependencias comerciales  
• Chart.js permite visualización rápida de datos históricos  

**Trade-offs:**
• Angular tiene curva de aprendizaje más pronunciada que React  
• Leaflet menos avanzado que Google Maps en features (pero más liviano)  

## Arquitectura General

```
 [Dispositivos IoT simulados] ---WS---> [Django WebSocket Consumer]
                                          |
                                          V
 [Django REST + WebSocket Backend] <--> [SQLite DB]
                                          |
                                          V
 [Angular Dashboard (Mapa + Chart.js)]
```

## Seguridad

• **JWT manual** sin librerías externas (firma, expiración, validación)  
• **Enmascaramiento de IDs** de dispositivos para usuarios no administradores  
• **Middleware personalizado** `@jwt_required` para proteger endpoints  

## Alertas Predictivas

• Si el combustible proyectado es **<1h de autonomía**, se genera alerta  
• Visible solo para **administradores**  

## Offline Support

• **Historial y selección** de dispositivo se almacenan en `localStorage`  
• **Gráficos funcionan offline** si ya fueron cargados anteriormente  

## Modularidad y Extensibilidad

• **División clara por componentes**: mapa, gráficos, alertas, login  
• El **backend está listo** para migrar a PostgreSQL con cambios mínimos  
• **Frontend puede extenderse** con PWA o versión móvil (React Native)