# -*- coding: utf-8 -*-
"""
Client principal Instagram pour insta_kendou - VERSION AMÉLIORÉE
Classe InstagramClient avec toutes les fonctionnalités complètes et headers exacts
"""

import os
import time
import json
import uuid
import random
import urllib.parse
import re
import base64
from datetime import datetime
from .auth import InstagramAuth
from .utils import DeviceManager, InstagramEncryption, MediaProcessor, URLResolver, validate_license
from .exceptions import *

class InstagramAPI:
    """API Instagram pour extraire media ID et user ID (intégrée au client) - CORRIGÉE"""
    
    def __init__(self, session, device_info: dict, user_id: str = None, auth_token: str = None):
        self.session = session
        self.device_info = device_info
        self.user_id = user_id
        self.auth_token = auth_token
        self.url_resolver = URLResolver()
    
    def shortcode_to_media_id(self, shortcode: str) -> str:
        """Convertir shortcode Instagram en media ID (algorithme exact)"""
        return self.url_resolver.shortcode_to_media_id(shortcode)
    
    def extract_media_id_from_url(self, url: str) -> str:
        """Extraire media ID depuis URL Instagram (utilise URLResolver)"""
        return self.url_resolver.extract_media_id_from_url(url)
    
    def extract_user_id_from_url(self, url: str) -> str:
        """Extraire user ID depuis URL de profil - CORRIGÉ avec recherche similaire"""
        try:
            # D'abord résoudre les liens courts
            resolved_url = self.url_resolver.resolve_short_url(url)
            
            # Extraire username depuis l'URL
            match = re.search(r'instagram\.com/([^/?]+)', resolved_url)
            if match:
                username = match.group(1).replace('@', '').strip()
                
                # Utiliser la recherche similaire EXACTEMENT comme script original
                user_id = self._search_similar_username(username)
                return user_id
            
            return None
            
        except Exception as e:
            return None
    
    def _search_similar_username(self, target_username: str) -> str:
        """Rechercher username similaire EXACTEMENT comme script original"""
        try:
            headers = {
                "user-agent": self.device_info['user_agent'],
                "x-ig-app-id": "567067343352427",
                "x-ig-android-id": self.device_info['android_id'],
                "x-ig-device-id": self.device_info['device_uuid'],
                "accept-language": "fr-FR, en-US",
                "authorization": self.auth_token,
            }
            
            search_params = {
                "timezone_offset": "10800",
                "q": target_username,
                "count": "20"
            }
            
            response = self.session.get(
                "https://i.instagram.com/api/v1/users/search/",
                params=search_params,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("status") == "ok" and "users" in data:
                        users = data["users"]
                        
                        # Recherche exacte d'abord
                        for user in users:
                            username = user.get("username", "").lower()
                            if username == target_username.lower():
                                user_id = str(user.get("pk"))
                                return user_id
                        
                        # Si pas trouvé exact, recherche similaire EXACTEMENT comme script original
                        target_lower = target_username.lower()
                        best_matches = []
                        
                        # Recherche par préfixe
                        for user in users:
                            username = user.get("username", "").lower()
                            if username.startswith(target_lower) and username != target_lower:
                                best_matches.append((user.get("pk"), username))
                        
                        if best_matches:
                            best_matches.sort(key=lambda x: len(x[1]))
                            user_id = str(best_matches[0][0])
                            return user_id
                        
                        # Recherche par parties de nom EXACTEMENT comme script original
                        for user in users:
                            username = user.get("username", "").lower()
                            if any(part in username for part in target_lower.split('_') + target_lower.split('.') if len(part) > 2):
                                user_id = str(user.get("pk"))
                                return user_id
                        
                except Exception:
                    pass
            
            # Si rien trouvé, utiliser fallback web
            return self._username_to_user_id_web_fallback(target_username)
            
        except Exception:
            return None
    
    def _username_to_user_id_web_fallback(self, username: str) -> str:
        """Fallback web pour username -> user ID"""
        try:
            web_response = self.session.get(
                f"https://www.instagram.com/{username}/",
                headers={"user-agent": "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36"},
                timeout=10
            )
            
            if web_response.status_code == 200:
                content = InstagramEncryption.safe_decode_response(web_response)
                
                # Extraire user ID depuis le HTML
                user_id_patterns = [
                    r'"profilePage_([0-9]+)"',
                    r'"user_id":"([0-9]+)"',
                    r'"owner":{"id":"([0-9]+)"'
                ]
                
                for pattern in user_id_patterns:
                    match = re.search(pattern, content)
                    if match:
                        user_id = match.group(1)
                        return user_id
            
            return None
            
        except Exception:
            return None
    
    def get_user_info(self, user_id: str) -> dict:
        """Récupérer informations d'un utilisateur"""
        try:
            headers = {
                "user-agent": self.device_info['user_agent'],
                "x-ig-app-id": "567067343352427",
                "x-ig-android-id": self.device_info['android_id'],
                "x-ig-device-id": self.device_info['device_uuid'],
                "accept-language": "fr-FR, en-US",
                "authorization": self.auth_token if self.auth_token else "",
            }
            
            response = self.session.get(
                f"https://i.instagram.com/api/v1/users/{user_id}/info/",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "ok":
                    return data.get("user", {})
            
            return {}
            
        except Exception as e:
            return {}
    
    def get_own_media_list(self, count: int = 20) -> list:
        """Récupérer la liste des médias de l'utilisateur connecté"""
        try:
            if not self.user_id:
                return []
            
            headers = {
                "user-agent": self.device_info['user_agent'],
                "x-ig-app-id": "567067343352427",
                "authorization": self.auth_token if self.auth_token else "",
                "x-ig-android-id": self.device_info['android_id'],
                "x-ig-device-id": self.device_info['device_uuid'],
            }
            
            params = {
                "count": str(count),
                "max_id": ""
            }
            
            response = self.session.get(
                f"https://i.instagram.com/api/v1/feed/user/{self.user_id}/",
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "ok":
                    items = data.get("items", [])
                    media_list = []
                    
                    for item in items:
                        media_info = {
                            "id": item.get("id"),
                            "code": item.get("code"),
                            "media_type": item.get("media_type"),
                            "taken_at": item.get("taken_at"),
                            "like_count": item.get("like_count", 0),
                            "comment_count": item.get("comment_count", 0)
                        }
                        
                        # Caption
                        caption_info = item.get("caption")
                        if caption_info:
                            media_info["caption"] = caption_info.get("text", "")
                        else:
                            media_info["caption"] = ""
                        
                        media_list.append(media_info)
                    
                    return media_list
            
            return []
            
        except Exception as e:
            return []

class InstagramClient:
    """Client Instagram complet avec toutes les fonctionnalités"""
    
    def __init__(self, session_data: dict = None):
        # Validation licence obligatoire
        if not validate_license():
            raise LicenseError("Ce script n'est pas autorisé à utiliser cette bibliothèque. Veuillez contacter le créateur via: 0389561802 ou https://t.me/Kenny5626")
        
        self.auth = InstagramAuth()
        self.session_data = session_data or {}
        self.api = None
        
        if session_data:
            self.auth.session_data = session_data
            # Restaurer cookies
            if "cookies" in session_data:
                for name, value in session_data["cookies"].items():
                    self.auth.session.cookies.set(name, value)
            
            # Initialiser API
            user_data = session_data.get("user_data", {}) or session_data.get("logged_in_user", {})
            auth_token = session_data.get("authorization_data", {}).get("authorization_header", "") or session_data.get("authorization", "")
            user_id = user_data.get("user_id", "") or session_data.get("account_id", "")
            
            if user_id:
                self.api = InstagramAPI(self.auth.session, self.auth.device_manager.device_info, user_id, auth_token)
    
    def login(self, username: str, password: str) -> dict:
        """Connexion Instagram avec gestion 2FA complète"""
        return self.auth.login(username, password)
    
    def load_session(self, username: str) -> dict:
        """Charger session depuis le disque"""
        session_data = self.auth.load_session(username)
        if session_data:
            self.session_data = session_data
            
            # Initialiser API avec session chargée
            user_data = session_data.get("user_data", {}) or session_data.get("logged_in_user", {})
            auth_token = session_data.get("authorization_data", {}).get("authorization_header", "") or session_data.get("authorization", "")
            user_id = user_data.get("user_id", "") or session_data.get("account_id", "")
            
            if user_id:
                self.api = InstagramAPI(self.auth.session, self.auth.device_manager.device_info, user_id, auth_token)
        
        return session_data
    
    def dump_session(self, username: str = None) -> dict:
        """Sauvegarder la session actuelle"""
        if not username and self.session_data:
            # Récupérer username depuis session_data
            user_data = self.session_data.get("user_data", {}) or self.session_data.get("logged_in_user", {})
            username = user_data.get("username") or self.session_data.get("account_username")
        
        if username and self.session_data:
            user_data = self.session_data.get("user_data", {}) or self.session_data.get("logged_in_user", {})
            # Utiliser _save_session_fixed de auth
            self.auth._save_session_fixed(username, self.session_data, user_data)
            return self.session_data
        
        return {}
    
    def get_x_mid(self) -> str:
        """Récupérer x-mid depuis le device manager"""
        return self.auth.device_manager.get_x_mid()
    
    def _get_username_from_session(self) -> str:
        """Récupérer le username depuis la session"""
        user_data = self.session_data.get("user_data", {}) or self.session_data.get("logged_in_user", {})
        username = user_data.get("username")
        
        if username and username != "":
            return username
        
        auth_data = self.session_data.get("authorization_data", {})
        username = auth_data.get("username")
        if username and username != "":
            return username
        
        account_username = self.session_data.get("account_username")
        if account_username and account_username != "":
            return account_username
        
        return "user_unknown"
    
    def _get_user_id_from_session(self) -> str:
        """Récupérer user ID depuis la session"""
        user_data = self.session_data.get("user_data", {}) or self.session_data.get("logged_in_user", {})
        user_id = user_data.get("user_id")
        
        if user_id:
            return str(user_id)
        
        auth_data = self.session_data.get("authorization_data", {})
        user_id = auth_data.get("ds_user_id")
        
        if user_id:
            return str(user_id)
        
        return "user_id_unknown"
    
    def _get_auth_token(self) -> str:
        """Récupérer token d'autorisation"""
        auth_data = self.session_data.get("authorization_data", {})
        auth_header = auth_data.get("authorization_header")
        
        if auth_header and "Bearer" in auth_header:
            return auth_header
        
        auth_token = self.session_data.get("authorization")
        if auth_token and "Bearer" in auth_token:
            return auth_token
        
        # Construire token basique si manquant
        user_id = self._get_user_id_from_session()
        sessionid = self.session_data.get("sessionid") or self.session_data.get("cookies", {}).get("sessionid")
        
        if sessionid:
            if '%3A' not in sessionid:
                sessionid = urllib.parse.quote(sessionid)
            
            token_data = {
                "ds_user_id": user_id,
                "sessionid": sessionid
            }
            
            encoded = base64.b64encode(json.dumps(token_data, separators=(',', ':')).encode()).decode()
            return f"Bearer IGT:2:{encoded}"
        
        return ""
    
    def _get_bandwidth_test_data(self) -> dict:
        """Récupérer données de test de bande passante depuis la session"""
        session_meta = self.session_data.get("session_metadata", {})
        bandwidth_data = session_meta.get("bandwidth_test_data", {})
        
        if bandwidth_data:
            return {
                "speed_kbps": str(int(bandwidth_data.get("speed_kbps", 2000))),
                "total_bytes": str(bandwidth_data.get("total_bytes", 1000000)),
                "total_time_ms": str(bandwidth_data.get("total_time_ms", 1000))
            }
        
        # Valeurs par défaut
        return {
            "speed_kbps": "2000",
            "total_bytes": "1000000", 
            "total_time_ms": "1000"
        }
    
    def _get_salt_ids(self) -> list:
        """Récupérer salt IDs depuis la session"""
        session_meta = self.session_data.get("session_metadata", {})
        salt_ids = session_meta.get("salt_ids", [])
        
        if salt_ids and len(salt_ids) >= 2:
            return salt_ids
        
        # Valeurs par défaut
        return [220145826, 220140399]
    
    def _get_pigeon_session_id(self) -> str:
        """Récupérer ou générer pigeon session ID"""
        session_meta = self.session_data.get("session_metadata", {})
        pigeon_id = session_meta.get("pigeon_session_id")
        
        if pigeon_id:
            return pigeon_id
        
        # Générer nouveau
        return f"UFS-{str(uuid.uuid4())}-1"
    
    def _get_conn_uuid_client(self) -> str:
        """Récupérer ou générer conn uuid client"""
        session_meta = self.session_data.get("session_metadata", {})
        conn_uuid = session_meta.get("conn_uuid_client")
        
        if conn_uuid:
            return conn_uuid
        
        # Générer nouveau
        return str(uuid.uuid4()).replace('-', '')[:32]
    
    def _get_network_type(self) -> str:
        """Détecter le type de réseau actuel"""
        try:
            import netifaces
            interfaces = netifaces.interfaces()
            
            # Vérifier interfaces WiFi
            for interface in interfaces:
                if 'wlan' in interface.lower() or 'wifi' in interface.lower():
                    addrs = netifaces.ifaddresses(interface)
                    if netifaces.AF_INET in addrs:
                        return "WIFI"
            
            # Vérifier interfaces cellulaires 
            for interface in interfaces:
                if any(x in interface.lower() for x in ['rmnet', 'mobile', 'cellular', 'ppp']):
                    addrs = netifaces.ifaddresses(interface)
                    if netifaces.AF_INET in addrs:
                        return "CELLULAR"
            
            # Par défaut
            return "WIFI"
            
        except ImportError:
            # Si netifaces pas disponible, utiliser méthode basique
            import socket
            try:
                # Tenter connexion pour détecter
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                s.close()
                return "WIFI"  # Par défaut si connexion OK
            except:
                return "WIFI"
    
    def _get_radio_type(self) -> str:
        """Obtenir type radio basé sur le réseau"""
        network_type = self._get_network_type()
        
        if network_type == "WIFI":
            return "wifi-none"
        elif network_type == "CELLULAR":
            return "lte"
        else:
            return "wifi-none"
    
    def _get_connection_type_headers(self) -> dict:
        """Obtenir headers liés au type de connexion"""
        network_type = self._get_network_type()
        
        return {
            "x-fb-connection-type": network_type,
            "x-ig-connection-type": network_type
        }
    
    def _get_device_specific_headers(self) -> dict:
        """Obtenir headers spécifiques au device depuis la session"""
        device_settings = self.session_data.get("device_settings", {})
        
        if not device_settings:
            # Fallback sur device_info
            device_info = self.auth.device_manager.device_info
            return {
                "x-ig-android-id": device_info.get('android_id', ''),
                "x-ig-device-id": device_info.get('device_uuid', ''),
                "user-agent": device_info.get('user_agent', '')
            }
        
        # Utiliser device_settings de la session
        android_version = device_settings.get('android_version', 32)
        android_release = device_settings.get('android_release', '12')
        dpi = device_settings.get('dpi', '320dpi')
        resolution = device_settings.get('resolution', '900x1600')
        manufacturer = device_settings.get('manufacturer', 'samsung')
        model = device_settings.get('model', 'SM-G991B')
        device = device_settings.get('device', 'z3q')
        app_version = device_settings.get('app_version', '394.0.0.46.81')
        version_code = device_settings.get('version_code', '779659870')
        
        # Récupérer IDs depuis uuids
        uuids = self.session_data.get("uuids", {})
        android_id = uuids.get("device_id", "android-" + str(uuid.uuid4()).replace('-', '')[:16])
        device_uuid = uuids.get("uuid", str(uuid.uuid4()))
        
        # Construire user agent
        user_agent = f"Instagram {app_version} Android ({android_version}/{android_release}; {dpi}; {resolution}; {manufacturer}; {model}; {device}; exynos8895; fr_FR; {version_code})"
        
        return {
            "x-ig-android-id": android_id,
            "x-ig-device-id": device_uuid,
            "user-agent": user_agent
        }
    
    def _get_ig_headers(self) -> dict:
        """Récupérer headers IG depuis la session"""
        ig_headers = self.session_data.get("ig_headers", {})
        
        headers = {}
        
        # x-ig-www-claim
        www_claim = ig_headers.get("x-ig-www-claim")
        if www_claim:
            headers["x-ig-www-claim"] = www_claim
        
        # ig-u-ds-user-id
        user_id = self._get_user_id_from_session()
        headers["ig-u-ds-user-id"] = user_id
        headers["ig-intended-user-id"] = user_id
        
        # ig-u-rur
        ig_u_rur = ig_headers.get("ig-u-rur")
        if ig_u_rur:
            headers["ig-u-rur"] = ig_u_rur
        else:
            # Générer ig-u-rur basique
            timestamp = int(time.time() + 30 * 24 * 3600)  # 30 jours
            random_hash = str(uuid.uuid4()).replace('-', '')[:40]
            headers["ig-u-rur"] = f"LLA,{user_id},{timestamp}:01fe{random_hash}"
        
        return headers
    
    def _generate_meta_zca(self) -> str:
        """Générer x-meta-zca dynamique avec données réelles"""
        import hashlib
        import secrets
        import base64
        
        try:
            # Timestamp actuel
            current_time = str(int(time.time() * 1000))
            
            # Générer hash unique basé sur timestamp + device + user
            device_headers = self._get_device_specific_headers()
            user_id = self._get_user_id_from_session()
            hash_data = f"{current_time}{device_headers.get('x-ig-device-id', '')}{user_id}"
            hash_value = hashlib.sha256(hash_data.encode()).digest()
            hash_b64 = base64.b64encode(hash_value).decode()[:43]
            
            # Générer nonce aléatoire (24 caractères base64)
            key_nonce = base64.b64encode(secrets.token_bytes(18)).decode()
            
            # Détecter niveau batterie réel ou simuler
            battery_level = self._get_battery_level()
            battery_status = self._get_battery_status()
            
            # Structure ZCA complète
            zca_data = {
                "android": {
                    "aka": {
                        "dataToSign": json.dumps({
                            "time": current_time,
                            "hash": hash_b64
                        }, separators=(',', ':')),
                        "keyNonce": key_nonce,
                        "errors": ["KEYSTORE_TOKEN_RETRIEVAL_ERROR"]
                    },
                    "gpia": {
                        "token": "",
                        "errors": ["PLAY_INTEGRITY_DISABLED_BY_CONFIG"]
                    },
                    "payload": {
                        "plugins": {
                            "bat": {
                                "sta": battery_status,
                                "lvl": battery_level
                            },
                            "sct": {}
                        }
                    }
                }
            }
            
            # Encoder en base64
            json_str = json.dumps(zca_data, separators=(',', ':'))
            encoded = base64.b64encode(json_str.encode()).decode()
            
            return encoded
            
        except Exception as e:
            # Fallback avec données minimales mais dynamiques
            current_time = str(int(time.time() * 1000))
            hash_fallback = hashlib.sha256(f"{current_time}{random.randint(1000, 9999)}".encode()).hexdigest()[:43]
            
            fallback_data = {
                "android": {
                    "aka": {
                        "dataToSign": f'{{"time":"{current_time}","hash":"{hash_fallback}"}}',
                        "keyNonce": base64.b64encode(secrets.token_bytes(18)).decode(),
                        "errors": ["KEYSTORE_TOKEN_RETRIEVAL_ERROR"]
                    },
                    "gpia": {
                        "token": "",
                        "errors": ["PLAY_INTEGRITY_DISABLED_BY_CONFIG"]
                    },
                    "payload": {
                        "plugins": {
                            "bat": {
                                "sta": "Unplugged",
                                "lvl": random.randint(20, 95)
                            },
                            "sct": {}
                        }
                    }
                }
            }
            
            json_str = json.dumps(fallback_data, separators=(',', ':'))
            return base64.b64encode(json_str.encode()).decode()
    
    def _get_battery_level(self) -> int:
        """Obtenir niveau batterie réel du système ou simuler"""
        try:
            # Tenter lecture batterie Linux/Android
            if os.path.exists("/sys/class/power_supply/BAT0/capacity"):
                with open("/sys/class/power_supply/BAT0/capacity", "r") as f:
                    return int(f.read().strip())
            elif os.path.exists("/sys/class/power_supply/BAT1/capacity"):
                with open("/sys/class/power_supply/BAT1/capacity", "r") as f:
                    return int(f.read().strip())
            else:
                # Simulation réaliste basée sur l'heure
                hour = datetime.now().hour
                if 6 <= hour <= 12:  # Matin - batterie élevée
                    return random.randint(75, 95)
                elif 12 <= hour <= 18:  # Après-midi - batterie moyenne
                    return random.randint(45, 80)
                else:  # Soir/nuit - batterie plus faible
                    return random.randint(20, 60)
        except:
            return random.randint(25, 90)
    
    def _get_battery_status(self) -> str:
        """Obtenir status batterie réel ou simuler"""
        try:
            # Tenter lecture status Linux/Android
            if os.path.exists("/sys/class/power_supply/BAT0/status"):
                with open("/sys/class/power_supply/BAT0/status", "r") as f:
                    status = f.read().strip().lower()
                    if "charging" in status:
                        return "Charging"
                    elif "full" in status:
                        return "Full"
                    else:
                        return "Unplugged"
            else:
                # Simulation réaliste
                battery_level = self._get_battery_level()
                if battery_level >= 95:
                    return random.choice(["Full", "Unplugged"])
                elif battery_level <= 25:
                    return random.choice(["Charging", "Unplugged"])
                else:
                    return random.choice(["Unplugged", "Unplugged", "Charging"])  # Plus probable unplugged
        except:
            return random.choice(["Unplugged", "Charging", "Full"])
    
    def _build_complete_headers(self, endpoint: str = "", friendly_name: str = "") -> dict:
        """Construire headers complets avec toutes les données de session"""
        user_id = self._get_user_id_from_session()
        bandwidth_data = self._get_bandwidth_test_data()
        salt_ids = self._get_salt_ids()
        device_headers = self._get_device_specific_headers()
        connection_headers = self._get_connection_type_headers()
        ig_headers = self._get_ig_headers()
        
        # Headers de base
        headers = {
            "accept-language": "fr-FR, en-US",
            "authorization": self._get_auth_token(),
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "x-fb-client-ip": "True",
            "x-fb-server-cluster": "True",
            "priority": "u=3",
            "x-ig-app-id": "567067343352427",
            "x-ig-app-locale": "fr_FR",
            "x-ig-device-locale": "fr_FR",
            "x-ig-mapped-locale": "fr_FR",
            "x-ig-timezone-offset": str(self.session_data.get("timezone_offset", 10800)),
            "x-ig-capabilities": "3brTv10=",
            "x-pigeon-rawclienttime": str(time.time()),
            "x-pigeon-session-id": self._get_pigeon_session_id(),
            "x-tigon-is-retry": "False",
            "accept-encoding": "zstd",
            "x-fb-http-engine": "Tigon/MNS/TCP",
            "x-fb-conn-uuid-client": self._get_conn_uuid_client()
        }
        
        # Ajouter headers spécifiques au device
        headers.update(device_headers)
        
        # Ajouter headers de connexion
        headers.update(connection_headers)
        
        # Ajouter headers IG
        headers.update(ig_headers)
        
        # Ajouter bande passante
        headers.update({
            "x-ig-bandwidth-speed-kbps": bandwidth_data["speed_kbps"],
            "x-ig-bandwidth-totalbytes-b": bandwidth_data["total_bytes"],
            "x-ig-bandwidth-totaltime-ms": bandwidth_data["total_time_ms"]
        })
        
        # Salt IDs
        if len(salt_ids) >= 1:
            headers["x-ig-salt-ids"] = str(salt_ids[0])
        
        # Headers Bloks
        headers.update({
            "x-bloks-is-layout-rtl": "false",
            "x-bloks-prism-button-version": "INDIGO_PRIMARY_BORDERED_SECONDARY",
            "x-bloks-prism-colors-enabled": "false",
            "x-bloks-prism-elevated-background-fix": "false",
            "x-bloks-prism-extended-palette-gray-red": "false",
            "x-bloks-prism-extended-palette-indigo": "false",
            "x-bloks-prism-font-enabled": "false",
            "x-bloks-prism-indigo-link-version": "1"
        })
        
        # Bloks version depuis session
        session_meta = self.session_data.get("session_metadata", {})
        bloks_version = session_meta.get("bloks_version_id")
        if bloks_version:
            headers["x-bloks-version-id"] = bloks_version
        else:
            headers["x-bloks-version-id"] = "ef88cb8e7a6a225af847577c11f18eeccda0582b87e294181c4c7425d28047b1"
        
        # Device languages depuis session
        locale = self.session_data.get("locale", "fr_FR")
        headers["x-ig-device-languages"] = f'{{"system_languages":"{locale}"}}'
        
        # Family device ID depuis session
        uuids = self.session_data.get("uuids", {})
        family_device_id = uuids.get("client_session_id")
        if family_device_id:
            headers["x-ig-family-device-id"] = family_device_id
        
        # x-mid depuis session ou device manager
        x_mid = self.get_x_mid()
        if x_mid:
            headers["x-mid"] = x_mid
        
        # Nav chain basique si non fournie
        current_time = int(time.time() * 1000)
        headers["x-ig-nav-chain"] = f"MainFeedFragment:feed_timeline:1:cold_start:{current_time}:::"
        
        # Endpoint spécifique
        if endpoint:
            headers["x-ig-client-endpoint"] = endpoint
        
        # Friendly name
        if friendly_name:
            headers["x-fb-friendly-name"] = friendly_name
        
        # Request analytics tags
        headers["x-fb-request-analytics-tags"] = '{"network_tags":{"product":"567067343352427","purpose":"fetch","surface":"undefined","request_category":"api","retry_attempt":"0"}}'
        
        # Zero headers pour économie de données
        headers.update({
            "x-zero-a-device-id": "",
            "x-zero-balance": "INIT",
            "x-zero-d-device-id": device_headers.get("x-ig-device-id", ""),
            "x-zero-eh": "",
            "x-zero-f-device-id": family_device_id or ""
        })
        
        # Générer Meta ZCA dynamique avec données réelles
        headers["x-meta-zca"] = self._generate_meta_zca()
        
        return headers
    
    def _build_nav_chain(self, action_type: str = "general") -> str:
        """Construire nav chain contextuel"""
        current_time = int(time.time() * 1000)
        
        nav_chains = {
            "like": f"MainFeedFragment:feed_timeline:1:cold_start:{current_time}:::,UserDetailFragment:profile:3:button:{current_time}:::,ProfileMediaTabFragment:profile:4:button:{current_time}:::,ContextualFeedFragment:feed_contextual:5:button:{current_time}:::",
            "comment": f"MainFeedFragment:feed_timeline:1:cold_start:{current_time}:::,UserDetailFragment:profile:3:button:{current_time}:::,ProfileMediaTabFragment:profile:4:button:{current_time}:::,ContextualFeedFragment:feed_contextual:7:button:{current_time}:::,CommentListBottomsheetFragment:comments_v2:8:button:{current_time}:::",
            "follow": f"MainFeedFragment:feed_timeline:1:cold_start:{current_time}:::,UserDetailFragment:profile:7:media_owner:{current_time}:::,ProfileMediaTabFragment:profile:8:button:{current_time}:::",
            "general": f"MainFeedFragment:feed_timeline:1:cold_start:{current_time}:::"
        }
        
        return nav_chains.get(action_type, nav_chains["general"])
    
    def handle_action_error(self, response_status: int, error_data: dict, response_text: str = "") -> dict:
        """Gérer les erreurs d'action avec messages simplifiés (IDENTIQUE AU SCRIPT ORIGINAL)"""
        try:
            username = self._get_username_from_session()
            
            # 1. VÉRIFIER FEEDBACK_REQUIRED EN PREMIER
            if isinstance(error_data, dict) and error_data.get("message") == "feedback_required":
                feedback_result = self.handle_feedback_required(error_data)
                if feedback_result["type"] == "rate_limit":
                    return feedback_result
                elif feedback_result["type"] == "pending_follow":
                    print(f"✅ {feedback_result['message']}")
                    return feedback_result
                else:
                    print(f"❌ {feedback_result['error']}")
                    return feedback_result
            
            # 2. VÉRIFIER LOGIN_REQUIRED
            if (isinstance(error_data, dict) and error_data.get("message") == "login_required") or \
               ("login_required" in response_text.lower()):
                return {
                    "success": False,
                    "error": f"Le compte @{username} est déconnecté, veuillez vous reconnecter"
                }
            
            # 3. VÉRIFIER SUSPENDED/DISABLED DANS LES CHALLENGES
            if isinstance(error_data, dict):
                challenge_info = self.handle_challenge_response(response_text, error_data)
                
                if not challenge_info["show_details"]:
                    if challenge_info["type"] == "suspended":
                        return {
                            "success": False,
                            "error": f"Le compte @{username} est suspendu, veuillez le régler manuellement"
                        }
                    elif challenge_info["type"] == "disabled":
                        return {
                            "success": False,
                            "error": f"Le compte @{username} est désactivé et ne peut plus être utilisé"
                        }
                    elif challenge_info["type"] == "general_challenge" and challenge_info.get("can_retry"):
                        return {
                            "success": False,
                            "error": "Challenge requis",
                            "challenge_data": challenge_info["challenge_data"]
                        }
            
            # 4. VÉRIFIER ERREURS SPÉCIFIQUES CONNUES
            error_text = str(error_data).lower()
            
            # Média supprimé
            if any(keyword in error_text for keyword in ["deleted", "supprime", "no longer available", "not found"]):
                return {"success": False, "error": "Ce media a été supprimé"}
            
            # Utilisateur introuvable
            if any(keyword in error_text for keyword in ["user not found", "utilisateur introuvable"]):
                return {"success": False, "error": "Utilisateur introuvable"}
            
            # 5. POUR TOUTES LES AUTRES ERREURS - AFFICHER DÉTAILS COMPLETS
            return {"success": False, "error": f"Erreur détaillée: {error_data}"}
            
        except Exception as e:
            return {"success": False, "error": f"Erreur inattendue: {str(e)}"}
    
    def handle_feedback_required(self, error_data: dict) -> dict:
        """NOUVEAU: Gérer spécifiquement les erreurs feedback_required"""
        try:
            feedback_message = error_data.get("feedback_message", "").lower()
            
            # Cas 1: Rate limit - "Réessayer plus tard"
            if "réessayer plus tard" in feedback_message or "limit" in feedback_message:
                return {
                    "success": False,
                    "error": "Votre compte a atteint la limite de cette action, veuillez réessayer plus tard",
                    "type": "rate_limit"
                }
            
            # Cas 2: Follow en attente - "Votre demande est en attente"
            elif "demande est en attente" in feedback_message or "examiner manuellement" in feedback_message:
                return {
                    "success": True,  # Considéré comme succès car le follow est en attente
                    "message": "Follow en attente de validation",
                    "type": "pending_follow"
                }
            
            # Cas 3: Autres feedback_required - afficher erreur détaillée
            else:
                return {
                    "success": False,
                    "error": f"Erreur détaillée: {error_data}",
                    "type": "other_feedback"
                }
                
        except Exception:
            return {
                "success": False,
                "error": f"Erreur détaillée: {error_data}",
                "type": "other_feedback"
            }
    
    def handle_challenge_response(self, response_text: str, response_data: dict = None) -> dict:
        """Gérer les réponses de challenge/checkpoint intelligemment"""
        try:
            challenge_url = ""
            checkpoint_url = ""
            
            if response_data:
                if "challenge" in response_data:
                    challenge_url = response_data["challenge"].get("url", "")
                elif "checkpoint_url" in response_data:
                    checkpoint_url = response_data.get("checkpoint_url", "")
            
            url_to_check = challenge_url or checkpoint_url
            
            # VÉRIFIER SUSPENDED/DISABLED DANS L'URL
            if "/accounts/suspended/" in url_to_check:
                return {"type": "suspended", "show_details": False}
            elif "/accounts/disabled/" in url_to_check:
                return {"type": "disabled", "show_details": False}
            elif "/challenge/" in url_to_check and "/accounts/suspended/" not in url_to_check and "/accounts/disabled/" not in url_to_check:
                return {"type": "general_challenge", "show_details": False, "can_retry": True, "challenge_data": response_data}
            elif "login_required" in response_text.lower() or "logged out" in response_text.lower():
                return {"type": "login_required", "show_details": False}
            else:
                return {"type": "other", "show_details": True}
                
        except Exception:
            return {"type": "other", "show_details": True}
    
    def solve_general_challenge(self, challenge_data: dict) -> bool:
        """Tenter de résoudre un challenge général automatiquement (SILENCIEUX)"""
        try:
            challenge = challenge_data.get("challenge", {})
            challenge_url = challenge.get("url", "")
            
            challenge_context = ""
            if "challenge_context=" in challenge_url:
                parsed_url = urllib.parse.urlparse(challenge_url)
                query_params = urllib.parse.parse_qs(parsed_url.query)
                challenge_context = query_params.get("challenge_context", [""])[0]
            
            user_id = self._get_user_id_from_session()
            
            challenge_payload = {
                "_uuid": self.auth.device_manager.device_info['device_uuid'],
                "has_follow_up_screens": "0",
                "bk_client_context": json.dumps({
                    "bloks_version": "e061cacfa956f06869fc2b678270bef1583d2480bf51f508321e64cfb5cc12bd",
                    "styles_id": "instagram"
                }),
                "challenge_context": challenge_context,
                "bloks_versioning_id": "e061cacfa956f06869fc2b678270bef1583d2480bf51f508321e64cfb5cc12bd"
            }
            
            challenge_headers = self._build_complete_headers(
                endpoint="challenge",
                friendly_name="Bloks: com.instagram.challenge.navigation.take_challenge"
            )
            
            payload_str = urllib.parse.urlencode(challenge_payload)
            
            response = self.auth.session.post(
                "https://b.i.instagram.com/api/v1/bloks/apps/com.instagram.challenge.navigation.take_challenge/",
                headers=challenge_headers,
                data=payload_str,
                timeout=15
            )
            
            return response.status_code == 200
                
        except Exception as e:
            return False
    
    def _execute_action_with_retry(self, action_type: str, *args, max_retries: int = 1) -> dict:
        """Exécuter une action avec retry automatique en cas de challenge général (SILENCIEUX)"""
        for attempt in range(max_retries + 1):
            
            # Exécuter l'action selon le type
            if action_type == "like":
                result = self._like_post_internal(args[0])
            elif action_type == "comment":
                result = self._comment_post_internal(args[0], args[1])
            elif action_type == "follow":
                result = self._follow_user_internal(args[0])
            elif action_type == "upload_story":
                result = self._upload_story_internal(args[0])
            elif action_type == "upload_post":
                result = self._upload_post_internal(args[0], args[1] if len(args) > 1 else "")
            elif action_type == "delete_post":
                result = self._delete_last_post_internal()
            else:
                return {"success": False, "error": "Type d'action non supporté"}
            
            # Si succès, retourner immédiatement
            if result["success"]:
                return result
            
            # Si échec, vérifier si c'est un challenge résolvable
            if "challenge_data" in result and attempt < max_retries:
                challenge_data = result["challenge_data"]
                
                # Tenter de résoudre le challenge (SILENCIEUX)
                if self.solve_general_challenge(challenge_data):
                    time.sleep(5)
                    continue
                else:
                    username = self._get_username_from_session()
                    return {"success": False, "error": f"Captcha détecté pour @{username}, veuillez le régler manuellement"}
            
            # Si c'est la deuxième tentative ET qu'il y a encore un challenge
            if attempt == max_retries and "challenge_data" in result:
                username = self._get_username_from_session()
                return {"success": False, "error": f"Captcha détecté pour @{username}, veuillez le régler manuellement"}
            
            # Si ce n'est pas un challenge mais une autre erreur, retourner l'erreur
            if "challenge_data" not in result:
                return result
        
        # Si on arrive ici, c'est qu'on a épuisé les tentatives sans succès
        username = self._get_username_from_session()
        return {"success": False, "error": f"Captcha détecté pour @{username}, veuillez le régler manuellement"}
    
    # ACTIONS PUBLIQUES AVEC RETRY AUTOMATIQUE
    def like_post(self, media_input: str) -> dict:
        """Liker un post Instagram avec retry automatique"""
        return self._execute_action_with_retry("like", media_input)
    
    def comment_post(self, media_input: str, comment_text: str) -> dict:
        """Commenter un post Instagram avec retry automatique"""
        return self._execute_action_with_retry("comment", media_input, comment_text)
    
    def follow_user(self, user_input: str) -> dict:
        """Suivre un utilisateur avec retry automatique"""
        return self._execute_action_with_retry("follow", user_input)
    
    def upload_story(self, image_path: str) -> dict:
        """Publier une story Instagram avec retry automatique"""
        return self._execute_action_with_retry("upload_story", image_path)
    
    def upload_post(self, image_path: str, caption: str = "") -> dict:
        """Publier un post Instagram avec retry automatique"""
        return self._execute_action_with_retry("upload_post", image_path, caption)
    
    def delete_last_post(self) -> dict:
        """Supprimer la dernière publication avec retry automatique"""
        return self._execute_action_with_retry("delete_post")
    
    # MÉTHODES INTERNES (appelées par _execute_action_with_retry)
    def _like_post_internal(self, media_input: str) -> dict:
        """Liker un post Instagram (méthode interne) - AVEC HEADERS COMPLETS"""
        try:
            # Utiliser l'API pour extraire media ID (SILENCIEUX)
            if self.api:
                media_id = self.api.extract_media_id_from_url(media_input)
            else:
                media_id = self._extract_media_id_basic(media_input)
            
            if not media_id:
                return {"success": False, "error": "Ce media a ete supprime"}
            
            user_id = self._get_user_id_from_session()
            if not user_id:
                return {"success": False, "error": "User ID non trouvé dans la session"}
            
            # Préparer données exactement comme script original
            like_data = {
                "is_2m_enabled": "false",
                "delivery_class": "organic", 
                "tap_source": "button",
                "media_id": media_id,
                "radio_type": self._get_radio_type(),
                "_uid": user_id,
                "_uuid": self._get_device_specific_headers()["x-ig-device-id"],
                "nav_chain": self._build_nav_chain("like"),
                "is_from_swipe": "false",
                "is_carousel_bumped_post": "false", 
                "floating_context_items": "[]",
                "container_module": "feed_contextual_profile",
                "feed_position": "0"
            }
            
            signed_body = InstagramEncryption.create_signed_body(like_data)
            
            # Headers complets avec toutes les données de session
            headers = self._build_complete_headers(
                endpoint="feed_contextual_profile",
                friendly_name=f"IgApi: media/{media_id}/like/"
            )
            
            response = self.auth.session.post(
                f"https://i.instagram.com/api/v1/media/{media_id}/like/",
                headers=headers,
                data={"signed_body": signed_body, "d": "0"},
                timeout=10
            )
            
            if response.status_code == 200:
                parsed_data = InstagramEncryption.safe_parse_json(response)
                
                if InstagramEncryption.is_success_response(response, parsed_data):
                    return {"success": True, "data": parsed_data}
                else:
                    return self.handle_action_error(response.status_code, parsed_data, 
                                                 InstagramEncryption.safe_decode_response(response))
            else:
                if response.status_code == 400:
                    parsed_data = InstagramEncryption.safe_parse_json(response)
                    return self.handle_action_error(response.status_code, parsed_data, 
                                                 InstagramEncryption.safe_decode_response(response))
                
                return self.handle_http_error(response.status_code, 
                                            InstagramEncryption.safe_decode_response(response))
                
        except Exception as e:
            return {"success": False, "error": "Ce media a ete supprime"}
    
    def _comment_post_internal(self, media_input: str, comment_text: str) -> dict:
        """Commenter un post Instagram (méthode interne) - AVEC PROCESS COMPLET CORRIGÉ"""
        try:
            if self.api:
                media_id = self.api.extract_media_id_from_url(media_input)
            else:
                media_id = self._extract_media_id_basic(media_input)
            
            if not media_id:
                return {"success": False, "error": "Ce média a été supprimé"}
            
            user_id = self._get_user_id_from_session()
            if not user_id:
                return {"success": False, "error": "User ID non trouvé dans la session"}
            
            # ÉTAPE 1: Check offensive comment (OBLIGATOIRE)
            comment_session_id = str(uuid.uuid4())
            
            check_data = {
                "media_id": media_id,
                "_uid": user_id,
                "comment_session_id": comment_session_id,
                "_uuid": self._get_device_specific_headers()["x-ig-device-id"],
                "comment_text": comment_text
            }
            
            signed_body_check = InstagramEncryption.create_signed_body(check_data)
            
            headers_check = self._build_complete_headers(
                endpoint="comments_v2_feed_contextual_profile",
                friendly_name="IgApi: media/comment/check_offensive_comment/"
            )
            
            # VÉRIFICATION OBLIGATOIRE
            check_response = self.auth.session.post(
                "https://i-fallback.instagram.com/api/v1/media/comment/check_offensive_comment/",
                headers=headers_check,
                data={"signed_body": signed_body_check},
                timeout=10
            )
            
            # ARRÊTER SI CHECK ÉCHOUE
            if check_response.status_code != 200:
                return {"success": False, "error": "Échec vérification commentaire"}
            
            try:
                check_result = check_response.json()
                if check_result.get("is_offensive", False):
                    return {"success": False, "error": "Commentaire détecté comme offensant"}
                if check_result.get("status") != "ok":
                    return {"success": False, "error": "Vérification commentaire échouée"}
            except:
                return {"success": False, "error": "Réponse check invalide"}
            
            # ÉTAPE 2: Post comment avec données exactes
            current_time = int(time.time())
            comment_creation_key = str(uuid.uuid4())
            
            # Calculer user_breadcrumb réel (timing utilisateur)
            breadcrumb_time = current_time * 1000 + 495
            user_breadcrumb = self._generate_user_breadcrumb(comment_text, breadcrumb_time)
            
            comment_data = {
                "include_media_code": "true",
                "user_breadcrumb": user_breadcrumb,
                "starting_clips_media_id": "null",
                "comment_creation_key": comment_creation_key,
                "delivery_class": "organic",
                "idempotence_token": comment_creation_key,  # Même que creation_key
                "client_position": "0",
                "carousel_child_mentions": "[]",
                "include_e2ee_mentioned_user_list": "true",
                "include_carousel_child_mentions": "false",
                "is_from_carousel_child_thread": "false",
                "carousel_index": "-1",
                "radio_type": self._get_radio_type(),
                "_uid": user_id,
                "is_text_app_xpost_attempt": "false",
                "_uuid": self._get_device_specific_headers()["x-ig-device-id"],
                "nav_chain": self._build_nav_chain("comment"),
                "comment_text": comment_text,
                "recs_ix": "-1",
                "is_carousel_bumped_post": "false",
                "floating_context_items": "[]",
                "container_module": "comments_v2_feed_contextual_profile",
                "feed_position": "0",
                "ranking_session_id": str(uuid.uuid4())
            }
            
            signed_body = InstagramEncryption.create_signed_body(comment_data)
            
            headers = self._build_complete_headers(
                endpoint="comments_v2_feed_contextual_profile",
                friendly_name=f"IgApi: media/{media_id}/comment/"
            )
            
            # UTILISER i-fallback.instagram.com comme dans l'exemple
            response = self.auth.session.post(
                f"https://i-fallback.instagram.com/api/v1/media/{media_id}/comment/",
                headers=headers,
                data={"signed_body": signed_body},
                timeout=10
            )
            
            if response.status_code == 200:
                parsed_data = InstagramEncryption.safe_parse_json(response)
                
                if InstagramEncryption.is_success_response(response, parsed_data):
                    return {"success": True, "data": parsed_data}
                else:
                    return self.handle_action_error(response.status_code, parsed_data, 
                                                 InstagramEncryption.safe_decode_response(response))
            else:
                if response.status_code == 400:
                    parsed_data = InstagramEncryption.safe_parse_json(response)
                    return self.handle_action_error(response.status_code, parsed_data, 
                                                 InstagramEncryption.safe_decode_response(response))
                
                return self.handle_http_error(response.status_code, 
                                            InstagramEncryption.safe_decode_response(response))
                
        except Exception as e:
            return {"success": False, "error": f"Erreur commentaire: {str(e)}"}
    
    def _generate_user_breadcrumb(self, comment_text: str, timestamp: int) -> str:
        """Générer user_breadcrumb réaliste pour commentaire"""
        import base64
        
        try:
            # Simuler timing de frappe (longueur texte * délai moyen)
            text_length = len(comment_text)
            typing_time = text_length * random.randint(80, 150)  # ms par caractère
            
            # Données de breadcrumb (simulation timing réel)
            breadcrumb_data = f"2CtNlMTofPYazH1tAZYSrseuaWwzOznZW4XAcSF9W74=\\nMTAgNTY4OCAwIDE3NTcxMzM2NzY0OTU=\\n"
            
            # Alternative : générer dynamiquement
            base_data = base64.b64encode(f"timing_{timestamp}_{typing_time}".encode()).decode()
            timing_data = base64.b64encode(f"10 5688 0 {timestamp}".encode()).decode()
            
            return f"{base_data}\\n{timing_data}\\n"
            
        except:
            # Fallback avec timestamp actuel
            return f"2CtNlMTofPYazH1tAZYSrseuaWwzOznZW4XAcSF9W74=\\nMTAgNTY4OCAwIDE3NTcxMzM2NzY0OTU=\\n"
    
    def _follow_user_internal(self, user_input: str) -> dict:
        """Suivre un utilisateur (méthode interne) - AVEC HEADERS COMPLETS"""
        try:
            if self.api:
                user_id = self.api.extract_user_id_from_url(user_input)
            else:
                user_id = self._extract_user_id_basic(user_input)
            
            # Si échec d'extraction, chercher username similaire EXACTEMENT comme script original
            if not user_id:
                # Extraire username depuis l'URL
                username_match = re.search(r'instagram\.com/([^/?]+)', user_input)
                if username_match:
                    target_username = username_match.group(1).replace('@', '').strip()
                    
                    # Recherche silencieuse d'utilisateurs similaires EXACTEMENT comme script original
                    user_id = self._search_similar_username(target_username)
                
                if not user_id:
                    return {"success": False, "error": "Utilisateur introuvable"}
            
            current_user_id = self._get_user_id_from_session()
            if not current_user_id:
                return {"success": False, "error": "User ID non trouvé dans la session"}
            
            # DONNÉES EXACTEMENT comme l'exemple
            follow_data = {
                "include_follow_friction_check": "1",
                "user_id": user_id,
                "radio_type": self._get_radio_type(),
                "_uid": current_user_id,
                "device_id": self._get_device_specific_headers()["x-ig-android-id"],
                "_uuid": self._get_device_specific_headers()["x-ig-device-id"],
                "nav_chain": self._build_nav_chain("follow"),
                "container_module": "profile"
            }
            
            signed_body = InstagramEncryption.create_signed_body(follow_data)
            
            # Headers complets avec toutes les données de session
            headers = self._build_complete_headers(
                endpoint="profile",
                friendly_name=f"IgApi: friendships/create/{user_id}/"
            )
            
            response = self.auth.session.post(
                f"https://i.instagram.com/api/v1/friendships/create/{user_id}/",
                headers=headers,
                data={"signed_body": signed_body},
                timeout=10
            )
            
            if response.status_code == 200:
                # UTILISER LE DÉCODAGE UNIFIÉ
                parsed_data = InstagramEncryption.safe_parse_json(response)
                
                if InstagramEncryption.is_success_response(response, parsed_data):
                    return {"success": True, "data": parsed_data}
                else:
                    return self.handle_action_error(response.status_code, parsed_data, 
                                                 InstagramEncryption.safe_decode_response(response))
            else:
                if response.status_code == 400:
                    parsed_data = InstagramEncryption.safe_parse_json(response)
                    return self.handle_action_error(response.status_code, parsed_data, 
                                                 InstagramEncryption.safe_decode_response(response))
                
                return self.handle_http_error(response.status_code, 
                                            InstagramEncryption.safe_decode_response(response))
                
        except Exception as e:
            return self.handle_media_error("Utilisateur introuvable")
    
    def _search_similar_username(self, target_username: str) -> str:
        """Rechercher username similaire EXACTEMENT comme script original"""
        try:
            if not self.api:
                return None
            
            headers = self._build_complete_headers(
                endpoint="user_search",
                friendly_name="IgApi: users/search/"
            )
            
            search_params = {
                "timezone_offset": str(self.session_data.get("timezone_offset", 10800)),
                "q": target_username,
                "count": "20"
            }
            
            response = self.auth.session.get(
                "https://i.instagram.com/api/v1/users/search/",
                params=search_params,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get("status") == "ok" and "users" in data:
                        users = data["users"]
                        
                        # Recherche exacte d'abord
                        for user in users:
                            username = user.get("username", "").lower()
                            if username == target_username.lower():
                                return str(user.get("pk"))
                        
                        # Si pas trouvé exact, recherche similaire EXACTEMENT comme script original
                        target_lower = target_username.lower()
                        best_matches = []
                        
                        # Recherche par préfixe
                        for user in users:
                            username = user.get("username", "").lower()
                            if username.startswith(target_lower) and username != target_lower:
                                best_matches.append((user.get("pk"), username))
                        
                        if best_matches:
                            best_matches.sort(key=lambda x: len(x[1]))
                            return str(best_matches[0][0])
                        
                        # Recherche par parties de nom EXACTEMENT comme script original
                        for user in users:
                            username = user.get("username", "").lower()
                            if any(part in username for part in target_lower.split('_') + target_lower.split('.') if len(part) > 2):
                                return str(user.get("pk"))
                        
                except Exception:
                    pass
            
            return None
            
        except Exception:
            return None
    
    def _upload_story_internal(self, image_path: str) -> dict:
        """Publier une story Instagram (méthode interne)"""
        try:
            if not os.path.exists(image_path):
                return {"success": False, "error": f"Image non trouvée: {image_path}"}
            
            image_data, image_size, error = MediaProcessor.prepare_image_for_instagram(image_path, story_mode=True)
            if error:
                return {"success": False, "error": error}
            
            upload_id = MediaProcessor.generate_upload_id()
            user_id = self._get_user_id_from_session()
            
            if not user_id:
                return {"success": False, "error": "User ID non trouvé"}
            
            upload_result = self._upload_image_data(image_data, upload_id, story_mode=True)
            if not upload_result["success"]:
                return upload_result
            
            story_result = self._configure_story(upload_id, image_size, user_id)
            return story_result
            
        except Exception as e:
            return {"success": False, "error": f"Erreur upload story: {str(e)}"}
    
    def _upload_post_internal(self, image_path: str, caption: str = "") -> dict:
        """Publier un post Instagram (méthode interne)"""
        try:
            if not os.path.exists(image_path):
                return {"success": False, "error": f"Image non trouvée: {image_path}"}
            
            image_data, image_size, error = MediaProcessor.prepare_image_for_instagram(image_path, story_mode=False)
            if error:
                return {"success": False, "error": error}
            
            upload_id = MediaProcessor.generate_upload_id()
            user_id = self._get_user_id_from_session()
            
            if not user_id:
                return {"success": False, "error": "User ID non trouvé"}
            
            upload_result = self._upload_image_data(image_data, upload_id, story_mode=False)
            if not upload_result["success"]:
                return upload_result
            
            post_result = self._configure_post(upload_id, image_size, user_id, caption)
            if post_result["success"]:
                # Mettre à jour PDQ hash
                self._update_media_pdq_hash(upload_id, image_data, user_id)
            
            return post_result
            
        except Exception as e:
            return {"success": False, "error": f"Erreur upload post: {str(e)}"}
    
    def _delete_last_post_internal(self) -> dict:
        """Supprimer la dernière publication (méthode interne)"""
        try:
            
            if not self.api:
                return {"success": False, "error": "API non initialisée"}
            
            media_list = self.api.get_own_media_list(count=1)
            
            if not media_list:
                return {"success": False, "error": "Aucune publication trouvée"}
            
            latest_media = media_list[0]
            media_id = latest_media["id"]
            
            return self._delete_media(media_id)
            
        except Exception as e:
            return {"success": False, "error": f"Erreur suppression: {str(e)}"}
    
    # MÉTHODES UTILITAIRES INTERNES
    def handle_http_error(self, response_status: int, response_text: str) -> dict:
        """Gérer les erreurs HTTP avec messages simplifiés"""
        try:
            username = self._get_username_from_session()
            
            if response_status == 403:
                if "login_required" in response_text.lower():
                    return {
                        "success": False,
                        "error": f"Le compte @{username} est déconnecté, veuillez vous reconnecter"
                    }
            
            print(f"❌ Erreur HTTP {response_status}: {response_text}")
            return {"success": False, "error": f"HTTP {response_status}: {response_text}"}
            
        except Exception as e:
            print(f"❌ Erreur HTTP inattendue: {str(e)}")
            return {"success": False, "error": f"Erreur HTTP inattendue: {str(e)}"}
    
    def handle_media_error(self, error_message: str) -> dict:
        """Gérer les erreurs spécifiques aux médias"""
        if "deleted" in error_message.lower() or "supprime" in error_message.lower():
            return {"success": False, "error": "Ce media a été supprimé"}
        else:
            print(f"❌ {error_message}")
            return {"success": False, "error": error_message}
    
    def _extract_media_id_basic(self, url: str) -> str:
        """Extraction basique media ID (fallback)"""
        patterns = [
            r'/p/([A-Za-z0-9_-]+)/',
            r'/reel/([A-Za-z0-9_-]+)/',
            r'media_id=([0-9]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                code = match.group(1)
                if code.isdigit():
                    return code
                return str(random.randint(1000000000000000000, 9999999999999999999))
        
        return None
    
    def _extract_user_id_basic(self, url: str) -> str:
        """Extraction basique user ID (fallback)"""
        match = re.search(r'instagram\.com/([^/?]+)', url)
        if match:
            username = match.group(1).replace('@', '')
            return str(random.randint(1000000000, 9999999999))
        return None
    
    def get_account_info(self) -> dict:
        """Récupérer informations du compte connecté"""
        try:
            user_id = self._get_user_id_from_session()
            if not user_id or not self.api:
                return {"success": False, "error": "Compte non connecté"}
            
            user_info = self.api.get_user_info(user_id)
            
            if user_info:
                account_status = "Privé" if user_info.get("is_private") else "Public"
                
                info = {
                    "success": True,
                    "data": {
                        "username": user_info.get("username", ""),
                        "full_name": user_info.get("full_name", ""),
                        "is_private": user_info.get("is_private", False),
                        "account_status": account_status,
                        "is_verified": user_info.get("is_verified", False),
                        "is_business": user_info.get("is_business", False),
                        "follower_count": user_info.get("follower_count", 0),
                        "following_count": user_info.get("following_count", 0),
                        "media_count": user_info.get("media_count", 0),
                        "biography": user_info.get("biography", "")
                    }
                }
                
                return info
            else:
                return {"success": False, "error": "Impossible de récupérer les informations"}
                
        except Exception as e:
            return {"success": False, "error": f"Erreur: {str(e)}"}
    
    def toggle_account_privacy(self) -> dict:
        """Changer la confidentialité du compte (public <-> privé)"""
        try:
            user_id = self._get_user_id_from_session()
            if not user_id:
                return {"success": False, "error": "User ID non trouvé"}
            
            account_info = self.get_account_info()
            if not account_info["success"]:
                return account_info
            
            current_private = account_info["data"]["is_private"]
            action = "set_public" if current_private else "set_private"
            
            privacy_data = {
                "_uid": user_id,
                "_uuid": self._get_device_specific_headers()["x-ig-device-id"]
            }
            
            signed_body = InstagramEncryption.create_signed_body(privacy_data)
            
            headers = self._build_complete_headers(
                endpoint="account_privacy",
                friendly_name=f"IgApi: accounts/{action}/"
            )
            
            response = self.auth.session.post(
                f"https://i.instagram.com/api/v1/accounts/{action}/",
                headers=headers,
                data={"signed_body": signed_body},
                timeout=10
            )
            
            if response.status_code == 200:
                parsed_data = InstagramEncryption.safe_parse_json(response)
                
                if InstagramEncryption.is_success_response(response, parsed_data):
                    new_status = "Public" if action == "set_public" else "Privé"
                    return {"success": True, "data": {"new_status": new_status}}
                else:
                    print(f"❌ Erreur changement privacy: {parsed_data}")
                    return {"success": False, "error": parsed_data}
            else:
                if response.status_code == 400:
                    parsed_data = InstagramEncryption.safe_parse_json(response)
                    return self.handle_action_error(response.status_code, parsed_data, 
                                                 InstagramEncryption.safe_decode_response(response))
                
                return self.handle_http_error(response.status_code, 
                                            InstagramEncryption.safe_decode_response(response))
                
        except Exception as e:
            return {"success": False, "error": f"Erreur: {str(e)}"}
    
    # MÉTHODES D'UPLOAD ET CONFIGURATION
    def _upload_image_data(self, image_data: bytes, upload_id: str, story_mode: bool = False) -> dict:
        """Upload des données d'image vers Instagram avec headers complets"""
        try:
            user_id = self._get_user_id_from_session()
            
            # Headers complets pour upload
            headers = self._build_complete_headers(
                endpoint="upload",
                friendly_name="IgApi: rupload_igphoto"
            )
            
            # Modifier content-type pour upload
            headers["content-type"] = "application/octet-stream"
            headers["offset"] = "0"
            headers["x-entity-length"] = str(len(image_data))
            headers["x-entity-name"] = f"{upload_id}_0_{random.randint(1000000000, 9999999999)}"
            headers["x-entity-type"] = "image/jpeg"
            
            share_type = "stories" if story_mode else "feed"
            
            upload_params = {
                "upload_id": upload_id,
                "session_id": upload_id,
                "media_type": "1",
                "upload_engine_config_enum": "0",
                "share_type": share_type,
                "is_optimistic_upload": "false",
                "image_compression": '{"lib_name":"libjpeg","lib_version":"9d","quality":"90","original_width":720,"original_height":1280}' if story_mode else '{"lib_name":"libjpeg","lib_version":"9d","quality":"90","original_width":1080,"original_height":1080}',
                "xsharing_user_ids": "[]",
                "retry_context": '{"num_reupload":0,"num_step_manual_retry":0,"num_step_auto_retry":0}'
            }
            
            headers["x-instagram-rupload-params"] = json.dumps(upload_params, separators=(',', ':'))
            
            response = self.auth.session.post(
                f"https://i.instagram.com/rupload_igphoto/{upload_id}_0_{random.randint(1000000000, 9999999999)}",
                headers=headers,
                data=image_data,
                timeout=30
            )
            
            if response.status_code == 200:
                return {"success": True, "data": "Upload réussi"}
            else:
                if response.status_code == 400:
                    parsed_data = InstagramEncryption.safe_parse_json(response)
                    return self.handle_action_error(response.status_code, parsed_data, 
                                                 InstagramEncryption.safe_decode_response(response))
                
                return self.handle_http_error(response.status_code, 
                                            InstagramEncryption.safe_decode_response(response))
                
        except Exception as e:
            return {"success": False, "error": f"Erreur upload image: {str(e)}"}
    
    def _configure_story(self, upload_id: str, image_size: tuple, user_id: str) -> dict:
        """Configurer la story après upload avec headers complets"""
        try:
            width, height = image_size
            
            # Récupérer device settings depuis session
            device_settings = self.session_data.get("device_settings", {})
            uuids = self.session_data.get("uuids", {})
            
            story_data = {
                "supported_capabilities_new": '[{"name":"SUPPORTED_SDK_VERSIONS","value":"149.0,150.0,151.0,152.0,153.0,154.0,155.0,156.0,157.0,158.0,159.0,160.0,161.0,162.0,163.0,164.0,165.0,166.0,167.0,168.0,169.0,170.0,171.0,172.0,173.0,174.0,175.0,176.0,177.0,178.0,179.0,180.0,181.0,182.0,183.0,184.0,185.0,186.0,187.0,188.0,189.0,190.0,191.0,192.0,193.0,194.0,195.0,196.0,197.0,198.0,199.0,200.0,201.0,202.0"},{"name":"SUPPORTED_BETA_SDK_VERSIONS","value":"182.0-beta,183.0-beta,184.0-beta,185.0-beta,186.0-beta,187.0-beta,188.0-beta,189.0-beta,190.0-beta,191.0-beta,192.0-beta,193.0-beta,194.0-beta,195.0-beta,196.0-beta,197.0-beta,198.0-beta,199.0-beta,200.0-beta,201.0-beta,202.0-beta"},{"name":"FACE_TRACKER_VERSION","value":"14"},{"name":"segmentation","value":"segmentation_enabled"},{"name":"COMPRESSION","value":"ETC2_COMPRESSION"},{"name":"gyroscope","value":"gyroscope_enabled"}]',
                "allow_multi_configures": "1",
                "has_camera_metadata": "0",
                "camera_entry_point": "11",
                "original_media_type": "1",
                "camera_session_id": str(uuid.uuid4()),
                "original_height": str(height),
                "include_e2ee_mentioned_user_list": "1",
                "hide_from_profile_grid": "false",
                "scene_capture_type": "",
                "timezone_offset": str(self.session_data.get("timezone_offset", 10800)),
                "client_shared_at": str(int(time.time())),
                "media_folder": "Screenshots",
                "configure_mode": "1",
                "source_type": "4",
                "camera_position": "unknown",
                "_uid": user_id,
                "device_id": self._get_device_specific_headers()["x-ig-android-id"],
                "composition_id": str(uuid.uuid4()),
                "_uuid": self._get_device_specific_headers()["x-ig-device-id"],
                "creation_tool_info": "[]",
                "creation_surface": "camera",
                "nav_chain": f"MainFeedFragment:feed_timeline:1:cold_start:{int(time.time() * 1000)}:::,QuickCaptureFragment:stories_precapture_camera:25:your_story_placeholder:{int(time.time() * 1000)}:::,PrivateStoryShareSheetFragment:private_stories_share_sheet:28:button:{int(time.time() * 1000)}::",
                "imported_taken_at": str(int(time.time()) - 3600),
                "capture_type": "normal",
                "audience": "default",
                "upload_id": upload_id,
                "client_timestamp": str(int(time.time())),
                "bottom_camera_dial_selected": "2",
                "publish_id": "1",
                "original_width": str(width),
                "media_transformation_info": f'{{"width":"{width}","height":"{height}","x_transform":"0","y_transform":"0","zoom":"1.0","rotation":"0.0","background_coverage":"0.0"}}',
                "edits": {
                    "filter_type": 0,
                    "filter_strength": 0.5,
                    "crop_original_size": [float(width), float(height)]
                },
                "extra": {
                    "source_width": width,
                    "source_height": height
                },
                "device": {
                    "manufacturer": device_settings.get('manufacturer', 'samsung'),
                    "model": device_settings.get('model', 'SM-G991B'),
                    "android_version": device_settings.get('android_version', 32),
                    "android_release": device_settings.get('android_release', '12')
                }
            }
            
            signed_body = InstagramEncryption.create_signed_body(story_data)
            
            headers = self._build_complete_headers(
                endpoint="story_configure",
                friendly_name="IgApi: media/configure_to_story/"
            )
            
            response = self.auth.session.post(
                "https://i.instagram.com/api/v1/media/configure_to_story/",
                headers=headers,
                data={"signed_body": signed_body},
                timeout=15
            )
            
            if response.status_code == 200:
                parsed_data = InstagramEncryption.safe_parse_json(response)
                
                if InstagramEncryption.is_success_response(response, parsed_data):
                    return {"success": True, "data": parsed_data}
                else:
                    print(f"❌ Erreur configuration story: {parsed_data}")
                    return {"success": False, "error": parsed_data}
            else:
                if response.status_code == 400:
                    parsed_data = InstagramEncryption.safe_parse_json(response)
                    return self.handle_action_error(response.status_code, parsed_data, 
                                                 InstagramEncryption.safe_decode_response(response))
                
                return self.handle_http_error(response.status_code, 
                                            InstagramEncryption.safe_decode_response(response))
                
        except Exception as e:
            return {"success": False, "error": f"Erreur configuration story: {str(e)}"}
    
    def _configure_post(self, upload_id: str, image_size: tuple, user_id: str, caption: str = "") -> dict:
        """Configurer le post après upload avec headers complets"""
        try:
            width, height = image_size
            
            # Récupérer device settings depuis session
            device_settings = self.session_data.get("device_settings", {})
            
            post_data = {
                "app_attribution_android_namespace": "",
                "camera_entry_point": "360",
                "camera_session_id": str(uuid.uuid4()),
                "original_height": str(height),
                "include_e2ee_mentioned_user_list": "1",
                "hide_from_profile_grid": "false",
                "scene_capture_type": "",
                "timezone_offset": str(self.session_data.get("timezone_offset", 10800)),
                "source_type": "4",
                "_uid": user_id,
                "device_id": self._get_device_specific_headers()["x-ig-android-id"],
                "_uuid": self._get_device_specific_headers()["x-ig-device-id"],
                "creation_tool_info": "[]",
                "creation_logger_session_id": str(uuid.uuid4()),
                "nav_chain": f"MainFeedFragment:feed_timeline:1:cold_start:{int(time.time() * 1000)}:::,GalleryPickerFragment:gallery_picker:50:camera_tab_bar:{int(time.time() * 1000)}:::,PhotoFilterFragment:photo_filter:51:button:{int(time.time() * 1000)}::",
                "caption": caption,
                "audience": "default",
                "upload_id": upload_id,
                "bottom_camera_dial_selected": "11",
                "publish_id": "1",
                "original_width": str(width),
                "edits": {
                    "filter_type": 0,
                    "filter_strength": 1.0,
                    "crop_original_size": [float(width), float(height)],
                    "crop_center": [-0.002429657, -0.06649882],
                    "crop_zoom": 1.782934
                },
                "extra": {
                    "source_width": width,
                    "source_height": height
                },
                "device": {
                    "manufacturer": device_settings.get('manufacturer', 'samsung'),
                    "model": device_settings.get('model', 'SM-G991B'),
                    "android_version": device_settings.get('android_version', 32),
                    "android_release": device_settings.get('android_release', '12')
                },
                "overlay_data": []
            }
            
            signed_body = InstagramEncryption.create_signed_body(post_data)
            
            headers = self._build_complete_headers(
                endpoint="post_configure",
                friendly_name="IgApi: media/configure/"
            )
            
            response = self.auth.session.post(
                "https://i.instagram.com/api/v1/media/configure/",
                headers=headers,
                data={"signed_body": signed_body},
                timeout=15
            )
            
            if response.status_code == 200:
                parsed_data = InstagramEncryption.safe_parse_json(response)
                
                if InstagramEncryption.is_success_response(response, parsed_data):
                    return {"success": True, "data": parsed_data}
                else:
                    print(f"❌ Erreur configuration post: {parsed_data}")
                    return {"success": False, "error": parsed_data}
            else:
                if response.status_code == 400:
                    parsed_data = InstagramEncryption.safe_parse_json(response)
                    return self.handle_action_error(response.status_code, parsed_data, 
                                                 InstagramEncryption.safe_decode_response(response))
                
                return self.handle_http_error(response.status_code, 
                                            InstagramEncryption.safe_decode_response(response))
                
        except Exception as e:
            return {"success": False, "error": f"Erreur configuration post: {str(e)}"}
    
    def _update_media_pdq_hash(self, upload_id: str, image_data: bytes, user_id: str) -> dict:
        """Mettre à jour le média avec le hash PDQ"""
        try:
            pdq_hash = MediaProcessor.generate_pdq_hash(image_data)
            
            pdq_data = {
                "pdq_hash_info": f'[{{"pdq_hash":"{pdq_hash}","frame_time":0}}]',
                "_uid": user_id,
                "_uuid": self._get_device_specific_headers()["x-ig-device-id"],
                "upload_id": upload_id
            }
            
            signed_body = InstagramEncryption.create_signed_body(pdq_data)
            
            headers = self._build_complete_headers(
                endpoint="pdq_update",
                friendly_name="IgApi: media/update_media_with_pdq_hash_info/"
            )
            
            response = self.auth.session.post(
                "https://i.instagram.com/api/v1/media/update_media_with_pdq_hash_info/",
                headers=headers,
                data={"signed_body": signed_body},
                timeout=10
            )
            
            if response.status_code == 200:
                return {"success": True}
            else:
                print(f"⚠️ Erreur PDQ hash: {response.status_code}")
                return {"success": False, "error": f"PDQ hash error: {response.status_code}"}
                
        except Exception as e:
            print(f"⚠️ Erreur PDQ hash: {str(e)}")
            return {"success": False, "error": f"PDQ hash error: {str(e)}"}
    
    def _delete_media(self, media_id: str) -> dict:
        """Supprimer un média par son ID - AVEC HEADERS COMPLETS"""
        try:
            user_id = self._get_user_id_from_session()
            
            delete_data = {
                "igtv_feed_preview": "false",
                "media_id": media_id,
                "_uid": user_id,
                "_uuid": self._get_device_specific_headers()["x-ig-device-id"]
            }
            
            signed_body = InstagramEncryption.create_signed_body(delete_data)
            
            headers = self._build_complete_headers(
                endpoint="media_delete",
                friendly_name=f"IgApi: media/{media_id}/delete/?media_type=PHOTO"
            )
            
            response = self.auth.session.post(
                f"https://i.instagram.com/api/v1/media/{media_id}/delete/?media_type=PHOTO",
                headers=headers,
                data={"signed_body": signed_body},
                timeout=10
            )
            
            if response.status_code == 200:
                parsed_data = InstagramEncryption.safe_parse_json(response)
                
                # Vérifier spécifiquement les indicateurs de suppression
                if (isinstance(parsed_data, dict) and 
                    (parsed_data.get("did_delete") == True or 
                     InstagramEncryption.is_success_response(response, parsed_data))):
                    return {"success": True, "data": parsed_data}
                else:
                    print(f"❌ Erreur suppression: {parsed_data}")
                    return {"success": False, "error": parsed_data}
            else:
                if response.status_code == 400:
                    parsed_data = InstagramEncryption.safe_parse_json(response)
                    return self.handle_action_error(response.status_code, parsed_data, 
                                                 InstagramEncryption.safe_decode_response(response))
                
                return self.handle_http_error(response.status_code, 
                                            InstagramEncryption.safe_decode_response(response))
                
        except Exception as e:
            return {"success": False, "error": f"Erreur suppression: {str(e)}"}
    
    # MÉTHODES SUPPLÉMENTAIRES POUR COMPATIBILITÉ COMPLÈTE
    def get_media_info(self, media_input: str) -> dict:
        """Récupérer informations d'un média"""
        try:
            if self.api:
                media_id = self.api.extract_media_id_from_url(media_input)
            else:
                media_id = self._extract_media_id_basic(media_input)
            
            if not media_id:
                return {"success": False, "error": "Media ID non trouvé"}
            
            headers = self._build_complete_headers(
                endpoint="media_info",
                friendly_name=f"IgApi: media/{media_id}/info/"
            )
            
            response = self.auth.session.get(
                f"https://i.instagram.com/api/v1/media/{media_id}/info/",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                parsed_data = InstagramEncryption.safe_parse_json(response)
                
                if InstagramEncryption.is_success_response(response, parsed_data):
                    items = parsed_data.get("items", [])
                    if items:
                        media = items[0]
                        return {
                            "success": True,
                            "data": {
                                "id": media.get("id"),
                                "code": media.get("code"),
                                "media_type": media.get("media_type"),
                                "like_count": media.get("like_count", 0),
                                "comment_count": media.get("comment_count", 0),
                                "caption": media.get("caption", {}).get("text", "") if media.get("caption") else "",
                                "owner": media.get("user", {})
                            }
                        }
                else:
                    return self.handle_action_error(response.status_code, parsed_data,
                                                 InstagramEncryption.safe_decode_response(response))
            else:
                return self.handle_http_error(response.status_code, 
                                            InstagramEncryption.safe_decode_response(response))
                
        except Exception as e:
            return {"success": False, "error": f"Erreur: {str(e)}"}
    
    def get_user_media_list(self, user_input: str, count: int = 20) -> dict:
        """Récupérer la liste des médias d'un utilisateur"""
        try:
            if self.api:
                user_id = self.api.extract_user_id_from_url(user_input)
            else:
                user_id = self._extract_user_id_basic(user_input)
            
            if not user_id:
                return {"success": False, "error": "User ID non trouvé"}
            
            headers = self._build_complete_headers(
                endpoint="user_feed",
                friendly_name=f"IgApi: feed/user/{user_id}/"
            )
            
            params = {
                "count": str(count),
                "max_id": ""
            }
            
            response = self.auth.session.get(
                f"https://i.instagram.com/api/v1/feed/user/{user_id}/",
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                parsed_data = InstagramEncryption.safe_parse_json(response)
                
                if InstagramEncryption.is_success_response(response, parsed_data):
                    items = parsed_data.get("items", [])
                    media_list = []
                    
                    for item in items:
                        media_info = {
                            "id": item.get("id"),
                            "code": item.get("code"),
                            "media_type": item.get("media_type"),
                            "taken_at": item.get("taken_at"),
                            "like_count": item.get("like_count", 0),
                            "comment_count": item.get("comment_count", 0)
                        }
                        
                        caption_info = item.get("caption")
                        if caption_info:
                            media_info["caption"] = caption_info.get("text", "")
                        else:
                            media_info["caption"] = ""
                        
                        media_list.append(media_info)
                    
                    return {"success": True, "data": media_list}
                else:
                    return self.handle_action_error(response.status_code, parsed_data,
                                                 InstagramEncryption.safe_decode_response(response))
            else:
                return self.handle_http_error(response.status_code, 
                                            InstagramEncryption.safe_decode_response(response))
                
        except Exception as e:
            return {"success": False, "error": f"Erreur: {str(e)}"}
    
    def get_user_info(self, user_input: str) -> dict:
        """Récupérer informations d'un utilisateur"""
        try:
            if self.api:
                user_id = self.api.extract_user_id_from_url(user_input)
            else:
                user_id = self._extract_user_id_basic(user_input)
            
            if not user_id:
                return {"success": False, "error": "User ID non trouvé"}
            
            if self.api:
                user_info = self.api.get_user_info(user_id)
                
                if user_info:
                    account_status = "Privé" if user_info.get("is_private") else "Public"
                    
                    info = {
                        "success": True,
                        "data": {
                            "user_id": str(user_info.get("pk", user_id)),
                            "username": user_info.get("username", ""),
                            "full_name": user_info.get("full_name", ""),
                            "is_private": user_info.get("is_private", False),
                            "account_status": account_status,
                            "is_verified": user_info.get("is_verified", False),
                            "is_business": user_info.get("is_business", False),
                            "follower_count": user_info.get("follower_count", 0),
                            "following_count": user_info.get("following_count", 0),
                            "media_count": user_info.get("media_count", 0),
                            "biography": user_info.get("biography", ""),
                            "profile_pic_url": user_info.get("profile_pic_url", "")
                        }
                    }
                    
                    return info
                else:
                    return {"success": False, "error": "Impossible de récupérer les informations"}
            else:
                return {"success": False, "error": "API non initialisée"}
                
        except Exception as e:
            return {"success": False, "error": f"Erreur: {str(e)}"}
    
    def unlike_post(self, media_input: str) -> dict:
        """Unliker un post Instagram"""
        try:
            if self.api:
                media_id = self.api.extract_media_id_from_url(media_input)
            else:
                media_id = self._extract_media_id_basic(media_input)
            
            if not media_id:
                return {"success": False, "error": "Ce media a ete supprime"}
            
            user_id = self._get_user_id_from_session()
            if not user_id:
                return {"success": False, "error": "User ID non trouvé dans la session"}
            
            unlike_data = {
                "media_id": media_id,
                "radio_type": self._get_radio_type(),
                "_uid": user_id,
                "_uuid": self._get_device_specific_headers()["x-ig-device-id"],
                "nav_chain": self._build_nav_chain("like"),
                "container_module": "feed_timeline"
            }
            
            signed_body = InstagramEncryption.create_signed_body(unlike_data)
            
            headers = self._build_complete_headers(
                endpoint="unlike",
                friendly_name=f"IgApi: media/{media_id}/unlike/"
            )
            
            response = self.auth.session.post(
                f"https://i.instagram.com/api/v1/media/{media_id}/unlike/",
                headers=headers,
                data={"signed_body": signed_body, "d": "0"},
                timeout=10
            )
            
            if response.status_code == 200:
                parsed_data = InstagramEncryption.safe_parse_json(response)
                
                if InstagramEncryption.is_success_response(response, parsed_data):
                    return {"success": True, "data": parsed_data}
                else:
                    return self.handle_action_error(response.status_code, parsed_data,
                                                 InstagramEncryption.safe_decode_response(response))
            else:
                if response.status_code == 400:
                    parsed_data = InstagramEncryption.safe_parse_json(response)
                    return self.handle_action_error(response.status_code, parsed_data,
                                                 InstagramEncryption.safe_decode_response(response))
                
                return self.handle_http_error(response.status_code, 
                                            InstagramEncryption.safe_decode_response(response))
                
        except Exception as e:
            return {"success": False, "error": "Ce media a ete supprime"}
    
    def unfollow_user(self, user_input: str) -> dict:
        """Ne plus suivre un utilisateur"""
        try:
            if self.api:
                user_id = self.api.extract_user_id_from_url(user_input)
            else:
                user_id = self._extract_user_id_basic(user_input)
            
            # Si échec d'extraction, chercher username similaire via API
            if not user_id and self.api:
                username_match = re.search(r'instagram\.com/([^/?]+)', user_input)
                if username_match:
                    target_username = username_match.group(1).replace('@', '').strip()
                    user_id = self._search_similar_username(target_username)
                
                if not user_id:
                    return {"success": False, "error": "Utilisateur introuvable"}
            
            current_user_id = self._get_user_id_from_session()
            if not current_user_id:
                return {"success": False, "error": "User ID non trouvé dans la session"}
            
            unfollow_data = {
                "user_id": user_id,
                "radio_type": self._get_radio_type(),
                "_uid": current_user_id,
                "device_id": self._get_device_specific_headers()["x-ig-android-id"],
                "_uuid": self._get_device_specific_headers()["x-ig-device-id"],
                "nav_chain": f"UserDetailFragment:profile:1:button:{int(time.time() * 1000)}:::{int(time.time() * 1000)}",
                "container_module": "profile"
            }
            
            signed_body = InstagramEncryption.create_signed_body(unfollow_data)
            
            headers = self._build_complete_headers(
                endpoint="unfollow",
                friendly_name=f"IgApi: friendships/destroy/{user_id}/"
            )
            
            response = self.auth.session.post(
                f"https://i.instagram.com/api/v1/friendships/destroy/{user_id}/",
                headers=headers,
                data={"signed_body": signed_body},
                timeout=10
            )
            
            if response.status_code == 200:
                parsed_data = InstagramEncryption.safe_parse_json(response)
                
                if InstagramEncryption.is_success_response(response, parsed_data):
                    return {"success": True, "data": parsed_data}
                else:
                    return self.handle_action_error(response.status_code, parsed_data,
                                                 InstagramEncryption.safe_decode_response(response))
            else:
                if response.status_code == 400:
                    parsed_data = InstagramEncryption.safe_parse_json(response)
                    return self.handle_action_error(response.status_code, parsed_data,
                                                 InstagramEncryption.safe_decode_response(response))
                
                return self.handle_http_error(response.status_code, 
                                            InstagramEncryption.safe_decode_response(response))
                
        except Exception as e:
            return {"success": False, "error": "Utilisateur introuvable"}
    
    # Méthodes supplémentaires pour la compatibilité complète...
    def delete_comment(self, media_input: str, comment_id: str) -> dict:
        """Supprimer un commentaire"""
        try:
            if self.api:
                media_id = self.api.extract_media_id_from_url(media_input)
            else:
                media_id = self._extract_media_id_basic(media_input)
            
            if not media_id:
                return {"success": False, "error": "Ce média a été supprimé"}
            
            user_id = self._get_user_id_from_session()
            if not user_id:
                return {"success": False, "error": "User ID non trouvé dans la session"}
            
            delete_comment_data = {
                "_uid": user_id,
                "_uuid": self._get_device_specific_headers()["x-ig-device-id"],
                "nav_chain": self._build_nav_chain("comment")
            }
            
            signed_body = InstagramEncryption.create_signed_body(delete_comment_data)
            
            headers = self._build_complete_headers(
                endpoint="comment_delete",
                friendly_name=f"IgApi: media/{media_id}/comment/{comment_id}/delete/"
            )
            
            response = self.auth.session.post(
                f"https://i.instagram.com/api/v1/media/{media_id}/comment/{comment_id}/delete/",
                headers=headers,
                data={"signed_body": signed_body},
                timeout=10
            )
            
            if response.status_code == 200:
                parsed_data = InstagramEncryption.safe_parse_json(response)
                
                if InstagramEncryption.is_success_response(response, parsed_data):
                    return {"success": True, "data": parsed_data}
                else:
                    return self.handle_action_error(response.status_code, parsed_data,
                                                 InstagramEncryption.safe_decode_response(response))
            else:
                if response.status_code == 400:
                    parsed_data = InstagramEncryption.safe_parse_json(response)
                    return self.handle_action_error(response.status_code, parsed_data,
                                                 InstagramEncryption.safe_decode_response(response))
                
                return self.handle_http_error(response.status_code, 
                                            InstagramEncryption.safe_decode_response(response))
                
        except Exception as e:
            return {"success": False, "error": f"Erreur: {str(e)}"}
    
    # Méthodes pour récupérer les followers, following, etc. avec headers complets
    def get_followers(self, user_input: str = None, count: int = 20) -> dict:
        """Récupérer la liste des abonnés"""
        try:
            if user_input:
                if self.api:
                    user_id = self.api.extract_user_id_from_url(user_input)
                else:
                    user_id = self._extract_user_id_basic(user_input)
            else:
                user_id = self._get_user_id_from_session()
            
            if not user_id:
                return {"success": False, "error": "User ID non trouvé"}
            
            headers = self._build_complete_headers(
                endpoint="followers",
                friendly_name=f"IgApi: friendships/{user_id}/followers/"
            )
            
            params = {
                "count": str(count),
                "max_id": ""
            }
            
            response = self.auth.session.get(
                f"https://i.instagram.com/api/v1/friendships/{user_id}/followers/",
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                parsed_data = InstagramEncryption.safe_parse_json(response)
                
                if InstagramEncryption.is_success_response(response, parsed_data):
                    users = parsed_data.get("users", [])
                    followers_list = []
                    
                    for user in users:
                        follower_info = {
                            "user_id": str(user.get("pk")),
                            "username": user.get("username", ""),
                            "full_name": user.get("full_name", ""),
                            "is_private": user.get("is_private", False),
                            "is_verified": user.get("is_verified", False),
                            "profile_pic_url": user.get("profile_pic_url", "")
                        }
                        followers_list.append(follower_info)
                    
                    return {"success": True, "data": followers_list}
                else:
                    return self.handle_action_error(response.status_code, parsed_data,
                                                 InstagramEncryption.safe_decode_response(response))
            else:
                return self.handle_http_error(response.status_code, 
                                            InstagramEncryption.safe_decode_response(response))
                
        except Exception as e:
            return {"success": False, "error": f"Erreur: {str(e)}"}
    
    def get_following(self, user_input: str = None, count: int = 20) -> dict:
        """Récupérer la liste des abonnements"""
        try:
            if user_input:
                if self.api:
                    user_id = self.api.extract_user_id_from_url(user_input)
                else:
                    user_id = self._extract_user_id_basic(user_input)
            else:
                user_id = self._get_user_id_from_session()
            
            if not user_id:
                return {"success": False, "error": "User ID non trouvé"}
            
            headers = self._build_complete_headers(
                endpoint="following",
                friendly_name=f"IgApi: friendships/{user_id}/following/"
            )
            
            params = {
                "count": str(count),
                "max_id": ""
            }
            
            response = self.auth.session.get(
                f"https://i.instagram.com/api/v1/friendships/{user_id}/following/",
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                parsed_data = InstagramEncryption.safe_parse_json(response)
                
                if InstagramEncryption.is_success_response(response, parsed_data):
                    users = parsed_data.get("users", [])
                    following_list = []
                    
                    for user in users:
                        following_info = {
                            "user_id": str(user.get("pk")),
                            "username": user.get("username", ""),
                            "full_name": user.get("full_name", ""),
                            "is_private": user.get("is_private", False),
                            "is_verified": user.get("is_verified", False),
                            "profile_pic_url": user.get("profile_pic_url", "")
                        }
                        following_list.append(following_info)
                    
                    return {"success": True, "data": following_list}
                else:
                    return self.handle_action_error(response.status_code, parsed_data,
                                                 InstagramEncryption.safe_decode_response(response))
            else:
                return self.handle_http_error(response.status_code, 
                                            InstagramEncryption.safe_decode_response(response))
                
        except Exception as e:
            return {"success": False, "error": f"Erreur: {str(e)}"}
    
    def search_users(self, query: str, count: int = 20) -> dict:
        """Rechercher des utilisateurs"""
        try:
            headers = self._build_complete_headers(
                endpoint="user_search",
                friendly_name="IgApi: users/search/"
            )
            
            search_params = {
                "timezone_offset": str(self.session_data.get("timezone_offset", 10800)),
                "q": query,
                "count": str(count)
            }
            
            response = self.auth.session.get(
                "https://i.instagram.com/api/v1/users/search/",
                params=search_params,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                parsed_data = InstagramEncryption.safe_parse_json(response)
                
                if InstagramEncryption.is_success_response(response, parsed_data):
                    users = parsed_data.get("users", [])
                    search_results = []
                    
                    for user in users:
                        user_info = {
                            "user_id": str(user.get("pk")),
                            "username": user.get("username", ""),
                            "full_name": user.get("full_name", ""),
                            "is_private": user.get("is_private", False),
                            "is_verified": user.get("is_verified", False),
                            "profile_pic_url": user.get("profile_pic_url", ""),
                            "follower_count": user.get("follower_count", 0)
                        }
                        search_results.append(user_info)
                    
                    return {"success": True, "data": search_results}
                else:
                    return self.handle_action_error(response.status_code, parsed_data,
                                                 InstagramEncryption.safe_decode_response(response))
            else:
                return self.handle_http_error(response.status_code, 
                                            InstagramEncryption.safe_decode_response(response))
                
        except Exception as e:
            return {"success": False, "error": f"Erreur: {str(e)}"}
    
    def get_media_comments(self, media_input: str, count: int = 20) -> dict:
        """Récupérer les commentaires d'un média"""
        try:
            if self.api:
                media_id = self.api.extract_media_id_from_url(media_input)
            else:
                media_id = self._extract_media_id_basic(media_input)
            
            if not media_id:
                return {"success": False, "error": "Ce média a été supprimé"}
            
            headers = self._build_complete_headers(
                endpoint="comments",
                friendly_name=f"IgApi: media/{media_id}/comments/"
            )
            
            params = {
                "count": str(count),
                "max_id": ""
            }
            
            response = self.auth.session.get(
                f"https://i.instagram.com/api/v1/media/{media_id}/comments/",
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                parsed_data = InstagramEncryption.safe_parse_json(response)
                
                if InstagramEncryption.is_success_response(response, parsed_data):
                    comments = parsed_data.get("comments", [])
                    comments_list = []
                    
                    for comment in comments:
                        comment_info = {
                            "comment_id": str(comment.get("pk")),
                            "text": comment.get("text", ""),
                            "created_at": comment.get("created_at"),
                            "user": {
                                "user_id": str(comment.get("user", {}).get("pk")),
                                "username": comment.get("user", {}).get("username", ""),
                                "full_name": comment.get("user", {}).get("full_name", ""),
                                "profile_pic_url": comment.get("user", {}).get("profile_pic_url", "")
                            }
                        }
                        comments_list.append(comment_info)
                    
                    return {"success": True, "data": comments_list}
                else:
                    return self.handle_action_error(response.status_code, parsed_data,
                                                 InstagramEncryption.safe_decode_response(response))
            else:
                return self.handle_http_error(response.status_code, 
                                            InstagramEncryption.safe_decode_response(response))
                
        except Exception as e:
            return {"success": False, "error": f"Erreur: {str(e)}"}
    
    def get_media_likers(self, media_input: str, count: int = 20) -> dict:
        """Récupérer les utilisateurs qui ont liké un média"""
        try:
            if self.api:
                media_id = self.api.extract_media_id_from_url(media_input)
            else:
                media_id = self._extract_media_id_basic(media_input)
            
            if not media_id:
                return {"success": False, "error": "Ce média a été supprimé"}
            
            headers = self._build_complete_headers(
                endpoint="likers",
                friendly_name=f"IgApi: media/{media_id}/likers/"
            )
            
            response = self.auth.session.get(
                f"https://i.instagram.com/api/v1/media/{media_id}/likers/",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                parsed_data = InstagramEncryption.safe_parse_json(response)
                
                if InstagramEncryption.is_success_response(response, parsed_data):
                    users = parsed_data.get("users", [])
                    likers_list = []
                    
                    for user in users[:count]:  # Limiter au nombre demandé
                        liker_info = {
                            "user_id": str(user.get("pk")),
                            "username": user.get("username", ""),
                            "full_name": user.get("full_name", ""),
                            "is_private": user.get("is_private", False),
                            "is_verified": user.get("is_verified", False),
                            "profile_pic_url": user.get("profile_pic_url", "")
                        }
                        likers_list.append(liker_info)
                    
                    return {"success": True, "data": likers_list}
                else:
                    return self.handle_action_error(response.status_code, parsed_data,
                                                 InstagramEncryption.safe_decode_response(response))
            else:
                return self.handle_http_error(response.status_code, 
                                            InstagramEncryption.safe_decode_response(response))
                
        except Exception as e:
            return {"success": False, "error": f"Erreur: {str(e)}"}
    
    def get_timeline_feed(self, count: int = 20) -> dict:
        """Récupérer le feed timeline"""
        try:
            user_id = self._get_user_id_from_session()
            
            headers = self._build_complete_headers(
                endpoint="timeline",
                friendly_name="IgApi: feed/timeline/"
            )
            
            params = {
                "count": str(count),
                "max_id": ""
            }
            
            response = self.auth.session.get(
                "https://i.instagram.com/api/v1/feed/timeline/",
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                parsed_data = InstagramEncryption.safe_parse_json(response)
                
                if InstagramEncryption.is_success_response(response, parsed_data):
                    items = parsed_data.get("feed_items", [])
                    timeline_list = []
                    
                    for item in items:
                        if item.get("media_or_ad"):
                            media = item["media_or_ad"]
                            timeline_info = {
                                "id": media.get("id"),
                                "code": media.get("code"),
                                "media_type": media.get("media_type"),
                                "taken_at": media.get("taken_at"),
                                "like_count": media.get("like_count", 0),
                                "comment_count": media.get("comment_count", 0),
                                "user": {
                                    "user_id": str(media.get("user", {}).get("pk")),
                                    "username": media.get("user", {}).get("username", ""),
                                    "full_name": media.get("user", {}).get("full_name", ""),
                                    "profile_pic_url": media.get("user", {}).get("profile_pic_url", "")
                                }
                            }
                            
                            caption_info = media.get("caption")
                            if caption_info:
                                timeline_info["caption"] = caption_info.get("text", "")
                            else:
                                timeline_info["caption"] = ""
                            
                            timeline_list.append(timeline_info)
                    
                    return {"success": True, "data": timeline_list}
                else:
                    return self.handle_action_error(response.status_code, parsed_data,
                                                 InstagramEncryption.safe_decode_response(response))
            else:
                return self.handle_http_error(response.status_code, 
                                            InstagramEncryption.safe_decode_response(response))
                
        except Exception as e:
            return {"success": False, "error": f"Erreur: {str(e)}"}
