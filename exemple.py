# -*- coding: utf-8 -*-
"""
🤖 INSTAGRAM BOT COMPLET - insta_kendou
Interface colorée avec toutes les fonctionnalités

Code d'accès obligatoire pour utiliser la bibliothèque
"""

from insta_kendou import InstagramClient
import os
import glob
import json
import time

# CODE D'ACCÈS OBLIGATOIRE - NÉCESSAIRE POUR UTILISER LA BIBLIOTHÈQUE
ACCESS_CODE = "MampifalyfelicienKennyNestinFoad56266325$17Mars2004FeliciteGemmellineNestine"

# Couleurs pour l'interface
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    ORANGE = '\033[38;5;208m'

def print_colored(text, color):
    """Afficher du texte coloré"""
    print(f"{color}{text}{Colors.RESET}")

def print_header(title):
    """Afficher un en-tête stylé"""
    print(f"\n{Colors.CYAN}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.WHITE}{title.center(60)}{Colors.RESET}")
    print(f"{Colors.CYAN}{'=' * 60}{Colors.RESET}")

def print_success(message):
    """Afficher un message de succès"""
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")

def print_error(message):
    """Afficher un message d'erreur"""
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")

def print_warning(message):
    """Afficher un avertissement"""
    print(f"{Colors.YELLOW}⚠️ {message}{Colors.RESET}")

def print_info(message):
    """Afficher une information"""
    print(f"{Colors.BLUE}ℹ️ {message}{Colors.RESET}")

def print_media_id(media_id):
    """Afficher un Media ID stylé"""
    print(f"{Colors.PURPLE}MEDIA ID{Colors.RESET}: {Colors.WHITE}{media_id}{Colors.RESET}")

def print_user_id(user_id):
    """Afficher un User ID stylé"""
    print(f"{Colors.PURPLE}USER ID{Colors.RESET}: {Colors.WHITE}{user_id}{Colors.RESET}")

def get_connected_accounts():
    """Récupérer la liste des comptes connectés"""
    accounts = []
    sessions_dir = "sessions"
    
    if os.path.exists(sessions_dir):
        session_files = glob.glob(os.path.join(sessions_dir, "*_ig_complete.json"))
        
        for file_path in session_files:
            try:
                filename = os.path.basename(file_path)
                username = filename.replace("_ig_complete.json", "")
                
                # Vérifier la validité du fichier
                with open(file_path, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                    
                user_data = session_data.get("user_data", {}) or session_data.get("logged_in_user", {})
                full_name = user_data.get("full_name", "")
                is_private = user_data.get("is_private", False)
                is_verified = user_data.get("is_verified", False)
                
                accounts.append({
                    "username": username,
                    "full_name": full_name,
                    "is_private": is_private,
                    "is_verified": is_verified,
                    "file_path": file_path
                })
            except Exception:
                continue
    
    return accounts

def show_accounts_menu():
    """Afficher le menu des comptes connectés"""
    accounts = get_connected_accounts()
    
    print_header("COMPTES CONNECTÉS")
    
    if not accounts:
        print_warning("Aucun compte connecté trouvé")
        return None
    
    print(f"{Colors.CYAN}📱 Comptes disponibles:{Colors.RESET}")
    for i, account in enumerate(accounts, 1):
        verified = f" {Colors.GREEN}✅{Colors.RESET}" if account['is_verified'] else ""
        private = f" {Colors.YELLOW}🔒{Colors.RESET}" if account['is_private'] else ""
        full_name = f" - {account['full_name']}" if account['full_name'] else ""
        
        print(f"{Colors.WHITE}{i:2d}.{Colors.RESET} {Colors.BOLD}@{account['username']}{Colors.RESET}{verified}{private}{full_name}")
    
    print(f"{Colors.RED}{len(accounts)+1:2d}. 🗑️  Supprimer un compte{Colors.RESET}")
    print(f"{Colors.BLUE}{len(accounts)+2:2d}. 🔙 Retour{Colors.RESET}")
    
    try:
        choice = int(input(f"\n{Colors.CYAN}🎯 Choisissez un compte: {Colors.RESET}")) - 1
        
        if choice == len(accounts):  # Supprimer
            return handle_delete_account(accounts)
        elif choice == len(accounts) + 1:  # Retour
            return None
        elif 0 <= choice < len(accounts):
            return accounts[choice]['username']
        else:
            print_error("Choix invalide")
            return None
    except (ValueError, KeyboardInterrupt):
        return None

def handle_delete_account(accounts):
    """Gérer la suppression d'un compte"""
    print_header("SUPPRIMER UN COMPTE")
    
    for i, account in enumerate(accounts, 1):
        print(f"{Colors.WHITE}{i:2d}.{Colors.RESET} @{account['username']}")
    
    print(f"{Colors.BLUE}{len(accounts)+1:2d}. 🔙 Annuler{Colors.RESET}")
    
    try:
        choice = int(input(f"\n{Colors.RED}🗑️  Compte à supprimer: {Colors.RESET}")) - 1
        
        if choice == len(accounts):  # Annuler
            return None
        elif 0 <= choice < len(accounts):
            account = accounts[choice]
            confirm = input(f"{Colors.RED}⚠️  Confirmer suppression de @{account['username']}? (oui/non): {Colors.RESET}").strip().lower()
            
            if confirm in ['oui', 'o', 'yes', 'y']:
                try:
                    os.remove(account['file_path'])
                    print_success(f"Compte @{account['username']} supprimé")
                except Exception as e:
                    print_error(f"Erreur suppression: {e}")
            else:
                print_info("Suppression annulée")
            return None
        else:
            print_error("Choix invalide")
            return None
    except (ValueError, KeyboardInterrupt):
        return None

def login_or_load_session():
    """Connexion ou chargement de session"""
    print_header("🔐 CONNEXION INSTAGRAM")
    
    # Vérifier s'il y a des comptes connectés
    accounts = get_connected_accounts()
    
    if accounts:
        print(f"{Colors.GREEN}📱 Comptes disponibles trouvés{Colors.RESET}")
        print(f"{Colors.BLUE}1.{Colors.RESET} Utiliser un compte existant")
        print(f"{Colors.CYAN}2.{Colors.RESET} Nouvelle connexion")
        
        try:
            choice = input(f"\n{Colors.CYAN}🎯 Votre choix: {Colors.RESET}").strip()
            
            if choice == "1":
                username = show_accounts_menu()
                if username:
                    client = InstagramClient()
                    session_data = client.load_session(username)
                    if session_data:
                        print_success(f"Session chargée pour @{username}")
                        return client, username
                    else:
                        print_error(f"Impossible de charger la session pour @{username}")
                        return None, None
        except KeyboardInterrupt:
            return None, None
    
    # Nouvelle connexion
    client = InstagramClient()
    
    while True:
        try:
            username = input(f"{Colors.CYAN}👤 Nom d'utilisateur Instagram: {Colors.RESET}").strip()
            if not username:
                print_error("Nom d'utilisateur requis")
                continue
            
            # Vérifier session existante
            session_data = client.load_session(username)
            if session_data:
                print_success(f"Session existante trouvée pour @{username}")
                return client, username
            
            # Demander mot de passe
            password = input(f"{Colors.CYAN}🔐 Mot de passe Instagram: {Colors.RESET}").strip()
            if not password:
                print_error("Mot de passe requis")
                continue
            
            print_info("Connexion en cours...")
            login_result = client.login(username, password)
            
            if login_result["success"]:
                account_status = login_result.get("status", "active")
                
                if account_status == "disabled":
                    print_error(f"Le compte @{username} est désactivé")
                    continue
                elif account_status == "suspended":
                    print_warning(f"Le compte @{username} est suspendu mais connecté")
                    print_success(f"Connexion réussie pour @{username}")
                    return client, username
                else:
                    print_success(f"Connexion réussie pour @{username}")
                    return client, username
            else:
                error_msg = login_result["message"]
                
                if error_msg == "user_not_found":
                    print_error(f"Le compte @{username} n'existe pas")
                elif error_msg == "password_incorrect":
                    print_error("Mot de passe incorrect")
                elif error_msg == "invalid_credentials":
                    print_error("Identifiants incorrects")
                elif error_msg == "rate_limit":
                    print_error("Trop de tentatives - Attendez quelques heures")
                    return None, None
                else:
                    print_error(f"Erreur: {error_msg}")
                
                continue
                
        except KeyboardInterrupt:
            print_info("\nConnexion annulée")
            return None, None

def show_main_menu():
    """Afficher le menu principal"""
    print_header("🎯 MENU PRINCIPAL")
    
    print(f"{Colors.CYAN}📱 ACTIONS DE BASE:{Colors.RESET}")
    print(f"{Colors.WHITE}1.{Colors.RESET} ❤️  Liker un post")
    print(f"{Colors.WHITE}2.{Colors.RESET} 👥 Suivre un utilisateur") 
    print(f"{Colors.WHITE}3.{Colors.RESET} 💬 Commenter un post")
    print(f"{Colors.WHITE}4.{Colors.RESET} 📸 Publier une story")
    print(f"{Colors.WHITE}5.{Colors.RESET} 📷 Publier un post")
    
    print(f"\n{Colors.CYAN}⚙️  GESTION COMPTE:{Colors.RESET}")
    print(f"{Colors.WHITE}6.{Colors.RESET} 🔒 Changer confidentialité")
    print(f"{Colors.WHITE}7.{Colors.RESET} 🗑️  Supprimer dernière publication")
    print(f"{Colors.WHITE}8.{Colors.RESET} ℹ️  Informations du compte")
    
    print(f"\n{Colors.CYAN}📋 GESTION SESSIONS:{Colors.RESET}")
    print(f"{Colors.WHITE}9.{Colors.RESET} 📱 Changer de compte")
    print(f"{Colors.WHITE}10.{Colors.RESET} 📋 Liste des comptes")
    
    print(f"\n{Colors.RED}0. 🚪 Quitter{Colors.RESET}")

def handle_like_action(client):
    """Gérer l'action de like"""
    print_header("❤️ LIKER UN POST")
    
    url = input(f"{Colors.CYAN}🔗 URL du post: {Colors.RESET}").strip()
    if not url:
        print_error("URL requise")
        return
    
    # Extraire et afficher le media ID
    if client.api:
        media_id = client.api.extract_media_id_from_url(url)
        if media_id:
            print_media_id(media_id)
        else:
            print_warning("Media ID non trouvé")
    
    print_info("Like en cours...")
    result = client.like_post(url)
    
    if result["success"]:
        print_success("Like réussi!")
    else:
        print_error(f"Échec: {result['error']}")

def handle_follow_action(client):
    """Gérer l'action de follow"""
    print_header("👥 SUIVRE UN UTILISATEUR")
    
    url = input(f"{Colors.CYAN}👤 URL du profil ou @username: {Colors.RESET}").strip()
    if not url:
        print_error("URL requise")
        return
    
    # Convertir username en URL si nécessaire
    if not url.startswith('http'):
        url = f"https://www.instagram.com/{url.replace('@', '')}/"
    
    # Extraire et afficher l'user ID
    if client.api:
        user_id = client.api.extract_user_id_from_url(url)
        if user_id:
            print_user_id(user_id)
        else:
            print_warning("User ID non trouvé")
    
    print_info("Follow en cours...")
    result = client.follow_user(url)
    
    if result["success"]:
        print_success("Follow réussi!")
    else:
        print_error(f"Échec: {result['error']}")

def handle_comment_action(client):
    """Gérer l'action de commentaire"""
    print_header("💬 COMMENTER UN POST")
    
    url = input(f"{Colors.CYAN}🔗 URL du post: {Colors.RESET}").strip()
    if not url:
        print_error("URL requise")
        return
    
    comment = input(f"{Colors.CYAN}💬 Votre commentaire: {Colors.RESET}").strip()
    if not comment:
        print_error("Commentaire requis")
        return
    
    # Extraire et afficher le media ID
    if client.api:
        media_id = client.api.extract_media_id_from_url(url)
        if media_id:
            print_media_id(media_id)
    
    print_info("Commentaire en cours...")
    result = client.comment_post(url, comment)
    
    if result["success"]:
        print_success("Commentaire ajouté!")
    else:
        print_error(f"Échec: {result['error']}")

def handle_story_upload(client):
    """Gérer l'upload de story"""
    print_header("📸 PUBLIER UNE STORY")
    
    image_path = input(f"{Colors.CYAN}📁 Chemin vers l'image: {Colors.RESET}").strip()
    if not image_path:
        print_error("Chemin requis")
        return
    
    if not os.path.exists(image_path):
        print_error(f"Fichier non trouvé: {image_path}")
        return
    
    print_info("Upload story en cours...")
    result = client.upload_story(image_path)
    
    if result["success"]:
        print_success("Story publiée!")
    else:
        print_error(f"Échec: {result['error']}")

def handle_post_upload(client):
    """Gérer l'upload de post"""
    print_header("📷 PUBLIER UN POST")
    
    image_path = input(f"{Colors.CYAN}📁 Chemin vers l'image: {Colors.RESET}").strip()
    if not image_path:
        print_error("Chemin requis")
        return
    
    if not os.path.exists(image_path):
        print_error(f"Fichier non trouvé: {image_path}")
        return
    
    caption = input(f"{Colors.CYAN}📝 Légende (optionnel): {Colors.RESET}").strip()
    
    print_info("Upload post en cours...")
    result = client.upload_post(image_path, caption)
    
    if result["success"]:
        print_success("Post publié!")
    else:
        print_error(f"Échec: {result['error']}")

def handle_privacy_toggle(client):
    """Gérer le changement de confidentialité"""
    print_header("🔒 CHANGER CONFIDENTIALITÉ")
    
    account_info = client.get_account_info()
    if account_info["success"]:
        current_status = account_info["data"]["account_status"]
        print_info(f"Statut actuel: {current_status}")
        
        action = "rendre public" if current_status == "Privé" else "rendre privé"
        confirm = input(f"{Colors.YELLOW}🔄 Confirmer {action}? (oui/non): {Colors.RESET}").strip().lower()
        
        if confirm in ['oui', 'o', 'yes', 'y']:
            result = client.toggle_account_privacy()
            if result["success"]:
                new_status = result["data"]["new_status"]
                print_success(f"Compte maintenant: {new_status}")
            else:
                print_error(f"Échec: {result['error']}")
        else:
            print_info("Changement annulé")
    else:
        print_error(f"Impossible de récupérer les infos: {account_info['error']}")

def handle_delete_post(client):
    """Gérer la suppression de post"""
    print_header("🗑️ SUPPRIMER DERNIÈRE PUBLICATION")
    
    confirm = input(f"{Colors.RED}⚠️  Confirmer la suppression? (oui/non): {Colors.RESET}").strip().lower()
    if confirm in ['oui', 'o', 'yes', 'y']:
        print_info("Suppression en cours...")
        result = client.delete_last_post()
        
        if result["success"]:
            print_success("Publication supprimée!")
        else:
            print_error(f"Échec: {result['error']}")
    else:
        print_info("Suppression annulée")

def handle_account_info(client):
    """Afficher les infos du compte"""
    print_header("ℹ️ INFORMATIONS DU COMPTE")
    
    account_info = client.get_account_info()
    if account_info["success"]:
        data = account_info["data"]
        print(f"{Colors.CYAN}👤 Username:{Colors.RESET} @{data['username']}")
        print(f"{Colors.CYAN}📝 Nom:{Colors.RESET} {data['full_name']}")
        print(f"{Colors.CYAN}🔒 Statut:{Colors.RESET} {data['account_status']}")
        print(f"{Colors.CYAN}✅ Vérifié:{Colors.RESET} {'Oui' if data['is_verified'] else 'Non'}")
        print(f"{Colors.CYAN}👥 Abonnés:{Colors.RESET} {data['follower_count']:,}")
        print(f"{Colors.CYAN}🔄 Abonnements:{Colors.RESET} {data['following_count']:,}")
        print(f"{Colors.CYAN}📸 Publications:{Colors.RESET} {data['media_count']:,}")
        
        # Informations techniques
        print(f"\n{Colors.PURPLE}🔧 User ID:{Colors.RESET} {Colors.WHITE}{client._get_user_id_from_session()}{Colors.RESET}")
        print(f"{Colors.PURPLE}🔧 X-MID:{Colors.RESET} {Colors.WHITE}{client.get_x_mid()[:20]}...{Colors.RESET}")
    else:
        print_error(f"Erreur: {account_info['error']}")

def main():
    """Fonction principale"""
    print_colored("🤖 INSTAGRAM BOT - BIBLIOTHÈQUE INSTA_KENDOU", Colors.BOLD + Colors.CYAN)
    print_colored("Created by Kenny - @Ken56266325", Colors.BLUE)
    
    # Connexion
    client, username = login_or_load_session()
    if not client:
        print_error("Connexion échouée")
        return
    
    current_username = username
    
    # Menu principal
    while True:
        print(f"\n{Colors.GREEN}📱 Connecté en tant que: @{current_username}{Colors.RESET}")
        show_main_menu()
        
        try:
            choice = input(f"\n{Colors.CYAN}🎯 Votre choix: {Colors.RESET}").strip()
            
            if choice == "0":
                print_success("Au revoir!")
                break
            elif choice == "1":
                handle_like_action(client)
            elif choice == "2":
                handle_follow_action(client)
            elif choice == "3":
                handle_comment_action(client)
            elif choice == "4":
                handle_story_upload(client)
            elif choice == "5":
                handle_post_upload(client)
            elif choice == "6":
                handle_privacy_toggle(client)
            elif choice == "7":
                handle_delete_post(client)
            elif choice == "8":
                handle_account_info(client)
            elif choice == "9":
                # Changer de compte
                new_client, new_username = login_or_load_session()
                if new_client:
                    client = new_client
                    current_username = new_username
                    print_success(f"Changé vers @{current_username}")
            elif choice == "10":
                # Liste des comptes
                show_accounts_menu()
            else:
                print_error("Choix invalide")
                
        except KeyboardInterrupt:
            print_info("\nRetour au menu")
            continue
        
        input(f"\n{Colors.BLUE}⏳ Appuyez sur Entrée pour continuer...{Colors.RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_colored("\n\n👋 Arrêt du script", Colors.YELLOW)
    except Exception as e:
        print_error(f"Erreur inattendue: {e}")
        print_info("💬 Support: 0389561802 | https://t.me/Kenny5626")
