# Unity Texture Checker Tool

A utility designed to verify the validity of 3D game texture assets, enforcing adherence to technical standards.

## Features

- Check texture resolution
- Validate required texture maps (Albedo, Normal, Metallic, Roughness, AO)
- Support for custom texture map types
- Save and load user preferences
- User-friendly GUI interface

## Requirements

- Python 3.6+
- PyQt5
- Pillow

## Installation

1. Clone the repository:
```bash
git clone https://github.com/PhanPhamjx/Tchecker-Tool.git
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:
```bash
python main.py
```

2. Select a folder containing textures
3. Configure required resolution and texture maps
4. Click "Check Textures" to validate

## Building Executable

To create a standalone executable:

```bash
pip install pyinstaller
.\build_simple.bat
```

The executable will be created in the `dist` folder.

## License

MIT License 