# -*- coding: utf-8 -*-
"""
Gestionnaire 2FA Alternatif pour Instagram
Gestion complète du flux alternatif avec entrypoint et code_entry
"""

import time
import json
import uuid
import random
import urllib.parse
import re
from ..utils.encryption import InstagramEncryption
from ..utils.device import get_optimal_encoding_for_environment

class AlternativeManager:
    """Gestionnaire du flux 2FA alternatif complet"""
    
    def __init__(self, auth_instance):
        self.auth = auth_instance
        self.challenge_data = {}
    
    def handle_2fa_flow(self, response_text: str) -> dict:
        """Gérer le nouveau flux 2FA alternatif AVEC L'ORDRE CORRECT"""
        try:
            print("\n🔐 2FA DETECTEE")
            print("=" * 50)
            
            # ÉTAPE 1: Extraire le context_data initial de la réponse de login
            initial_context = self._extract_context_from_alternative_response(response_text)
            
            if not initial_context:
                print("❌ Impossible d'extraire le context_data initial")
                return {"success": False, "error": "Context_data initial non trouvé"}
            
            self.challenge_data = {"challenge_context": initial_context}
            
            # ÉTAPE 2: Requête entrypoint_async IMMÉDIATE
            entrypoint_result = self._call_alternative_entrypoint(initial_context)
            
            if not entrypoint_result["success"]:
                return {"success": False, "error": f"Échec entrypoint: {entrypoint_result['error']}"}
            
            # ÉTAPE 3: Appel code_entry DIRECTEMENT après entrypoint (PAS challenge_picker)
            code_entry_result = self._load_direct_code_entry_screen()
            
            if not code_entry_result["success"]:
                return {"success": False, "error": f"Échec code_entry: {code_entry_result['error']}"}
            
            # ÉTAPE 4: Demander le code à l'utilisateur IMMÉDIATEMENT
            print("📱 Un code de vérification a été envoyé")
            return self._handle_alternative_code_verification()
            
        except Exception as e:
            return {"success": False, "error": f"Erreur flux alternatif: {str(e)}"}
    
    def _extract_context_from_alternative_response(self, response_text: str) -> str:
        """Extraire context_data du nouveau flux"""
        try:
            print("🔍 Extraction context_data alternatif...")
            
            # Patterns pour le nouveau flux
            context_patterns = [
                r'"context_data"[^"]*"([A-Za-z0-9+/=_-]{500,}(?:\|[a-zA-Z]+)?)"',
                r'context_data["\\\s:]*([A-Za-z0-9+/=_-]{500,}(?:\|[a-zA-Z]+)?)',
                r'([A-Za-z0-9+/=_-]{500,}\|[a-zA-Z]{4,})'
            ]
            
            for pattern in context_patterns:
                matches = re.findall(pattern, response_text)
                if matches:
                    context = matches[0]
                    # Nettoyer les échappements
                    context = context.replace('\\/', '/').replace('\\"', '"')
                    if len(context) > 500:
                        print(f"✅ Context_data alternatif trouvé: {context[:50]}...{context[-15:]}")
                        return context
            
            # Fallback avec suffixe standard
            fallback = "Adng8k4lYCNZHf6znKemw4Lr5VxOZizmQIzhG0JnvsG4vKXuM78CT2DxDuJ09R8x|aplc"
            print(f"⚠️ Fallback context_data: {fallback}")
            return fallback
            
        except Exception as e:
            print(f"❌ Erreur extraction context alternatif: {e}")
            return "fallback_context_data|aplc"
    
    def _call_alternative_entrypoint(self, context_data: str) -> dict:
        """Appel au entrypoint_async alternatif"""
        try:
            print("📡 Appel entrypoint alternatif...")
            
            current_timestamp = time.time()
            
            entrypoint_params = {
                "client_input_params": {
                    "auth_secure_device_id": "",
                    "accounts_list": [],
                    "has_whatsapp_installed": 0,
                    "family_device_id": self.auth.device_manager.device_info['family_device_id'],
                    "machine_id": self.auth.device_manager.get_x_mid()
                },
                "server_params": {
                    "context_data": context_data,
                    "INTERNAL__latency_qpl_marker_id": 36707139,
                    "INTERNAL__latency_qpl_instance_id": float(f"1.0{random.randint(1000000000000, 9999999999999)}E14"),
                    "device_id": self.auth.device_manager.device_info['device_uuid']
                }
            }
            
            headers = {
                "accept-language": "fr-FR, en-US",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "ig-intended-user-id": "0",
                "priority": "u=3",
                "x-bloks-is-layout-rtl": "false",
                "x-bloks-prism-button-version": "CONTROL",
                "x-bloks-prism-colors-enabled": "false",
                "x-bloks-prism-elevated-background-fix": "false",
                "x-bloks-prism-extended-palette-gray-red": "false",
                "x-bloks-prism-extended-palette-indigo": "false",
                "x-bloks-prism-font-enabled": "false",
                "x-bloks-prism-indigo-link-version": "0",
                "x-bloks-version-id": "ef88cb8e7a6a225af847577c11f18eeccda0582b87e294181c4c7425d28047b1",
                "x-fb-client-ip": "True",
                "x-fb-connection-type": "WIFI",
                "x-fb-friendly-name": "IgApi: bloks/async_action/com.bloks.www.ap.two_step_verification.entrypoint_async/",
                "x-fb-request-analytics-tags": '{"network_tags":{"product":"567067343352427","purpose":"fetch","surface":"undefined","request_category":"api","retry_attempt":"0"}}',
                "x-fb-server-cluster": "True",
                "x-ig-android-id": self.auth.device_manager.device_info['android_id'],
                "x-ig-app-id": "567067343352427",
                "x-ig-app-locale": "fr_FR",
                "x-ig-bandwidth-speed-kbps": "-1.000",
                "x-ig-bandwidth-totalbytes-b": "0",
                "x-ig-bandwidth-totaltime-ms": "0",
                "x-ig-client-endpoint": "com.bloks.www.caa.login.login_homepage",
                "x-ig-capabilities": "3brTv10=",
                "x-ig-connection-type": "WIFI",
                "x-ig-device-id": self.auth.device_manager.device_info['device_uuid'],
                "x-ig-device-locale": "fr_FR",
                "x-ig-family-device-id": self.auth.device_manager.device_info['family_device_id'],
                "x-ig-mapped-locale": "fr_FR",
                "x-ig-timezone-offset": "10800",
                "x-ig-www-claim": "0",
                "x-mid": self.auth.device_manager.get_x_mid(),
                "x-meta-zca": "eyJhbmRyb2lkIjp7ImFrYSI6eyJkYXRhVG9TaWduIjoiIiwiZXJyb3JzIjpbIktFWVNUT1JFX0RJU0FCTEVEX0JZX0NPTkZJRyJdfSwiZ3BpYSI6eyJ0b2tlbiI6IiIsImVycm9ycyI6WyJQTEFZX0lOVEVHUklUWV9ESVNBQkxFRF9CWV9DT05GSUciXX0sInBheWxvYWQiOnsicGx1Z2lucyI6eyJiYXQiOnsic3RhIjoiVW5wbHVnZ2VkIiwibHZsIjo4Mn0sInNjdCI6e319fX19",
                "x-pigeon-rawclienttime": f"{current_timestamp:.3f}",
                "x-pigeon-session-id": f"UFS-{uuid.uuid4()}-0",
                "x-tigon-is-retry": "False",
                "accept-encoding": get_optimal_encoding_for_environment(),
                "user-agent": self.auth.device_manager.device_info['user_agent'],
                "x-fb-conn-uuid-client": str(uuid.uuid4()).replace('-', ''),
                "x-fb-http-engine": "Tigon/MNS/TCP"
            }
            
            payload = f"params={urllib.parse.quote(json.dumps(entrypoint_params, separators=(',', ':')))}&bk_client_context={urllib.parse.quote(json.dumps({'bloks_version': 'ef88cb8e7a6a225af847577c11f18eeccda0582b87e294181c4c7425d28047b1', 'styles_id': 'instagram'}))}&bloks_versioning_id=ef88cb8e7a6a225af847577c11f18eeccda0582b87e294181c4c7425d28047b1"
            
            print("🚀 Envoi requête entrypoint...")
            
            response = self.auth.session.post(
                "https://i.instagram.com/api/v1/bloks/async_action/com.bloks.www.ap.two_step_verification.entrypoint_async/",
                headers=headers,
                data=payload,
                timeout=120
            )
            
            response_text = InstagramEncryption.safe_decode_response(response)
            
            if response.status_code == 200:
                # Mettre à jour le context_data
                new_context = self._extract_context_from_alternative_response(response_text)
                if new_context and len(new_context) > 100:
                    self.challenge_data["challenge_context"] = new_context
                    print("🔄 Context_data mis à jour depuis entrypoint")
                
                print("✅ Entrypoint alternatif réussi")
                return {"success": True, "response": response_text}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": f"Erreur entrypoint: {str(e)}"}
    
    def _load_direct_code_entry_screen(self) -> dict:
        """Charger directement l'écran de saisie du code après entrypoint"""
        try:
            print("📱 Chargement écran saisie code direct...")
            
            current_context = self.challenge_data.get("challenge_context", "")
            
            entry_params = {
                "server_params": {
                    "context_data": current_context,
                    "device_id": self.auth.device_manager.device_info['device_uuid'],
                    "INTERNAL_INFRA_screen_id": "generic_code_entry"
                }
            }
            
            headers = {
                "accept-language": "fr-FR, en-US",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "ig-intended-user-id": "0",
                "priority": "u=3",
                "x-bloks-is-layout-rtl": "false",
                "x-bloks-prism-button-version": "CONTROL",
                "x-bloks-prism-colors-enabled": "false",
                "x-bloks-prism-elevated-background-fix": "false",
                "x-bloks-prism-extended-palette-gray-red": "false",
                "x-bloks-prism-extended-palette-indigo": "false",
                "x-bloks-prism-font-enabled": "false",
                "x-bloks-prism-indigo-link-version": "0",
                "x-bloks-version-id": "ef88cb8e7a6a225af847577c11f18eeccda0582b87e294181c4c7425d28047b1",
                "x-fb-client-ip": "True",
                "x-fb-connection-type": "WIFI",
                "x-fb-friendly-name": "IgApi: bloks/apps/com.bloks.www.ap.two_step_verification.code_entry/",
                "x-fb-request-analytics-tags": '{"network_tags":{"product":"567067343352427","purpose":"fetch","surface":"undefined","request_category":"api","retry_attempt":"0"}}',
                "x-fb-server-cluster": "True",
                "x-ig-android-id": self.auth.device_manager.device_info['android_id'],
                "x-ig-app-id": "567067343352427",
                "x-ig-app-locale": "fr_FR",
                "x-ig-bandwidth-speed-kbps": "-1.000",
                "x-ig-bandwidth-totalbytes-b": "0",
                "x-ig-bandwidth-totaltime-ms": "0",
                "x-ig-client-endpoint": "com.bloks.www.caa.login.login_homepage",
                "x-ig-capabilities": "3brTv10=",
                "x-ig-connection-type": "WIFI",
                "x-ig-device-id": self.auth.device_manager.device_info['device_uuid'],
                "x-ig-device-locale": "fr_FR",
                "x-ig-family-device-id": self.auth.device_manager.device_info['family_device_id'],
                "x-ig-mapped-locale": "fr_FR",
                "x-ig-timezone-offset": "10800",
                "x-ig-www-claim": "0",
                "x-mid": self.auth.device_manager.get_x_mid(),
                "x-pigeon-rawclienttime": f"{time.time():.3f}",
                "x-pigeon-session-id": f"UFS-{uuid.uuid4()}-0",
                "x-tigon-is-retry": "False",
                "accept-encoding": get_optimal_encoding_for_environment(),
                "user-agent": self.auth.device_manager.device_info['user_agent'],
                "x-fb-conn-uuid-client": str(uuid.uuid4()).replace('-', ''),
                "x-fb-http-engine": "Tigon/MNS/TCP"
            }
            
            payload = f"params={urllib.parse.quote(json.dumps(entry_params, separators=(',', ':')))}&bk_client_context={urllib.parse.quote(json.dumps({'bloks_version': 'ef88cb8e7a6a225af847577c11f18eeccda0582b87e294181c4c7425d28047b1', 'styles_id': 'instagram'}))}&bloks_versioning_id=ef88cb8e7a6a225af847577c11f18eeccda0582b87e294181c4c7425d28047b1"
            
            print("🚀 Envoi requête code_entry...")
            
            response = self.auth.session.post(
                "https://i.instagram.com/api/v1/bloks/apps/com.bloks.www.ap.two_step_verification.code_entry/",
                headers=headers,
                data=payload,
                timeout=120
            )
            
            response_text = InstagramEncryption.safe_decode_response(response)
            
            if response.status_code == 200:
                # Mettre à jour context_data final
                final_context = self._extract_context_from_alternative_response(response_text)
                if final_context and len(final_context) > 100:
                    self.challenge_data["challenge_context"] = final_context
                    print("🔄 Context_data final mis à jour")
                
                print("✅ Écran saisie code prêt")
                return {"success": True}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": f"Erreur écran code: {str(e)}"}
    
    def _handle_alternative_code_verification(self) -> dict:
        """Gérer vérification code alternatif AVEC OPTIONS DE CHANGEMENT ET SÉLECTION"""
        try:
            max_retries = 3
            
            for retry_count in range(max_retries):
                if retry_count > 0:
                    print(f"❌ Code incorrect. Tentative {retry_count + 1}/{max_retries}")
                
                print(f"\n🔢 Entrez le code reçu:")
                print("(Le code doit contenir 6 chiffres)")
                print("ℹ️  Tapez 'changer' pour essayer une autre méthode")
                
                try:
                    code = input("Code: ").strip()
                    
                    if not code:
                        print("❌ Code requis")
                        continue
                    
                    # OPTION: Changer de méthode
                    if code.lower() == "changer":
                        return self._change_alternative_verification_method()
                    
                    if not code.isdigit() or len(code) != 6:
                        print("❌ Le code doit contenir exactement 6 chiffres")
                        continue
                    
                    # Vérifier le code
                    result = self._submit_alternative_verification_code(code)
                    
                    if result["success"]:
                        return result
                    elif "incorrect" in result.get("error", "").lower():
                        continue  # Code incorrect, réessayer
                    else:
                        return result  # Autre erreur
                        
                except KeyboardInterrupt:
                    return {"success": False, "error": "Annulé par l'utilisateur"}
            
            return {"success": False, "error": "Trop de tentatives de code incorrect"}
            
        except Exception as e:
            return {"success": False, "error": f"Erreur vérification: {str(e)}"}
    
    def _change_alternative_verification_method(self) -> dict:
        """NOUVELLE FONCTION: Changer de méthode dans le flux alternatif"""
        try:
            print("🔄 CHANGEMENT DE MÉTHODE DE VÉRIFICATION")
            
            current_context = self.challenge_data.get("challenge_context", "")
            
            # REQUÊTE "is_try_another_way" comme dans l'exemple
            another_way_params = {
                "client_input_params": {},
                "server_params": {
                    "context_data": current_context,
                    "INTERNAL__latency_qpl_marker_id": 36707139,
                    "INTERNAL__latency_qpl_instance_id": float(f"1.0{random.randint(1000000000000, 9999999999999)}E14"),
                    "device_id": self.auth.device_manager.device_info['device_uuid'],
                    "is_try_another_way": 1  # CLEF IMPORTANTE
                }
            }
            
            headers = {
                "accept-language": "fr-FR, en-US",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "ig-intended-user-id": "0",
                "priority": "u=3",
                "x-bloks-is-layout-rtl": "false",
                "x-bloks-prism-button-version": "CONTROL",
                "x-bloks-prism-colors-enabled": "false",
                "x-bloks-prism-elevated-background-fix": "false",
                "x-bloks-prism-extended-palette-gray-red": "false",
                "x-bloks-prism-extended-palette-indigo": "false",
                "x-bloks-prism-font-enabled": "false",
                "x-bloks-prism-indigo-link-version": "0",
                "x-bloks-version-id": "ef88cb8e7a6a225af847577c11f18eeccda0582b87e294181c4c7425d28047b1",
                "x-fb-client-ip": "True",
                "x-fb-connection-type": "WIFI",
                "x-fb-friendly-name": "IgApi: bloks/async_action/com.bloks.www.ap.two_step_verification.code_entry_async/",
                "x-fb-request-analytics-tags": '{"network_tags":{"product":"567067343352427","purpose":"fetch","surface":"undefined","request_category":"api","retry_attempt":"0"}}',
                "x-fb-server-cluster": "True",
                "x-ig-android-id": self.auth.device_manager.device_info['android_id'],
                "x-ig-app-id": "567067343352427",
                "x-ig-app-locale": "fr_FR",
                "x-ig-bandwidth-speed-kbps": "-1.000",
                "x-ig-bandwidth-totalbytes-b": "0",
                "x-ig-bandwidth-totaltime-ms": "0",
                "x-ig-client-endpoint": "com.bloks.www.ap.two_step_verification.code_entry",
                "x-ig-capabilities": "3brTv10=",
                "x-ig-connection-type": "WIFI",
                "x-ig-device-id": self.auth.device_manager.device_info['device_uuid'],
                "x-ig-device-locale": "fr_FR",
                "x-ig-family-device-id": self.auth.device_manager.device_info['family_device_id'],
                "x-ig-mapped-locale": "fr_FR",
                "x-ig-timezone-offset": "10800",
                "x-ig-www-claim": "0",
                "x-mid": self.auth.device_manager.get_x_mid(),
                "x-pigeon-rawclienttime": f"{time.time():.3f}",
                "x-pigeon-session-id": f"UFS-{uuid.uuid4()}-0",
                "x-tigon-is-retry": "False",
                "accept-encoding": get_optimal_encoding_for_environment(),
                "user-agent": self.auth.device_manager.device_info['user_agent'],
                "x-fb-conn-uuid-client": str(uuid.uuid4()).replace('-', ''),
                "x-fb-http-engine": "Tigon/MNS/TCP"
            }
            
            payload = f"params={urllib.parse.quote(json.dumps(another_way_params, separators=(',', ':')))}&bk_client_context={urllib.parse.quote(json.dumps({'bloks_version': 'ef88cb8e7a6a225af847577c11f18eeccda0582b87e294181c4c7425d28047b1', 'styles_id': 'instagram'}))}&bloks_versioning_id=ef88cb8e7a6a225af847577c11f18eeccda0582b87e294181c4c7425d28047b1"
            
            print("🔄 Essai autre méthode...")
            
            response = self.auth.session.post(
                "https://i.instagram.com/api/v1/bloks/async_action/com.bloks.www.ap.two_step_verification.code_entry_async/",
                headers=headers,
                data=payload,
                timeout=120
            )
            
            response_text = InstagramEncryption.safe_decode_response(response)
            
            if response.status_code == 200:
                # Mettre à jour context et récupérer les méthodes
                new_context = self._extract_context_from_alternative_response(response_text)
                if new_context:
                    self.challenge_data["challenge_context"] = new_context
                
                # Maintenant récupérer les méthodes disponibles
                methods_result = self._get_alternative_verification_methods(self.challenge_data["challenge_context"])
                
                if methods_result["success"]:
                    # Afficher les méthodes à l'utilisateur et lui demander de choisir
                    selected_method = self._show_alternative_method_selection(methods_result["methods"])
                    
                    if selected_method:
                        # Soumettre le choix
                        choice_result = self._submit_alternative_method_choice(selected_method)
                        
                        if choice_result["success"]:
                            # Charger l'écran de code et demander le code
                            code_screen_result = self._load_alternative_code_entry_screen()
                            
                            if code_screen_result["success"]:
                                # Maintenant demander le code avec la nouvelle méthode
                                return self._handle_alternative_code_verification()
                            else:
                                return {"success": False, "error": f"Échec écran code: {code_screen_result['error']}"}
                        else:
                            return {"success": False, "error": f"Échec choix: {choice_result['error']}"}
                    else:
                        return {"success": False, "error": "Aucune méthode sélectionnée"}
                else:
                    return {"success": False, "error": f"Échec récupération méthodes: {methods_result['error']}"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": f"Erreur changement méthode: {str(e)}"}
    
    def _get_alternative_verification_methods(self, context_data: str) -> dict:
        """Récupérer les méthodes via challenge_picker alternatif"""
        try:
            print("🔍 Récupération méthodes alternatives...")
            
            picker_params = {
                "server_params": {
                    "context_data": context_data,
                    "device_id": self.auth.device_manager.device_info['device_uuid'],
                    "INTERNAL_INFRA_screen_id": "method_picker"
                }
            }
            
            headers = {
                "accept-language": "fr-FR, en-US",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "ig-intended-user-id": "0",
                "priority": "u=3",
                "x-bloks-is-layout-rtl": "false",
                "x-bloks-prism-button-version": "CONTROL",
                "x-bloks-prism-colors-enabled": "false",
                "x-bloks-prism-elevated-background-fix": "false",
                "x-bloks-prism-extended-palette-gray-red": "false",
                "x-bloks-prism-extended-palette-indigo": "false",
                "x-bloks-prism-font-enabled": "false",
                "x-bloks-prism-indigo-link-version": "0",
                "x-bloks-version-id": "ef88cb8e7a6a225af847577c11f18eeccda0582b87e294181c4c7425d28047b1",
                "x-fb-client-ip": "True",
                "x-fb-connection-type": "WIFI",
                "x-fb-friendly-name": "IgApi: bloks/apps/com.bloks.www.ap.two_step_verification.challenge_picker/",
                "x-fb-request-analytics-tags": '{"network_tags":{"product":"567067343352427","purpose":"fetch","surface":"undefined","request_category":"api","retry_attempt":"0"}}',
                "x-fb-server-cluster": "True",
                "x-ig-android-id": self.auth.device_manager.device_info['android_id'],
                "x-ig-app-id": "567067343352427",
                "x-ig-app-locale": "fr_FR",
                "x-ig-bandwidth-speed-kbps": "-1.000",
                "x-ig-bandwidth-totalbytes-b": "0",
                "x-ig-bandwidth-totaltime-ms": "0",
                "x-ig-client-endpoint": "com.bloks.www.ap.two_step_verification.code_entry",
                "x-ig-capabilities": "3brTv10=",
                "x-ig-connection-type": "WIFI",
                "x-ig-device-id": self.auth.device_manager.device_info['device_uuid'],
                "x-ig-device-locale": "fr_FR",
                "x-ig-family-device-id": self.auth.device_manager.device_info['family_device_id'],
                "x-ig-mapped-locale": "fr_FR",
                "x-ig-timezone-offset": "10800",
                "x-ig-www-claim": "0",
                "x-mid": self.auth.device_manager.get_x_mid(),
                "x-pigeon-rawclienttime": f"{time.time():.3f}",
                "x-pigeon-session-id": f"UFS-{uuid.uuid4()}-0",
                "x-tigon-is-retry": "False",
                "accept-encoding": get_optimal_encoding_for_environment(),
                "user-agent": self.auth.device_manager.device_info['user_agent'],
                "x-fb-conn-uuid-client": str(uuid.uuid4()).replace('-', ''),
                "x-fb-http-engine": "Tigon/MNS/TCP"
            }
            
            payload = f"params={urllib.parse.quote(json.dumps(picker_params, separators=(',', ':')))}&bk_client_context={urllib.parse.quote(json.dumps({'bloks_version': 'ef88cb8e7a6a225af847577c11f18eeccda0582b87e294181c4c7425d28047b1', 'styles_id': 'instagram'}))}&bloks_versioning_id=ef88cb8e7a6a225af847577c11f18eeccda0582b87e294181c4c7425d28047b1"
            
            response = self.auth.session.post(
                "https://i.instagram.com/api/v1/bloks/apps/com.bloks.www.ap.two_step_verification.challenge_picker/",
                headers=headers,
                data=payload,
                timeout=15
            )
            
            response_text = InstagramEncryption.safe_decode_response(response)
            
            if response.status_code == 200:
                # Mettre à jour context_data et extraire méthodes
                new_context = self._extract_context_from_alternative_response(response_text)
                if new_context and len(new_context) > 100:
                    self.challenge_data["challenge_context"] = new_context
                
                methods = self._extract_alternative_verification_methods(response_text)
                return {"success": True, "methods": methods}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": f"Erreur méthodes: {str(e)}"}
    
    def _extract_alternative_verification_methods(self, response_text: str) -> list:
        """Extraire les méthodes du challenge_picker alternatif"""
        try:
            methods = []
            
            print("🔍 Extraction méthodes alternatives...")
            
            # Rechercher SMS
            sms_patterns = [
                r'Texto.*?(\+\d{1,3}\s+\*+\s+\*+\s+\*+\s+\d{2})',
                r'SMS.*?(\+\d{1,3}\s+\*+\s+\*+\s+\*+\s+\d{2})',
                r'(\+\d{1,3}\s+\*+\s+\*+\s+\*+\s+\d{2})'
            ]
            
            for pattern in sms_patterns:
                matches = re.findall(pattern, response_text)
                for match in matches:
                    if match not in [m.get("value") for m in methods]:
                        methods.append({
                            "id": "SMS",
                            "type": "sms",
                            "label": f"SMS au {match}",
                            "value": match
                        })
                        print(f"📱 SMS alternatif trouvé: {match}")
                        break
            
            # Rechercher Email
            email_patterns = [
                r'Email.*?([a-zA-Z0-9]\*+[a-zA-Z0-9]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
                r'([a-zA-Z0-9]\*+[a-zA-Z0-9]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
            ]
            
            for pattern in email_patterns:
                matches = re.findall(pattern, response_text)
                for match in matches:
                    if match not in [m.get("value") for m in methods]:
                        methods.append({
                            "id": "EMAIL",
                            "type": "email", 
                            "label": f"Email à {match}",
                            "value": match
                        })
                        print(f"📧 Email alternatif trouvé: {match}")
                        break
            
            # Rechercher WhatsApp (si mentionné avec google_oauth_token)
            if "google_oauth_token" in response_text and any(m["type"] == "sms" for m in methods):
                sms_number = next(m["value"] for m in methods if m["type"] == "sms")
                methods.append({
                    "id": "WHATSAPP",
                    "type": "whatsapp",
                    "label": f"WhatsApp au {sms_number}",
                    "value": sms_number
                })
                print(f"💬 WhatsApp alternatif trouvé: {sms_number}")
            
            return methods
            
        except Exception as e:
            print(f"❌ Erreur extraction méthodes alternatives: {e}")
            return []
    
    def _show_alternative_method_selection(self, methods: list) -> dict:
        """Afficher sélection méthodes alternatives AVEC CHOIX UTILISATEUR"""
        try:
            if not methods:
                print("❌ Aucune méthode alternative disponible")
                return None
            
            print("\n📱 MÉTHODES DE VÉRIFICATION DISPONIBLES:")
            print("=" * 60)
            
            for i, method in enumerate(methods):
                emoji = "📱" if method["type"] == "sms" else "📧" if method["type"] == "email" else "💬"
                print(f"{i+1}. {emoji} {method['label']}")
            
            print(f"{len(methods)+1}. 🚪 Quitter et changer de compte")
            
            while True:
                try:
                    max_choice = len(methods) + 1
                    choice_input = input(f"\n🎯 Choisissez une méthode (1-{max_choice}): ").strip()
                    choice_index = int(choice_input) - 1
                    
                    if choice_index == len(methods):
                        return {"success": False, "error": "restart_login", "restart_requested": True}
                    elif 0 <= choice_index < len(methods):
                        selected_method = methods[choice_index]
                        print(f"✅ Méthode sélectionnée: {selected_method['label']}")
                        return selected_method
                    else:
                        print("❌ Choix invalide, réessayez")
                        
                except ValueError:
                    print("❌ Veuillez entrer un numéro valide")
                except KeyboardInterrupt:
                    return None
                    
        except Exception as e:
            print(f"❌ Erreur sélection alternative: {e}")
            return None
    
    def _submit_alternative_method_choice(self, selected_method: dict) -> dict:
        """Soumettre choix méthode alternative"""
        try:
            print(f"🚀 Soumission choix alternatif: {selected_method['label']}")
            
            current_context = self.challenge_data.get("challenge_context", "")
            
            choice_params = {
                "client_input_params": {
                    "selected_challenge": selected_method["id"]
                },
                "server_params": {
                    "context_data": current_context,
                    "INTERNAL__latency_qpl_marker_id": 36707139,
                    "INTERNAL__latency_qpl_instance_id": float(f"1.0{random.randint(1000000000000, 9999999999999)}E14"),
                    "device_id": self.auth.device_manager.device_info['device_uuid']
                }
            }
            
            headers = {
                "accept-language": "fr-FR, en-US",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "ig-intended-user-id": "0",
                "priority": "u=3",
                "x-bloks-is-layout-rtl": "false",
                "x-bloks-prism-button-version": "CONTROL",
                "x-bloks-prism-colors-enabled": "false",
                "x-bloks-prism-elevated-background-fix": "false",
                "x-bloks-prism-extended-palette-gray-red": "false",
                "x-bloks-prism-extended-palette-indigo": "false",
                "x-bloks-prism-font-enabled": "false",
                "x-bloks-prism-indigo-link-version": "0",
                "x-bloks-version-id": "ef88cb8e7a6a225af847577c11f18eeccda0582b87e294181c4c7425d28047b1",
                "x-fb-client-ip": "True",
                "x-fb-connection-type": "WIFI",
                "x-fb-friendly-name": "IgApi: bloks/async_action/com.bloks.www.bloks.ap.two_step_verification.challenge_picker.async/",
                "x-fb-request-analytics-tags": '{"network_tags":{"product":"567067343352427","purpose":"fetch","surface":"undefined","request_category":"api","retry_attempt":"0"}}',
                "x-fb-server-cluster": "True",
                "x-ig-android-id": self.auth.device_manager.device_info['android_id'],
                "x-ig-app-id": "567067343352427",
                "x-ig-app-locale": "fr_FR",
                "x-ig-bandwidth-speed-kbps": "-1.000",
                "x-ig-bandwidth-totalbytes-b": "0",
                "x-ig-bandwidth-totaltime-ms": "0",
                "x-ig-client-endpoint": "com.bloks.www.ap.two_step_verification.challenge_picker",
                "x-ig-capabilities": "3brTv10=",
                "x-ig-connection-type": "WIFI",
                "x-ig-device-id": self.auth.device_manager.device_info['device_uuid'],
                "x-ig-device-locale": "fr_FR",
                "x-ig-family-device-id": self.auth.device_manager.device_info['family_device_id'],
                "x-ig-mapped-locale": "fr_FR",
                "x-ig-timezone-offset": "10800",
                "x-ig-www-claim": "0",
                "x-mid": self.auth.device_manager.get_x_mid(),
                "x-pigeon-rawclienttime": f"{time.time():.3f}",
                "x-pigeon-session-id": f"UFS-{uuid.uuid4()}-0",
                "x-tigon-is-retry": "False",
                "accept-encoding": get_optimal_encoding_for_environment(),
                "user-agent": self.auth.device_manager.device_info['user_agent'],
                "x-fb-conn-uuid-client": str(uuid.uuid4()).replace('-', ''),
                "x-fb-http-engine": "Tigon/MNS/TCP"
            }
            
            payload = f"params={urllib.parse.quote(json.dumps(choice_params, separators=(',', ':')))}&bk_client_context={urllib.parse.quote(json.dumps({'bloks_version': 'ef88cb8e7a6a225af847577c11f18eeccda0582b87e294181c4c7425d28047b1', 'styles_id': 'instagram'}))}&bloks_versioning_id=ef88cb8e7a6a225af847577c11f18eeccda0582b87e294181c4c7425d28047b1"
            
            response = self.auth.session.post(
                "https://i.instagram.com/api/v1/bloks/async_action/com.bloks.www.bloks.ap.two_step_verification.challenge_picker.async/",
                headers=headers,
                data=payload,
                timeout=15
            )
            
            response_text = InstagramEncryption.safe_decode_response(response)
            
            if response.status_code == 200:
                # Mettre à jour context_data et lancer écran code
                new_context = self._extract_context_from_alternative_response(response_text)
                if new_context and len(new_context) > 100:
                    self.challenge_data["challenge_context"] = new_context
                
                # Appeler écran de saisie code
                code_screen_result = self._load_alternative_code_entry_screen()
                return code_screen_result
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": f"Erreur choix alternatif: {str(e)}"}
    
    def _load_alternative_code_entry_screen(self) -> dict:
        """Charger écran saisie code alternatif"""
        try:
            print("📱 Chargement écran saisie code alternatif...")
            
            current_context = self.challenge_data.get("challenge_context", "")
            
            entry_params = {
                "server_params": {
                    "context_data": current_context,
                    "device_id": self.auth.device_manager.device_info['device_uuid'],
                    "INTERNAL_INFRA_screen_id": "generic_code_entry"
                }
            }
            
            headers = {
                "accept-language": "fr-FR, en-US",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "ig-intended-user-id": "0",
                "priority": "u=3",
                "x-bloks-is-layout-rtl": "false",
                "x-bloks-prism-button-version": "CONTROL",
                "x-bloks-prism-colors-enabled": "false",
                "x-bloks-prism-elevated-background-fix": "false",
                "x-bloks-prism-extended-palette-gray-red": "false",
                "x-bloks-prism-extended-palette-indigo": "false",
                "x-bloks-prism-font-enabled": "false",
                "x-bloks-prism-indigo-link-version": "0",
                "x-bloks-version-id": "ef88cb8e7a6a225af847577c11f18eeccda0582b87e294181c4c7425d28047b1",
                "x-fb-client-ip": "True",
                "x-fb-connection-type": "WIFI",
                "x-fb-friendly-name": "IgApi: bloks/apps/com.bloks.www.ap.two_step_verification.code_entry/",
                "x-fb-request-analytics-tags": '{"network_tags":{"product":"567067343352427","purpose":"fetch","surface":"undefined","request_category":"api","retry_attempt":"0"}}',
                "x-fb-server-cluster": "True",
                "x-ig-android-id": self.auth.device_manager.device_info['android_id'],
                "x-ig-app-id": "567067343352427",
                "x-ig-app-locale": "fr_FR",
                "x-ig-bandwidth-speed-kbps": "-1.000",
                "x-ig-bandwidth-totalbytes-b": "0",
                "x-ig-bandwidth-totaltime-ms": "0",
                "x-ig-client-endpoint": "com.bloks.www.ap.two_step_verification.challenge_picker",
                "x-ig-capabilities": "3brTv10=",
                "x-ig-connection-type": "WIFI",
                "x-ig-device-id": self.auth.device_manager.device_info['device_uuid'],
                "x-ig-device-locale": "fr_FR",
                "x-ig-family-device-id": self.auth.device_manager.device_info['family_device_id'],
                "x-ig-mapped-locale": "fr_FR",
                "x-ig-timezone-offset": "10800",
                "x-ig-www-claim": "0",
                "x-mid": self.auth.device_manager.get_x_mid(),
                "x-pigeon-rawclienttime": f"{time.time():.3f}",
                "x-pigeon-session-id": f"UFS-{uuid.uuid4()}-0",
                "x-tigon-is-retry": "False",
                "accept-encoding": get_optimal_encoding_for_environment(),
                "user-agent": self.auth.device_manager.device_info['user_agent'],
                "x-fb-conn-uuid-client": str(uuid.uuid4()).replace('-', ''),
                "x-fb-http-engine": "Tigon/MNS/TCP"
            }
            
            payload = f"params={urllib.parse.quote(json.dumps(entry_params, separators=(',', ':')))}&bk_client_context={urllib.parse.quote(json.dumps({'bloks_version': 'ef88cb8e7a6a225af847577c11f18eeccda0582b87e294181c4c7425d28047b1', 'styles_id': 'instagram'}))}&bloks_versioning_id=ef88cb8e7a6a225af847577c11f18eeccda0582b87e294181c4c7425d28047b1"
            
            response = self.auth.session.post(
                "https://i.instagram.com/api/v1/bloks/apps/com.bloks.www.ap.two_step_verification.code_entry/",
                headers=headers,
                data=payload,
                timeout=120
            )
            
            response_text = InstagramEncryption.safe_decode_response(response)
            
            if response.status_code == 200:
                # Mettre à jour context_data final
                final_context = self._extract_context_from_alternative_response(response_text)
                if final_context and len(final_context) > 100:
                    self.challenge_data["challenge_context"] = final_context
                
                print("✅ Écran saisie code alternatif prêt")
                return {"success": True}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": f"Erreur écran code: {str(e)}"}
    
    def _submit_alternative_verification_code(self, code: str) -> dict:
        """Soumettre code vérification alternatif"""
        try:
            print(f"🔢 Vérification code alternatif: {code}")
            
            current_context = self.challenge_data.get("challenge_context", "")
            
            code_params = {
                "client_input_params": {
                    "auth_secure_device_id": "",
                    "code": code,
                    "family_device_id": self.auth.device_manager.device_info['family_device_id'],
                    "device_id": self.auth.device_manager.device_info['android_id'],
                    "machine_id": self.auth.device_manager.get_x_mid()
                },
                "server_params": {
                    "context_data": current_context,
                    "INTERNAL__latency_qpl_marker_id": 36707139,
                    "INTERNAL__latency_qpl_instance_id": float(f"1.0{random.randint(1000000000000, 9999999999999)}E14"),
                    "device_id": self.auth.device_manager.device_info['device_uuid']
                }
            }
            
            headers = {
                "accept-language": "fr-FR, en-US",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "ig-intended-user-id": "0",
                "priority": "u=3",
                "x-bloks-is-layout-rtl": "false",
                "x-bloks-prism-button-version": "CONTROL",
                "x-bloks-prism-colors-enabled": "false",
                "x-bloks-prism-elevated-background-fix": "false",
                "x-bloks-prism-extended-palette-gray-red": "false",
                "x-bloks-prism-extended-palette-indigo": "false",
                "x-bloks-prism-font-enabled": "false",
                "x-bloks-prism-indigo-link-version": "0",
                "x-bloks-version-id": "ef88cb8e7a6a225af847577c11f18eeccda0582b87e294181c4c7425d28047b1",
                "x-fb-client-ip": "True",
                "x-fb-connection-type": "WIFI",
                "x-fb-friendly-name": "IgApi: bloks/async_action/com.bloks.www.ap.two_step_verification.code_entry_async/",
                "x-fb-request-analytics-tags": '{"network_tags":{"product":"567067343352427","purpose":"fetch","surface":"undefined","request_category":"api","retry_attempt":"0"}}',
                "x-fb-server-cluster": "True",
                "x-ig-android-id": self.auth.device_manager.device_info['android_id'],
                "x-ig-app-id": "567067343352427",
                "x-ig-app-locale": "fr_FR",
                "x-ig-bandwidth-speed-kbps": "-1.000",
                "x-ig-bandwidth-totalbytes-b": "0",
                "x-ig-bandwidth-totaltime-ms": "0",
                "x-ig-client-endpoint": "com.bloks.www.ap.two_step_verification.code_entry",
                "x-ig-capabilities": "3brTv10=",
                "x-ig-connection-type": "WIFI",
                "x-ig-device-id": self.auth.device_manager.device_info['device_uuid'],
                "x-ig-device-locale": "fr_FR",
                "x-ig-family-device-id": self.auth.device_manager.device_info['family_device_id'],
                "x-ig-mapped-locale": "fr_FR",
                "x-ig-timezone-offset": "10800",
                "x-ig-www-claim": "0",
                "x-mid": self.auth.device_manager.get_x_mid(),
                "x-pigeon-rawclienttime": f"{time.time():.3f}",
                "x-pigeon-session-id": f"UFS-{uuid.uuid4()}-0",
                "x-tigon-is-retry": "False",
                "accept-encoding": get_optimal_encoding_for_environment(),
                "user-agent": self.auth.device_manager.device_info['user_agent'],
                "x-fb-conn-uuid-client": str(uuid.uuid4()).replace('-', ''),
                "x-fb-http-engine": "Tigon/MNS/TCP"
            }
            
            payload = f"params={urllib.parse.quote(json.dumps(code_params, separators=(',', ':')))}&bk_client_context={urllib.parse.quote(json.dumps({'bloks_version': 'ef88cb8e7a6a225af847577c11f18eeccda0582b87e294181c4c7425d28047b1', 'styles_id': 'instagram'}))}&bloks_versioning_id=ef88cb8e7a6a225af847577c11f18eeccda0582b87e294181c4c7425d28047b1"
            
            print("🚀 Verification en Cours... ♻")
            
            response = self.auth.session.post(
                "https://i.instagram.com/api/v1/bloks/async_action/com.bloks.www.ap.two_step_verification.code_entry_async/",
                headers=headers,
                data=payload,
                timeout=120
            )
            
            response_text = InstagramEncryption.safe_decode_response(response)
            
            if response.status_code == 200:
                # Vérifier si code incorrect
                if "Error during code validation" in response_text or "incorrect" in response_text.lower():
                    return {"success": False, "error": "Code incorrect"}
                
                # Utiliser la nouvelle fonction de vérification avec le décodage existant
                parsed_data = InstagramEncryption.safe_parse_json(response)
                verification_result = self._verify_2fa_login_success(response_text, parsed_data)
                
                if verification_result["success"]:
                    print("🎉 CODE VÉRIFIÉ AVEC SUCCÈS (ALTERNATIF)!")
                    return {
                        "success": True,
                        "message": verification_result["message"],
                        "data": {
                            "user_data": verification_result["user_data"],
                            "session_data": verification_result["session_data"]
                        },
                        "status": verification_result.get("status", "active")
                    }
                else:
                    return {"success": False, "error": "Code incorrect"}
            else:
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            return {"success": False, "error": f"Erreur code alternatif: {str(e)}"}
    
    def _verify_2fa_login_success(self, response_text: str, parsed_data: dict = None) -> dict:
        """Vérifier le succès de connexion après 2FA alternatif"""
        try:
            if parsed_data is None:
                try:
                    parsed_data = json.loads(response_text)
                except json.JSONDecodeError:
                    parsed_data = {"raw_text": response_text}
                except Exception:
                    parsed_data = {}
            
            # Vérifier si la connexion a réussi
            if not self.auth._check_login_success(parsed_data):
                return {"success": False, "error": "Connexion 2FA échouée"}
            
            # Extraire les données utilisateur
            user_data = self.auth._extract_user_data_fixed(response_text)
            
            # Créer un objet response simulé
            class MockResponse:
                def __init__(self, text, cookies_dict=None):
                    self.text = text
                    self.cookies = MockCookies(cookies_dict or {})
                    self.headers = {}
                    self.status_code = 200
                    
            class MockCookies:
                def __init__(self, cookies_dict):
                    self._cookies = cookies_dict
                    
                def __iter__(self):
                    for name, value in self._cookies.items():
                        yield MockCookie(name, value)
                        
            class MockCookie:
                def __init__(self, name, value):
                    self.name = name
                    self.value = value
            
            mock_response = MockResponse(response_text, self.auth.session.cookies.get_dict())
            
            # Extraire les données de session
            session_data = self.auth._extract_session_data_fixed(mock_response, user_data)
            
            # Vérifier le statut du compte
            username = user_data.get("username", "user_from_2fa")
            password_placeholder = "password_from_2fa"
            
            temp_result = {
                "success": True,
                "message": "2FA vérifié avec succès",
                "user_data": user_data,
                "session_data": session_data
            }
            
            final_result = self.auth.check_account_status_after_login(username, password_placeholder, temp_result)
            
            # Sauvegarder la session
            if final_result.get("status") != "disabled":
                self.auth._save_session_fixed(username, session_data, user_data)
            
            return final_result
            
        except Exception as e:
            print(f"❌ Erreur vérification 2FA alternatif: {str(e)}")
            return {"success": False, "error": f"Erreur vérification 2FA: {str(e)}"}
