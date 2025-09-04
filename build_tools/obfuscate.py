#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'obfuscation pour insta_kendou
Compilation et obfuscation du code source pour protection
"""

import os
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path

def obfuscate_python_files():
    """Obfusquer tous les fichiers Python du projet"""
    
    project_root = Path(__file__).parent.parent
    source_dir = project_root / "insta_kendou"
    build_dir = project_root / "build" / "obfuscated"
    
    print("🔒 Début de l'obfuscation...")
    
    # Créer le dossier de build
    build_dir.mkdir(parents=True, exist_ok=True)
    
    # Copier la structure
    shutil.copytree(source_dir, build_dir / "insta_kendou", dirs_exist_ok=True)
    
    # Compiler tous les fichiers .py en .pyc
    for py_file in (build_dir / "insta_kendou").rglob("*.py"):
        try:
            # Compiler avec optimisation maximale
            subprocess.run([
                sys.executable, "-O", "-O", "-m", "py_compile", str(py_file)
            ], check=True, capture_output=True)
            
            # Supprimer le fichier source
            py_file.unlink()
            
            print(f"✅ Obfusqué: {py_file.relative_to(build_dir)}")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur compilation {py_file}: {e}")
    
    # Créer les fichiers __init__.py minimaux pour les __pycache__
    for pycache_dir in (build_dir / "insta_kendou").rglob("__pycache__"):
        init_file = pycache_dir.parent / "__init__.py"
        if not init_file.exists():
            init_file.write_text("# Compiled module\n")
    
    print("🔒 Obfuscation terminée!")
    print(f"📁 Fichiers obfusqués dans: {build_dir}")
    
    return build_dir

def create_distribution():
    """Créer la distribution finale"""
    
    print("📦 Création de la distribution...")
    
    # Obfusquer d'abord
    obfuscated_dir = obfuscate_python_files()
    
    project_root = Path(__file__).parent.parent
    dist_dir = project_root / "dist"
    dist_dir.mkdir(exist_ok=True)
    
    # Copier les fichiers nécessaires
    files_to_copy = [
        "setup.py",
        "README.md", 
        "requirements.txt",
        "MANIFEST.in"
    ]
    
    for file_name in files_to_copy:
        src_file = project_root / file_name
        if src_file.exists():
            shutil.copy2(src_file, obfuscated_dir.parent)
    
    # Créer le package wheel
    os.chdir(obfuscated_dir.parent)
    
    try:
        # Installer wheel si pas présent
        subprocess.run([sys.executable, "-m", "pip", "install", "wheel"], 
                      capture_output=True)
        
        # Créer le package
        result = subprocess.run([
            sys.executable, "setup.py", "bdist_wheel", "--dist-dir", str(dist_dir)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Distribution créée avec succès!")
            print(f"📦 Package disponible dans: {dist_dir}")
            
            # Lister les fichiers créés
            for wheel_file in dist_dir.glob("*.whl"):
                print(f"📄 Fichier: {wheel_file.name}")
                
        else:
            print(f"❌ Erreur création distribution: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Erreur: {e}")

def clean_build():
    """Nettoyer les fichiers de build"""
    
    project_root = Path(__file__).parent.parent
    
    directories_to_clean = [
        "build",
        "dist", 
        "*.egg-info"
    ]
    
    for pattern in directories_to_clean:
        for path in project_root.glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"🧹 Supprimé: {path}")
    
    # Supprimer les __pycache__
    for pycache in project_root.rglob("__pycache__"):
        shutil.rmtree(pycache)
        print(f"🧹 Supprimé: {pycache}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Obfuscation et build d'insta_kendou")
    parser.add_argument("action", choices=["obfuscate", "build", "clean"], 
                       help="Action à effectuer")
    
    args = parser.parse_args()
    
    if args.action == "obfuscate":
        obfuscate_python_files()
    elif args.action == "build":
        create_distribution()
    elif args.action == "clean":
        clean_build()
    
    print("✨ Terminé!")
