#!/usr/bin/env python3
# -*- coding: utf-8 Creditos a by SWAT-*-
"""
Descargador Universal con PyQt6
Soporta YouTube, videos de redes sociales y descargas directas
Compatible con Arch Linux Creditos a by SWAT
"""

import sys
import os
import requests
import mimetypes
import threading
import time
import re
import subprocess
import json
import shutil
from pathlib import Path
from urllib.parse import urlparse, unquote
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QProgressBar, QTextEdit, QGroupBox, QFileDialog,
                            QMessageBox, QGridLayout, QFrame, QSplitter,
                            QStatusBar, QMenuBar, QMenu, QComboBox, QCheckBox,
                            QTabWidget, QSpinBox)
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPalette, QColor, QAction

class UniversalDownloadWorker(QThread):
    """Worker thread para manejar descargas universales sin bloquear la UI"""
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    log_updated = pyqtSignal(str)
    download_finished = pyqtSignal(bool, str, str)
    
    def __init__(self, url, download_path, file_categories, is_video_platform=False, 
                 video_quality="best", audio_only=False, custom_name=""):
        super().__init__()
        self.url = url
        self.download_path = download_path
        self.file_categories = file_categories
        self.is_video_platform = is_video_platform
        self.video_quality = video_quality
        self.audio_only = audio_only
        self.custom_name = custom_name
        self.is_cancelled = False
        self.process = None
    
    def cancel(self):
        self.is_cancelled = True
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                try:
                    self.process.kill()
                except:
                    pass
    
    def detect_video_platform(self, url):
        """Detecta si la URL es de una plataforma de video soportada"""
        video_patterns = [
            r'youtube\.com/watch',
            r'youtu\.be/',
            r'vimeo\.com/',
            r'tiktok\.com/',
            r'instagram\.com/',
            r'facebook\.com/',
            r'twitter\.com/',
            r'x\.com/',
            r'twitch\.tv/',
            r'dailymotion\.com/',
            r'metacafe\.com/',
            r'veoh\.com/'
        ]
        
        for pattern in video_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        return False
    
    def check_ytdlp_available(self):
        """Verifica si yt-dlp está disponible"""
        try:
            result = subprocess.run(['yt-dlp', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            try:
                result = subprocess.run([sys.executable, '-m', 'yt_dlp', '--version'], 
                                      capture_output=True, text=True, timeout=5)
                return result.returncode == 0
            except:
                return False
    
    def install_ytdlp(self):
        """Intenta instalar yt-dlp automáticamente"""
        self.log_updated.emit("🔧 yt-dlp no encontrado, intentando instalar...")
        self.status_updated.emit("Instalando yt-dlp...")
        
        try:
            # Intentar con pacman primero (Arch Linux)
            result = subprocess.run(['sudo', 'pacman', '-S', '--noconfirm', 'yt-dlp'],
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                self.log_updated.emit("✅ yt-dlp instalado con pacman")
                return True
        except:
            pass
        
        try:
            # Fallback a pip
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', '--user', 'yt-dlp'],
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                self.log_updated.emit("✅ yt-dlp instalado con pip")
                return True
        except:
            pass
        
        self.log_updated.emit("❌ No se pudo instalar yt-dlp automáticamente")
        return False
    
    def get_file_category(self, filename):
        """Determina la categoría del archivo basándose en su extensión"""
        file_ext = Path(filename).suffix.lower()
        
        for category, info in self.file_categories.items():
            if file_ext in info['extensions']:
                return info['folder']
        
        return self.file_categories['otros']['folder']
    
    def download_with_ytdlp(self):
        """Descarga usando yt-dlp para plataformas de video"""
        try:
            # Verificar si yt-dlp está disponible
            if not self.check_ytdlp_available():
                if not self.install_ytdlp():
                    return False, "yt-dlp no está disponible y no se pudo instalar"
            
            # Determinar carpeta de destino
            if self.audio_only:
                dest_folder = os.path.join(self.download_path, self.file_categories['musica']['folder'])
                file_extension = 'mp3'
            else:
                dest_folder = os.path.join(self.download_path, self.file_categories['videos']['folder'])
                file_extension = 'mp4'
            
            os.makedirs(dest_folder, exist_ok=True)
            
            # Configurar comando yt-dlp
            cmd = ['yt-dlp']
            
            # Verificar si el comando existe, si no usar python -m
            if not shutil.which('yt-dlp'):
                cmd = [sys.executable, '-m', 'yt_dlp']
            
            if self.audio_only:
                cmd.extend([
                    '-x',  # Extraer audio
                    '--audio-format', 'mp3',
                    '--audio-quality', '192K'
                ])
            else:
                if self.video_quality == "best":
                    cmd.extend(['-f', 'best[height<=?1080]'])
                elif self.video_quality == "720p":
                    cmd.extend(['-f', 'best[height<=?720]'])
                elif self.video_quality == "480p":
                    cmd.extend(['-f', 'best[height<=?480]'])
            
            # Configurar nombre de archivo
            if self.custom_name:
                safe_name = re.sub(r'[^\w\s-]', '', self.custom_name)
                cmd.extend(['-o', os.path.join(dest_folder, f'{safe_name}.%(ext)s')])
            else:
                cmd.extend(['-o', os.path.join(dest_folder, '%(title)s.%(ext)s')])
            
            cmd.append(self.url)
            
            self.log_updated.emit(f"🎥 Procesando con yt-dlp: {self.url}")
            
            # Ejecutar yt-dlp
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                universal_newlines=True
            )
            
            output_lines = []
            while True:
                if self.is_cancelled:
                    return False, "Descarga cancelada"
                
                output = self.process.stdout.readline()
                if output == '' and self.process.poll() is not None:
                    break
                
                if output:
                    output_lines.append(output.strip())
                    
                    # Parsear progreso de yt-dlp
                    if '[download]' in output and '%' in output:
                        try:
                            # Buscar porcentaje en la línea
                            match = re.search(r'(\d+\.?\d*)%', output)
                            if match:
                                progress = float(match.group(1))
                                self.progress_updated.emit(int(progress))
                                self.status_updated.emit(f"Descargando... {progress:.1f}%")
                        except:
                            pass
                    
                    # Mostrar información relevante en el log
                    if any(keyword in output.lower() for keyword in ['title:', 'destination:', 'finished']):
                        self.log_updated.emit(f"ℹ️  {output.strip()}")
            
            # Verificar resultado
            return_code = self.process.poll()
            
            if return_code == 0:
                self.log_updated.emit("✅ Descarga completada con yt-dlp")
                
                # Buscar archivos descargados recientes
                recent_files = []
                for ext in ['.mp4', '.webm', '.mkv', '.mp3', '.m4a']:
                    pattern = os.path.join(dest_folder, f'*{ext}')
                    import glob
                    files = glob.glob(pattern)
                    for f in files:
                        if os.path.getmtime(f) > time.time() - 60:  # Archivos de los últimos 60 segundos
                            recent_files.append(f)
                
                if recent_files:
                    newest_file = max(recent_files, key=os.path.getmtime)
                    filename = os.path.basename(newest_file)
                    category = self.file_categories['musica']['folder'] if self.audio_only else self.file_categories['videos']['folder']
                    return True, f"Video descargado exitosamente:\n{filename}\n\nGuardado en: {category}/", newest_file
                else:
                    return True, "Descarga completada pero no se pudo localizar el archivo", ""
            else:
                error_output = '\n'.join(output_lines[-10:])  # Últimas 10 líneas de error
                return False, f"Error en yt-dlp:\n{error_output}"
                
        except Exception as e:
            return False, f"Error ejecutando yt-dlp: {str(e)}"
    
    def download_direct_file(self):
        """Descarga archivos directos usando requests"""
        try:
            self.log_updated.emit(f"🔄 Descarga directa: {self.url}")
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': '*/*',
                'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
                'Connection': 'keep-alive'
            }
            
            response = requests.get(self.url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()
            
            if self.is_cancelled:
                return False, "Descarga cancelada"
            
            # Obtener información del archivo
            content_disposition = response.headers.get('Content-Disposition')
            filename = self.get_filename_from_url(self.url, content_disposition)
            
            if self.custom_name:
                # Usar nombre personalizado pero conservar extensión
                original_ext = Path(filename).suffix
                safe_name = re.sub(r'[^\w\s-]', '', self.custom_name)
                filename = f"{safe_name}{original_ext}" if original_ext else f"{safe_name}.bin"
            
            # Si no tiene extensión, intentar detectar por content-type
            if '.' not in filename:
                content_type = response.headers.get('Content-Type', '').split(';')[0]
                extension = mimetypes.guess_extension(content_type)
                if extension:
                    filename += extension
                else:
                    filename += '.bin'
            
            # Determinar carpeta de destino
            category_folder = self.get_file_category(filename)
            dest_folder = os.path.join(self.download_path, category_folder)
            os.makedirs(dest_folder, exist_ok=True)
            
            # Manejar archivos duplicados
            final_path = self.get_unique_filepath(dest_folder, filename)
            
            # Obtener tamaño del archivo
            total_size = int(response.headers.get('Content-Length', 0))
            downloaded_size = 0
            
            self.log_updated.emit(f"📄 Archivo: {os.path.basename(final_path)}")
            self.log_updated.emit(f"📁 Guardando en: {category_folder}/")
            
            if total_size > 0:
                self.log_updated.emit(f"📏 Tamaño: {self.format_bytes(total_size)}")
            
            # Descargar archivo
            chunk_size = 8192
            with open(final_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if self.is_cancelled:
                        file.close()
                        os.remove(final_path)
                        return False, "Descarga cancelada"
                    
                    if chunk:
                        file.write(chunk)
                        downloaded_size += len(chunk)
                        
                        if total_size > 0:
                            progress = int((downloaded_size / total_size) * 100)
                            self.progress_updated.emit(progress)
                            self.status_updated.emit(f"Descargando... {progress}%")
            
            filename_result = os.path.basename(final_path)
            return True, f"Archivo descargado exitosamente:\n{filename_result}\n\nGuardado en: {category_folder}/", final_path
            
        except requests.RequestException as e:
            return False, f"Error de conexión: {str(e)}"
        except Exception as e:
            return False, f"Error inesperado: {str(e)}"
    
    def get_filename_from_url(self, url, content_disposition=None):
        """Extrae el nombre del archivo de la URL o del header Content-Disposition"""
        if content_disposition:
            if 'filename=' in content_disposition:
                filename = content_disposition.split('filename=')[1].strip('"\'')
                return unquote(filename)
        
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        
        if filename and '.' in filename:
            return unquote(filename)
        
        return "archivo_descargado"
    
    def get_unique_filepath(self, directory, filename):
        """Genera un path único para evitar sobrescribir archivos"""
        base_name = os.path.splitext(filename)[0]
        extension = os.path.splitext(filename)[1]
        counter = 1
        final_path = os.path.join(directory, filename)
        
        while os.path.exists(final_path):
            new_filename = f"{base_name}_{counter}{extension}"
            final_path = os.path.join(directory, new_filename)
            counter += 1
        
        return final_path
    
    def format_bytes(self, bytes_size):
        """Convierte bytes a formato legible"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} TB"
    
    def run(self):
        try:
            self.status_updated.emit("Analizando URL...")
            self.progress_updated.emit(0)
            
            # Detectar si es plataforma de video
            if self.detect_video_platform(self.url):
                self.log_updated.emit("🎥 Plataforma de video detectada")
                success, message, filepath = self.download_with_ytdlp()
            else:
                self.log_updated.emit("📁 Descarga directa detectada")
                success, message, filepath = self.download_direct_file()
            
            if success:
                self.progress_updated.emit(100)
                self.status_updated.emit("✅ Descarga completada")
                self.log_updated.emit(f"✅ {message}")
                if filepath:
                    self.log_updated.emit(f"📍 Ubicación: {filepath}")
            
            self.download_finished.emit(success, message, filepath)
            
        except Exception as e:
            error_msg = f"Error inesperado: {str(e)}"
            self.log_updated.emit(f"❌ {error_msg}")
            self.status_updated.emit("Error inesperado")
            self.download_finished.emit(False, error_msg, "")

class UniversalDownloaderGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.download_worker = None
        
        # Configuración de carpetas por tipo
        self.file_categories = {
            'imagenes': {
                'extensions': ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp', '.tiff', '.ico', '.heic', '.avif'],
                'folder': 'Imágenes',
                'icon': '🖼️'
            },
            'musica': {
                'extensions': ['.mp3', '.flac', '.ogg', '.wav', '.aac', '.m4a', '.wma', '.opus', '.alac'],
                'folder': 'Música',
                'icon': '🎵'
            },
            'videos': {
                'extensions': ['.mp4', '.webm', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.m4v', '.3gp', '.ogv'],
                'folder': 'Videos',
                'icon': '🎥'
            },
            'documentos': {
                'extensions': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx'],
                'folder': 'Documentos',
                'icon': '📄'
            },
            'archivos': {
                'extensions': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'],
                'folder': 'Archivos',
                'icon': '📦'
            },
            'otros': {
                'extensions': [],
                'folder': 'Otros',
                'icon': '📁'
            }
        }
        
        self.download_path = os.path.expanduser("~/Descargas")
        self.init_ui()
        self.setup_style()
        
    def init_ui(self):
        self.setWindowTitle("🌐 Descargador Universal - YouTube & Archivos Directos")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(900, 700)
        
        # Widget central con tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Título y subtítulo
        self.create_header(main_layout)
        
        # Crear tabs
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # Tab principal de descarga
        self.create_download_tab()
        
        # Tab de configuración
        self.create_settings_tab()
        
        # Barra de estado
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Listo para descargar")
        
        # Menu bar
        self.create_menu_bar()
        
    def create_header(self, layout):
        header_frame = QFrame()
        header_layout = QVBoxLayout(header_frame)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_label = QLabel("🌐 Descargador Universal by SWAT")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        subtitle_label = QLabel("YouTube, TikTok, Instagram, Vimeo + Archivos Directos")
        subtitle_label.setObjectName("subtitle")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        layout.addWidget(header_frame)
    
    def create_download_tab(self):
        download_widget = QWidget()
        download_layout = QVBoxLayout(download_widget)
        
        # Crear splitter
        splitter = QSplitter(Qt.Orientation.Vertical)
        download_layout.addWidget(splitter)
        
        # Panel superior
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        
        # Grupo de URL y opciones
        self.create_url_group(top_layout)
        
        # Grupo de opciones de video
        self.create_video_options_group(top_layout)
        
        # Grupo de formatos soportados
        self.create_platforms_group(top_layout)
        
        splitter.addWidget(top_widget)
        
        # Panel inferior con progreso y log
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        
        # Grupo de progreso
        self.create_progress_group(bottom_layout)
        
        splitter.addWidget(bottom_widget)
        
        # Configurar proporciones del splitter
        splitter.setSizes([500, 300])
        
        self.tabs.addTab(download_widget, "🎬 Descarga")
    
    def create_settings_tab(self):
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        
        # Grupo de configuración de carpeta
        self.create_folder_config_group(settings_layout)
        
        # Grupo de formatos soportados
        self.create_formats_group(settings_layout)
        
        # Espaciador
        settings_layout.addStretch()
        
        self.tabs.addTab(settings_widget, "⚙️ Configuración")
    
    def create_url_group(self, layout):
        url_group = QGroupBox("🔗 URL a Descargar")
        url_layout = QVBoxLayout(url_group)
        
        # URL input
        url_input_layout = QHBoxLayout()
        url_label = QLabel("URL:")
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("Pega aquí la URL de YouTube, TikTok, Instagram, archivo directo...")
        self.url_edit.returnPressed.connect(self.start_download)
        
        url_input_layout.addWidget(url_label)
        url_input_layout.addWidget(self.url_edit, 1)
        
        # Nombre personalizado
        name_layout = QHBoxLayout()
        name_label = QLabel("Nombre personalizado (opcional):")
        self.custom_name_edit = QLineEdit()
        self.custom_name_edit.setPlaceholderText("Deja vacío para usar el nombre original")
        
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.custom_name_edit, 1)
        
        url_layout.addLayout(url_input_layout)
        url_layout.addLayout(name_layout)
        
        layout.addWidget(url_group)
    
    def create_video_options_group(self, layout):
        options_group = QGroupBox("🎥 Opciones de Video")
        options_layout = QHBoxLayout(options_group)
        
        # Calidad de video
        quality_layout = QVBoxLayout()
        quality_label = QLabel("Calidad de video:")
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Mejor disponible", "720p", "480p", "360p"])
        self.quality_combo.setCurrentIndex(0)
        
        quality_layout.addWidget(quality_label)
        quality_layout.addWidget(self.quality_combo)
        
        # Solo audio
        audio_layout = QVBoxLayout()
        audio_label = QLabel("Descargar:")
        self.audio_only_check = QCheckBox("Solo audio (MP3)")
        self.audio_only_check.stateChanged.connect(self.toggle_audio_only)
        
        audio_layout.addWidget(audio_label)
        audio_layout.addWidget(self.audio_only_check)
        
        # Botones de acción
        buttons_layout = QVBoxLayout()
        buttons_label = QLabel("Acciones:")
        
        self.download_btn = QPushButton("⬇️ Descargar")
        self.download_btn.clicked.connect(self.start_download)
        self.download_btn.setObjectName("download_btn")
        
        self.cancel_btn = QPushButton("❌ Cancelar")
        self.cancel_btn.clicked.connect(self.cancel_download)
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setObjectName("cancel_btn")
        
        clear_btn = QPushButton("🗑️ Limpiar")
        clear_btn.clicked.connect(self.clear_inputs)
        
        buttons_layout.addWidget(buttons_label)
        buttons_layout.addWidget(self.download_btn)
        buttons_layout.addWidget(self.cancel_btn)
        buttons_layout.addWidget(clear_btn)
        
        options_layout.addLayout(quality_layout)
        options_layout.addLayout(audio_layout)
        options_layout.addLayout(buttons_layout)
        options_layout.addStretch()
        
        layout.addWidget(options_group)
    
    def create_platforms_group(self, layout):
        platforms_group = QGroupBox("🌐 Plataformas Soportadas")
        platforms_layout = QGridLayout(platforms_group)
        
        platforms = [
            ("🎥", "YouTube", "Videos, listas, canales"),
            ("🎵", "TikTok", "Videos cortos, audio"),
            ("📸", "Instagram", "Posts, stories, reels"),
            ("🐦", "Twitter/X", "Videos, GIFs"),
            ("📺", "Vimeo", "Videos HD"),
            ("🎮", "Twitch", "Clips, VODs"),
            ("📁", "Archivos directos", "PDF, ZIP, MP4, etc.")
        ]
        
        for i, (icon, name, description) in enumerate(platforms):
            row = i // 3
            col = (i % 3) * 3
            
            icon_label = QLabel(icon)
            icon_label.setFont(QFont("Arial", 16))
            name_label = QLabel(f"<b>{name}</b>")
            desc_label = QLabel(description)
            desc_label.setStyleSheet("color: #aaa;")
            
            platforms_layout.addWidget(icon_label, row, col)
            platforms_layout.addWidget(name_label, row, col + 1)
            platforms_layout.addWidget(desc_label, row, col + 2)
        
        layout.addWidget(platforms_group)
    
    def create_folder_config_group(self, layout):
        config_group = QGroupBox("📁 Configuración de Carpetas")
        config_layout = QVBoxLayout(config_group)
        
        # Ruta principal
        path_layout = QHBoxLayout()
        path_label = QLabel("Carpeta de descarga:")
        self.path_edit = QLineEdit(self.download_path)
        browse_btn = QPushButton("Examinar")
        browse_btn.clicked.connect(self.browse_folder)
        
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.path_edit, 1)
        path_layout.addWidget(browse_btn)
        
        config_layout.addLayout(path_layout)
        
        # Información de organización
        info_label = QLabel("""
        <b>Organización automática por carpetas:</b><br>
        • Videos de plataformas → Videos/<br>
        • Audio extraído → Música/<br>
        • Archivos directos → según su tipo<br>
        • Archivos sin categoría → Otros/
        """)
        info_label.setWordWrap(True)
        config_layout.addWidget(info_label)
        
        layout.addWidget(config_group)
    
    def create_formats_group(self, layout):
        formats_group = QGroupBox("📋 Tipos de Archivo Soportados")
        formats_layout = QGridLayout(formats_group)
        
        row = 0
        for category, info in self.file_categories.items():
            if category == 'otros':
                continue
                
            icon_label = QLabel(info['icon'])
            icon_label.setFont(QFont("Arial", 16))
            
            name_label = QLabel(f"<b>{info['folder']}:</b>")
            
            extensions_text = ", ".join(info['extensions'][:8])
            if len(info['extensions']) > 8:
                extensions_text += f" (+{len(info['extensions']) - 8} más)"
            
            ext_label = QLabel(extensions_text)
            ext_label.setWordWrap(True)
            
            formats_layout.addWidget(icon_label, row, 0)
            formats_layout.addWidget(name_label, row, 1)
            formats_layout.addWidget(ext_label, row, 2)
            
            row += 1
        
        layout.addWidget(formats_group)
    
    def create_progress_group(self, layout):
        progress_group = QGroupBox("📊 Progreso y Log")
        progress_layout = QVBoxLayout(progress_group)
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        
        # Log de descargas
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(250)
        self.log_text.setFont(QFont("Consolas", 9))
        
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.log_text)
        
        layout.addWidget(progress_group)
        
        # Log inicial
        self.log("🚀 Descargador Universal iniciado correctamente")
        self.log(f"📁 Carpeta de descarga: {self.download_path}")
        self.log("🎥 Soporta: YouTube, TikTok, Instagram, Vimeo, archivos directos")
        self.log("🐧 Sistema: Arch Linux")
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # Menú Archivo
        file_menu = menubar.addMenu('Archivo')
        
        change_folder_action = QAction('Cambiar carpeta de descarga', self)
        change_folder_action.triggered.connect(self.browse_folder)
        file_menu.addAction(change_folder_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Salir', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menú Herramientas
        tools_menu = menubar.addMenu('Herramientas')
        
        check_ytdlp_action = QAction('Verificar yt-dlp', self)
        check_ytdlp_action.triggered.connect(self.check_ytdlp_status)
        tools_menu.addAction(check_ytdlp_action)
        
        install_ytdlp_action = QAction('Instalar/Actualizar yt-dlp', self)
        install_ytdlp_action.triggered.connect(self.install_ytdlp_manual)
        tools_menu.addAction(install_ytdlp_action)
        
        # Menú Ayuda
        help_menu = menubar.addMenu('Ayuda')
        
        about_action = QAction('Acerca de', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def toggle_audio_only(self, state):
        """Desactiva opciones de calidad cuando se selecciona solo audio"""
        if state == Qt.CheckState.Checked.value:
            self.quality_combo.setEnabled(False)
            self.log("🎵 Modo solo audio activado - descargará MP3")
        else:
            self.quality_combo.setEnabled(True)
            self.log("🎥 Modo video activado")
    
    def check_ytdlp_status(self):
        """Verifica el estado de yt-dlp"""
        try:
            result = subprocess.run(['yt-dlp', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version = result.stdout.strip()
                QMessageBox.information(self, "yt-dlp Status", 
                                      f"✅ yt-dlp está instalado\nVersión: {version}")
                self.log(f"✅ yt-dlp disponible: {version}")
            else:
                QMessageBox.warning(self, "yt-dlp Status", "❌ yt-dlp no responde correctamente")
        except:
            try:
                result = subprocess.run([sys.executable, '-m', 'yt_dlp', '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    version = result.stdout.strip()
                    QMessageBox.information(self, "yt-dlp Status", 
                                          f"✅ yt-dlp está instalado (Python)\nVersión: {version}")
                    self.log(f"✅ yt-dlp disponible via Python: {version}")
                else:
                    QMessageBox.warning(self, "yt-dlp Status", "❌ yt-dlp no está disponible")
            except:
                QMessageBox.warning(self, "yt-dlp Status", 
                                  "❌ yt-dlp no está instalado\n\n"
                                  "Para instalar:\n"
                                  "• sudo pacman -S yt-dlp\n"
                                  "• pip install --user yt-dlp")
    
    def install_ytdlp_manual(self):
        """Instala yt-dlp manualmente"""
        reply = QMessageBox.question(self, "Instalar yt-dlp", 
                                   "¿Deseas instalar/actualizar yt-dlp?\n\n"
                                   "Esto ejecutará:\nsudo pacman -S yt-dlp\n\n"
                                   "¿Continuar?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.log("🔧 Instalando yt-dlp...")
            try:
                result = subprocess.run(['sudo', 'pacman', '-S', '--noconfirm', 'yt-dlp'],
                                      capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    QMessageBox.information(self, "Éxito", "✅ yt-dlp instalado correctamente")
                    self.log("✅ yt-dlp instalado con pacman")
                else:
                    QMessageBox.warning(self, "Error", f"❌ Error al instalar:\n{result.stderr}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"❌ Error: {str(e)}")
    
    def setup_style(self):
        """Configura el tema oscuro moderno"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            
            QTabWidget::pane {
                border: 2px solid #3b3b3b;
                border-radius: 8px;
                background-color: #2b2b2b;
            }
            
            QTabWidget::tab-bar {
                alignment: center;
            }
            
            QTabBar::tab {
                background-color: #3b3b3b;
                color: #ffffff;
                padding: 12px 24px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            
            QTabBar::tab:selected {
                background-color: #0078d4;
            }
            
            QTabBar::tab:hover {
                background-color: #4b4b4b;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3b3b3b;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 15px;
                background-color: #2b2b2b;
                color: #ffffff;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                color: #ffffff;
                font-size: 14px;
            }
            
            QLabel#title {
                font-size: 28px;
                font-weight: bold;
                color: #00d4ff;
                margin: 15px;
            }
            
            QLabel#subtitle {
                font-size: 14px;
                color: #cccccc;
                margin-bottom: 25px;
            }
            
            QLineEdit {
                background-color: #3b3b3b;
                border: 2px solid #555555;
                border-radius: 8px;
                padding: 12px;
                color: #ffffff;
                font-size: 12px;
            }
            
            QLineEdit:focus {
                border: 2px solid #00d4ff;
            }
            
            QComboBox {
                background-color: #3b3b3b;
                border: 2px solid #555555;
                border-radius: 8px;
                padding: 8px 12px;
                color: #ffffff;
                font-size: 12px;
            }
            
            QComboBox:focus {
                border: 2px solid #00d4ff;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            
            QComboBox::down-arrow {
                image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAGCAYAAAD37n+BAAAABHNCSVQICAgIfAhkiAAAAAlwSFlzAAAAdgAAAHYBTnsmCAAAABl0RVh0U29mdHdhcmUAd3d3Lmlua3NjYXBlLm9yZ5vuPBoAAAFKSURBVBiVY/j//z8DJQAggBhIBQABBBBADKQCgABiIBUABBADqQAggBhIBQABxEAqAAgghv///xMNAAQQw7+/f4kGAAKI4d/fP0QDAAHEQCoACCAGUgFAADGQCgACiIFUABBADKQCgABiIBUABBADqQAggBhIBQABxEAqAAgghv///xMNAAQQA6kAIIAYSAUAAcRAKgAIIAZSAUAAMZAKAAKIgVQAEEAMpAKAAGIgFQAEEAOpACCAGEgFAAHEQCoACCAGUgFAADGQCgACiIFUABBADKQCgABiIBUABBADqQAggBhIBQABxEAqAAgghv///xMNAAQQA6kAIIAYSAUAAcRAKgAIIAZSAUAAMZAKAAKIgVQAEEAMpAKAAGIgFQAEEAOpACCAGEgFAAHEQCoACCAGUgFAADGQCgACiIFUABBADKQCgABiIBUABBADqYD/AwwMAGCKP7VmSKm9AAAAAElFTkSuQmCC);
            }
            
            QComboBox QAbstractItemView {
                background-color: #3b3b3b;
                border: 1px solid #555555;
                selection-background-color: #0078d4;
                color: #ffffff;
            }
            
            QCheckBox {
                color: #ffffff;
                font-size: 12px;
                spacing: 8px;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #555555;
                border-radius: 4px;
                background-color: #3b3b3b;
            }
            
            QCheckBox::indicator:checked {
                background-color: #00d4ff;
                border-color: #00d4ff;
            }
            
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 12px;
                min-height: 20px;
            }
            
            QPushButton:hover {
                background-color: #106ebe;
            }
            
            QPushButton:pressed {
                background-color: #005a9e;
            }
            
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
            
            QPushButton#download_btn {
                background-color: #16c60c;
                font-size: 14px;
                padding: 15px 30px;
            }
            
            QPushButton#download_btn:hover {
                background-color: #13a10e;
            }
            
            QPushButton#cancel_btn {
                background-color: #d13438;
            }
            
            QPushButton#cancel_btn:hover {
                background-color: #a4272a;
            }
            
            QProgressBar {
                border: 2px solid #555555;
                border-radius: 8px;
                background-color: #2b2b2b;
                text-align: center;
                color: #ffffff;
                font-weight: bold;
                font-size: 12px;
                height: 25px;
            }
            
            QProgressBar::chunk {
                background-color: #00d4ff;
                border-radius: 6px;
            }
            
            QTextEdit {
                background-color: #1e1e1e;
                border: 2px solid #555555;
                border-radius: 8px;
                color: #00ff00;
                padding: 12px;
                font-family: 'Consolas', 'Monaco', monospace;
            }
            
            QStatusBar {
                background-color: #2b2b2b;
                border-top: 1px solid #555555;
                color: #ffffff;
                padding: 5px;
            }
            
            QMenuBar {
                background-color: #2b2b2b;
                color: #ffffff;
                border-bottom: 1px solid #555555;
                padding: 2px;
            }
            
            QMenuBar::item {
                background-color: transparent;
                padding: 6px 12px;
                border-radius: 4px;
            }
            
            QMenuBar::item:selected {
                background-color: #0078d4;
            }
            
            QMenu {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 2px solid #555555;
                border-radius: 6px;
                padding: 4px;
            }
            
            QMenu::item {
                padding: 8px 16px;
                border-radius: 4px;
            }
            
            QMenu::item:selected {
                background-color: #0078d4;
            }
        """)
    
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta de descarga", self.download_path)
        if folder:
            self.download_path = folder
            self.path_edit.setText(folder)
            self.log(f"📁 Carpeta de descarga cambiada a: {folder}")
    
    def clear_inputs(self):
        self.url_edit.clear()
        self.custom_name_edit.clear()
        self.audio_only_check.setChecked(False)
        self.quality_combo.setCurrentIndex(0)
        self.log("🗑️ Campos limpiados")
    
    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        # Auto-scroll al final
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def get_video_quality_setting(self):
        """Convierte la selección del combo a formato yt-dlp"""
        quality_map = {
            "Mejor disponible": "best",
            "720p": "720p",
            "480p": "480p", 
            "360p": "360p"
        }
        return quality_map.get(self.quality_combo.currentText(), "best")
    
    def start_download(self):
        url = self.url_edit.text().strip()
        
        if not url:
            QMessageBox.warning(self, "Advertencia", "Por favor, ingresa una URL")
            return
        
        # Agregar https:// si no tiene protocolo
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            self.url_edit.setText(url)
        
        # Actualizar ruta de descarga
        self.download_path = self.path_edit.text()
        
        # Obtener configuraciones
        custom_name = self.custom_name_edit.text().strip()
        video_quality = self.get_video_quality_setting()
        audio_only = self.audio_only_check.isChecked()
        
        # Configurar UI para descarga
        self.download_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        
        # Log de inicio
        if audio_only:
            self.log(f"🎵 Iniciando descarga de audio: {url}")
        else:
            self.log(f"🎥 Iniciando descarga: {url} (Calidad: {video_quality})")
        
        # Crear y iniciar worker thread
        self.download_worker = UniversalDownloadWorker(
            url=url,
            download_path=self.download_path,
            file_categories=self.file_categories,
            video_quality=video_quality,
            audio_only=audio_only,
            custom_name=custom_name
        )
        
        self.download_worker.progress_updated.connect(self.progress_bar.setValue)
        self.download_worker.status_updated.connect(self.status_bar.showMessage)
        self.download_worker.log_updated.connect(self.log)
        self.download_worker.download_finished.connect(self.download_finished)
        self.download_worker.start()
    
    def cancel_download(self):
        if self.download_worker and self.download_worker.isRunning():
            self.log("⏹️ Cancelando descarga...")
            self.download_worker.cancel()
            self.download_worker.wait(5000)  # Esperar máximo 5 segundos
            self.log("❌ Descarga cancelada por el usuario")
            self.download_finished(False, "Descarga cancelada", "")
    
    def download_finished(self, success, message, filepath):
        # Restaurar UI
        self.download_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        
        if success:
            QMessageBox.information(self, "✅ Éxito", message)
            self.status_bar.showMessage("Descarga completada")
            # Ofrecer abrir carpeta
            if filepath and os.path.exists(filepath):
                reply = QMessageBox.question(self, "Abrir carpeta", 
                                           "¿Deseas abrir la carpeta de destino?",
                                           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.Yes:
                    try:
                        subprocess.run(['xdg-open', os.path.dirname(filepath)])
                    except:
                        pass
        else:
            if "cancelada" not in message.lower():
                QMessageBox.critical(self, "❌ Error", message)
            self.status_bar.showMessage("Listo para descargar")
    
    def show_about(self):
        QMessageBox.about(self, "Acerca del Descargador Universal", 
                         """
                         <h2>🌐 Descargador Universal by SWAT</h2>
                         <p><b>Versión:</b> 2.0</p>
                         <p><b>Sistema:</b> Arch Linux</p>
                         <br>
                         <p><b>Características:</b></p>
                         <ul>
                         <li>✅ YouTube, TikTok, Instagram, Vimeo</li>
                         <li>✅ Descargas directas de archivos</li>
                         <li>✅ Organización automática por tipo</li>
                         <li>✅ Múltiples calidades de video</li>
                         <li>✅ Extracción de audio a MP3</li>
                         <li>✅ Nombres personalizados</li>
                         <li>✅ Interfaz moderna y oscura</li>
                         </ul>
                         <br>
                         <p><b>Tecnologías:</b> PyQt6, yt-dlp, requests</p>
                         <p><b>Licencia:</b> Software libre</p>
                         """)
    
    def closeEvent(self, event):
        if self.download_worker and self.download_worker.isRunning():
            reply = QMessageBox.question(self, "Confirmar salida", 
                                       "Hay una descarga en curso. ¿Deseas cancelarla y salir?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.download_worker.cancel()
                self.download_worker.wait(3000)
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Descargador Universal")
    app.setApplicationVersion("2.0")
    
    # Configurar tema oscuro nativo si está disponible
    app.setStyle('Fusion')
    
    window = UniversalDownloaderGUI()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()