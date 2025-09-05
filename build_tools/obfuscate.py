#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Outil d'obfuscation pour insta_kendou
Protection du code source contre la décompilation
"""

import os
import sys
import ast
import base64
import marshal
import zlib
import random
import string
from pathlib import Path

class CodeObfuscator:
    """Obfuscateur de code Python avancé"""
    
    def __init__(self):
        self.obfuscation_map = {}
        self.reserved_names = {
            '__init__', '__name__', '__main__', '__file__', '__doc__',
            'self', 'cls', 'super', 'print', 'input', 'len', 'str',
            'int', 'float', 'bool', 'list', 'dict', 'tuple', 'set'
        }
    
    def generate_random_name(self, length=8):
        """Générer un nom aléatoire"""
        chars = string.ascii_letters + '_'
        return ''.join(random.choice(chars) for _ in range(length))
    
    def obfuscate_names(self, code):
        """Obfusquer les noms de variables et fonctions"""
        try:
            tree = ast.parse(code)
            
            # Identifier les noms à obfusquer
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if node.name not in self.reserved_names and not node.name.startswith('_'):
                        if node.name not in self.obfuscation_map:
                            self.obfuscation_map[node.name] = self.generate_random_name()
                
                elif isinstance(node, ast.Name):
                    if isinstance(node.ctx, ast.Store):
                        if node.id not in self.reserved_names and not node.id.startswith('_'):
                            if node.id not in self.obfuscation_map:
                                self.obfuscation_map[node.id] = self.generate_random_name()
            
            # Appliquer les remplacements
            for original, obfuscated in self.obfuscation_map.items():
                code = code.replace(original, obfuscated)
            
            return code
            
        except SyntaxError:
            return code
    
    def compress_code(self, code):
        """Compresser le code"""
        try:
            # Compilation en bytecode
            compiled = compile(code, '<string>', 'exec', optimize=2)
            
            # Sérialisation
            marshalled = marshal.dumps(compiled)
            
            # Compression
            compressed = zlib.compress(marshalled, level=9)
            
            # Encodage base64
            encoded = base64.b64encode(compressed).decode('utf-8')
            
            return encoded
            
        except Exception as e:
            print(f"Erreur compression: {e}")
            return None
    
    def create_loader(self, compressed_code):
        """Créer un loader pour le code compressé"""
        loader_template = f'''
# -*- coding: utf-8 -*-
import base64, zlib, marshal, sys
def _load():
    try:
        _data = base64.b64decode("{compressed_code}")
        _decompressed = zlib.decompress(_data)
        _code = marshal.loads(_decompressed)
        exec(_code, globals())
    except Exception as e:
        print(f"Erreur chargement: {{e}}")
        sys.exit(1)
_load()
'''
        return loader_template
    
    def obfuscate_strings(self, code):
        """Obfusquer les chaînes de caractères"""
        import re
        
        def encode_string(match):
            string_content = match.group(1)
            # Encoder en base64
            encoded = base64.b64encode(string_content.encode()).decode()
            return f'base64.b64decode("{encoded}").decode()'
        
        # Remplacer les chaînes simples
        code = re.sub(r'"([^"]*)"', encode_string, code)
        code = re.sub(r"'([^']*)'", encode_string, code)
        
        return code
    
    def obfuscate_file(self, input_path, output_path):
        """Obfusquer un fichier Python"""
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                original_code = f.read()
            
            print(f"Obfuscation de {input_path}...")
            
            # Étapes d'obfuscation
            obfuscated_code = original_code
            
            # 1. Obfuscation des noms
            obfuscated_code = self.obfuscate_names(obfuscated_code)
            
            # 2. Obfuscation des chaînes
            obfuscated_code = self.obfuscate_strings(obfuscated_code)
            
            # 3. Compression
            compressed = self.compress_code(obfuscated_code)
            
            if compressed:
                # 4. Création du loader
                final_code = self.create_loader(compressed)
            else:
                final_code = obfuscated_code
            
            # Écriture du fichier obfusqué
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(final_code)
            
            print(f"✅ Fichier obfusqué: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Erreur obfuscation {input_path}: {e}")
            return False
    
    def obfuscate_directory(self, input_dir, output_dir, exclude_patterns=None):
        """Obfusquer tous les fichiers Python d'un répertoire"""
        if exclude_patterns is None:
            exclude_patterns = ['__pycache__', '.git', '.pytest_cache', 'build', 'dist']
        
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        success_count = 0
        total_count = 0
        
        for py_file in input_path.rglob('*.py'):
            # Vérifier les exclusions
            if any(pattern in str(py_file) for pattern in exclude_patterns):
                continue
            
            total_count += 1
            
            # Chemin de sortie correspondant
            relative_path = py_file.relative_to(input_path)
            output_file = output_path / relative_path
            
            if self.obfuscate_file(py_file, output_file):
                success_count += 1
        
        print(f"\nObfuscation terminée: {success_count}/{total_count} fichiers traités")
        return success_count == total_count

def main():
    """Fonction principale d'obfuscation"""
    if len(sys.argv) < 3:
        print("Usage: python obfuscate.py <input_dir> <output_dir>")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    
    if not os.path.exists(input_dir):
        print(f"Erreur: Le répertoire {input_dir} n'existe pas")
        sys.exit(1)
    
    obfuscator = CodeObfuscator()
    
    print("🔒 DÉBUT DE L'OBFUSCATION")
    print("=" * 50)
    
    success = obfuscator.obfuscate_directory(input_dir, output_dir)
    
    if success:
        print("🎉 Obfuscation réussie!")
    else:
        print("❌ Erreurs lors de l'obfuscation")
        sys.exit(1)

if __name__ == '__main__':
    main()
