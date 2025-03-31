import os
import sys
from PIL import Image
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QFileDialog, QListWidget,
                             QMessageBox, QCheckBox, QGroupBox, QSpinBox, QFormLayout)
from PyQt5.QtCore import Qt


class TextureCheckerTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Unity Texture Checker Tool")
        self.setGeometry(100, 100, 800, 600)
        
        # Default texture maps to check
        self.required_maps = {
            "BaseColor": True,
            "AO": True,
            "Normal": True,
            "RM": True,
            "Emissive": False  # Not required by default
        }
        
        self.required_resolution = 512
        self.required_format = ".tga"
        
        self.init_ui()
    
    def init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Path selection
        path_group = QGroupBox("Texture Folder Path")
        path_layout = QHBoxLayout()
        
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Select folder containing textures...")
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_folder)
        
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(browse_btn)
        path_group.setLayout(path_layout)
        
        # Settings
        settings_group = QGroupBox("Texture Settings")
        settings_layout = QFormLayout()
        
        self.resolution_spinbox = QSpinBox()
        self.resolution_spinbox.setRange(1, 8192)
        self.resolution_spinbox.setValue(self.required_resolution)
        
        # Map checkboxes
        self.map_checkboxes = {}
        for map_name in self.required_maps:
            cb = QCheckBox(map_name)
            cb.setChecked(self.required_maps[map_name])
            self.map_checkboxes[map_name] = cb
            settings_layout.addRow(f"Check {map_name}:", cb)
        
        settings_layout.addRow("Required Resolution:", self.resolution_spinbox)
        settings_group.setLayout(settings_layout)
        
        # Add new map type
        add_map_group = QGroupBox("Add Custom Map Type")
        add_map_layout = QHBoxLayout()
        
        self.new_map_input = QLineEdit()
        self.new_map_input.setPlaceholderText("Enter new map type (e.g., Height)")
        add_map_btn = QPushButton("+")
        add_map_btn.clicked.connect(self.add_new_map_type)
        
        add_map_layout.addWidget(self.new_map_input)
        add_map_layout.addWidget(add_map_btn)
        add_map_group.setLayout(add_map_layout)
        
        # Check button
        check_btn = QPushButton("Check Textures")
        check_btn.clicked.connect(self.check_textures)
        
        # Results display
        self.results_list = QListWidget()
        
        # Assemble main layout
        main_layout.addWidget(path_group)
        main_layout.addWidget(settings_group)
        main_layout.addWidget(add_map_group)
        main_layout.addWidget(check_btn)
        main_layout.addWidget(QLabel("Results:"))
        main_layout.addWidget(self.results_list)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
    
    def browse_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Texture Folder")
        if folder_path:
            self.path_input.setText(folder_path)
    
    def add_new_map_type(self):
        new_map = self.new_map_input.text().strip()
        if new_map:
            if new_map not in self.map_checkboxes:
                cb = QCheckBox(new_map)
                self.map_checkboxes[new_map] = cb
                
                # Add to settings layout
                settings_group = self.findChild(QGroupBox, "Texture Settings")
                settings_layout = settings_group.layout()
                settings_layout.addRow(f"Check {new_map}:", cb)
                
                self.new_map_input.clear()
            else:
                QMessageBox.warning(self, "Warning", f"Map type '{new_map}' already exists!")
    
    def check_textures(self):
        folder_path = self.path_input.text()
        if not folder_path or not os.path.isdir(folder_path):
            QMessageBox.critical(self, "Error", "Please select a valid folder path!")
            return
        
        # Update settings from UI
        self.required_resolution = self.resolution_spinbox.value()
        
        # Get which maps to check
        maps_to_check = [map_name for map_name, cb in self.map_checkboxes.items() if cb.isChecked()]
        
        self.results_list.clear()
        
        # Collect all texture files
        texture_files = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(self.required_format.lower()):
                    texture_files.append(os.path.join(root, file))
        
        if not texture_files:
            self.results_list.addItem(f"No {self.required_format} files found in the selected folder.")
            return
        
        # Analyze textures
        texture_sets = self.organize_textures_by_set(texture_files, maps_to_check)
        
        # Check each texture set
        for base_name, texture_set in texture_sets.items():
            self.check_texture_set(base_name, texture_set, maps_to_check)
    
    def organize_textures_by_set(self, texture_files, maps_to_check):
        texture_sets = {}
        
        for file_path in texture_files:
            file_name = os.path.basename(file_path)
            
            # Extract base name (assuming format: Name_MapType.tga)
            parts = file_name.split('_')
            if len(parts) < 2:
                base_name = file_name.split('.')[0]
                map_type = "Unknown"
            else:
                base_name = '_'.join(parts[:-1])
                map_type = parts[-1].split('.')[0]
            
            if base_name not in texture_sets:
                texture_sets[base_name] = {}
            
            texture_sets[base_name][map_type] = file_path
        
        return texture_sets
    
    def check_texture_set(self, base_name, texture_set, required_maps):
        # Check for missing maps
        missing_maps = [map_name for map_name in required_maps if map_name not in texture_set]
        
        if missing_maps:
            self.results_list.addItem(f"❌ {base_name}: Missing maps - {', '.join(missing_maps)}")
        else:
            self.results_list.addItem(f"✅ {base_name}: All required maps present")
        
        # Check each existing texture
        for map_type, file_path in texture_set.items():
            try:
                with Image.open(file_path) as img:
                    width, height = img.size
                    
                    errors = []
                    if width != self.required_resolution or height != self.required_resolution:
                        errors.append(f"size {width}x{height} (expected {self.required_resolution}x{self.required_resolution})")
                    
                    if map_type not in required_maps:
                        errors.append("map not required")
                    
                    if errors:
                        self.results_list.addItem(f"  ⚠ {map_type}: {', '.join(errors)}")
                    else:
                        self.results_list.addItem(f"  ✓ {map_type}: OK")
            
            except Exception as e:
                self.results_list.addItem(f"  ❗ {map_type}: Error loading file - {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TextureCheckerTool()
    window.show()
    sys.exit(app.exec_())