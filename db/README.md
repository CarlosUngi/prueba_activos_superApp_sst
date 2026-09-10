# Base de Datos PostgreSQL

Esta carpeta contiene la configuración para levantar la base de datos PostgreSQL mediante Docker.

## Instrucciones para levantar la base de datos

1. Asegúrate de tener **Docker** y **Docker Compose** instalados en tu sistema.
2. Abre tu terminal y navega hasta este directorio (`db`).
3. Ejecuta el siguiente comando para levantar el contenedor en segundo plano:

```bash
docker compose up -d
```
> *Nota: Si en tu sistema Linux necesitas permisos de administrador, usa `sudo docker compose up -d`.*

## Credenciales por defecto

* **Host:** localhost
* **Puerto:** 5432
* **Usuario:** superapp_user
* **Contraseña:** superapp_password
* **Base de datos:** superapp_sst

## Detener la base de datos

Para detener y apagar el contenedor sin borrar la información:

```bash
docker compose stop
```

Si deseas detener el contenedor y eliminarlo (los datos se conservan en el volumen de Docker):

```bash
docker compose down
```
