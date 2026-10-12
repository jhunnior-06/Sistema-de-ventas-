# Sistema de Ventas

Aplicación web para gestionar productos, inventario y ventas de cualquier tipo de negocio.

## Incluye
- Panel con indicadores de ventas e inventario.
- Catálogo de productos: crear, editar, activar/desactivar y eliminar.
- Registro de ventas con carrito y descuentos.
- Actualización automática de stock y alerta de existencias bajas.
- Historial reciente de ventas.
- Base de datos SQLite para empezar sin configuración; PostgreSQL lista para producción mediante `DATABASE_URL`.
- Dockerfile y configuración para Render.

## Ejecutar localmente

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Abre http://127.0.0.1:8000.

## Despliegue

Configura `DATABASE_URL` en tu plataforma. Para producción usa PostgreSQL y una variable como:

```
postgresql+psycopg://usuario:contrasena@host:5432/sistema_ventas
```

En Render, crea un servicio web desde este repositorio. El archivo `render.yaml` contiene el comando de inicio.
