from PIL import Image
import os

class TextureValidator:
    def validate_folder(self, folder_path, required_maps, required_resolution, required_format):
        texture_files = self._collect_texture_files(folder_path, required_format)
        texture_sets = self._organize_textures_by_set(texture_files)
        return self._validate_texture_sets(texture_sets, required_maps, required_resolution)
    
    def _collect_texture_files(self, folder_path, required_format):
        texture_files = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(required_format.lower()):
                    texture_files.append(os.path.join(root, file))
        return texture_files
    
    def _organize_textures_by_set(self, texture_files):
        texture_sets = {}
        for file_path in texture_files:
            file_name = os.path.basename(file_path)
            base_name, map_type = self._extract_texture_info(file_name)
            
            if base_name not in texture_sets:
                texture_sets[base_name] = {}
            
            texture_sets[base_name][map_type] = file_path
        return texture_sets
    
    def _extract_texture_info(self, file_name):
        parts = file_name.split('_')
        if len(parts) < 2:
            return file_name.split('.')[0], "Unknown"
        return '_'.join(parts[:-1]), parts[-1].split('.')[0]
    
    def _validate_texture_sets(self, texture_sets, required_maps, required_resolution):
        results = []
        for base_name, texture_set in texture_sets.items():
            result = self._validate_single_set(base_name, texture_set, required_maps, required_resolution)
            results.append(result)
        return results
    
    def _validate_single_set(self, base_name, texture_set, required_maps, required_resolution):
        missing_maps = [map_name for map_name in required_maps if map_name not in texture_set]
        details = []
        
        if missing_maps:
            return {
                "texture_set": base_name,
                "status": "invalid",
                "message": f"Missing maps: {', '.join(missing_maps)}"
            }
        
        for map_type, file_path in texture_set.items():
            try:
                with Image.open(file_path) as img:
                    width, height = img.size
                    if width != required_resolution or height != required_resolution:
                        details.append(
                            f"{map_type}: Incorrect size {width}x{height} "
                            f"(expected {required_resolution}x{required_resolution})"
                        )
            except Exception as e:
                details.append(f"{map_type}: Error loading file - {str(e)}")
        
        if details:
            return {
                "texture_set": base_name,
                "status": "invalid",
                "message": "Some maps have issues",
                "details": details
            }
        
        return {
            "texture_set": base_name,
            "status": "valid",
            "message": "All requirements met"
        }