# -*- coding: utf-8 -*-
"""
SCRIPT D'EXEMPLE COMPLET - insta_kendou
Démonstration de toutes les fonctionnalités avec gestion de session personnalisée

Code d'accès obligatoire pour utiliser la bibliothèque
"""

from insta_kendou import InstagramClient
import os
import time
import glob

# CODE D'ACCÈS OBLIGATOIRE - NÉCESSAIRE POUR UTILISER LA BIBLIOTHÈQUE
ACCESS_CODE = "MampifalyfelicienKennyNestinFoad56266325$17Mars2004FeliciteGemmellineNestine"

# Configuration des chemins de session personnalisés
SESSIONS_DIR = "mes_comptes_instagram"  # Dossier personnalisé
SESSION_SUFFIX = "_session.json"        # Suffixe personnalisé

def main():
    """Fonction principale avec gestion multi-comptes"""
    print("=" * 60)
    print("🤖 INSTAGRAM BOT - BIBLIOTHÈQUE INSTA_KENDOU")
    print("=" * 60)

    # Créer le dossier de sessions s'il n'existe pas
    if not os.path.exists(SESSIONS_DIR):
        os.makedirs(SESSIONS_DIR)

    # Initialiser le client
    client = InstagramClient()

    # Menu de sélection de compte
    while True:
        print("\n🔐 GESTION DES COMPTES")
        print("=" * 40)
        print("1. 📱 Se connecter à un compte")
        print("2. 🔄 Charger un compte existant")
        print("3. 📊 Voir tous les comptes")
        print("4. 🗑️ Supprimer un compte")
        print("0. 🚪 Quitter")

        choice = input("\n🎯 Votre choix: ").strip()

        if choice == "0":
            print("👋 Au revoir!")
            return
        elif choice == "1":
            if login_account(client):
                break
        elif choice == "2":
            if load_existing_account(client):
                break
        elif choice == "3":
            show_all_accounts()
        elif choice == "4":
            delete_account()
        else:
            print("❌ Choix invalide")

    # Menu principal des actions
    main_menu(client)

def login_account(client):
    """Connexion et sauvegarde d'un nouveau compte"""
    print("\n🔑 CONNEXION NOUVEAU COMPTE")
    print("=" * 40)

    username = input("👤 Nom d'utilisateur Instagram: ").strip()
    if not username:
        print("❌ Nom d'utilisateur requis")
        return False

    password = input("🔐 Mot de passe Instagram: ").strip()
    if not password:
        print("❌ Mot de passe requis")
        return False

    # Définir le fichier de session personnalisé
    session_file = os.path.join(SESSIONS_DIR, f"{username}{SESSION_SUFFIX}")

    print("♻ Connexion en cours...")
    login_result = client.login(username, password)

    if login_result["success"]:
        # Sauvegarder la session avec nom personnalisé
        print(f"💾 Sauvegarde de la session...")
        client.dump_session(session_file)
        
        # Afficher les informations du compte
        show_account_info(client)
        print(f"✅ Compte @{username} connecté et sauvegardé dans {session_file}")
        return True
    else:
        handle_login_error(login_result["message"], username)
        return False

def load_existing_account(client):
    """Charger un compte existant"""
    print("\n📂 COMPTES EXISTANTS")
    print("=" * 40)

    # Lister tous les comptes disponibles
    accounts = get_available_accounts()
    
    if not accounts:
        print("❌ Aucun compte sauvegardé trouvé")
        return False

    print("Comptes disponibles:")
    for i, account in enumerate(accounts, 1):
        print(f"{i}. @{account['username']} ({account['file']})")

    try:
        choice = int(input(f"\n🎯 Choisir un compte (1-{len(accounts)}): ").strip())
        if 1 <= choice <= len(accounts):
            selected_account = accounts[choice - 1]
            session_file = selected_account["file"]
            
            print(f"🔄 Chargement de la session depuis {session_file}...")
            session_data = client.load_session(session_file)
            
            if session_data:
                show_account_info(client)
                return True
            else:
                print("❌ Échec du chargement de la session")
                return False
        else:
            print("❌ Choix invalide")
            return False
    except ValueError:
        print("❌ Veuillez entrer un numéro valide")
        return False

def get_available_accounts():
    """Récupérer la liste des comptes disponibles"""
    accounts = []
    pattern = os.path.join(SESSIONS_DIR, f"*{SESSION_SUFFIX}")
    
    for session_file in glob.glob(pattern):
        filename = os.path.basename(session_file)
        username = filename.replace(SESSION_SUFFIX, "")
        
        # Vérifier si la session est valide
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                import json
                session_data = json.load(f)
            
            created_at = session_data.get("created_at") or session_data.get("last_login") or session_data.get("session_created", 0)
            if time.time() - created_at < 7 * 24 * 3600:  # Session valide
                accounts.append({
                    "username": username,
                    "file": session_file,
                    "valid": True
                })
            else:
                accounts.append({
                    "username": username,
                    "file": session_file,
                    "valid": False
                })
        except:
            accounts.append({
                "username": username,
                "file": session_file,
                "valid": False
            })
    
    return accounts

def show_all_accounts():
    """Afficher tous les comptes avec leur statut"""
    print("\n📊 TOUS LES COMPTES")
    print("=" * 50)

    accounts = get_available_accounts()
    
    if not accounts:
        print("❌ Aucun compte trouvé")
        return

    for i, account in enumerate(accounts, 1):
        status = "✅ Valide" if account["valid"] else "❌ Expiré"
        print(f"{i:2d}. @{account['username']} - {status}")
        print(f"     📄 {account['file']}")

def delete_account():
    """Supprimer un compte sauvegardé"""
    print("\n🗑️ SUPPRIMER UN COMPTE")
    print("=" * 40)

    accounts = get_available_accounts()
    
    if not accounts:
        print("❌ Aucun compte à supprimer")
        return

    print("Comptes disponibles:")
    for i, account in enumerate(accounts, 1):
        status = "✅" if account["valid"] else "❌"
        print(f"{i}. @{account['username']} {status}")

    try:
        choice = int(input(f"\n🎯 Compte à supprimer (1-{len(accounts)}): ").strip())
        if 1 <= choice <= len(accounts):
            selected_account = accounts[choice - 1]
            
            confirm = input(f"⚠️ Confirmer suppression de @{selected_account['username']}? (oui/non): ").strip().lower()
            if confirm in ['oui', 'o', 'yes', 'y']:
                os.remove(selected_account["file"])
                print(f"✅ Compte @{selected_account['username']} supprimé")
            else:
                print("❌ Suppression annulée")
        else:
            print("❌ Choix invalide")
    except ValueError:
        print("❌ Veuillez entrer un numéro valide")

def handle_login_error(error_msg, username):
    """Gérer les erreurs de connexion"""
    if error_msg == "user_not_found":
        print(f"❌ Le compte @{username} n'existe pas")
    elif error_msg == "password_incorrect":
        print("❌ Mot de passe incorrect")
    elif error_msg == "invalid_credentials":
        print("❌ Identifiants incorrects")
    elif error_msg == "rate_limit":
        print("❌ Trop de tentatives de connexion")
    elif error_msg.startswith("Échec 2FA:"):
        print(f"❌ {error_msg}")
    else:
        print(f"❌ Erreur de connexion: {error_msg}")

def show_account_info(client):
    """Afficher les informations du compte connecté"""
    account_info = client.get_account_info()
    if account_info["success"]:
        data = account_info["data"]
        print(f"\n📋 COMPTE CONNECTÉ")
        print(f"👤 @{data['username']}")
        print(f"🆔 User ID: {client._get_user_id_from_session()}")
        print(f"📊 {data['follower_count']:,} abonnés | {data['media_count']:,} posts")

def main_menu(client):
    """Menu principal des actions"""
    while True:
        print("\n" + "=" * 60)
        print("🎯 MENU PRINCIPAL")
        print("=" * 60)
        print("📱 ACTIONS DE BASE:")
        print("1. ❤️  Liker un post")
        print("2. 💬 Commenter un post")
        print("3. 👥 Suivre un utilisateur")
        print("4. 📸 Publier une story")
        print("5. 📷 Publier un post")

        print("\n📊 INFORMATIONS:")
        print("6. ℹ️  Infos de mon compte")
        print("7. 👤 Infos d'un utilisateur")
        print("8. 📷 Infos d'un post")

        print("\n🔍 DÉCOUVERTE:")
        print("9. 🔎 Rechercher utilisateurs")
        print("10. 📱 Timeline/Feed")
        print("11. 👥 Abonnés/Abonnements")

        print("\n⚙️ GESTION:")
        print("12. 💾 Sauvegarder session")
        print("13. 🔄 Changer de compte")
        print("14. 🚀 Actions avancées")

        print("\n0. 🚪 Quitter")
        print("=" * 60)

        choice = input("🎯 Votre choix: ").strip()

        if choice == "0":
            print("👋 Au revoir!")
            break
        elif choice == "1":
            action_like(client)
        elif choice == "2":
            action_comment(client)
        elif choice == "3":
            action_follow(client)
        elif choice == "4":
            action_upload_story(client)
        elif choice == "5":
            action_upload_post(client)
        elif choice == "6":
            action_account_info(client)
        elif choice == "7":
            action_user_info(client)
        elif choice == "8":
            action_media_info(client)
        elif choice == "9":
            action_search_users(client)
        elif choice == "10":
            action_timeline(client)
        elif choice == "11":
            action_followers_following(client)
        elif choice == "12":
            action_save_session(client)
        elif choice == "13":
            if switch_account(client):
                continue
            else:
                break
        elif choice == "14":
            action_advanced(client)
        else:
            print("❌ Choix invalide")

        input("\n⏳ Appuyez sur Entrée pour continuer...")

def action_like(client):
    """Action: Liker un post"""
    print("\n❤️ LIKER UN POST")
    print("=" * 40)
    
    url = input("🔗 URL du post: ").strip()
    if not url:
        print("❌ URL requise")
        return

    # Afficher le media ID extrait
    if client.api:
        media_id = client.api.extract_media_id_from_url(url)
        if media_id:
            print(f"📷 Media ID extrait: {media_id}")

    print("🔄 Like en cours...")
    result = client.like_post(url)

    # Afficher le résultat
    if result["success"]:
        print("✅ Like réussi!")
        print(f"📊 Résultat: {result}")
    else:
        print(f"❌ Erreur: {result['error']}")

def action_comment(client):
    """Action: Commenter un post"""
    print("\n💬 COMMENTER UN POST")
    print("=" * 40)
    
    url = input("🔗 URL du post: ").strip()
    if not url:
        print("❌ URL requise")
        return

    comment = input("💬 Votre commentaire: ").strip()
    if not comment:
        print("❌ Commentaire requis")
        return

    # Afficher le media ID
    if client.api:
        media_id = client.api.extract_media_id_from_url(url)
        if media_id:
            print(f"📷 Media ID: {media_id}")

    print("🔄 Commentaire en cours...")
    result = client.comment_post(url, comment)

    if result["success"]:
        print("✅ Commentaire ajouté!")
    else:
        print(f"❌ Erreur: {result['error']}")

def action_follow(client):
    """Action: Suivre un utilisateur"""
    print("\n👥 SUIVRE UN UTILISATEUR")
    print("=" * 40)
    
    url = input("👤 URL du profil ou @username: ").strip()
    if not url:
        print("❌ URL requise")
        return

    # Convertir simple username en URL
    if not url.startswith('http'):
        url = f"https://www.instagram.com/{url.replace('@', '')}/"

    # Afficher l'user ID
    if client.api:
        user_id = client.api.extract_user_id_from_url(url)
        if user_id:
            print(f"👤 User ID: {user_id}")

    print("🔄 Follow en cours...")
    result = client.follow_user(url)

    if result["success"]:
        print("✅ Follow réussi!")
    else:
        print(f"❌ Erreur: {result['error']}")

def action_upload_story(client):
    """Action: Upload story"""
    print("\n📸 PUBLIER UNE STORY")
    print("=" * 40)
    
    image_path = input("📁 Chemin vers l'image: ").strip()
    if not image_path or not os.path.exists(image_path):
        print("❌ Fichier non trouvé")
        return

    print("🔄 Upload story en cours...")
    result = client.upload_story(image_path)

    if result["success"]:
        print("✅ Story publiée!")
    else:
        print(f"❌ Erreur: {result['error']}")

def action_upload_post(client):
    """Action: Upload post"""
    print("\n📷 PUBLIER UN POST")
    print("=" * 40)
    
    image_path = input("📁 Chemin vers l'image: ").strip()
    if not image_path or not os.path.exists(image_path):
        print("❌ Fichier non trouvé")
        return

    caption = input("📝 Légende (optionnel): ").strip()

    print("🔄 Upload post en cours...")
    result = client.upload_post(image_path, caption)

    if result["success"]:
        print("✅ Post publié!")
    else:
        print(f"❌ Erreur: {result['error']}")

def action_account_info(client):
    """Action: Infos du compte"""
    print("\n📊 INFORMATIONS DU COMPTE")
    print("=" * 50)

    result = client.get_account_info()
    if result["success"]:
        data = result["data"]
        print(f"👤 Username: @{data['username']}")
        print(f"🆔 User ID: {client._get_user_id_from_session()}")
        print(f"📝 Nom: {data['full_name']}")
        print(f"🔒 Statut: {data['account_status']}")
        print(f"👥 {data['follower_count']:,} abonnés")
        print(f"🔄 {data['following_count']:,} abonnements")
        print(f"📸 {data['media_count']:,} publications")
        print(f"🔧 X-MID: {client.get_x_mid()}")
    else:
        print(f"❌ Erreur: {result['error']}")

def action_user_info(client):
    """Action: Infos d'un utilisateur"""
    print("\n👤 INFORMATIONS UTILISATEUR")
    print("=" * 40)
    
    url = input("👤 URL du profil ou @username: ").strip()
    if not url:
        print("❌ URL requise")
        return

    if not url.startswith('http'):
        url = f"https://www.instagram.com/{url.replace('@', '')}/"

    result = client.get_user_info(url)
    if result["success"]:
        data = result["data"]
        print(f"\n📋 @{data['username']}")
        print(f"🆔 User ID: {data['user_id']}")
        print(f"📝 Nom: {data['full_name']}")
        print(f"🔒 {data['account_status']}")
        print(f"👥 {data['follower_count']:,} abonnés")
        print(f"📸 {data['media_count']:,} posts")
    else:
        print(f"❌ Erreur: {result['error']}")

def action_media_info(client):
    """Action: Infos d'un post"""
    print("\n📷 INFORMATIONS POST")
    print("=" * 40)
    
    url = input("🔗 URL du post: ").strip()
    if not url:
        print("❌ URL requise")
        return

    result = client.get_media_info(url)
    if result["success"]:
        data = result["data"]
        print(f"\n📸 Post {data['code']}")
        print(f"🆔 Media ID: {data['id']}")
        print(f"❤️ {data['like_count']:,} likes")
        print(f"💬 {data['comment_count']:,} commentaires")
        print(f"👤 @{data['owner'].get('username', 'N/A')}")
    else:
        print(f"❌ Erreur: {result['error']}")

def action_search_users(client):
    """Action: Rechercher utilisateurs"""
    print("\n🔎 RECHERCHER UTILISATEURS")
    print("=" * 40)
    
    query = input("🔍 Terme de recherche: ").strip()
    if not query:
        print("❌ Terme requis")
        return

    result = client.search_users(query, 10)
    if result["success"]:
        users = result["data"]
        print(f"\n🔍 {len(users)} résultats:")
        for i, user in enumerate(users, 1):
            verified = " ✅" if user['is_verified'] else ""
            print(f"{i:2d}. @{user['username']}{verified}")
            print(f"     👤 User ID: {user['user_id']}")
            print(f"     👥 {user['follower_count']:,} abonnés")
    else:
        print(f"❌ Erreur: {result['error']}")

def action_timeline(client):
    """Action: Timeline"""
    print("\n📱 TIMELINE")
    print("=" * 40)
    
    result = client.get_timeline_feed(10)
    if result["success"]:
        posts = result["data"]
        print(f"\n📱 {len(posts)} posts:")
        for i, post in enumerate(posts[:5], 1):
            user = post['user']
            print(f"{i}. @{user['username']}")
            print(f"   📷 Media ID: {post['id']}")
            print(f"   ❤️ {post['like_count']:,} | 💬 {post['comment_count']:,}")
    else:
        print(f"❌ Erreur: {result['error']}")

def action_followers_following(client):
    """Action: Abonnés/Abonnements"""
    print("\n👥 ABONNÉS/ABONNEMENTS")
    print("=" * 40)
    print("1. 👥 Mes abonnés")
    print("2. 🔄 Mes abonnements")
    
    choice = input("Choix: ").strip()
    
    if choice == "1":
        result = client.get_followers(count=10)
        title = "MES ABONNÉS"
    elif choice == "2":
        result = client.get_following(count=10)
        title = "MES ABONNEMENTS"
    else:
        print("❌ Choix invalide")
        return

    if result["success"]:
        users = result["data"]
        print(f"\n👥 {title} ({len(users)}):")
        for i, user in enumerate(users[:10], 1):
            print(f"{i:2d}. @{user['username']}")
            print(f"     👤 User ID: {user['user_id']}")
    else:
        print(f"❌ Erreur: {result['error']}")

def action_save_session(client):
    """Action: Sauvegarder session"""
    print("\n💾 SAUVEGARDER SESSION")
    print("=" * 40)
    
    # Nom de fichier personnalisé
    username = client._get_username_from_session()
    default_file = os.path.join(SESSIONS_DIR, f"{username}{SESSION_SUFFIX}")
    
    custom_file = input(f"📄 Nom du fichier (défaut: {default_file}): ").strip()
    session_file = custom_file if custom_file else default_file
    
    result = client.dump_session(session_file)
    if result:
        print(f"✅ Session sauvegardée dans {session_file}")
    else:
        print("❌ Erreur sauvegarde")

def switch_account(client):
    """Changer de compte"""
    print("\n🔄 CHANGER DE COMPTE")
    print("=" * 40)
    
    # Charger toutes les sessions disponibles
    pattern = os.path.join(SESSIONS_DIR, f"*{SESSION_SUFFIX}")
    all_sessions = client.load_all_sessions(pattern)
    
    if not all_sessions:
        print("❌ Aucun autre compte disponible")
        return False

    print("Comptes disponibles:")
    usernames = list(all_sessions.keys())
    for i, username in enumerate(usernames, 1):
        print(f"{i}. @{username}")

    try:
        choice = int(input(f"\n🎯 Choisir un compte (1-{len(usernames)}): ").strip())
        if 1 <= choice <= len(usernames):
            selected_username = usernames[choice - 1]
            session_data = all_sessions[selected_username]["session_data"]
            
            if client.switch_session(session_data):
                show_account_info(client)
                return True
        else:
            print("❌ Choix invalide")
    except ValueError:
        print("❌ Numéro invalide")
    
    return False

def action_advanced(client):
    """Actions avancées"""
    print("\n🚀 ACTIONS AVANCÉES")
    print("=" * 40)
    print("1. 💔 Unlike un post")
    print("2. 👋 Ne plus suivre")
    print("3. 🗑️ Supprimer dernière publication")
    print("4. 🔍 Test extraction IDs")
    
    choice = input("Choix: ").strip()
    
    if choice == "1":
        url = input("🔗 URL du post: ").strip()
        if url:
            result = client.unlike_post(url)
            print("✅ Unlike réussi!" if result["success"] else f"❌ {result['error']}")
    
    elif choice == "2":
        url = input("👤 URL du profil: ").strip()
        if url:
            if not url.startswith('http'):
                url = f"https://www.instagram.com/{url.replace('@', '')}/"
            result = client.unfollow_user(url)
            print("✅ Unfollow réussi!" if result["success"] else f"❌ {result['error']}")
    
    elif choice == "3":
        confirm = input("⚠️ Confirmer suppression? (oui/non): ").strip().lower()
        if confirm in ['oui', 'o']:
            result = client.delete_last_post()
            print("✅ Publication supprimée!" if result["success"] else f"❌ {result['error']}")
    
    elif choice == "4":
        url = input("🔗 URL à tester: ").strip()
        if url and client.api:
            if '/p/' in url or '/reel/' in url:
                media_id = client.api.extract_media_id_from_url(url)
                print(f"📷 Media ID: {media_id or 'Non trouvé'}")
            else:
                user_id = client.api.extract_user_id_from_url(url)
                print(f"👤 User ID: {user_id or 'Non trouvé'}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Arrêt du script")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        print("💬 Support: 0389561802 | https://t.me/Kenny5626")
