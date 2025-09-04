# -*- coding: utf-8 -*-
"""
Module d'authentification Instagram pour insta_kendou
Gestion complète de la connexion et de l'authentification 2FA
"""

from .authentication import InstagramAuth
from .bloks_2fa import BloksManager
from .alternative_2fa import AlternativeManager  
from .classic_2fa import ClassicManager
from .challenge_handler import ChallengeHandler

__all__ = [
    'InstagramAuth',
    'BloksManager', 
    'AlternativeManager',
    'ClassicManager',
    'ChallengeHandler'
]
