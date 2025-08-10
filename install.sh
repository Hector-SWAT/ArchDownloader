#!/bin/bash

# Script de instalación para Descargador Universal - Arch Linux Creditos a by SWAT
# Solo instala dependencias y configura el sistema para usar tu descargador.py

set -e  # Salir si hay algún error

echo "🐧 Instalador del Descargador Universal para Arch Linux Creditos a by SWAT"
echo "====================================================="
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para mostrar mensajes con colores
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar que estamos en Arch Linux
print_info "Verificando sistema operativo..."
if [[ ! -f /etc/arch-release ]]; then
    print_error "Este script está diseñado para Arch Linux"
    print_info "Sistema detectado: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'=' -f2 | tr -d '\"')"
    exit 1
fi

print_success "Sistema Arch Linux detectado correctamente"

# Verificar conexión a internet
print_info "Verificando conexión a internet..."
if ! ping -c 1 archlinux.org &> /dev/null; then
    print_error "No hay conexión a internet"
    exit 1
fi
print_success "Conexión a internet OK"

# Verificar que existe el archivo descargador.py en el directorio actual
DESCARGADOR_FILE=""
if [[ -f "./youtube_latest.py" ]]; then
    DESCARGADOR_FILE="./youtube_latest.py"
    print_success "Encontrado archivo: youtube_latest.py"
elif [[ -f "./descargador.py" ]]; then
    DESCARGADOR_FILE="./descargador.py"
    print_success "Encontrado archivo: descargador.py"
else
    print_error "No se encontró youtube_latest.py ni descargador.py en el directorio actual"
    print_info "Asegúrate de ejecutar este script desde la carpeta que contiene tu aplicación"
    exit 1
fi

# Actualizar el sistema
print_info "Actualizando base de datos de paquetes..."
sudo pacman -Sy --noconfirm

# Instalar dependencias del sistema
print_info "Instalando dependencias del sistema..."
PACKAGES=(
    "python"
    "python-pip"
    "python-pyqt6"
    "python-requests"
    "git"
)

for package in "${PACKAGES[@]}"; do
    if pacman -Q $package &> /dev/null; then
        print_success "$package ya está instalado"
    else
        print_info "Instalando $package..."
        sudo pacman -S --noconfirm $package || {
            print_error "Error al instalar $package"
            exit 1
        }
        print_success "$package instalado correctamente"
    fi
done

# Instalar dependencias de Python usando pacman (método recomendado en Arch)
print_info "Instalando dependencias adicionales de Python..."
ARCH_PYTHON_PACKAGES=(
    "yt-dlp"
    "python-requests"
)

for package in "${ARCH_PYTHON_PACKAGES[@]}"; do
    if pacman -Q $package &> /dev/null; then
        print_success "$package ya está instalado"
    else
        print_info "Instalando $package desde repositorios de Arch..."
        sudo pacman -S --noconfirm $package || {
            print_warning "No se pudo instalar $package desde pacman"
            # Intentar con pip como fallback usando --user y --break-system-packages
            if [[ "$package" == "yt-dlp" ]]; then
                print_info "Intentando instalar yt-dlp con pip como fallback..."
                python -m pip install --user --break-system-packages yt-dlp || {
                    print_warning "yt-dlp no se instaló, pero se puede instalar automáticamente desde la app"
                }
            fi
        }
        if pacman -Q $package &> /dev/null; then
            print_success "$package instalado correctamente"
        fi
    fi
done

# Verificar instalación de PyQt6
print_info "Verificando instalación de PyQt6..."
python -c "from PyQt6.QtWidgets import QApplication" 2>/dev/null || {
    print_error "PyQt6 no se instaló correctamente"
    print_info "Intentando instalar desde pip..."
    python -m pip install --user PyQt6 || {
        print_error "Error al instalar PyQt6 desde pip"
        exit 1
    }
}
print_success "PyQt6 verificado correctamente"

# Crear directorio de la aplicación
APP_DIR="$HOME/.local/share/descargador-archivos"
print_info "Creando directorio de aplicación: $APP_DIR"
mkdir -p "$APP_DIR"
print_success "Directorio creado: $APP_DIR"

# Verificar que no estamos ejecutando desde el directorio de instalación
CURRENT_DIR="$(pwd)"
if [[ "$CURRENT_DIR" == "$APP_DIR" ]]; then
    print_error "No puedes ejecutar este script desde el directorio de instalación"
    print_info "Directorio actual: $CURRENT_DIR"
    print_info "Directorio de instalación: $APP_DIR"
    print_info "Por favor, ejecuta el script desde donde tienes tu archivo fuente"
    exit 1
fi

# Copiar el archivo de la aplicación
DEST_FILE="$APP_DIR/descargador.py"
print_info "Copiando tu archivo $DESCARGADOR_FILE al directorio de instalación..."

# Verificar que los archivos no son el mismo
if [[ "$(realpath "$DESCARGADOR_FILE")" == "$(realpath "$DEST_FILE")" ]]; then
    print_warning "El archivo fuente y destino son el mismo"
    print_info "Esto significa que ya está instalado correctamente"
else
    cp "$DESCARGADOR_FILE" "$DEST_FILE"
    chmod +x "$DEST_FILE"
    print_success "Archivo copiado y configurado como ejecutable"
fi

# Crear script de lanzamiento en /usr/local/bin
print_info "Creando script de lanzamiento global..."
sudo tee /usr/local/bin/descargador-archivos > /dev/null << EOF
#!/bin/bash
# Lanzador del Descargador Universal
cd "$APP_DIR"
exec python descargador.py "\$@"
EOF

sudo chmod +x /usr/local/bin/descargador-archivos
print_success "Script de lanzamiento creado: /usr/local/bin/descargador-archivos"

# Crear script de actualización personalizado
print_info "Creando script de actualización personalizado..."
cat > "$APP_DIR/actualizar.sh" << EOF
#!/bin/bash

# Script de actualización automática
# Este script busca el archivo original para actualizarlo

set -e

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "\${BLUE}🔄 Actualizador del Descargador Universal\${NC}"
echo "========================================"

# Buscar el archivo original
ORIGINAL_FILE=""
SEARCH_PATHS=(
    "\$HOME/descargador-archivos/youtube_latest.py"
    "\$HOME/descargador-archivos/descargador.py"
    "\$HOME/Downloads/youtube_latest.py"
    "\$HOME/Downloads/descargador.py"
    "\$HOME/Descargas/youtube_latest.py"
    "\$HOME/Descargas/descargador.py"
    "./youtube_latest.py"
    "./descargador.py"
)

for path in "\${SEARCH_PATHS[@]}"; do
    if [[ -f "\$path" ]]; then
        ORIGINAL_FILE="\$path"
        echo -e "\${GREEN}✅ Encontrado: \$path\${NC}"
        break
    fi
done

if [[ -z "\$ORIGINAL_FILE" ]]; then
    echo -e "\${RED}❌ No se encontró el archivo original\${NC}"
    echo -e "\${YELLOW}ℹ️  Rutas buscadas:\${NC}"
    for path in "\${SEARCH_PATHS[@]}"; do
        echo "   - \$path"
    done
    echo ""
    echo -e "\${BLUE}💡 Para actualizar manualmente:\${NC}"
    echo "   cp /ruta/a/tu/archivo.py $APP_DIR/descargador.py"
    exit 1
fi

echo -e "\${BLUE}ℹ️  Actualizando desde: \$ORIGINAL_FILE\${NC}"
cp "\$ORIGINAL_FILE" "$APP_DIR/descargador.py"
chmod +x "$APP_DIR/descargador.py"

echo -e "\${GREEN}✅ Actualización completada\${NC}"
echo ""
echo -e "\${BLUE}¿Quieres ejecutar la aplicación ahora? (y/N)\${NC}"
read -r response
if [[ "\$response" =~ ^[Yy]\$ ]]; then
    echo -e "\${BLUE}ℹ️  Iniciando aplicación...\${NC}"
    python "$APP_DIR/descargador.py" &
    echo -e "\${GREEN}✅ Aplicación iniciada\${NC}"
fi
EOF

chmod +x "$APP_DIR/actualizar.sh"
print_success "Script de actualización creado: $APP_DIR/actualizar.sh"

# Crear archivo .desktop para el menú de aplicaciones
DESKTOP_DIR="$HOME/.local/share/applications"
mkdir -p "$DESKTOP_DIR"

print_info "Creando entrada en el menú de aplicaciones..."
cat > "$DESKTOP_DIR/descargador-archivos.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Descargador Universal
Name[es]=Descargador Universal
Comment=Descarga videos de YouTube y archivos directos con auto-organización
Comment[es]=Descarga videos de YouTube y archivos directos con auto-organización
Exec=/usr/local/bin/descargador-archivos
Icon=folder-download
Terminal=false
Categories=Network;FileTransfer;Utility;AudioVideo;
Keywords=download;descargar;youtube;videos;archivos;files;yt-dlp;
StartupNotify=true
EOF

print_success "Entrada de menú creada correctamente"

# Actualizar base de datos de aplicaciones del escritorio
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
fi

# Crear alias en el shell del usuario
print_info "Configurando alias en el shell..."
SHELL_RC=""
if [[ $SHELL == *"zsh"* ]]; then
    SHELL_RC="$HOME/.zshrc"
elif [[ $SHELL == *"bash"* ]]; then
    SHELL_RC="$HOME/.bashrc"
fi

if [[ -n "$SHELL_RC" ]] && [[ -f "$SHELL_RC" ]]; then
    # Verificar si el alias ya existe
    if ! grep -q "alias descargador=" "$SHELL_RC"; then
        echo "" >> "$SHELL_RC"
        echo "# Descargador Universal" >> "$SHELL_RC"
        echo "alias descargador='descargador-archivos'" >> "$SHELL_RC"
        echo "alias actualizar-descargador='$APP_DIR/actualizar.sh'" >> "$SHELL_RC"
        print_success "Alias agregados a $SHELL_RC"
    else
        print_info "Alias ya existen en $SHELL_RC"
    fi
fi

# Crear directorio de descargas si no existe
DOWNLOADS_DIR="$HOME/Descargas"
if [[ ! -d "$DOWNLOADS_DIR" ]]; then
    mkdir -p "$DOWNLOADS_DIR"
    print_success "Directorio de descargas creado: $DOWNLOADS_DIR"
fi

# Verificar que yt-dlp funciona
print_info "Verificando yt-dlp..."
if command -v yt-dlp &> /dev/null; then
    YT_DLP_VERSION=$(yt-dlp --version 2>/dev/null || echo "unknown")
    print_success "yt-dlp está disponible globalmente: $YT_DLP_VERSION"
elif python -c "import yt_dlp; print('OK')" &> /dev/null; then
    print_success "yt-dlp está disponible para Python"
else
    print_warning "yt-dlp no está disponible"
    print_info "La aplicación intentará instalarlo automáticamente cuando sea necesario"
fi

# Verificar instalación completa
print_info "Verificando instalación completa..."
if python -c "from PyQt6.QtWidgets import QApplication; import requests; print('✅ Dependencias OK')" 2>/dev/null; then
    print_success "Todas las dependencias están correctamente instaladas"
else
    print_error "Hay problemas con las dependencias"
    exit 1
fi

echo ""
echo "🎉 ¡Instalación completada exitosamente!"
echo "========================================"
echo ""
print_success "Tu aplicación se ha instalado correctamente"
echo ""
print_info "📍 Ubicación de archivos:"
echo "   • Aplicación: $APP_DIR/descargador.py"
echo "   • Actualizador: $APP_DIR/actualizar.sh"
echo "   • Lanzador: /usr/local/bin/descargador-archivos"
echo "   • Menú: $DESKTOP_DIR/descargador-archivos.desktop"
echo ""
print_info "🚀 Formas de ejecutar:"
echo "   1. Desde el menú: busca 'Descargador Universal'"
echo "   2. Terminal: descargador-archivos"
echo "   3. Alias: descargador (reinicia terminal)"
echo "   4. Directo: python $APP_DIR/descargador.py"
echo ""
print_info "🔄 Para actualizar:"
echo "   1. Desde terminal: actualizar-descargador"
echo "   2. Desde la app: $APP_DIR/actualizar.sh"
echo "   3. Manual: cp tu_archivo.py $APP_DIR/descargador.py"
echo "   4. Con pipx: pipx install --force yt-dlp (si usas pipx)"
echo ""
print_info "🎥 Características instaladas:"
echo "   • YouTube, Vimeo, TikTok, Instagram, etc."
echo "   • Descargas directas de archivos"
echo "   • Auto-organización por tipo de archivo"
echo "   • Calidad seleccionable de video"
echo "   • Descarga solo audio (MP3)"
echo "   • Interfaz gráfica moderna"
echo "   • yt-dlp integrado"
echo ""

# Función para mostrar test opcional
print_info "¿Te gustaría probar la aplicación ahora? (y/N)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    print_info "Iniciando aplicación de prueba..."
    python "$APP_DIR/descargador.py" &
    print_success "Aplicación iniciada en segundo plano"
else
    print_info "Puedes iniciar la aplicación cuando quieras"
fi

echo ""
print_success "¡Disfruta tu Descargador Universal! 🎯 Creditos a by SWAT"
echo ""
print_info "💡 Consejos:"
echo "   • Para instalar yt-dlp manualmente: sudo pacman -S yt-dlp"
echo "   • O con pipx (recomendado): pipx install yt-dlp"
echo "   • Para desinstalar: sudo rm /usr/local/bin/descargador-archivos && rm -rf $APP_DIR"
echo "   • Si tienes problemas con pip, usa solo los paquetes de Arch"
echo ""
