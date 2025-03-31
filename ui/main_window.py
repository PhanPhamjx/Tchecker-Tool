from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QFileDialog, 
                             QListWidget, QMessageBox, QCheckBox, QGroupBox, 
                             QSpinBox, QFormLayout, QDialog, QInputDialog)
from PyQt5.QtCore import Qt
from modules.texture_validator import TextureValidator
from modules.config_manager import ConfigManager
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Unity Texture Checker Tool")
        self.setGeometry(100, 100, 800, 600)
        
        self.validator = TextureValidator()
        self.config_manager = ConfigManager(os.path.join("data", "settings.json"))
        
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Folder selection
        folder_group = QGroupBox("Texture Folder")
        folder_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_folder)
        folder_layout.addWidget(self.path_input)
        folder_layout.addWidget(browse_button)
        folder_group.setLayout(folder_layout)
        main_layout.addWidget(folder_group)
        
        # Settings group
        settings_group = QGroupBox("Settings")
        settings_layout = QFormLayout()
        
        # Resolution setting
        self.resolution_spinbox = QSpinBox()
        self.resolution_spinbox.setRange(32, 4096)
        self.resolution_spinbox.setValue(512)
        self.resolution_spinbox.setSingleStep(32)
        settings_layout.addRow("Required Resolution:", self.resolution_spinbox)
        
        # Map checkboxes with add button
        maps_layout = QVBoxLayout()
        maps_header = QHBoxLayout()
        maps_label = QLabel("Required Maps:")
        add_map_button = QPushButton("+")
        add_map_button.setFixedWidth(30)
        add_map_button.clicked.connect(self.add_custom_map)
        maps_header.addWidget(maps_label)
        maps_header.addWidget(add_map_button)
        maps_header.addStretch()
        maps_layout.addLayout(maps_header)
        
        self.map_checkboxes = {}
        self.map_layout = QVBoxLayout()
        self.default_maps = ["Albedo", "Normal", "Metallic", "Roughness", "AO"]
        for map_name in self.default_maps:
            checkbox = QCheckBox(map_name)
            checkbox.setChecked(True)
            self.map_checkboxes[map_name] = checkbox
            self.map_layout.addWidget(checkbox)
        
        maps_layout.addLayout(self.map_layout)
        settings_layout.addRow(maps_layout)
        
        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)
        
        # Check button
        check_button = QPushButton("Check Textures")
        check_button.clicked.connect(self.check_textures)
        main_layout.addWidget(check_button)
        
        # Results list
        self.results_list = QListWidget()
        main_layout.addWidget(self.results_list)
    
    def add_custom_map(self):
        try:
            text, ok = QInputDialog.getText(self, 'Add Custom Map', 'Enter map name:')
            if ok and text:
                # Check if map name already exists
                if text in self.map_checkboxes:
                    QMessageBox.warning(self, "Warning", "This map type already exists!")
                    return
                
                # Create new checkbox
                checkbox = QCheckBox(text)
                checkbox.setChecked(True)
                self.map_checkboxes[text] = checkbox
                self.map_layout.addWidget(checkbox)
                
                # Update settings
                try:
                    settings = self.config_manager.load_settings()
                    if "custom_maps" not in settings:
                        settings["custom_maps"] = []
                    if text not in settings["custom_maps"]:
                        settings["custom_maps"].append(text)
                    self.config_manager.update_settings(settings)
                except Exception as e:
                    QMessageBox.warning(self, "Warning", f"Could not save custom map: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
    
    def browse_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Texture Folder")
        if folder_path:
            self.path_input.setText(folder_path)
            self.config_manager.update_setting("last_folder", folder_path)
    
    def check_textures(self):
        folder_path = self.path_input.text()
        if not folder_path or not os.path.isdir(folder_path):
            QMessageBox.critical(self, "Error", "Please select a valid folder path!")
            return
        
        # Get settings from UI
        settings = {
            "required_resolution": self.resolution_spinbox.value(),
            "required_format": ".tga",
            "required_maps": [map_name for map_name, cb in self.map_checkboxes.items() if cb.isChecked()]
        }
        
        # Save settings
        self.config_manager.update_settings(settings)
        
        # Check textures
        results = self.validator.validate_folder(
            folder_path,
            settings["required_maps"],
            settings["required_resolution"],
            settings["required_format"]
        )
        
        # Display results
        self.display_results(results)
    
    def display_results(self, results):
        self.results_list.clear()
        for result in results:
            if result["status"] == "valid":
                self.results_list.addItem(f"✅ {result['texture_set']}: All requirements met")
            else:
                self.results_list.addItem(f"❌ {result['texture_set']}: {result['message']}")
                for detail in result.get("details", []):
                    self.results_list.addItem(f"  ⚠ {detail}")
    
    def load_settings(self):
        try:
            settings = self.config_manager.load_settings()
            if settings:
                # Set resolution
                try:
                    self.resolution_spinbox.setValue(settings.get("required_resolution", 512))
                except Exception as e:
                    print(f"Error setting resolution: {str(e)}")
                
                # Set last folder
                try:
                    if "last_folder" in settings:
                        self.path_input.setText(settings["last_folder"])
                except Exception as e:
                    print(f"Error setting last folder: {str(e)}")
                
                # Load custom maps
                try:
                    if "custom_maps" in settings:
                        for map_name in settings["custom_maps"]:
                            if map_name and map_name not in self.map_checkboxes:
                                checkbox = QCheckBox(map_name)
                                checkbox.setChecked(True)
                                self.map_checkboxes[map_name] = checkbox
                                self.map_layout.addWidget(checkbox)
                except Exception as e:
                    print(f"Error loading custom maps: {str(e)}")
                
                # Set checkbox states
                try:
                    for map_name, cb in self.map_checkboxes.items():
                        cb.setChecked(map_name in settings.get("required_maps", []))
                except Exception as e:
                    print(f"Error setting checkbox states: {str(e)}")
        except Exception as e:
            print(f"Error loading settings: {str(e)}")
    
    def closeEvent(self, event):
        try:
            self.config_manager.save_settings()
        except Exception as e:
            print(f"Error saving settings: {str(e)}")
        super().closeEvent(event)