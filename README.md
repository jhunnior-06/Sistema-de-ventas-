# Sistema de Ventas

Aplicación web en Python para cualquier negocio: tiendas, bodegas, ferreterías, librerías, ropa, tecnología y más.

## Funciones implementadas

- Panel principal con ventas del día, productos activos y alerta de stock mínimo.
- Registro de productos con código, categoría, costos, precios y existencias.
- Activación y desactivación de productos sin perder su historial.
- Pantalla de caja con carrito, cantidad, descuento, cliente y método de pago.
- Validación de existencias: una venta nunca puede dejar el stock en negativo.
- Descuento automático de inventario y generación de comprobante interno por venta.
- Historial de últimas ventas.
- Diseño responsive para computadora y celular.
- Base de datos SQLite para iniciar rápidamente y compatibilidad con PostgreSQL para producción.
- Docker y archivo de despliegue para Render.

## Tecnologías

- Python 3.12
- FastAPI
- SQLAlchemy
- Jinja2, HTML, CSS y JavaScript
- SQLite / PostgreSQL

## Ejecutar en VS Code

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
uvicorn app.main:app --reload
```

Abre [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Primer uso

1. Ingresa a **Productos** y registra al menos un producto con stock mayor a cero.
2. Ingresa a **Nueva venta**, selecciona productos y confirma la operación.
3. Vuelve al **Panel** para revisar las ventas y alertas de inventario.

## Despliegue

Para producción configura la variable `DATABASE_URL` con PostgreSQL:

```
DATABASE_URL=postgresql+psycopg://usuario:contrasena@host:5432/sistema_ventas
```

El repositorio incluye `Dockerfile` y `render.yaml`. En Render crea un servicio web desde GitHub, agrega `DATABASE_URL` y `SECRET_KEY`, y despliega.
