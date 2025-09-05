# -*- coding: utf-8 -*-
"""
Client Instagram principal pour insta_kendou
Intégration complète de toutes les fonctionnalité Instagram
"""

import os
import time
import json
import uuid
import random
import hashlib
import hmac
import base64
import urllib.parse
import requests
from typing import Dict, Optional, Any

from .utils.license import validate_license
from .utils.device import DeviceManager
from .utils.encryption import InstagramEncryption
from .utils.media import MediaProcessor
from .utils.url_resolver import URLResolver
from .auth.authentication import InstagramAuth
from .exceptions import *

class InstagramAPI:
    """API Instagram pour extraire media ID et user ID"""
    
    def __init__(self, session: requests.Session, device_info: dict, user_id: str = None, auth_token: str = None, url_resolver: URLResolver = None):
        self.session = session
        self.device_info = device_info
        self.user_id = user_id
        self.auth_token = auth_token
        self.url_resolver = url_resolver or URLResolver()
        
    def shortcode_to_media_id(self, shortcode: str) -> str:
        """Convertir shortcode Instagram en media ID (algorithme exact)"""
        return self.url_resolver.shortcode_to_media_id(shortcode)
    
    def username_to_user_id(self, username: str) -> str:
        """Convertir username en user ID via API Instagram avec recherche similaire"""
        return self.url_resolver._username_to_user_id_with_similarity(username, self)
    
    def extract_media_id_from_url(self, url: str) -> str:
        """Extraire media ID depuis URL Instagram avec support liens courts"""
        return self.url_resolver.extract_media_id_from_url(url)
    
    def extract_user_id_from_url(self, url: str) -> str:
        """Extraire user ID depuis URL de profil avec support liens courts"""
        return self.url_resolver.extract_user_id_from_url(url, self)
    
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
            raise LicenseError()
        
        self.auth = InstagramAuth()
        self.session_data = session_data or {}
        self.url_resolver = URLResolver()
        self.media_processor = MediaProcessor()
        
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
                self.auth.api = InstagramAPI(self.auth.session, self.auth.device_manager.device_info, user_id, auth_token, self.url_resolver)
    
    def login(self, username: str, password: str) -> dict:
        """Connexion Instagram avec gestion 2FA complète"""
        result = self.auth.login(username, password)
        
        if result["success"]:
            # Initialiser l'API après connexion réussie
            user_data = result.get("user_data", {})
            session_data = result.get("session_data", {})
            auth_token = session_data.get("authorization", "")
            user_id = user_data.get("user_id", "")
            
            if user_id and auth_token:
                self.auth.api = InstagramAPI(self.auth.session, self.auth.device_manager.device_info, user_id, auth_token, self.url_resolver)
                self.session_data = session_data
        
        return result
    
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
                self.auth.api = InstagramAPI(self.auth.session, self.auth.device_manager.device_info, user_id, auth_token, self.url_resolver)
        
        return session_data
    
    def dump_session(self, filename: str = None) -> bool:
        """Sauvegarder la session actuelle"""
        try:
            if not self.session_data:
                return False
            
            if not filename:
                username = self._get_username_from_session()
                filename = f"sessions/{username}_ig_complete.json"
            
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.session_data, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            return False
    
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
        
        return "user"
    
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
        
        return ""
    
    def _get_auth_token(self) -> str:
        """Récupérer token d'autorisation"""
        auth_data = self.session_data.get("authorization_data", {})
        auth_header = auth_data.get("authorization_header")
        
        if auth_header and "Bearer" in auth_header:
            return auth_header
        
        auth_token = self.session_data.get("authorization")
        if auth_token and "Bearer" in auth_token:
            return auth_token
        
        # Construire depuis sessionid si disponible
        sessionid = None
        
        if "sessionid" in self.session_data:
            sessionid = self.session_data["sessionid"]
        else:
            cookies = self.session_data.get("cookies", {})
            for key, value in cookies.items():
                if "sessionid" in key.lower():
                    sessionid = value
                    break
        
        if sessionid:
            user_id = self._get_user_id_from_session()
            
            if '%3A' not in sessionid:
                sessionid = urllib.parse.quote(sessionid)
            
            token_data = {
                "ds_user_id": user_id,
                "sessionid": sessionid
            }
            
            encoded = base64.b64encode(json.dumps(token_data, separators=(',', ':')).encode()).decode()
            return f"Bearer IGT:2:{encoded}"
        
        return ""
    
    def handle_action_error(self, response_status: int, error_data: dict, response_text: str = "") -> dict:
        """Gérer les erreurs d'action avec messages simplifiés"""
        try:
            username = self._get_username_from_session()
            
            # Vérifier FEEDBACK_REQUIRED en premier
            if isinstance(error_data, dict) and error_data.get("message") == "feedback_required":
                feedback_result = self.handle_feedback_required(error_data)
                if feedback_result["type"] == "rate_limit":
                    print(f"❌ {feedback_result['error']}")
                    return feedback_result
                elif feedback_result["type"] == "pending_follow":
                    print(f"✅ {feedback_result['message']}")
                    return feedback_result
                else:
                    print(f"❌ {feedback_result['error']}")
                    return feedback_result
            
            # Vérifier LOGIN_REQUIRED
            if (isinstance(error_data, dict) and error_data.get("message") == "login_required") or \
               ("login_required" in response_text.lower()):
                print(f"❌ Le compte @{username} est déconnecté, veuillez vous reconnecter")
                return {
                    "success": False,
                    "error": f"Le compte @{username} est déconnecté, veuillez vous reconnecter"
                }
            
            # Vérifier SUSPENDED/DISABLED dans les challenges
            if isinstance(error_data, dict):
                challenge_info = self.handle_challenge_response(response_text, error_data)
                
                if not challenge_info["show_details"]:
                    if challenge_info["type"] == "suspended":
                        print(f"❌ Le compte @{username} est suspendu, veuillez le régler manuellement")
                        return {
                            "success": False,
                            "error": f"Le compte @{username} est suspendu, veuillez le régler manuellement"
                        }
                    elif challenge_info["type"] == "disabled":
                        print(f"❌ Le compte @{username} est désactivé et ne peut plus être utilisé")
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
            
            # Vérifier erreurs spécifiques connues
            error_text = str(error_data).lower()
            
            if any(keyword in error_text for keyword in ["deleted", "supprime", "no longer available", "not found"]):
                print("❌ Ce media a été supprimé")
                return {"success": False, "error": "Ce media a été supprimé"}
            
            if any(keyword in error_text for keyword in ["user not found", "utilisateur introuvable"]):
                print("❌ Utilisateur introuvable")
                return {"success": False, "error": "Utilisateur introuvable"}
            
            # Autres erreurs - afficher détails complets
            print(f"❌ Erreur détaillée: {error_data}")
            return {"success": False, "error": f"Erreur détaillée: {error_data}"}
            
        except Exception as e:
            print(f"❌ Erreur inattendue: {str(e)}")
            return {"success": False, "error": f"Erreur inattendue: {str(e)}"}
    
    def handle_http_error(self, response_status: int, response_text: str) -> dict:
        """Gérer les erreurs HTTP avec messages simplifiés"""
        try:
            username = self._get_username_from_session()
            
            if response_status == 403:
                if "login_required" in response_text.lower():
                    print(f"❌ Le compte @{username} est déconnecté, veuillez vous reconnecter")
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
            print("❌ Ce media a été supprimé")
            return {"success": False, "error": "Ce media a été supprimé"}
        else:
            print(f"❌ {error_message}")
            return {"success": False, "error": error_message}
    
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
    
    def handle_feedback_required(self, error_data: dict) -> dict:
        """Gérer spécifiquement les erreurs feedback_required"""
        try:
            feedback_message = error_data.get("feedback_message", "").lower()
            
            if "réessayer plus tard" in feedback_message or "limit" in feedback_message:
                return {
                    "success": False,
                    "error": "Votre compte a atteint la limite de cette action, veuillez réessayer plus tard",
                    "type": "rate_limit"
                }
            
            elif "demande est en attente" in feedback_message or "examiner manuellement" in feedback_message:
                return {
                    "success": True,
                    "message": "Follow en attente de validation",
                    "type": "pending_follow"
                }
            
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
    
    def solve_general_challenge(self, challenge_data: dict) -> bool:
        """Tenter de résoudre un challenge général automatiquement"""
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
            
            challenge_headers = {
                "accept-language": "fr-FR, en-US",
                "authorization": self._get_auth_token(),
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "ig-intended-user-id": user_id,
                "ig-u-ds-user-id": user_id,
                "user-agent": self.auth.device_manager.device_info['user_agent'],
            }
            
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
        """Exécuter une action avec retry automatique en cas de challenge général"""
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
                
                # Tenter de résoudre le challenge
                if self.solve_general_challenge(challenge_data):
                    time.sleep(5)
                    continue
                else:
                    username = self._get_username_from_session()
                    print(f"❌ Captcha détecté pour @{username}, veuillez le régler manuellement")
                    return {"success": False, "error": f"Captcha détecté pour @{username}, veuillez le régler manuellement"}
            
            # Si c'est la deuxième tentative ET qu'il y a encore un challenge
            if attempt == max_retries and "challenge_data" in result:
                username = self._get_username_from_session()
                print(f"❌ Captcha détecté pour @{username}, veuillez le régler manuellement")
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
    
    # MÉTHODES INTERNES
    def _like_post_internal(self, media_input: str) -> dict:
        """Liker un post Instagram (méthode interne)"""
        try:
            if self.auth.api:
                media_id = self.auth.api.extract_media_id_from_url(media_input)
            else:
                media_id = self._extract_media_id_basic(media_input)
            
            if not media_id:
                return {"success": False, "error": "Ce media a ete supprime"}
            
            user_id = self._get_user_id_from_session()
            if not user_id:
                return {"success": False, "error": "User ID non trouvé dans la session"}
            
            like_data = {
                "is_2m_enabled": "false",
                "delivery_class": "organic", 
                "tap_source": "button",
                "media_id": media_id,
                "radio_type": "wifi-none",
                "_uid": user_id,
                "_uuid": self.auth.device_manager.device_info['device_uuid'],
                "nav_chain": f"MainFeedFragment:feed_timeline:1:cold_start:{int(time.time() * 1000)}:::{int(time.time() * 1000)}",
                "is_from_swipe": "false",
                "is_carousel_bumped_post": "false", 
                "floating_context_items": "[]",
                "container_module": "feed_timeline",
                "feed_position": "0"
            }
            
            signed_body = InstagramEncryption.create_signed_body(like_data)
            
            headers = {
                "accept-language": "fr-FR, en-US",
                "authorization": self._get_auth_token(),
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "ig-intended-user-id": user_id,
                "ig-u-ds-user-id": user_id,
                "user-agent": self.auth.device_manager.device_info['user_agent'],
                "x-fb-friendly-name": f"IgApi: media/{media_id}/like/",
            }
            
            response = self.auth.session.post(
                f"https://i.instagram.com/api/v1/media/{media_id}/like/",
                headers=headers,
                data={"signed_body": signed_body, "d": "0"},
                timeout=10
            )
            
            if response.status_code == 200:
                parsed_data = InstagramEncryption.safe_parse_json(response)
                
                if InstagramEncryption.is_success_response(response, parsed_data):
                    print("✅ Like réussi")
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
            print("❌ Ce media a ete supprime")
            return {"success": False, "error": "Ce media a ete supprime"}
    
    def _comment_post_internal(self, media_input: str, comment_text: str) -> dict:
        """Commenter un post Instagram (méthode interne)"""
        try:
            if self.auth.api:
                media_id = self.auth.api.extract_media_id_from_url(media_input)
            else:
                media_id = self._extract_media_id_basic(media_input)
            
            if not media_id:
                return {"success": False, "error": "Ce média a été supprimé"}
            
            user_id = self._get_user_id_from_session()
            if not user_id:
                return {"success": False, "error": "User ID non trouvé dans la session"}
            
            # Utiliser directement l'approche web qui fonctionne
            try:
                web_response = self.auth.session.get(
                    media_input,
                    headers={"user-agent": "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36"},
                    timeout=10
                )
                
                if web_response.status_code == 200:
                    web_content = InstagramEncryption.safe_decode_response(web_response)
                    
                    csrf_match = re.search(r'"csrf_token":"([^"]+)"', web_content)
                    if csrf_match:
                        csrf_token = csrf_match.group(1)
                        
                        web_comment_data = {
                            "comment_text": comment_text,
                            "replied_to_comment_id": "",
                            "media_id": media_id
                        }
                        
                        web_headers = {
                            "accept": "*/*",
                            "accept-language": "fr-FR,fr;q=0.9,en;q=0.8",
                            "content-type": "application/x-www-form-urlencoded",
                            "user-agent": "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
                            "x-csrftoken": csrf_token,
                            "x-ig-app-id": "567067343352427",
                            "x-ig-www-claim": "0",
                            "x-requested-with": "XMLHttpRequest"
                        }
                        
                        cookies = self.session_data.get("cookies", {})
                        cookies["csrftoken"] = csrf_token
                        
                        for name, value in cookies.items():
                            self.auth.session.cookies.set(name, value)
                        
                        response = self.auth.session.post(
                            f"https://www.instagram.com/api/v1/web/comments/{media_id}/add/",
                            headers=web_headers,
                            data=web_comment_data,
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            parsed_data = InstagramEncryption.safe_parse_json(response)
                            
                            if InstagramEncryption.is_success_response(response, parsed_data):
                                print("✅ Commentaire réussi")
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
                    else:
                        print("❌ Ce média a été supprimé")
                        return {"success": False, "error": "Ce média a été supprimé"}
                else:
                    print("❌ Ce media a ete supprime")
                    return {"success": False, "error": "Ce media a ete supprime"}
            except Exception as web_error:
                return self.handle_media_error("Ce média a été supprimé")
                
        except Exception as e:
            return self.handle_media_error("Ce media a ete supprime")
    
    def _follow_user_internal(self, user_input: str) -> dict:
        """Suivre un utilisateur (méthode interne)"""
        try:
            if self.auth.api:
                user_id = self.auth.api.extract_user_id_from_url(user_input)
            else:
                user_id = self._extract_user_id_basic(user_input)
            
            if not user_id:
                username_match = re.search(r'instagram\.com/([^/?]+)', user_input)
                if username_match:
                    target_username = username_match.group(1).replace('@', '').strip()
                    user_id = self._search_similar_username(target_username)
                
                if not user_id:
                    print("❌ Utilisateur introuvable")
                    return {"success": False, "error": "Utilisateur introuvable"}
            
            current_user_id = self._get_user_id_from_session()
            if not current_user_id:
                return {"success": False, "error": "User ID non trouvé dans la session"}
            
            follow_data = {
                "inventory_source": "media_or_ad",
                "include_follow_friction_check": "1",
                "user_id": user_id,
                "radio_type": "wifi-none",
                "_uid": current_user_id,
                "device_id": self.auth.device_manager.device_info['android_id'],
                "_uuid": self.auth.device_manager.device_info['device_uuid'],
                "nav_chain": f"MainFeedFragment:feed_timeline:1:cold_start:{int(time.time() * 1000)}:::{int(time.time() * 1000)},UserDetailFragment:profile:7:media_owner:{int(time.time() * 1000)}:::{int(time.time() * 1000)},ProfileMediaTabFragment:profile:8:button:{int(time.time() * 1000)}:::{int(time.time() * 1000)}",
                "container_module": "profile"
            }
            
            signed_body = InstagramEncryption.create_signed_body(follow_data)
            
            headers = {
                "accept-language": "fr-FR, en-US",
                "authorization": self._get_auth_token(),
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "ig-intended-user-id": current_user_id,
                "ig-u-ds-user-id": current_user_id,
                "user-agent": self.auth.device_manager.device_info['user_agent'],
                "x-fb-friendly-name": f"IgApi: friendships/create/{user_id}/",
            }
            
            response = self.auth.session.post(
                f"https://i.instagram.com/api/v1/friendships/create/{user_id}/",
                headers=headers,
                data={"signed_body": signed_body},
                timeout=10
            )
            
            if response.status_code == 200:
                parsed_data = InstagramEncryption.safe_parse_json(response)
                
                if InstagramEncryption.is_success_response(response, parsed_data):
                    print("✅ Follow réussi")
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
    
    def _upload_story_internal(self, image_path: str) -> dict:
        """Publier une story Instagram (méthode interne)"""
        try:
            print(f"📷 Upload story: {image_path}")
            
            if not os.path.exists(image_path):
                return {"success": False, "error": f"Image non trouvée: {image_path}"}
            
            image_data, image_size, error = self.media_processor.prepare_image_for_instagram(image_path, story_mode=True)
            if error:
                return {"success": False, "error": error}
            
            upload_id = self.media_processor.generate_upload_id()
            user_id = self._get_user_id_from_session()
            
            if not user_id:
                return {"success": False, "error": "User ID non trouvé"}
            
            upload_result = self._upload_image_data(image_data, upload_id, story_mode=True)
            if not upload_result["success"]:
                if "challenge_data" in upload_result:
                    return upload_result
                
                error_msg = upload_result.get("error", "")
                if "suspended" in error_msg.lower():
                    username = self._get_username_from_session()
                    return {"success": False, "error": f"⚠️ Le compte @{username} est suspendu, veuillez le réactiver manuellement"}
                elif "disabled" in error_msg.lower():
                    username = self._get_username_from_session()
                    return {"success": False, "error": f"❌ Le compte @{username} est désactivé et ne peut plus être utilisé"}
                elif "login_required" in error_msg.lower() or "déconnecté" in error_msg.lower():
                    username = self._get_username_from_session()
                    return {"success": False, "error": f"❌ Le compte @{username} est déconnecté, veuillez vous reconnecter"}
                
                return upload_result
            
            story_result = self._configure_story(upload_id, image_size, user_id)
            if not story_result["success"]:
                if "challenge_data" in story_result:
                    return story_result
                
                error_msg = story_result.get("error", "")
                if "suspended" in error_msg.lower():
                    username = self._get_username_from_session()
                    return {"success": False, "error": f"⚠️ Le compte @{username} est suspendu, veuillez le réactiver manuellement"}
                elif "disabled" in error_msg.lower():
                    username = self._get_username_from_session()
                    return {"success": False, "error": f"❌ Le compte @{username} est désactivé et ne peut plus être utilisé"}
                elif "login_required" in error_msg.lower() or "déconnecté" in error_msg.lower():
                    username = self._get_username_from_session()
                    return {"success": False, "error": f"❌ Le compte @{username} est déconnecté, veuillez vous reconnecter"}
            
            return story_result
            
        except Exception as e:
            return {"success": False, "error": f"Erreur upload story: {str(e)}"}
    
    def _upload_post_internal(self, image_path: str, caption: str = "") -> dict:
        """Publier un post Instagram (méthode interne)"""
        try:
            print(f"📷 Upload post: {image_path}")
            
            if not os.path.exists(image_path):
                return {"success": False, "error": f"Image non trouvée: {image_path}"}
            
            image_data, image_size, error = self.media_processor.prepare_image_for_instagram(image_path, story_mode=False)
            if error:
                return {"success": False, "error": error}
            
            upload_id = self.media_processor.generate_upload_id()
            user_id = self._get_user_id_from_session()
            
            if not user_id:
                return {"success": False, "error": "User ID non trouvé"}
            
            upload_result = self._upload_image_data(image_data, upload_id, story_mode=False)
            if not upload_result["success"]:
                if "challenge_data" in upload_result:
                    return upload_result
                
                error_msg = upload_result.get("error", "")
                if "suspended" in error_msg.lower():
                    username = self._get_username_from_session()
                    return {"success": False, "error": f"⚠️ Le compte @{username} est suspendu, veuillez le réactiver manuellement"}
                elif "disabled" in error_msg.lower():
                    username = self._get_username_from_session()
                    return {"success": False, "error": f"❌ Le compte @{username} est désactivé et ne peut plus être utilisé"}
                elif "login_required" in error_msg.lower() or "déconnecté" in error_msg.lower():
                    username = self._get_username_from_session()
                    return {"success": False, "error": f"❌ Le compte @{username} est déconnecté, veuillez vous reconnecter"}
                
                return upload_result
            
            post_result = self._configure_post(upload_id, image_size, user_id, caption)
            if not post_result["success"]:
                if "challenge_data" in post_result:
                    return post_result
                
                error_msg = post_result.get("error", "")
                if "suspended" in error_msg.lower():
                    username = self._get_username_from_session()
                    return {"success": False, "error": f"⚠️ Le compte @{username} est suspendu, veuillez le réactiver manuellement"}
                elif "disabled" in error_msg.lower():
                    username = self._get_username_from_session()
                    return {"success": False, "error": f"❌ Le compte @{username} est désactivé et ne peut plus être utilisé"}
                elif "login_required" in error_msg.lower() or "déconnecté" in error_msg.lower():
                    username = self._get_username_from_session()
                    return {"success": False, "error": f"❌ Le compte @{username} est déconnecté, veuillez vous reconnecter"}
                
                return post_result
            
            pdq_result = self._update_media_pdq_hash(upload_id, image_data, user_id)
            
            return post_result
            
        except Exception as e:
            return {"success": False, "error": f"Erreur upload post: {str(e)}"}
    
    def _delete_last_post_internal(self) -> dict:
        """Supprimer la dernière publication (méthode interne)"""
        try:
            print("🗑️ Suppression dernière publication...")
            
            if not self.auth.api:
                return {"success": False, "error": "API non initialisée"}
            
            media_list = self.auth.api.get_own_media_list(count=1)
            
            if not media_list:
                return {"success": False, "error": "Aucune publication trouvée"}
            
            latest_media = media_list[0]
            media_id = latest_media["id"]
            
            print(f"📷 Suppression media ID: {media_id}")
            
            delete_result = self._delete_media(media_id)
            if not delete_result["success"]:
                if "challenge_data" in delete_result:
                    return delete_result
                
                error_msg = delete_result.get("error", "")
                if "suspended" in error_msg.lower():
                    username = self._get_username_from_session()
                    return {"success": False, "error": f"⚠️ Le compte @{username} est suspendu, veuillez le réactiver manuellement"}
                elif "disabled" in error_msg.lower():
                    username = self._get_username_from_session()
                    return {"success": False, "error": f"❌ Le compte @{username} est désactivé et ne peut plus être utilisé"}
                elif "login_required" in error_msg.lower() or "déconnecté" in error_msg.lower():
                    username = self._get_username_from_session()
                    return {"success": False, "error": f"❌ Le compte @{username} est déconnecté, veuillez vous reconnecter"}
            
            return delete_result
            
        except Exception as e:
            return {"success": False, "error": f"Erreur suppression: {str(e)}"}
    
    def _search_similar_username(self, target_username: str) -> str:
        """Rechercher username similaire silencieusement"""
        try:
            if not self.auth.api:
                return None
            
            headers = {
                "user-agent": self.auth.device_manager.device_info['user_agent'],
                "x-ig-app-id": "567067343352427",
                "x-ig-android-id": self.auth.device_manager.device_info['android_id'],
                "x-ig-device-id": self.auth.device_manager.device_info['device_uuid'],
                "accept-language": "fr-FR, en-US",
                "authorization": self._get_auth_token(),
            }
            
            search_params = {
                "timezone_offset": "10800",
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
                        
                        for user in users:
                            username = user.get("username", "").lower()
                            if username == target_username.lower():
                                return str(user.get("pk"))
                        
                        target_lower = target_username.lower()
                        best_matches = []
                        
                        for user in users:
                            username = user.get("username", "").lower()
                            if username.startswith(target_lower) and username != target_lower:
                                best_matches.append((user.get("pk"), username))
                        
                        if best_matches:
                            best_matches.sort(key=lambda x: len(x[1]))
                            return str(best_matches[0][0])
                        
                        for user in users:
                            username = user.get("username", "").lower()
                            if any(part in username for part in target_lower.split('_') + target_lower.split('.')):
                                return str(user.get("pk"))
                        
                except Exception:
                    pass
            
            return None
            
        except Exception:
            return None
    
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
            if not user_id or not self.auth.api:
                return {"success": False, "error": "Compte non connecté"}
            
            user_info = self.auth.api.get_user_info(user_id)
            
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
                "_uuid": self.auth.device_manager.device_info['device_uuid']
            }
            
            signed_body = InstagramEncryption.create_signed_body(privacy_data)
            
            headers = {
                "accept-language": "fr-FR, en-US",
                "authorization": self._get_auth_token(),
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "ig-intended-user-id": user_id,
                "ig-u-ds-user-id": user_id,
                "user-agent": self.auth.device_manager.device_info['user_agent'],
                "x-fb-friendly-name": f"IgApi: accounts/{action}/",
            }
            
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
                    print(f"✅ Compte maintenant: {new_status}")
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
    
    def _upload_image_data(self, image_data: bytes, upload_id: str, story_mode: bool = False) -> dict:
        """Upload des données d'image vers Instagram"""
        try:
            user_id = self._get_user_id_from_session()
            
            headers = {
                "accept-language": "fr-FR, en-US",
                "authorization": self._get_auth_token(),
                "content-type": "application/octet-stream",
                "ig-intended-user-id": user_id,
                "ig-u-ds-user-id": user_id,
                "offset": "0",
                "priority": "u=6, i",
                "x-entity-length": str(len(image_data)),
                "x-entity-name": f"{upload_id}_0_{random.randint(1000000000, 9999999999)}",
                "x-entity-type": "image/jpeg",
                "user-agent": self.auth.device_manager.device_info['user_agent'],
                "accept-encoding": "gzip, deflate",
            }
            
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
                print("✅ Image uploadée avec succès")
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
        """Configurer la story après upload"""
        try:
            width, height = image_size
            
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
                "timezone_offset": "10800",
                "client_shared_at": str(int(time.time())),
                "media_folder": "Screenshots",
                "configure_mode": "1",
                "source_type": "4",
                "camera_position": "unknown",
                "_uid": user_id,
                "device_id": self.auth.device_manager.device_info['android_id'],
                "composition_id": str(uuid.uuid4()),
                "_uuid": self.auth.device_manager.device_info['device_uuid'],
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
                    "manufacturer": self.auth.device_manager.device_info.get('manufacturer', 'samsung'),
                    "model": self.auth.device_manager.device_info.get('model', 'SM-S9210'),
                    "android_version": int(self.auth.device_manager.device_info.get('sdk_version', 28)),
                    "android_release": self.auth.device_manager.device_info.get('android_version', '9')
                }
            }
            
            signed_body = InstagramEncryption.create_signed_body(story_data)
            
            headers = {
                "accept-language": "fr-FR, en-US",
                "authorization": self._get_auth_token(),
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "ig-intended-user-id": user_id,
                "ig-u-ds-user-id": user_id,
                "user-agent": self.auth.device_manager.device_info['user_agent'],
                "x-fb-friendly-name": "IgApi: media/configure_to_story/",
            }
            
            response = self.auth.session.post(
                "https://i.instagram.com/api/v1/media/configure_to_story/",
                headers=headers,
                data={"signed_body": signed_body},
                timeout=15
            )
            
            if response.status_code == 200:
                parsed_data = InstagramEncryption.safe_parse_json(response)
                
                if InstagramEncryption.is_success_response(response, parsed_data):
                    print("✅ Story publiée avec succès")
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
        """Configurer le post après upload"""
        try:
            width, height = image_size
            
            post_data = {
                "app_attribution_android_namespace": "",
                "camera_entry_point": "360",
                "camera_session_id": str(uuid.uuid4()),
                "original_height": str(height),
                "include_e2ee_mentioned_user_list": "1",
                "hide_from_profile_grid": "false",
                "scene_capture_type": "",
                "timezone_offset": "10800",
                "source_type": "4",
                "_uid": user_id,
                "device_id": self.auth.device_manager.device_info['android_id'],
                "_uuid": self.auth.device_manager.device_info['device_uuid'],
                "creation_tool_info": "[]",
                "creation_logger_session_id": str(uuid.uuid4()),
                "nav_chain": f"MainFeedFragment:feed_timeline:1:cold_start:{int(time.time() * 1000)}:::,GalleryPickerFragment:gallery_picker:50:camera_tab_bar:{int(time.time() * 1000)}:::,PhotoFilterFragment:photo_filter:51:button:{int(time.time() * 1000)}:::",
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
                    "manufacturer": self.auth.device_manager.device_info.get('manufacturer', 'samsung'),
                    "model": self.auth.device_manager.device_info.get('model', 'SM-S9210'),
                    "android_version": int(self.auth.device_manager.device_info.get('sdk_version', 28)),
                    "android_release": self.auth.device_manager.device_info.get('android_version', '9')
                },
                "overlay_data": []
            }
            
            signed_body = InstagramEncryption.create_signed_body(post_data)
            
            headers = {
                "accept-language": "fr-FR, en-US",
                "authorization": self._get_auth_token(),
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "ig-intended-user-id": user_id,
                "ig-u-ds-user-id": user_id,
                "user-agent": self.auth.device_manager.device_info['user_agent'],
                "x-fb-friendly-name": "IgApi: media/configure/",
            }
            
            response = self.auth.session.post(
                "https://i.instagram.com/api/v1/media/configure/",
                headers=headers,
                data={"signed_body": signed_body},
                timeout=15
            )
            
            if response.status_code == 200:
                parsed_data = InstagramEncryption.safe_parse_json(response)
                
                if InstagramEncryption.is_success_response(response, parsed_data):
                    print("✅ Post publié avec succès")
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
            pdq_hash = self.media_processor.generate_pdq_hash(image_data)
            
            pdq_data = {
                "pdq_hash_info": f'[{{"pdq_hash":"{pdq_hash}","frame_time":0}}]',
                "_uid": user_id,
                "_uuid": self.auth.device_manager.device_info['device_uuid'],
                "upload_id": upload_id
            }
            
            signed_body = InstagramEncryption.create_signed_body(pdq_data)
            
            headers = {
                "accept-language": "fr-FR, en-US",
                "authorization": self._get_auth_token(),
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "ig-intended-user-id": user_id,
                "ig-u-ds-user-id": user_id,
                "user-agent": self.auth.device_manager.device_info['user_agent'],
                "x-fb-friendly-name": "IgApi: media/update_media_with_pdq_hash_info/",
            }
            
            response = self.auth.session.post(
                "https://i.instagram.com/api/v1/media/update_media_with_pdq_hash_info/",
                headers=headers,
                data={"signed_body": signed_body},
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Hash PDQ mis à jour")
                return {"success": True}
            else:
                print(f"⚠️ Erreur PDQ hash: {response.status_code}")
                return {"success": False, "error": f"PDQ hash error: {response.status_code}"}
                
        except Exception as e:
            print(f"⚠️ Erreur PDQ hash: {str(e)}")
            return {"success": False, "error": f"PDQ hash error: {str(e)}"}
    
    def _delete_media(self, media_id: str) -> dict:
        """Supprimer un média par son ID"""
        try:
            user_id = self._get_user_id_from_session()
            
            delete_data = {
                "igtv_feed_preview": "false",
                "media_id": media_id,
                "_uid": user_id,
                "_uuid": self.auth.device_manager.device_info['device_uuid']
            }
            
            signed_body = InstagramEncryption.create_signed_body(delete_data)
            
            headers = {
                "accept-language": "fr-FR, en-US",
                "authorization": self._get_auth_token(),
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "ig-intended-user-id": user_id,
                "ig-u-ds-user-id": user_id,
                "user-agent": self.auth.device_manager.device_info['user_agent'],
                "x-fb-friendly-name": f"IgApi: media/{media_id}/delete/?media_type=PHOTO",
            }
            
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
                    print("✅ Publication supprimée avec succès")
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

    # MÉTHODES ADDITIONNELLES POUR COMPATIBILITÉ COMPLÈTE
    def get_media_info(self, media_input: str) -> dict:
        """Récupérer informations d'un média"""
        try:
            if self.auth.api:
                media_id = self.auth.api.extract_media_id_from_url(media_input)
            else:
                media_id = self._extract_media_id_basic(media_input)
            
            if not media_id:
                return {"success": False, "error": "Media ID non trouvé"}
            
            headers = {
                "user-agent": self.auth.device_manager.device_info['user_agent'],
                "x-ig-app-id": "567067343352427",
                "authorization": self._get_auth_token(),
                "x-ig-android-id": self.auth.device_manager.device_info['android_id'],
                "x-ig-device-id": self.auth.device_manager.device_info['device_uuid'],
            }
            
            response = self.auth.session.get(
                f"https://i.instagram.com/api/v1/media/{media_id}/info/",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                parsed_data = InstagramEncryption.safe_parse_json(response)
                if InstagramEncryption.is_success_response(response, parsed_data):
                    return {"success": True, "data": parsed_data}
                else:
                    return {"success": False, "error": "Média non accessible"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": f"Erreur: {str(e)}"}

    def get_user_media(self, user_input: str, count: int = 12) -> dict:
        """Récupérer les médias d'un utilisateur"""
        try:
            if self.auth.api:
                user_id = self.auth.api.extract_user_id_from_url(user_input)
            else:
                user_id = self._extract_user_id_basic(user_input)
            
            if not user_id:
                return {"success": False, "error": "User ID non trouvé"}
            
            headers = {
                "user-agent": self.auth.device_manager.device_info['user_agent'],
                "x-ig-app-id": "567067343352427",
                "authorization": self._get_auth_token(),
                "x-ig-android-id": self.auth.device_manager.device_info['android_id'],
                "x-ig-device-id": self.auth.device_manager.device_info['device_uuid'],
            }
            
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
                    return {"success": True, "data": parsed_data}
                else:
                    return {"success": False, "error": "Médias non accessibles"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": f"Erreur: {str(e)}"}

    def unfollow_user(self, user_input: str) -> dict:
        """Ne plus suivre un utilisateur"""
        try:
            if self.auth.api:
                user_id = self.auth.api.extract_user_id_from_url(user_input)
            else:
                user_id = self._extract_user_id_basic(user_input)
            
            if not user_id:
                username_match = re.search(r'instagram\.com/([^/?]+)', user_input)
                if username_match:
                    target_username = username_match.group(1).replace('@', '').strip()
                    user_id = self._search_similar_username(target_username)
                
                if not user_id:
                    print("❌ Utilisateur introuvable")
                    return {"success": False, "error": "Utilisateur introuvable"}
            
            current_user_id = self._get_user_id_from_session()
            if not current_user_id:
                return {"success": False, "error": "User ID non trouvé dans la session"}
            
            unfollow_data = {
                "user_id": user_id,
                "radio_type": "wifi-none",
                "_uid": current_user_id,
                "device_id": self.auth.device_manager.device_info['android_id'],
                "_uuid": self.auth.device_manager.device_info['device_uuid'],
                "container_module": "profile"
            }
            
            signed_body = InstagramEncryption.create_signed_body(unfollow_data)
            
            headers = {
                "accept-language": "fr-FR, en-US",
                "authorization": self._get_auth_token(),
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "ig-intended-user-id": current_user_id,
                "ig-u-ds-user-id": current_user_id,
                "user-agent": self.auth.device_manager.device_info['user_agent'],
                "x-fb-friendly-name": f"IgApi: friendships/destroy/{user_id}/",
            }
            
            response = self.auth.session.post(
                f"https://i.instagram.com/api/v1/friendships/destroy/{user_id}/",
                headers=headers,
                data={"signed_body": signed_body},
                timeout=10
            )
            
            if response.status_code == 200:
                parsed_data = InstagramEncryption.safe_parse_json(response)
                
                if InstagramEncryption.is_success_response(response, parsed_data):
                    print("✅ Unfollow réussi")
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
            return {"success": False, "error": f"Erreur unfollow: {str(e)}"}

    def unlike_post(self, media_input: str) -> dict:
        """Retirer le like d'un post"""
        try:
            if self.auth.api:
                media_id = self.auth.api.extract_media_id_from_url(media_input)
            else:
                media_id = self._extract_media_id_basic(media_input)
            
            if not media_id:
                return {"success": False, "error": "Ce media a ete supprime"}
            
            user_id = self._get_user_id_from_session()
            if not user_id:
                return {"success": False, "error": "User ID non trouvé dans la session"}
            
            unlike_data = {
                "media_id": media_id,
                "radio_type": "wifi-none",
                "_uid": user_id,
                "_uuid": self.auth.device_manager.device_info['device_uuid'],
                "container_module": "feed_timeline"
            }
            
            signed_body = InstagramEncryption.create_signed_body(unlike_data)
            
            headers = {
                "accept-language": "fr-FR, en-US",
                "authorization": self._get_auth_token(),
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "ig-intended-user-id": user_id,
                "ig-u-ds-user-id": user_id,
                "user-agent": self.auth.device_manager.device_info['user_agent'],
                "x-fb-friendly-name": f"IgApi: media/{media_id}/unlike/",
            }
            
            response = self.auth.session.post(
                f"https://i.instagram.com/api/v1/media/{media_id}/unlike/",
                headers=headers,
                data={"signed_body": signed_body, "d": "0"},
                timeout=10
            )
            
            if response.status_code == 200:
                parsed_data = InstagramEncryption.safe_parse_json(response)
                
                if InstagramEncryption.is_success_response(response, parsed_data):
                    print("✅ Unlike réussi")
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
            print("❌ Ce media a ete supprime")
            return {"success": False, "error": "Ce media a ete supprime"}
