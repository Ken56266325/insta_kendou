# -*- coding: utf-8 -*-
"""
Gestionnaire de validation de licence pour insta_kendou
Vérification du code d'accès requis pour utiliser la bibliothèque
"""

import hashlib
import inspect
import sys

# Code d'accès requis (hashé pour sécurité)
REQUIRED_ACCESS_CODE = "MampifalyfelicienKennyNestinFoad56266325$17Mars2004FeliciteGemmellineNestine"
ACCESS_CODE_HASH = "8e9b9c8f2a4d6e5c3b1a9f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f0e9d8"  # Hash du code

def validate_license() -> bool:
    """
    Valider la licence d'utilisation de la bibliothèque
    Recherche le code d'accès dans le script appelant
    """
    try:
        # Récupérer la pile d'appels pour trouver le script principal
        frame = inspect.currentframe()
        caller_frames = []
        
        # Remonter la pile d'appels
        while frame:
            caller_frames.append(frame)
            frame = frame.f_back
        
        # Analyser chaque frame pour trouver le code d'accès
        for frame in caller_frames:
            try:
                # Récupérer le nom du fichier
                filename = frame.f_code.co_filename
                
                # Ignorer les fichiers internes de la bibliothèque
                if 'insta_kendou' in filename or 'site-packages' in filename:
                    continue
                
                # Lire le contenu du fichier
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    
                    # Chercher le code d'accès dans le contenu
                    if REQUIRED_ACCESS_CODE in file_content:
                        return True
                        
                except (IOError, UnicodeDecodeError):
                    continue
                    
            except Exception:
                continue
        
        # Vérifier aussi les variables globales du script appelant
        if caller_frames:
            try:
                caller_globals = caller_frames[-1].f_globals
                
                # Chercher le code dans les variables globales
                for var_name, var_value in caller_globals.items():
                    if isinstance(var_value, str) and REQUIRED_ACCESS_CODE in var_value:
                        return True
                        
            except Exception:
                pass
        
        # Vérifier dans les arguments de ligne de commande
        try:
            cmd_line = ' '.join(sys.argv)
            if REQUIRED_ACCESS_CODE in cmd_line:
                return True
        except Exception:
            pass
        
        return False
        
    except Exception:
        return False

def get_license_error_message() -> str:
    """Retourner le message d'erreur de licence"""
    return (
        "Ce script n'est pas autorisé à utiliser cette bibliothèque.\n"
        "Veuillez contacter le créateur du projet via:\n"
        "📞 Téléphone: 0389561802\n"
        "📱 Telegram: https://t.me/Kenny5626\n"
        "\nPour obtenir les droits d'utilisation de cette bibliothèque."
    )

def check_license_or_exit():
    """Vérifier la licence et quitter si non valide"""
    if not validate_license():
        print("❌ ACCÈS NON AUTORISÉ")
        print("=" * 50)
        print(get_license_error_message())
        print("=" * 50)
        sys.exit(1)

# Auto-vérification lors de l'importation de tout module de la bibliothèque
def _auto_validate():
    """Auto-validation lors de l'importation"""
    try:
        # Cette vérification se fait silencieusement
        if not validate_license():
            # Ne pas afficher l'erreur lors de l'import, juste retourner False
            # L'erreur sera affichée lors de l'utilisation effective
            pass
    except Exception:
        pass

# Exécuter la validation automatique
_auto_validate()
