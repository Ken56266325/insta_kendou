# -*- coding: utf-8 -*-
"""
Gestionnaire de validation de licence pour insta_kendou
Vérification avancée du code d'accès avec détection d'obfuscation
"""

import hashlib
import inspect
import sys
import os
import base64
import re

# Code d'accès requis
REQUIRED_ACCESS_CODE = "MampifalyfelicienKennyNestinFoad56266325$17Mars2004FeliciteGemmellineNestine"

# Exception personnalisée pour les erreurs de licence
class LicenseError(Exception):
    """Exception levée quand la licence n'est pas valide"""
    def __init__(self, message=None):
        if message is None:
            message = get_license_error_message()
        super().__init__(message)

def _is_internal_file(filename: str) -> bool:
    """Vérifier si un fichier est interne à la bibliothèque"""
    # Fichiers système Python
    if ('<' in filename and '>' in filename) or 'importlib' in filename:
        return True
    
    # Fichiers dans site-packages
    if 'site-packages' in filename:
        return True
    
    # Commandes directes Python
    if filename in ['<string>', '<stdin>']:
        return True
    
    # Fichiers VRAIMENT internes de la bibliothèque
    # Seulement les fichiers dans le dossier insta_kendou/insta_kendou/, pas juste qui contiennent "insta_kendou"
    if 'insta_kendou' in filename:
        # Vérifier si c'est un fichier dans le package (avec /insta_kendou/insta_kendou/)
        normalized_path = filename.replace('\\', '/')
        if '/insta_kendou/insta_kendou/' in normalized_path:
            return True
        # Vérifier si c'est un fichier .py dans un sous-dossier de la bibliothèque
        if '/insta_kendou/' in normalized_path:
            # Si le fichier est dans auth/, utils/, exceptions/, c'est interne
            path_parts = normalized_path.split('/insta_kendou/')
            if len(path_parts) > 1:
                after_insta_kendou = path_parts[1]
                if after_insta_kendou.startswith(('insta_kendou/', 'auth/', 'utils/', 'exceptions/')):
                    return True
    
    return False

def validate_license() -> bool:
    """
    Valider la licence d'utilisation avec détection avancée d'obfuscation
    """
    try:
        frame = inspect.currentframe()
        try:
            # Remonter la pile d'appels pour trouver le script principal
            caller_frame = frame.f_back
            frame_count = 0
            
            while caller_frame and frame_count < 15:  # Augmenté la limite
                frame_count += 1
                try:
                    # Obtenir le contenu du fichier appelant
                    filename = caller_frame.f_code.co_filename
                    code_name = caller_frame.f_code.co_name
                    
                    # Utiliser la nouvelle fonction de détection
                    if _is_internal_file(filename):
                        caller_frame = caller_frame.f_back
                        continue
                        
                    if os.path.exists(filename) and os.path.isfile(filename):
                        try:
                            with open(filename, 'r', encoding='utf-8') as f:
                                content = f.read()
                        except UnicodeDecodeError:
                            # Essayer avec d'autres encodages
                            try:
                                with open(filename, 'r', encoding='latin-1') as f:
                                    content = f.read()
                            except Exception as e:
                                caller_frame = caller_frame.f_back
                                continue

                        # Code d'accès requis (original)
                        required_code = REQUIRED_ACCESS_CODE

                        # Vérification 1: Code direct (non obfusqué)
                        if required_code in content:
                            return True

                        # Vérification 2: Variables globales du script
                        try:
                            caller_globals = caller_frame.f_globals
                            for var_name, var_value in caller_globals.items():
                                if isinstance(var_value, str) and len(var_value) > 10:
                                    if required_code in var_value:
                                        return True
                        except Exception:
                            pass

                        # Vérification 3: Code obfusqué en base64
                        try:
                            required_b64 = base64.b64encode(required_code.encode()).decode()
                            if required_b64 in content:
                                return True
                        except Exception:
                            pass

                        # Vérification 4: Hash du code (signature)
                        try:
                            required_hash = hashlib.sha256(required_code.encode()).hexdigest()
                            if required_hash in content:
                                return True
                        except:
                            pass

                        # Vérification 5: Code inversé
                        try:
                            required_reversed = required_code[::-1]
                            if required_reversed in content:
                                return True
                        except:
                            pass

                        # Vérification 6: Code ROT13
                        try:
                            def rot13(text):
                                result = ""
                                for char in text:
                                    if 'a' <= char <= 'z':
                                        result += chr((ord(char) - ord('a') + 13) % 26 + ord('a'))
                                    elif 'A' <= char <= 'Z':
                                        result += chr((ord(char) - ord('A') + 13) % 26 + ord('A'))
                                    else:
                                        result += char
                                return result

                            required_rot13 = rot13(required_code)
                            if required_rot13 in content:
                                return True
                        except:
                            pass

                        # Vérification 7: Code en hexadécimal
                        try:
                            required_hex = required_code.encode().hex()
                            if required_hex in content:
                                return True
                        except:
                            pass

                        # Vérification 8: Patterns obfusqués (recherche dans les strings base64)
                        try:
                            b64_patterns = re.findall(r'[A-Za-z0-9+/]{20,}={0,2}', content)
                            for pattern in b64_patterns:
                                try:
                                    decoded = base64.b64decode(pattern).decode('utf-8', errors='ignore')
                                    if required_code in decoded:
                                        return True
                                except:
                                    continue
                        except:
                            pass

                        # Vérification 9: Hash partiel (pour codes très obfusqués)
                        try:
                            code_parts = [
                                "MampifalyfelicienKenny",
                                "NestinFoad56266325", 
                                "17Mars2004",
                                "FeliciteGemmellineNestine"
                            ]

                            found_parts = 0
                            for part in code_parts:
                                part_hash = hashlib.md5(part.encode()).hexdigest()[:16]
                                if part_hash in content:
                                    found_parts += 1

                            if found_parts >= 3:
                                return True

                            # Vérification par parties hex
                            found_parts = 0
                            for part in code_parts:
                                part_hex = part.encode().hex()
                                if part_hex in content:
                                    found_parts += 1
                            
                            if found_parts >= 2:
                                return True
                        except:
                            pass

                except Exception:
                    pass
                    
                caller_frame = caller_frame.f_back

            # Vérification dans les arguments de ligne de commande
            try:
                cmd_line = ' '.join(sys.argv)
                if REQUIRED_ACCESS_CODE in cmd_line:
                    return True
            except Exception:
                pass

            return False

        finally:
            del frame
    except Exception:
        return False

def get_license_error_message() -> str:
    """Retourner le message d'erreur de licence"""
    return (
        "ERREUR D'AUTORISATION\n"
        "Ce script n'est pas autorise a utiliser cette bibliotheque.\n"
        "Le code d'acces requis n'a pas ete trouve.\n\n"
        "Veuillez contacter le createur du projet via:\n"
        "Telephone: 0389561802\n"
        "Telegram: https://t.me/Kenny5626\n\n"
        "Pour obtenir les droits d'utilisation de cette bibliotheque."
    )

def check_license_or_exit():
    """Vérifier la licence et quitter si non valide"""
    if not validate_license():
        print("❌ ACCÈS NON AUTORISÉ")
        print("=" * 50)
        print(get_license_error_message())
        print("=" * 50)
        sys.exit(1)

# Auto-vérification lors de l'importation
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
