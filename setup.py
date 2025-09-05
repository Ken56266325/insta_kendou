#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup script pour insta_kendou
Bibliothèque Instagram complète avec authentification 2FA
"""

import os
import sys
from setuptools import setup, find_packages

# Vérification version Python
if sys.version_info < (3, 8):
    raise RuntimeError("insta_kendou nécessite Python 3.8 ou supérieur")

# Lecture des dépendances
def read_requirements():
    try:
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        return [
            'requests>=2.31.0',
            'Pillow>=10.0.0',
            'pycryptodome>=3.19.0',
            'PyNaCl>=1.5.0'
        ]

# Lecture du README
def read_readme():
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Bibliothèque Instagram complète avec authentification 2FA et gestion des médias"

# Configuration du package
setup(
    name="insta_kendou",
    version="1.0.0",
    author="Kenny",
    author_email="mampifaly56266325@gmail.com",
    description="Bibliothèque Instagram complète avec authentification 2FA et gestion des médias",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Ken56266325/insta_kendou",
    
    # Configuration des packages
    packages=find_packages(),
    include_package_data=True,
    
    # Dépendances
    install_requires=read_requirements(),
    
    # Métadonnées
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    
    python_requires=">=3.8",
    
    # Fichiers supplémentaires
    package_data={
        'insta_kendou': ['*.md', '*.txt'],
    },
    
    # Points d'entrée
    entry_points={
        'console_scripts': [
            'insta-kendou=insta_kendou.client:main',
        ],
    },
    
    # Options de build
    zip_safe=False,
    
    # Mots-clés
    keywords="instagram api automation social media 2fa authentication",
    
    # Licence
    license="Proprietary",
    
    # Plateformes supportées
    platforms=["any"],
)
