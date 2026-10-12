# Sistema de Ventas

Aplicación web en Python para administrar ventas y ofrecer compras con carrito desde el celular o computadora.

## Accesos

| Perfil | Enlace | Funciones |
|---|---|---|
| Administrador | `/admin` | Registra ventas, gestiona productos, precios, inventario y cuentas. |
| Cliente | `/cliente` | Crea su cuenta, ve el catálogo y confirma pedidos con carrito. |

El administrador también cumple la función de vendedor, por lo que no hace falta crear una cuenta de vendedor independiente.

## Funciones implementadas

- Catálogo de productos, precios y control de existencias.
- Carrito para ventas atendidas por el administrador.
- Carrito de compras para clientes registrados.
- Descuento automático de inventario al confirmar una venta o pedido.
- Panel administrativo con ventas recientes.
- Registro de clientes desde la web.
- Diseño adaptable a celulares.
- PostgreSQL mediante Neon para producción en Vercel.

## Ejecutar en VS Code

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Abre [http://127.0.0.1:8000](http://127.0.0.1:8000).

Para desarrollo local, el administrador inicial es:

- Usuario: `admin`
- Contraseña: `admin123`

## Despliegue en Vercel

En **Settings → Environment Variables** configura:

- `DATABASE_URL` o las variables creadas automáticamente por Neon.
- `SECRET_KEY`
- `ADMIN_USERNAME`
- `ADMIN_NAME`
- `ADMIN_PASSWORD`

No uses SQLite en Vercel porque el almacenamiento de las funciones no es permanente.
