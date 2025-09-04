# -*- coding: utf-8 -*-
"""
Configuration de la bibliothèque insta_kendou
Installation et dépendances pour GitHub
"""

from setuptools import setup, find_packages
import os
import sys

# Version de la bibliothèque
VERSION = "1.0.0"

# Description longue depuis README si disponible
long_description = "Bibliothèque Instagram complète avec authentification 2FA et gestion des médias"
readme_path = os.path.join(os.path.dirname(__file__), "README.md")
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()

# Dépendances requises
INSTALL_REQUIRES = [
    "requests>=2.25.0",
    "Pillow>=8.0.0",
    "pycryptodome>=3.15.0",
    "PyNaCl>=1.5.0"
]

# Dépendances optionnelles pour différents environnements
EXTRAS_REQUIRE = {
    "termux": [
        "zstandard>=0.18.0; platform_system=='Linux'",
    ],
    "dev": [
        "pytest>=7.0.0",
        "pytest-cov>=4.0.0",
        "black>=22.0.0",
        "flake8>=5.0.0"
    ]
}

# Classifiers PyPI
CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "License :: Other/Proprietary License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Topic :: Internet :: WWW/HTTP",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Communications :: Chat",
    "Topic :: Multimedia :: Graphics"
]

def check_dependencies():
    """Vérifier et installer les dépendances automatiquement"""
    missing_deps = []
    
    # Vérifier les dépendances critiques
    try:
        import requests
    except ImportError:
        missing_deps.append("requests")
    
    try:
        from PIL import Image
    except ImportError:
        missing_deps.append("Pillow")
    
    try:
        from Crypto.Cipher import AES
    except ImportError:
        missing_deps.append("pycryptodome")
    
    try:
        import nacl
    except ImportError:
        missing_deps.append("PyNaCl")
    
    if missing_deps:
        print(f"⚠️  Dépendances manquantes détectées: {', '.join(missing_deps)}")
        print("📦 Installation automatique en cours...")
        
        import subprocess
        for dep in missing_deps:
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", dep, 
                    "--quiet", "--no-warn-script-location"
                ])
                print(f"✅ {dep} installé avec succès")
            except subprocess.CalledProcessError as e:
                print(f"❌ Erreur installation {dep}: {e}")
                return False
        
        print("✅ Toutes les dépendances ont été installées")
    
    return True

# Hook post-installation
def post_install():
    """Actions après installation"""
    print("\n" + "=" * 50)
    print("📦 INSTALLATION INSTA_KENDOU TERMINÉE")
    print("=" * 50)
    print("✅ Bibliothèque installée avec succès")
    print("🔐 Validation de licence requise pour utilisation")
    print("📞 Contact: 0389561802 | https://t.me/Kenny5626")
    print("=" * 50)

# Configuration principale
setup(
    name="insta_kendou",
    version=VERSION,
    author="Kenny",
    author_email="mampifaly56266325@gmail.com",
    description="Bibliothèque Instagram complète avec authentification 2FA",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ken56266325/insta_kendou",
    packages=find_packages(),
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    python_requires=">=3.7",
    classifiers=CLASSIFIERS,
    license="Proprietary",
    platforms=["any"],
    keywords="instagram api bot automation 2fa social-media",
    
    # Configuration des points d'entrée
    entry_points={
        "console_scripts": [
            "insta-kendou=insta_kendou.client:main",
        ],
    },
    
    # Fichiers additionnels à inclure
    package_data={
        "insta_kendou": [
            "*.json",
            "*.txt",
            "*.md"
        ],
    },
    
    # Configuration ZIP safe
    zip_safe=False,
    
    # Métadonnées de projet
    project_urls={
        "Bug Reports": "https://github.com/Ken56266325/insta_kendou/issues",
        "Source": "https://github.com/Ken56266325/insta_kendou",
        "Contact": "https://t.me/Kenny5626",
    },
)

# Vérifications post-setup
if __name__ == "__main__":
    # Vérifier les dépendances avant installation
    if "install" in sys.argv:
        print("🔧 Vérification des dépendances...")
        if check_dependencies():
            print("✅ Prêt pour l'installation")
        
        # Hook post-installation
        import atexit
        atexit.register(post_install)
