# -*- coding: utf-8 -*-
"""
insta_kendou - Bibliothèque Instagram complète
Gestion de l'authentification, 2FA, actions et médias Instagram

Version: 1.0.0
Auteur: Kenny (@Ken56266325)
Contact: 0389561802 | https://t.me/Kenny5626
"""

from .client import InstagramClient
from .exceptions import *
from .utils.license import validate_license, LicenseError

# Validation de licence au niveau de la bibliothèque
if not validate_license():
    raise LicenseError()

# Informations de la bibliothèque
__version__ = "1.0.0"
__author__ = "Kenny"
__email__ = "mampifaly56266325@gmail.com"
__url__ = "https://github.com/Ken56266325/insta_kendou"
__description__ = "Bibliothèque Instagram complète avec authentification 2FA et gestion des médias"

# Exports principaux
__all__ = [
    'InstagramClient',
    # Exceptions
    'InstagramError',
    'AuthenticationError',
    'TwoFactorError',
    'ChallengeError',
    'MediaError',
    'UserNotFoundError',
    'AccountSuspendedError',
    'AccountDisabledError',
    'RateLimitError',
    'LoginRequiredError',
    'InvalidCredentialsError',
    'PasswordIncorrectError',
    'LicenseError'
]

def get_version():
    """Retourner la version de la bibliothèque"""
    return __version__

def check_license():
    """Vérifier la licence d'utilisation"""
    return validate_license()

# Message de bienvenue (silencieux)
def _init_message():
    """Message d'initialisation silencieux"""
    try:
        import sys
        if hasattr(sys.stdout, 'write'):
            pass  # Initialisation silencieuse
    except:
        pass

_init_message()
