# Sistema de Ventas

Aplicación web en Python para cualquier negocio: tiendas, bodegas, ferreterías, librerías, ropa, tecnología y más.

## Funciones implementadas

- Acceso con cuentas independientes para **administrador** y **usuario de ventas**.
- Panel administrativo: indicadores, productos, inventario, cuentas y ventas recientes.
- Usuario de ventas: acceso restringido únicamente a la caja para registrar ventas.
- Registro de productos con código, categoría, costos, precios y existencias.
- Carrito, descuentos, cliente y métodos de pago.
- Validación de existencias y descuento automático de inventario.
- Vendedor identificado en cada venta.
- Diseño responsive para computadora y celular.
- SQLite para desarrollo local y PostgreSQL persistente en Vercel.

## Roles

| Rol | Permisos |
|---|---|
| Administrador | Panel, productos, inventario, crear/desactivar usuarios y registrar ventas. |
| Usuario de ventas | Iniciar sesión y registrar ventas desde el celular o computadora. |

## Ejecutar en VS Code

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Abre [http://127.0.0.1:8000](http://127.0.0.1:8000).

Para desarrollo local, ingresa inicialmente con:

- Usuario: `admin`
- Contraseña: `admin123`

Cambia esta contraseña creando un administrador nuevo antes de usar el sistema en un negocio.

## Despliegue en Vercel

1. Fusiona el Pull Request y entra a [Vercel](https://vercel.com/new).
2. Importa el repositorio `jhunnior-06/Sistema-de-ventas-`.
3. Crea una base PostgreSQL administrada (por ejemplo, Neon) y copia su URL de conexión SQLAlchemy:
   `postgresql+psycopg://usuario:contrasena@host:5432/sistema_ventas`.
4. En **Settings → Environment Variables**, agrega:
   - `DATABASE_URL`: la URL de PostgreSQL.
   - `SECRET_KEY`: una cadena aleatoria larga.
   - `ADMIN_USERNAME`: el usuario del primer administrador, por ejemplo `briam.admin`.
   - `ADMIN_NAME`: nombre visible del administrador.
   - `ADMIN_PASSWORD`: contraseña segura del primer administrador.
5. Pulsa **Deploy**.

> No uses SQLite en Vercel: el almacenamiento de las funciones no es permanente. La aplicación requiere `DATABASE_URL`, `SECRET_KEY` y `ADMIN_PASSWORD` en producción.

El archivo `vercel.json` ya dirige todas las rutas hacia FastAPI e incluye las plantillas y archivos estáticos.
