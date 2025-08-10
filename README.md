# ArchDownloader 🎥🎵📸
[![Python](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://python.org)
[![Arch Linux](https://img.shields.io/badge/OS-Arch%20Linux-blue.svg)](https://archlinux.org)


Una aplicación completa para Arch Linux que permite descargar videos, audios, imágenes y otros archivos multimedia desde múltiples plataformas populares de manera sencilla y eficiente.

<div align="center">
  <img src="https://i.imgur.com/HaDXjDC.png" alt="ArchDownloader Interface" width="800">
  <p><i>Interfaz principal de ArchDownloader</i></p>
</div>
Una aplicación completa para Arch Linux que permite descargar videos, audios, imágenes y otros archivos multimedia desde múltiples plataformas populares de manera sencilla y eficiente.

## ✨ Características

- 🎬 **Descarga de videos** en múltiples resoluciones y formatos
- 🎵 **Extracción de audio** en formatos MP3, WAV, FLAC
- 📸 **Descarga de imágenes** y contenido multimedia
- 🌐 **Soporte multiplataforma**: YouTube, TikTok, Instagram, Twitter/X, Vimeo, Twitch
- 📁 **Descarga de archivos directos** desde URLs
- 🖥️ **Interfaz gráfica intuitiva** desarrollada con PyQt6
- ⚡ **Descargas rápidas** y eficientes
- 🔄 **Actualizaciones automáticas** incluidas

## 🎯 Plataformas soportadas

| Plataforma | Videos | Audio | Imágenes | Estado |
|------------|--------|--------|----------|--------|
| YouTube    | ✅     | ✅     | ✅       | Estable |
| TikTok     | ✅     | ✅     | ✅       | Estable |
| Instagram  | ✅     | ✅     | ✅       | Estable |
| Twitter/X  | ✅     | ✅     | ✅       | Estable |
| Vimeo      | ✅     | ✅     | ❌       | Estable |
| Twitch     | ✅     | ✅     | ❌       | Beta    |

## 📋 Requisitos del sistema

- **Sistema Operativo**: Arch Linux (verificado automáticamente)
- **Python**: 3.7 o superior
- **Conexión a Internet**: Requerida para instalación y uso
- **Espacio en disco**: Mínimo 100 MB para la aplicación

## 🚀 Instalación

### Instalación automática (Recomendada)

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/Hector-SWAT/ArchDownloader.git
   cd ArchDownloader
   ```

2. **Ejecuta el instalador:**
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

### Instalación manual

Si prefieres instalar manualmente las dependencias:

```bash
# Actualizar el sistema
sudo pacman -Sy

# Instalar dependencias
sudo pacman -S python python-pip python-pyqt6 python-requests git

# Instalar dependencias de Python
pip install --user yt-dlp requests pyqt6
```

## 🔧 ¿Qué hace el instalador?

El script `install.sh` realiza las siguientes verificaciones y configuraciones:

- ✅ **Verificación del SO**: Confirma que ejecutas Arch Linux
- 🌐 **Conexión a internet**: Prueba conectividad con `archlinux.org`
- 📁 **Archivos necesarios**: Verifica la presencia de `descargador.py`
- 📦 **Actualización de paquetes**: Ejecuta `sudo pacman -Sy`
- 🔽 **Instalación de dependencias**:
  - `python` - Intérprete de Python
  - `python-pip` - Gestor de paquetes de Python
  - `python-pyqt6` - Interfaz gráfica
  - `python-requests` - Manejo de peticiones HTTP
  - `git` - Control de versiones
- ⚙️ **Configuración final**: Prepara la aplicación para su uso

## 💻 Uso

### Interfaz gráfica

Inicia la aplicación con interfaz gráfica:

```bash
python descargador.py
```

### Línea de comandos

Para usuarios avanzados, también puedes usar la aplicación desde terminal:

```bash
# Descargar video
python descargador.py --url "https://youtube.com/watch?v=VIDEO_ID"

# Descargar solo audio
python descargador.py --audio-only --url "https://youtube.com/watch?v=VIDEO_ID"

# Especificar directorio de descarga
python descargador.py --output "/home/usuario/Descargas" --url "URL"

# Descargar en calidad específica
python descargador.py --quality "720p" --url "URL"
```

### Opciones disponibles

| Opción | Descripción | Ejemplo |
|--------|-------------|---------|
| `--url` | URL del contenido a descargar | `--url "https://youtube.com/watch?v=abc123"` |
| `--output` | Directorio de descarga | `--output "/home/usuario/Videos"` |
| `--quality` | Calidad del video (480p, 720p, 1080p) | `--quality "1080p"` |
| `--audio-only` | Descargar solo audio | `--audio-only` |
| `--format` | Formato de salida (mp4, webm, mp3) | `--format "mp4"` |
| `--help` | Mostrar ayuda | `--help` |

## 🔄 Actualización

Mantén ArchDownloader siempre actualizado:

```bash
chmod +x update.sh
./update.sh
```

El script de actualización:
- Descarga la última versión desde GitHub
- Verifica la integridad de los archivos
- Actualiza las dependencias si es necesario
- Preserva tu configuración personal

## 📂 Estructura del proyecto

```
ArchDownloader/
├── README.md                 # Este archivo
├── install.sh               # Script de instalación
├── update.sh                # Script de actualización
├── descargador.py           # Script principal
├── requirements.txt         # Dependencias de Python
├── assets/                  # Recursos de la aplicación
│   ├── icons/              # Iconos de la interfaz
│   └── themes/             # Temas de la aplicación
└── docs/                   # Documentación adicional
    ├── CHANGELOG.md        # Registro de cambios
    └── CONTRIBUTING.md     # Guía para contribuir
```

## 🐛 Solución de problemas

### Problemas comunes

**Error: "No se puede conectar a internet"**
```bash
# Verifica tu conexión
ping -c 4 archlinux.org
```

**Error: "Python no encontrado"**
```bash
# Instala Python
sudo pacman -S python python-pip
```

**Error: "Dependencias faltantes"**
```bash
# Reinstala dependencias
pip install --user --upgrade yt-dlp requests pyqt6
```

**Error de permisos**
```bash
# Asegúrate de que los scripts tengan permisos de ejecución
chmod +x install.sh update.sh
```

### Obtener ayuda

Si encuentras problemas no listados aquí:

1. Revisa los [Issues existentes](https://github.com/Hector-SWAT/ArchDownloader/issues)
2. Crea un [nuevo Issue](https://github.com/Hector-SWAT/ArchDownloader/issues/new) con:
   - Versión de Arch Linux
   - Versión de Python
   - Mensaje de error completo
   - Pasos para reproducir el problema

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Puedes ayudar de varias formas:

- 🐛 **Reportar bugs**: Abre un issue describiendo el problema
- 💡 **Sugerir mejoras**: Propón nuevas características
- 🔧 **Contribuir código**: Envía pull requests
- 📖 **Mejorar documentación**: Ayuda a mejorar este README
- 🌐 **Traducciones**: Ayuda a traducir la aplicación

### Proceso de contribución

1. Fork el repositorio
2. Crea una rama para tu función: `git checkout -b nueva-caracteristica`
3. Commit tus cambios: `git commit -am 'Agregar nueva característica'`
4. Push a la rama: `git push origin nueva-caracteristica`
5. Abre un Pull Request

## 👨‍💻 Autor

**Héctor Hernández**
- 📧 Email: [hectorhernadez51@gmail.com](mailto:hectorhernadez51@gmail.com)
- 🐙 GitHub: [@Hector-SWAT](https://github.com/Hector-SWAT)

## 🙏 Reconocimientos

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Biblioteca principal para descarga de videos
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - Framework para la interfaz gráfica
- [Arch Linux](https://archlinux.org) - La mejor distribución Linux

## 📊 Estado del proyecto

- ✅ **Versión actual**: 1.0.0
- 🔄 **Estado**: En desarrollo activo
- 📅 **Última actualización**: Agosto 2025
- 🎯 **Próximas características**: 
  - Soporte para más plataformas
  - Descarga en lotes
  - Programación de descargas
  - Plugin para navegador

---

<div align="center">

**¿Te gusta ArchDownloader? ¡Dale una ⭐ al repositorio!**

[🐛 Reportar Bug](https://github.com/Hector-SWAT/ArchDownloader/issues) • [💡 Solicitar Función](https://github.com/Hector-SWAT/ArchDownloader/issues) • [📖 Documentación](https://github.com/Hector-SWAT/ArchDownloader/wiki)

</div>
