# Guía de Despliegue en Render

Esta guía te ayudará a desplegar tu API de Análisis Postural en Render.

## 📋 Pre-requisitos

1. Cuenta en [Render](https://render.com) (gratis)
2. Cuenta en [GitHub](https://github.com) o [GitLab](https://gitlab.com)
3. Tus credenciales de API:
   - Cloudinary (cloud_name, api_key, api_secret)
   - OpenAI (api_key)

## 🚀 Pasos para Desplegar

### 1. Preparar el Repositorio

Asegúrate de que tu proyecto esté en un repositorio de Git:

```bash
# Si aún no has inicializado git
git init

# Agregar todos los archivos
git add .

# Hacer commit
git commit -m "Preparar para despliegue en Render"

# Crear repositorio en GitHub/GitLab y conectarlo
git remote add origin https://github.com/tu-usuario/tu-repo.git
git push -u origin main
```

### 2. Conectar Render con tu Repositorio

1. Ve a [https://dashboard.render.com](https://dashboard.render.com)
2. Haz clic en **"New +"** → **"Web Service"**
3. Conecta tu cuenta de GitHub/GitLab
4. Selecciona el repositorio `analisis-postural-analisis-back`

### 3. Configurar el Servicio

Render detectará automáticamente el archivo `render.yaml`, pero puedes configurarlo manualmente:

#### Configuración Básica:
- **Name**: `analisis-postural-api` (o el nombre que prefieras)
- **Runtime**: `Python 3`
- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn app:app`
- **Instance Type**: `Free` (para empezar)

### 4. Configurar Variables de Entorno

En la sección **"Environment"** de Render, agrega las siguientes variables:

```
FLASK_ENV=production
PORT=10000
SECRET_KEY=tu-secret-key-generada-aqui
CLOUDINARY_CLOUD_NAME=tu-cloud-name
CLOUDINARY_API_KEY=tu-cloudinary-api-key
CLOUDINARY_API_SECRET=tu-cloudinary-api-secret
OPENAI_API_KEY=sk-tu-openai-api-key
```

**⚠️ IMPORTANTE:**
- Genera un `SECRET_KEY` aleatorio seguro
- **NUNCA** subas estas credenciales al repositorio
- Usa las variables de entorno de Render

### 5. Desplegar

1. Haz clic en **"Create Web Service"**
2. Render iniciará el build automáticamente
3. Espera 5-10 minutos para que el servicio esté listo

### 6. Verificar el Despliegue

Una vez desplegado, tu API estará disponible en:
```
https://tu-servicio.onrender.com
```

Prueba los endpoints:
```bash
# Health check
curl https://tu-servicio.onrender.com/health

# Info del módulo
curl https://tu-servicio.onrender.com/api/analisis-ergonomico/info

# Análisis (con imagen)
curl -X POST https://tu-servicio.onrender.com/api/analisis-ergonomico/analyze \
  -F "image=@tu-imagen.jpg"
```

## 📝 Archivos de Configuración

### `requirements.txt`
Contiene todas las dependencias Python necesarias:
- Flask
- OpenAI
- MediaPipe
- Cloudinary
- OpenCV (headless para servidores)
- Gunicorn (servidor de producción)

### `build.sh`
Script que se ejecuta durante el build:
- Instala las dependencias
- Crea directorios necesarios

### `render.yaml`
Configuración declarativa para Render (opcional pero recomendada).

## ⚙️ Configuración de Producción

### Variables de Entorno Requeridas:

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `FLASK_ENV` | Entorno de Flask | `production` |
| `PORT` | Puerto del servidor | `10000` |
| `SECRET_KEY` | Clave secreta de Flask | `tu-secret-key-aleatorio` |
| `CLOUDINARY_CLOUD_NAME` | Nombre de tu cloud en Cloudinary | `mi-cloud` |
| `CLOUDINARY_API_KEY` | API key de Cloudinary | `123456789` |
| `CLOUDINARY_API_SECRET` | API secret de Cloudinary | `abcdef...` |
| `OPENAI_API_KEY` | API key de OpenAI | `sk-proj-...` |

## 🔄 Actualizaciones

Para actualizar tu servicio:

```bash
# Hacer cambios en tu código
git add .
git commit -m "Descripción de los cambios"
git push origin main
```

Render detectará el push y redesplegará automáticamente.

## 🐛 Troubleshooting

### Error: "opencv-python no se puede instalar"
**Solución**: Usa `opencv-python-headless` en lugar de `opencv-python` en `requirements.txt` (ya está configurado).

### Error: "No module named 'app'"
**Solución**: Verifica que el `startCommand` sea `gunicorn app:app` (sin extensión .py).

### Error: "Build failed"
**Solución**:
1. Verifica que `build.sh` tenga permisos de ejecución: `chmod +x build.sh`
2. Revisa los logs de build en el dashboard de Render

### Error: "Application failed to start"
**Solución**:
1. Verifica que todas las variables de entorno estén configuradas
2. Revisa los logs en el dashboard de Render
3. Asegúrate de que el puerto sea `10000` en las variables de entorno

### OpenAI API no funciona
**Solución**:
1. Verifica que `OPENAI_API_KEY` esté configurado correctamente
2. Verifica que tu API key de OpenAI tenga créditos disponibles
3. Revisa los logs para ver el error específico

## 💰 Costos

- **Plan Free de Render**: Gratis, pero con limitaciones:
  - 750 horas de servicio al mes
  - El servicio se duerme después de 15 minutos de inactividad
  - Puede tardar 30-60 segundos en despertar

- **Plan Starter ($7/mes)**: Recomendado para producción:
  - Siempre activo
  - Sin tiempos de espera
  - Mejor rendimiento

## 📚 Recursos Adicionales

- [Documentación de Render](https://render.com/docs)
- [Documentación de Flask](https://flask.palletsprojects.com/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)

## ✅ Checklist de Despliegue

- [ ] Repositorio en GitHub/GitLab
- [ ] Archivo `requirements.txt` actualizado
- [ ] Archivo `build.sh` creado y con permisos
- [ ] Archivo `render.yaml` configurado
- [ ] Variables de entorno configuradas en Render
- [ ] Build exitoso en Render
- [ ] Endpoints verificados y funcionando
- [ ] OpenAI API funcionando correctamente
- [ ] Cloudinary funcionando correctamente

## 🎉 ¡Listo!

Tu API de Análisis Postural ahora está desplegada y lista para ser consumida por tu frontend.

**URL de tu API**: `https://tu-servicio.onrender.com`
