#!/bin/bash

# Script de actualización inteligente para el Descargador Universal Creditos a by SWAT
# Busca automáticamente tu archivo y lo actualiza

set -e

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🔄 Actualizador Inteligente del Descargador Universal${NC}"
echo "=================================================="
echo ""

APP_DIR="$HOME/.local/share/descargador-archivos"

# Verificar que existe el directorio de instalación
if [[ ! -d "$APP_DIR" ]]; then
    echo -e "${RED}❌ Error: La aplicación no está instalada${NC}"
    echo -e "${YELLOW}💡 Ejecuta primero: ./install_improved_fixed.sh${NC}"
    exit 1
fi

# Función para buscar archivos
find_source_file() {
    local files_found=()
    local search_patterns=(
        "./youtube_latest.py"
        "./descargador.py"
        "./youtube*.py"
        "./descargador*.py"
        "../youtube_latest.py"
        "../descargador.py"
        "$HOME/descargador-archivos/youtube_latest.py"
        "$HOME/descargador-archivos/descargador.py"
        "$HOME/Downloads/youtube_latest.py"
        "$HOME/Downloads/descargador.py"
        "$HOME/Descargas/youtube_latest.py"
        "$HOME/Descargas/descargador.py"
        "$HOME/Desktop/youtube_latest.py"
        "$HOME/Desktop/descargador.py"
        "$HOME/Escritorio/youtube_latest.py"
        "$HOME/Escritorio/descargador.py"
    )
    
    echo -e "${BLUE}🔍 Buscando archivos fuente...${NC}"
    
    for pattern in "${search_patterns[@]}"; do
        # Usar find para patrones con wildcards, ls para archivos específicos
        if [[ "$pattern" == *"*"* ]]; then
            while IFS= read -r -d '' file; do
                if [[ -f "$file" ]] && [[ "$file" == *.py ]]; then
                    files_found+=("$file")
                    echo -e "${GREEN}   ✓ Encontrado: $file${NC}"
                fi
            done < <(find "$(dirname "$pattern")" -name "$(basename "$pattern")" -type f -print0 2>/dev/null || true)
        else
            if [[ -f "$pattern" ]]; then
                files_found+=("$pattern")
                echo -e "${GREEN}   ✓ Encontrado: $pattern${NC}"
            fi
        fi
    done
    
    echo "${files_found[@]}"
}

# Buscar archivos fuente
source_files=($(find_source_file))

if [[ ${#source_files[@]} -eq 0 ]]; then
    echo -e "${RED}❌ No se encontraron archivos fuente${NC}"
    echo ""
    echo -e "${YELLOW}💡 Asegúrate de estar en el directorio correcto o tener uno de estos archivos:${NC}"
    echo "   • youtube_latest.py"
    echo "   • descargador.py"
    echo ""
    echo -e "${BLUE}🔧 Para actualizar manualmente:${NC}"
    echo "   cp /ruta/a/tu/archivo.py $APP_DIR/descargador.py"
    echo "   chmod +x $APP_DIR/descargador.py"
    exit 1
fi

# Si hay múltiples archivos, mostrar opciones
selected_file=""
if [[ ${#source_files[@]} -eq 1 ]]; then
    selected_file="${source_files[0]}"
    echo -e "${BLUE}ℹ️  Usando archivo: $selected_file${NC}"
else
    echo ""
    echo -e "${YELLOW}🔍 Se encontraron múltiples archivos:${NC}"
    for i in "${!source_files[@]}"; do
        echo "   $((i+1)). ${source_files[i]}"
    done
    echo "   0. Cancelar"
    echo ""
    while true; do
        echo -e "${BLUE}Selecciona el archivo a usar (1-${#source_files[@]}): ${NC}"
        read -r choice
        
        if [[ "$choice" == "0" ]]; then
            echo -e "${YELLOW}⚠️  Actualización cancelada${NC}"
            exit 0
        elif [[ "$choice" =~ ^[0-9]+$ ]] && [[ "$choice" -ge 1 ]] && [[ "$choice" -le ${#source_files[@]} ]]; then
            selected_file="${source_files[$((choice-1))]}"
            break
        else
            echo -e "${RED}❌ Selección inválida. Usa un número entre 1 y ${#source_files[@]}${NC}"
        fi
    done
fi

# Verificar que el archivo seleccionado existe y es válido
if [[ ! -f "$selected_file" ]]; then
    echo -e "${RED}❌ Error: El archivo seleccionado no existe: $selected_file${NC}"
    exit 1
fi

# Verificar que es un archivo Python válido
if ! head -n 5 "$selected_file" | grep -q "python" || ! grep -q "PyQt6" "$selected_file"; then
    echo -e "${YELLOW}⚠️  Advertencia: El archivo no parece ser la aplicación correcta${NC}"
    echo -e "${BLUE}¿Continuar de todas formas? (y/N): ${NC}"
    read -r continue_anyway
    if [[ ! "$continue_anyway" =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}⚠️  Actualización cancelada${NC}"
        exit 0
    fi
fi

# Hacer backup del archivo actual
backup_file="$APP_DIR/descargador.py.backup.$(date +%Y%m%d_%H%M%S)"
if [[ -f "$APP_DIR/descargador.py" ]]; then
    echo -e "${BLUE}ℹ️  Creando backup: $(basename "$backup_file")${NC}"
    cp "$APP_DIR/descargador.py" "$backup_file"
fi

# Actualizar archivo
echo -e "${BLUE}ℹ️  Actualizando desde: $selected_file${NC}"
echo -e "${BLUE}ℹ️  Destino: $APP_DIR/descargador.py${NC}"

if cp "$selected_file" "$APP_DIR/descargador.py"; then
    chmod +x "$APP_DIR/descargador.py"
    echo -e "${GREEN}✅ Archivo actualizado correctamente${NC}"
else
    echo -e "${RED}❌ Error al copiar el archivo${NC}"
    # Restaurar backup si existe
    if [[ -f "$backup_file" ]]; then
        echo -e "${BLUE}ℹ️  Restaurando backup...${NC}"
        cp "$backup_file" "$APP_DIR/descargador.py"
        rm "$backup_file"
    fi
    exit 1
fi

# Verificar que el archivo actualizado funciona
echo -e "${BLUE}ℹ️  Verificando que el archivo actualizado funciona...${NC}"
if python -c "
import sys
sys.path.insert(0, '$APP_DIR')
try:
    exec(open('$APP_DIR/descargador.py').read())
except SystemExit:
    pass  # Es normal que termine con sys.exit()
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)
print('OK')
" >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Verificación exitosa${NC}"
else
    echo -e "${RED}❌ El archivo actualizado tiene errores${NC}"
    if [[ -f "$backup_file" ]]; then
        echo -e "${BLUE}ℹ️  Restaurando backup...${NC}"
        cp "$backup_file" "$APP_DIR/descargador.py"
        echo -e "${YELLOW}⚠️  Se restauró la versión anterior${NC}"
    fi
    exit 1
fi

# Limpiar backup si todo salió bien
if [[ -f "$backup_file" ]]; then
    rm "$backup_file"
fi

# Actualizar yt-dlp si está disponible
echo -e "${BLUE}ℹ️  Verificando actualización de yt-dlp...${NC}"

# Intentar con pacman primero (método recomendado en Arch)
if command -v pacman >/dev/null 2>&1; then
    if pacman -Q yt-dlp >/dev/null 2>&1; then
        echo -e "${BLUE}ℹ️  Actualizando yt-dlp con pacman...${NC}"
        sudo pacman -Syu --noconfirm yt-dlp >/dev/null 2>&1 && {
            echo -e "${GREEN}✅ yt-dlp actualizado con pacman${NC}"
        } || {
            echo -e "${YELLOW}⚠️  No se pudo actualizar yt-dlp con pacman${NC}"
        }
    else
        # Intentar instalar con pacman si no está instalado
        echo -e "${BLUE}ℹ️  Instalando yt-dlp con pacman...${NC}"
        sudo pacman -S --noconfirm yt-dlp >/dev/null 2>&1 && {
            echo -e "${GREEN}✅ yt-dlp instalado con pacman${NC}"
        } || {
            echo -e "${YELLOW}⚠️  No se pudo instalar yt-dlp con pacman${NC}"
        }
    fi
# Fallback con pipx si está disponible
elif command -v pipx >/dev/null 2>&1; then
    echo -e "${BLUE}ℹ️  Actualizando yt-dlp con pipx...${NC}"
    pipx upgrade yt-dlp >/dev/null 2>&1 || pipx install yt-dlp >/dev/null 2>&1 && {
        echo -e "${GREEN}✅ yt-dlp actualizado/instalado con pipx${NC}"
    } || {
        echo -e "${YELLOW}⚠️  No se pudo actualizar yt-dlp con pipx${NC}"
    }
# Último recurso: pip con --break-system-packages (no recomendado)
elif command -v python >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Intentando con pip (no recomendado en Arch)...${NC}"
    python -m pip install --user --break-system-packages --upgrade yt-dlp >/dev/null 2>&1 && {
        echo -e "${GREEN}✅ yt-dlp actualizado con pip${NC}"
    } || {
        echo -e "${YELLOW}⚠️  No se pudo actualizar yt-dlp${NC}"
        echo -e "${BLUE}💡 Instala manualmente: sudo pacman -S yt-dlp${NC}"
    }
fi

echo ""
echo -e "${GREEN}🎉 ¡Actualización completada exitosamente!${NC}"
echo "========================================"
echo ""
echo -e "${BLUE}📍 Información de la actualización:${NC}"
echo "   • Archivo fuente: $selected_file"
echo "   • Archivo destino: $APP_DIR/descargador.py"
echo "   • Fecha: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo -e "${BLUE}🚀 Para ejecutar la aplicación actualizada:${NC}"
echo "   1. Terminal: descargador-archivos"
echo "   2. Menú: busca 'Descargador Universal'"
echo "   3. Alias: descargador"
echo ""

# Preguntar si quiere ejecutar la aplicación
echo -e "${BLUE}¿Quieres ejecutar la aplicación ahora? (y/N): ${NC}"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}ℹ️  Iniciando aplicación actualizada...${NC}"
    
    # Intentar diferentes métodos de ejecución
    if command -v descargador-archivos >/dev/null 2>&1; then
        descargador-archivos &
    elif [[ -x "$APP_DIR/descargador.py" ]]; then
        python "$APP_DIR/descargador.py" &
    else
        cd "$APP_DIR" && python descargador.py &
    fi
    
    echo -e "${GREEN}✅ Aplicación iniciada en segundo plano${NC}"
    echo -e "${BLUE}💡 Puedes cerrar esta terminal si quieres${NC}"
else
    echo -e "${BLUE}ℹ️  Puedes ejecutar la aplicación cuando quieras${NC}"
fi

echo ""
echo -e "${GREEN}✅ Actualización finalizada correctamente Creditos a by SWAT${NC}"
echo ""
