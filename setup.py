# -*- coding: utf-8 -*-
"""
Setup configuration pour insta_kendou
Installation et distribution de la bibliothèque Instagram complète
"""

from setuptools import setup, find_packages
import os
import sys

# Lecture du fichier README pour la description longue
def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return "Bibliothèque Instagram complète avec authentification 2FA et gestion des médias"

# Liste des dépendances requises
REQUIRED_PACKAGES = [
    "requests>=2.28.0",
    "Pillow>=8.0.0",
    "PyNaCl>=1.5.0",
    "pycryptodome>=3.15.0",
    "urllib3>=1.26.0",
]

# Dépendances optionnelles pour des fonctionnalités avancées
OPTIONAL_PACKAGES = {
    "dev": [
        "pytest>=6.0",
        "pytest-cov>=2.10",
        "black>=21.0",
    ],
    "full": [
        "zstandard>=0.18.0",  # Pour décompression zstd
    ]
}

# Métadonnées du package
setup(
    name="insta_kendou",
    version="1.0.0",
    author="Kenny",
    author_email="mampifaly56266325@gmail.com",
    description="Bibliothèque Instagram complète avec authentification 2FA et gestion des médias",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Ken56266325/insta_kendou",
    project_urls={
        "Bug Reports": "https://github.com/Ken56266325/insta_kendou/issues",
        "Source": "https://github.com/Ken56266325/insta_kendou",
        "Telegram": "https://t.me/Kenny5626"
    },
    
    # Configuration des packages
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "insta_kendou": ["*.json", "*.txt"],
    },
    
    # Classification PyPI
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: Chat",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Operating System :: Android",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
    ],
    
    # Configuration Python
    python_requires=">=3.7",
    install_requires=REQUIRED_PACKAGES,
    extras_require=OPTIONAL_PACKAGES,
    
    # Points d'entrée (optionnel)
    entry_points={
        "console_scripts": [
            # Pas de scripts console pour cette bibliothèque privée
        ],
    },
    
    # Configuration des données
    zip_safe=False,
    
    # Licence personnalisée
    license="Proprietary",
    
    # Mots-clés pour la recherche
    keywords="instagram api bot automation 2fa authentication social media",
    
    # Options de build
    options={
        "build_py": {
            "compile": True,
            "optimize": 2,
        }
    },
    
    # Commandes personnalisées post-installation
    cmdclass={},
    
    # Validation des dépendances au moment de l'installation
    setup_requires=[
        "setuptools>=40.0",
        "wheel>=0.30.0",
    ],
)
