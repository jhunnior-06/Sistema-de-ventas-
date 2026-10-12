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
- SQLite para desarrollo local y PostgreSQL persistente en Vercel.

## Tecnologías

- Python 3.12
- FastAPI
- SQLAlchemy
- Jinja2, HTML, CSS y JavaScript
- PostgreSQL

## Ejecutar en VS Code

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Abre [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Primer uso

1. Ingresa a **Productos** y registra al menos un producto con stock mayor a cero.
2. Ingresa a **Nueva venta**, selecciona productos y confirma la operación.
3. Vuelve al **Panel** para revisar las ventas y alertas de inventario.

## Despliegue en Vercel

1. Fusiona el Pull Request y entra a [Vercel](https://vercel.com/new).
2. Importa el repositorio `jhunnior-06/Sistema-de-ventas-`.
3. Crea una base PostgreSQL administrada (por ejemplo, Neon) y copia su URL de conexión SQLAlchemy:
   `postgresql+psycopg://usuario:contrasena@host:5432/sistema_ventas`.
4. En **Settings → Environment Variables**, agrega:
   - `DATABASE_URL`: la URL de PostgreSQL.
   - `SECRET_KEY`: una cadena aleatoria larga.
5. Pulsa **Deploy**.

> No uses SQLite en Vercel: el almacenamiento de las funciones no es permanente. La aplicación requiere `DATABASE_URL` en producción para que las ventas y productos no se pierdan.

El archivo `vercel.json` ya dirige todas las rutas hacia FastAPI e incluye las plantillas y archivos estáticos.
