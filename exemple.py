# -*- coding: utf-8 -*-
"""
SCRIPT D'EXEMPLE COMPLET - insta_kendou
Démonstration de toutes les fonctionnalités de la bibliothèque Instagram

Code d'accès obligatoir pour utiliser la bibliothèque
"""

from insta_kendou import InstagramClient
import os
import time

# CODE D'ACCÈS OBLIGATOIRE - NÉCESSAIRE POUR UTILISER LA BIBLIOTHÈQUE
ACCESS_CODE = "MampifalyfelicienKennyNestinFoad56266325$17Mars2004FeliciteGemmellineNestine"

def main():
    """Fonction principale avec menu interactif"""
    print("=" * 60)
    print("🤖 INSTAGRAM BOT - BIBLIOTHÈQUE INSTA_KENDOU")
    print("=" * 60)
    
    # Initialisation du client
    client = InstagramClient()
    
    # Connexion
    print("\n🔐 CONNEXION INSTAGRAM")
    print("=" * 40)
    
    while True:
        username = input("👤 Nom d'utilisateur Instagram: ").strip()
        if not username:
            print("❌ Nom d'utilisateur requis")
            continue
            
        # Essayer de charger une session existante
        print(f"🔍 Recherche de session existante pour @{username}...")
        session_data = client.load_session(username)
        
        if session_data:
            print(f"✅ Session chargée pour @{username}")
            # Afficher les informations du compte
            show_account_info(client)
            break
        else:
            print("🔑 Aucune session trouvée, connexion requise")
            password = input("🔐 Mot de passe Instagram: ").strip()
            if not password:
                print("❌ Mot de passe requis")
                continue
            
            print("♻ Connexion en cours...")
            login_result = client.login(username, password)
            
            if login_result["success"]:
                # Gérer le statut du compte
                account_status = login_result.get("status", "active")
                
                if account_status == "disabled":
                    print(f"❌ Le compte @{username} est désactivé et ne peut plus être utilisé")
                    continue
                elif account_status == "suspended":
                    print(f"⚠️ Le compte @{username} est suspendu mais connecté")
                    print("✅ Connexion réussie malgré la suspension")
                    show_account_info(client)
                    break
                else:
                    # Afficher les stats si disponibles
                    if "user_stats" in login_result:
                        stats = login_result["user_stats"]
                        print(f"✅ Connexion réussie pour @{username}")
                        print(f"📊 {stats.get('follower_count', 0)} abonnés | {stats.get('following_count', 0)} abonnements | {stats.get('media_count', 0)} publications")
                        status = "Privé" if stats.get("is_private") else "Public"
                        verified = " ✅" if stats.get("is_verified") else ""
                        print(f"🔒 Compte {status}{verified}")
                    else:
                        print(f"✅ Connexion réussie pour @{username}")
                    
                    show_account_info(client)
                    break
            else:
                error_msg = login_result["message"]
                
                if error_msg == "restart_login":
                    print("🔄 Redémarrage de la connexion...")
                    continue
                elif error_msg == "user_not_found":
                    print(f"❌ Le compte @{username} n'existe pas")
                    print("Vérifiez le nom d'utilisateur et réessayez.")
                    continue
                elif error_msg == "password_incorrect":
                    print("❌ Mot de passe incorrect")
                    print("Veuillez entrer le bon mot de passe.")
                    continue
                elif error_msg == "invalid_credentials":
                    print("❌ Identifiants incorrects")
                    print("Vérifiez vos informations de connexion.")
                    continue
                elif error_msg == "rate_limit":
                    print("❌ Trop de tentatives de connexion")
                    print("Attendez quelques heures avant de réessayer.")
                    return
                elif error_msg.startswith("Échec 2FA:"):
                    print(f"❌ {error_msg}")
                    print("Vérifiez votre connexion et réessayez.")
                    continue
                else:
                    print(f"❌ Erreur de connexion: {error_msg}")
                    continue
    
    # Menu principal
    while True:
        show_main_menu()
        choice = input("🎯 Votre choix: ").strip()
        
        if choice == "0":
            print("👋 Au revoir!")
            break
        elif choice == "1":
            handle_like_action(client)
        elif choice == "2":
            handle_comment_action(client)
        elif choice == "3":
            handle_follow_action(client)
        elif choice == "4":
            handle_story_upload(client)
        elif choice == "5":
            handle_post_upload(client)
        elif choice == "6":
            handle_delete_post(client)
        elif choice == "7":
            handle_account_info(client)
        elif choice == "8":
            handle_privacy_toggle(client)
        elif choice == "9":
            handle_user_info(client)
        elif choice == "10":
            handle_media_info(client)
        elif choice == "11":
            handle_search_users(client)
        elif choice == "12":
            handle_timeline_feed(client)
        elif choice == "13":
            handle_followers_following(client)
        elif choice == "14":
            handle_user_media(client)
        elif choice == "15":
            handle_media_interactions(client)
        elif choice == "16":
            handle_session_management(client)
        elif choice == "17":
            handle_advanced_actions(client)
        else:
            print("❌ Choix invalide")
        
        input("\n⏳ Appuyez sur Entrée pour continuer...")

def show_account_info(client):
    """Afficher les informations du compte connecté"""
    account_info = client.get_account_info()
    if account_info["success"]:
        data = account_info["data"]
        print(f"\n📋 INFORMATIONS DU COMPTE")
        print(f"👤 Username: @{data['username']}")
        print(f"🆔 User ID: {client._get_user_id_from_session()}")
        print(f"🔧 X-MID: {client.get_x_mid()}")

def show_main_menu():
    """Afficher le menu principal"""
    print("\n" + "=" * 60)
    print("🎯 MENU PRINCIPAL - TOUTES LES ACTIONS")
    print("=" * 60)
    print("📱 ACTIONS DE BASE:")
    print("1. ❤️  Liker un post")
    print("2. 💬 Commenter un post")
    print("3. 👥 Suivre un utilisateur")
    print("4. 📸 Publier une story")
    print("5. 📷 Publier un post")
    print("6. 🗑️  Supprimer dernière publication")
    
    print("\n📊 INFORMATIONS:")
    print("7. ℹ️  Voir infos de mon compte")
    print("8. 🔒 Changer confidentialité")
    print("9. 👤 Infos d'un utilisateur")
    print("10. 📷 Infos d'un post")
    
    print("\n🔍 RECHERCHE ET DÉCOUVERTE:")
    print("11. 🔎 Rechercher utilisateurs")
    print("12. 📱 Voir timeline/feed")
    print("13. 👥 Mes abonnés/abonnements")
    print("14. 📸 Posts d'un utilisateur")
    print("15. 💬 Interactions d'un post")
    
    print("\n⚙️ AVANCÉ:")
    print("16. 💾 Gestion session")
    print("17. 🚀 Actions avancées")
    
    print("\n0. 🚪 Quitter")
    print("=" * 60)

def handle_like_action(client):
    """Gérer l'action de like"""
    print("\n❤️ LIKER UN POST")
    print("=" * 40)
    print("Formats supportés:")
    print("- https://www.instagram.com/p/ABC123/")
    print("- https://instagr.am/p/ABC123/")
    print("- https://vt.tiktok.com/SHORT_LINK/")
    print("- Liens courts (bit.ly, t.co, etc.)")
    
    url = input("🔗 URL du post: ").strip()
    if not url:
        print("❌ URL requise")
        return
    
    # Afficher le media ID si possible
    if client.api:
        media_id = client.api.extract_media_id_from_url(url)
        if media_id:
            print(f"📷 Media ID extrait: {media_id}")
    
    print("🔄 Like en cours...")
    result = client.like_post(url)
    
    if result["success"]:
        print("✅ Like réussi!")
    else:
        print(f"❌ Erreur: {result['error']}")

def handle_comment_action(client):
    """Gérer l'action de commentaire"""
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
    
    # Afficher le media ID si possible
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

def handle_follow_action(client):
    """Gérer l'action de follow"""
    print("\n👥 SUIVRE UN UTILISATEUR")
    print("=" * 40)
    print("Formats supportés:")
    print("- https://www.instagram.com/username/")
    print("- @username")
    print("- username (recherche similaire activée)")
    
    url = input("👤 URL du profil: ").strip()
    if not url:
        print("❌ URL requise")
        return
    
    # Si c'est juste un username, convertir en URL
    if not url.startswith('http') and not '@' in url:
        url = f"https://www.instagram.com/{url.replace('@', '')}/"
    
    # Afficher l'user ID si possible
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

def handle_story_upload(client):
    """Gérer l'upload de story"""
    print("\n📸 PUBLIER UNE STORY")
    print("=" * 40)
    print("Formats supportés: JPG, PNG")
    print("Résolution optimale: 720x1280 (9:16)")
    
    image_path = input("📁 Chemin vers l'image: ").strip()
    if not image_path:
        print("❌ Chemin requis")
        return
    
    if not os.path.exists(image_path):
        print(f"❌ Fichier non trouvé: {image_path}")
        return
    
    print("🔄 Upload story en cours...")
    result = client.upload_story(image_path)
    
    if result["success"]:
        print("✅ Story publiée avec succès!")
    else:
        print(f"❌ Erreur: {result['error']}")

def handle_post_upload(client):
    """Gérer l'upload de post"""
    print("\n📷 PUBLIER UN POST")
    print("=" * 40)
    
    image_path = input("📁 Chemin vers l'image: ").strip()
    if not image_path:
        print("❌ Chemin requis")
        return
    
    if not os.path.exists(image_path):
        print(f"❌ Fichier non trouvé: {image_path}")
        return
    
    caption = input("📝 Légende (optionnel): ").strip()
    
    print("🔄 Upload post en cours...")
    result = client.upload_post(image_path, caption)
    
    if result["success"]:
        print("✅ Post publié avec succès!")
    else:
        print(f"❌ Erreur: {result['error']}")

def handle_delete_post(client):
    """Gérer la suppression de post"""
    print("\n🗑️ SUPPRIMER DERNIÈRE PUBLICATION")
    print("=" * 40)
    
    confirm = input("⚠️ Confirmer la suppression? (oui/non): ").strip().lower()
    if confirm not in ['oui', 'o', 'yes', 'y']:
        print("❌ Suppression annulée")
        return
    
    print("🔄 Suppression en cours...")
    result = client.delete_last_post()
    
    if result["success"]:
        print("✅ Publication supprimée!")
    else:
        print(f"❌ Erreur: {result['error']}")

def handle_account_info(client):
    """Afficher les infos complètes du compte"""
    print("\n📊 INFORMATIONS COMPLÈTES DU COMPTE")
    print("=" * 50)
    
    account_info = client.get_account_info()
    if account_info["success"]:
        data = account_info["data"]
        print(f"👤 Username: @{data['username']}")
        print(f"📝 Nom complet: {data['full_name']}")
        print(f"🆔 User ID: {client._get_user_id_from_session()}")
        print(f"🔒 Statut: {data['account_status']}")
        print(f"✅ Vérifié: {'Oui' if data['is_verified'] else 'Non'}")
        print(f"🏢 Business: {'Oui' if data['is_business'] else 'Non'}")
        print(f"👥 Abonnés: {data['follower_count']:,}")
        print(f"🔄 Abonnements: {data['following_count']:,}")
        print(f"📸 Publications: {data['media_count']:,}")
        if data['biography']:
            print(f"📄 Bio: {data['biography']}")
        
        print(f"\n🔧 Informations techniques:")
        print(f"🔧 X-MID: {client.get_x_mid()}")
        print(f"🔗 Auth Token: {'Présent' if client._get_auth_token() else 'Absent'}")
    else:
        print(f"❌ Erreur: {account_info['error']}")

def handle_privacy_toggle(client):
    """Gérer le changement de confidentialité"""
    print("\n🔒 CHANGER CONFIDENTIALITÉ")
    print("=" * 40)
    
    account_info = client.get_account_info()
    if account_info["success"]:
        current_status = account_info["data"]["account_status"]
        print(f"📊 Statut actuel: {current_status}")
        
        action = "rendre public" if current_status == "Privé" else "rendre privé"
        confirm = input(f"🔄 Confirmer {action}? (oui/non): ").strip().lower()
        
        if confirm in ['oui', 'o', 'yes', 'y']:
            result = client.toggle_account_privacy()
            if result["success"]:
                new_status = result["data"]["new_status"]
                print(f"✅ Compte maintenant: {new_status}")
            else:
                print(f"❌ Erreur: {result['error']}")
        else:
            print("❌ Changement annulé")
    else:
        print(f"❌ Impossible de récupérer les infos: {account_info['error']}")

def handle_user_info(client):
    """Afficher les infos d'un utilisateur"""
    print("\n👤 INFORMATIONS D'UN UTILISATEUR")
    print("=" * 40)
    
    url = input("👤 URL du profil ou @username: ").strip()
    if not url:
        print("❌ URL requise")
        return
    
    # Convertir username simple en URL
    if not url.startswith('http'):
        url = f"https://www.instagram.com/{url.replace('@', '')}/"
    
    result = client.get_user_info(url)
    if result["success"]:
        data = result["data"]
        print(f"\n📋 PROFIL DE @{data['username']}")
        print(f"📝 Nom: {data['full_name']}")
        print(f"🆔 User ID: {data['user_id']}")
        print(f"🔒 {data['account_status']}")
        print(f"✅ Vérifié: {'Oui' if data['is_verified'] else 'Non'}")
        print(f"🏢 Business: {'Oui' if data['is_business'] else 'Non'}")
        print(f"👥 {data['follower_count']:,} abonnés")
        print(f"🔄 {data['following_count']:,} abonnements")
        print(f"📸 {data['media_count']:,} publications")
        if data['biography']:
            print(f"📄 Bio: {data['biography']}")
    else:
        print(f"❌ Erreur: {result['error']}")

def handle_media_info(client):
    """Afficher les infos d'un post"""
    print("\n📷 INFORMATIONS D'UN POST")
    print("=" * 40)
    
    url = input("🔗 URL du post: ").strip()
    if not url:
        print("❌ URL requise")
        return
    
    result = client.get_media_info(url)
    if result["success"]:
        data = result["data"]
        print(f"\n📸 POST {data['code']}")
        print(f"🆔 Media ID: {data['id']}")
        print(f"📊 Type: {data['media_type']}")
        print(f"❤️ {data['like_count']:,} likes")
        print(f"💬 {data['comment_count']:,} commentaires")
        print(f"👤 Auteur: @{data['owner'].get('username', 'N/A')}")
        if data['caption']:
            print(f"📝 Caption: {data['caption'][:200]}...")
    else:
        print(f"❌ Erreur: {result['error']}")

def handle_search_users(client):
    """Rechercher des utilisateurs"""
    print("\n🔎 RECHERCHER UTILISATEURS")
    print("=" * 40)
    
    query = input("🔍 Terme de recherche: ").strip()
    if not query:
        print("❌ Terme requis")
        return
    
    count = input("📊 Nombre de résultats (défaut: 20): ").strip()
    try:
        count = int(count) if count else 20
    except ValueError:
        count = 20
    
    result = client.search_users(query, count)
    if result["success"]:
        users = result["data"]
        print(f"\n🔍 {len(users)} résultats pour '{query}':")
        
        for i, user in enumerate(users, 1):
            verified = " ✅" if user['is_verified'] else ""
            private = " 🔒" if user['is_private'] else ""
            print(f"{i:2d}. @{user['username']}{verified}{private}")
            print(f"     {user['full_name']} - {user['follower_count']:,} abonnés")
            if i >= 10:  # Limiter l'affichage
                remaining = len(users) - 10
                if remaining > 0:
                    print(f"     ... et {remaining} autres résultats")
                break
    else:
        print(f"❌ Erreur: {result['error']}")

def handle_timeline_feed(client):
    """Afficher le timeline/feed"""
    print("\n📱 TIMELINE / FEED")
    print("=" * 40)
    
    count = input("📊 Nombre de posts (défaut: 15): ").strip()
    try:
        count = int(count) if count else 15
    except ValueError:
        count = 15
    
    result = client.get_timeline_feed(count)
    if result["success"]:
        posts = result["data"]
        print(f"\n📱 {len(posts)} posts dans votre timeline:")
        
        for i, post in enumerate(posts[:10], 1):  # Afficher max 10
            user = post['user']
            print(f"{i:2d}. @{user['username']}")
            print(f"     ❤️ {post['like_count']:,} | 💬 {post['comment_count']:,}")
            if post['caption']:
                caption = post['caption'][:80] + "..." if len(post['caption']) > 80 else post['caption']
                print(f"     📝 {caption}")
            print()
        
        if len(posts) > 10:
            print(f"... et {len(posts) - 10} autres posts")
    else:
        print(f"❌ Erreur: {result['error']}")

def handle_followers_following(client):
    """Gérer abonnés/abonnements"""
    print("\n👥 ABONNÉS / ABONNEMENTS")
    print("=" * 40)
    print("1. 👥 Mes abonnés")
    print("2. 🔄 Mes abonnements")
    print("3. 👤 Abonnés d'un utilisateur")
    print("4. 🔄 Abonnements d'un utilisateur")
    
    choice = input("Choix: ").strip()
    
    count = input("📊 Nombre à afficher (défaut: 20): ").strip()
    try:
        count = int(count) if count else 20
    except ValueError:
        count = 20
    
    if choice == "1":
        result = client.get_followers(count=count)
        title = "MES ABONNÉS"
    elif choice == "2":
        result = client.get_following(count=count)
        title = "MES ABONNEMENTS"
    elif choice in ["3", "4"]:
        url = input("👤 URL du profil: ").strip()
        if not url:
            print("❌ URL requise")
            return
        
        if not url.startswith('http'):
            url = f"https://www.instagram.com/{url.replace('@', '')}/"
        
        if choice == "3":
            result = client.get_followers(url, count)
            title = "ABONNÉS"
        else:
            result = client.get_following(url, count)
            title = "ABONNEMENTS"
    else:
        print("❌ Choix invalide")
        return
    
    if result["success"]:
        users = result["data"]
        print(f"\n👥 {title} ({len(users)} utilisateurs):")
        
        for i, user in enumerate(users[:15], 1):  # Afficher max 15
            verified = " ✅" if user['is_verified'] else ""
            private = " 🔒" if user['is_private'] else ""
            print(f"{i:2d}. @{user['username']}{verified}{private}")
            if user['full_name']:
                print(f"     {user['full_name']}")
        
        if len(users) > 15:
            print(f"... et {len(users) - 15} autres")
    else:
        print(f"❌ Erreur: {result['error']}")

def handle_user_media(client):
    """Afficher les posts d'un utilisateur"""
    print("\n📸 POSTS D'UN UTILISATEUR")
    print("=" * 40)
    
    url = input("👤 URL du profil: ").strip()
    if not url:
        print("❌ URL requise")
        return
    
    if not url.startswith('http'):
        url = f"https://www.instagram.com/{url.replace('@', '')}/"
    
    count = input("📊 Nombre de posts (défaut: 12): ").strip()
    try:
        count = int(count) if count else 12
    except ValueError:
        count = 12
    
    result = client.get_user_media_list(url, count)
    if result["success"]:
        posts = result["data"]
        print(f"\n📸 {len(posts)} derniers posts:")
        
        for i, post in enumerate(posts[:10], 1):
            print(f"{i:2d}. Post {post['code']}")
            print(f"     ❤️ {post['like_count']:,} | 💬 {post['comment_count']:,}")
            if post['caption']:
                caption = post['caption'][:60] + "..." if len(post['caption']) > 60 else post['caption']
                print(f"     📝 {caption}")
            print()
        
        if len(posts) > 10:
            print(f"... et {len(posts) - 10} autres posts")
    else:
        print(f"❌ Erreur: {result['error']}")

def handle_media_interactions(client):
    """Gérer les interactions d'un post"""
    print("\n💬 INTERACTIONS D'UN POST")
    print("=" * 40)
    print("1. 💬 Commentaires")
    print("2. ❤️ Utilisateurs qui ont liké")
    
    choice = input("Choix: ").strip()
    
    url = input("🔗 URL du post: ").strip()
    if not url:
        print("❌ URL requise")
        return
    
    count = input("📊 Nombre à afficher (défaut: 20): ").strip()
    try:
        count = int(count) if count else 20
    except ValueError:
        count = 20
    
    if choice == "1":
        result = client.get_media_comments(url, count)
        if result["success"]:
            comments = result["data"]
            print(f"\n💬 {len(comments)} commentaires:")
            
            for i, comment in enumerate(comments[:10], 1):
                user = comment['user']
                print(f"{i:2d}. @{user['username']}")
                print(f"     {comment['text']}")
                print()
            
            if len(comments) > 10:
                print(f"... et {len(comments) - 10} autres commentaires")
        else:
            print(f"❌ Erreur: {result['error']}")
    
    elif choice == "2":
        result = client.get_media_likers(url, count)
        if result["success"]:
            likers = result["data"]
            print(f"\n❤️ {len(likers)} utilisateurs ont liké:")
            
            for i, user in enumerate(likers[:15], 1):
                verified = " ✅" if user['is_verified'] else ""
                print(f"{i:2d}. @{user['username']}{verified}")
                if user['full_name']:
                    print(f"     {user['full_name']}")
            
            if len(likers) > 15:
                print(f"... et {len(likers) - 15} autres")
        else:
            print(f"❌ Erreur: {result['error']}")
    
    else:
        print("❌ Choix invalide")

def handle_session_management(client):
    """Gestion de session"""
    print("\n💾 GESTION DE SESSION")
    print("=" * 40)
    print("1. 💾 Sauvegarder session actuelle")
    print("2. ℹ️ Informations de session")
    
    choice = input("Choix: ").strip()
    
    if choice == "1":
        result = client.dump_session()
        if result:
            username = result.get("user_data", {}).get("username", "utilisateur")
            print(f"✅ Session sauvegardée pour @{username}")
            print(f"📄 Fichier: sessions/{username}_ig_complete.json")
        else:
            print("❌ Impossible de sauvegarder la session")
    
    elif choice == "2":
        print(f"\n📋 INFORMATIONS DE SESSION:")
        print(f"👤 Username: @{client._get_username_from_session()}")
        print(f"🆔 User ID: {client._get_user_id_from_session()}")
        print(f"🔧 X-MID: {client.get_x_mid()}")
        print(f"🔗 Auth Token: {'Présent' if client._get_auth_token() else 'Absent'}")
        
        if client.session_data:
            created = client.session_data.get("created_at") or client.session_data.get("session_created")
            if created:
                import datetime
                date = datetime.datetime.fromtimestamp(created)
                print(f"📅 Session créée: {date.strftime('%d/%m/%Y %H:%M:%S')}")
    
    else:
        print("❌ Choix invalide")

def handle_advanced_actions(client):
    """Actions avancées"""
    print("\n🚀 ACTIONS AVANCÉES")
    print("=" * 40)
    print("1. 💔 Unlike un post")
    print("2. 👋 Ne plus suivre")
    print("3. 🗑️ Supprimer un commentaire")
    print("4. 📊 Mes dernières publications")
    print("5. 🔍 Test extraction d'IDs")
    
    choice = input("Choix: ").strip()
    
    if choice == "1":
        url = input("🔗 URL du post à unliker: ").strip()
        if url:
            result = client.unlike_post(url)
            print("✅ Unlike réussi!" if result["success"] else f"❌ Erreur: {result['error']}")
    
    elif choice == "2":
        url = input("👤 URL du profil à ne plus suivre: ").strip()
        if url:
            if not url.startswith('http'):
                url = f"https://www.instagram.com/{url.replace('@', '')}/"
            result = client.unfollow_user(url)
            print("✅ Unfollow réussi!" if result["success"] else f"❌ Erreur: {result['error']}")
    
    elif choice == "3":
        print("⚠️ Nécessite le comment_id du commentaire à supprimer")
        url = input("🔗 URL du post: ").strip()
        comment_id = input("🆔 ID du commentaire: ").strip()
        if url and comment_id:
            result = client.delete_comment(url, comment_id)
            print("✅ Commentaire supprimé!" if result["success"] else f"❌ Erreur: {result['error']}")
    
    elif choice == "4":
        if client.api:
            posts = client.api.get_own_media_list(10)
            if posts:
                print(f"\n📸 Mes {len(posts)} dernières publications:")
                for i, post in enumerate(posts, 1):
                    print(f"{i:2d}. {post['code']} - ❤️ {post['like_count']:,}")
                    if post['caption']:
                        caption = post['caption'][:50] + "..." if len(post['caption']) > 50 else post['caption']
                        print(f"     📝 {caption}")
            else:
                print("❌ Aucune publication trouvée")
        else:
            print("❌ API non initialisée")
    
    elif choice == "5":
        print("\n🔍 TEST EXTRACTION D'IDs")
        url = input("🔗 URL à tester: ").strip()
        if url and client.api:
            if '/p/' in url or '/reel/' in url:
                media_id = client.api.extract_media_id_from_url(url)
                print(f"📷 Media ID: {media_id}" if media_id else "❌ Media ID non trouvé")
            else:
                user_id = client.api.extract_user_id_from_url(url)
                print(f"👤 User ID: {user_id}" if user_id else "❌ User ID non trouvé")
    
    else:
        print("❌ Choix invalide")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Arrêt du script par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur inattendue: {e}")
        print("💬 Contactez le support: 0389561802 | https://t.me/Kenny5626")
