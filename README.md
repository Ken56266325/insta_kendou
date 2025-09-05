# 🤖 insta_kendou - Bibliothèque Instagram Complète

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Private-red.svg)]()

## 📋 Description

**insta_kendou** est une bibliothèque Python complète pour l'automatisation Instagram avec support de l'authentification 2FA, gestion des médias, et toutes les fonctionnalités sociales.

### ✨ Caractéristiques principales

- 🔐 **Authentification 2FA complète** (Bloks, Alternative, Classique)
- 📱 **Gestion automatique des sessions** 
- ❤️ **Actions sociales** (Like, Follow, Comment)
- 📸 **Upload de médias** (Stories, Posts)
- 🔧 **Extraction d'IDs** (Media ID, User ID)
- 🔗 **Support liens courts** (TikTok, bit.ly, etc.)
- 🛡️ **Système de licence** intégré

---

## 🚀 Installation

```bash
# Installation depuis GitHub
pip install git+https://github.com/Ken56266325/insta_kendou.git

# Ou téléchargement direct
git clone https://github.com/Ken56266325/insta_kendou.git
cd insta_kendou
pip install -e .
```

### 📦 Dépendances

La bibliothèque installe automatiquement :
- `requests` - Requêtes HTTP
- `Pillow` - Traitement d'images
- `pycryptodome` - Chiffrement
- `PyNaCl` - Chiffrement avancé

---

## 🔑 Code d'accès requis

⚠️ **IMPORTANT** : Cette bibliothèque nécessite un code d'accès pour fonctionner.

```python
# À inclure dans votre script
ACCESS_CODE = "MampifalyfelicienKennyNestinFoad56266325$17Mars2004FeliciteGemmellineNestine"
```

Sans ce code, vous obtiendrez l'erreur :
```
❌ Ce script n'est pas autorisé à utiliser cette bibliothèque.
Veuillez contacter le créateur via: 0389561802 ou https://t.me/Kenny5626
```

---

## 💾 Gestion automatique des sessions

### 📁 Structure des fichiers

La bibliothèque gère automatiquement les sessions dans :
```
sessions/
├── username1_ig_complete.json
├── username2_ig_complete.json
└── username3_ig_complete.json
```

### 🔄 Chargement automatique

```python
from insta_kendou import InstagramClient

client = InstagramClient()

# Chargement automatique si session existe
session_data = client.load_session("username")
if session_data:
    print("✅ Session chargée automatiquement")
else:
    print("🔑 Connexion requise")
```

---

## 🔐 Authentification

### Connexion simple

```python
from insta_kendou import InstagramClient

# Code d'accès obligatoire
ACCESS_CODE = "MampifalyfelicienKennyNestinFoad56266325$17Mars2004FeliciteGemmellineNestine"

client = InstagramClient()

# Connexion avec gestion 2FA automatique
result = client.login("username", "password")

if result["success"]:
    print(f"✅ Connecté : @{result['user_data']['username']}")
    print(f"🆔 User ID : {result['user_data']['user_id']}")
else:
    print(f"❌ Erreur : {result['message']}")
```

### Gestion des erreurs de connexion

```python
# Types d'erreurs possibles
error_types = {
    "user_not_found": "Utilisateur inexistant",
    "password_incorrect": "Mot de passe incorrect", 
    "invalid_credentials": "Identifiants invalides",
    "rate_limit": "Trop de tentatives",
    "account_suspended": "Compte suspendu",
    "account_disabled": "Compte désactivé"
}

result = client.login("username", "password")
if not result["success"]:
    error_type = result["message"]
    print(f"❌ {error_types.get(error_type, error_type)}")
```

### 2FA automatique

La bibliothèque gère automatiquement tous les types de 2FA :

```python
# Le 2FA est géré automatiquement
result = client.login("username", "password")

# Si 2FA requis, suivez les instructions à l'écran :
# 📱 MÉTHODES DE VÉRIFICATION DISPONIBLES:
# 1. 📱 SMS au +261 ** ** *** 45
# 2. 💬 WhatsApp au +261 ** ** *** 45  
# 3. 📧 Email à e***@gmail.com
# 
# 🎯 Choisissez une méthode (1-3): 1
# 🔢 Entrez le code reçu : 123456
```

---

## 💾 Gestion des sessions

### Sauvegarder session

```python
# Sauvegarde automatique après connexion réussie
client.login("username", "password")

# Ou sauvegarde manuelle
session_data = client.dump_session("username")
print("✅ Session sauvegardée")
```

### Charger session

```python
# Chargement automatique
client = InstagramClient()
session_data = client.load_session("username")

if session_data:
    print("✅ Session chargée")
    # Prêt à utiliser - pas besoin de se reconnecter
else:
    print("🔑 Connexion requise")
```

### Informations de session

```python
# Récupérer infos de session
username = client._get_username_from_session()
user_id = client._get_user_id_from_session()
auth_token = client._get_auth_token()
x_mid = client.get_x_mid()

print(f"👤 Username: @{username}")
print(f"🆔 User ID: {user_id}")
print(f"🔧 X-MID: {x_mid}")
print(f"🔗 Auth: {'✅' if auth_token else '❌'}")
```

---

## ❤️ Actions sociales

### Like d'un post

```python
# Like avec affichage du Media ID
url = "https://www.instagram.com/p/ABC123/"

# Extraire Media ID (optionnel pour debug)
if client.api:
    media_id = client.api.extract_media_id_from_url(url)
    print(f"MEDIA ID: {media_id}")

# Effectuer le like
result = client.like_post(url)

if result["success"]:
    print("✅ Like réussi!")
else:
    print(f"❌ Erreur: {result['error']}")
```

**Formats d'URL supportés :**
- `https://www.instagram.com/p/ABC123/`
- `https://instagr.am/p/ABC123/`
- `https://vt.tiktok.com/SHORT_LINK/` (résolu automatiquement)
- Tous liens courts (bit.ly, t.co, etc.)

### Follow d'un utilisateur

```python
# Follow avec affichage du User ID
url = "https://www.instagram.com/username/"

# Extraire User ID (optionnel pour debug)
if client.api:
    user_id = client.api.extract_user_id_from_url(url)
    print(f"USER ID: {user_id}")

# Effectuer le follow
result = client.follow_user(url)

if result["success"]:
    print("✅ Follow réussi!")
    
    # Vérifier si en attente (compte privé)
    if "en attente" in str(result.get("data", {})):
        print("⏳ Demande en attente de validation")
else:
    print(f"❌ Erreur: {result['error']}")
```

**Formats supportés :**
- `https://www.instagram.com/username/`
- `@username` 
- `username` (recherche similaire automatique)

### Commenter un post

```python
# Commentaire avec Media ID
url = "https://www.instagram.com/p/ABC123/"
comment = "Super post! 👍"

# Afficher Media ID
if client.api:
    media_id = client.api.extract_media_id_from_url(url)
    print(f"MEDIA ID: {media_id}")

result = client.comment_post(url, comment)

if result["success"]:
    print("✅ Commentaire ajouté!")
else:
    print(f"❌ Erreur: {result['error']}")
```

### Unlike et Unfollow

```python
# Unlike un post
result = client.unlike_post("https://www.instagram.com/p/ABC123/")

# Ne plus suivre
result = client.unfollow_user("https://www.instagram.com/username/")

# Vérifier résultats
if result["success"]:
    print("✅ Action réussie!")
else:
    print(f"❌ Erreur: {result['error']}")
```

---

## 📸 Upload de médias

### Publier une Story

```python
# Upload story (format 9:16 optimal)
image_path = "/path/to/image.jpg"

result = client.upload_story(image_path)

if result["success"]:
    print("✅ Story publiée!")
else:
    print(f"❌ Erreur: {result['error']}")
```

**Formats supportés :**
- JPG, PNG
- Résolution optimale : 720x1280 (9:16)
- Redimensionnement automatique

### Publier un Post

```python
# Upload post avec légende
image_path = "/path/to/image.jpg"
caption = "Ma nouvelle publication! #instagram #photo"

result = client.upload_post(image_path, caption)

if result["success"]:
    print("✅ Post publié!")
else:
    print(f"❌ Erreur: {result['error']}")
```

**Formats supportés :**
- JPG, PNG
- Résolution optimale : 1080x1080 (1:1)
- Légende optionnelle

### Supprimer la dernière publication

```python
# Suppression avec confirmation
result = client.delete_last_post()

if result["success"]:
    print("✅ Publication supprimée!")
else:
    print(f"❌ Erreur: {result['error']}")
```

---

## ℹ️ Récupération d'informations

### Informations du compte connecté

```python
# Infos complètes du compte
result = client.get_account_info()

if result["success"]:
    data = result["data"]
    print(f"👤 @{data['username']}")
    print(f"📝 {data['full_name']}")
    print(f"🔒 {data['account_status']}")  # Public/Privé
    print(f"✅ Vérifié: {data['is_verified']}")
    print(f"👥 {data['follower_count']:,} abonnés")
    print(f"🔄 {data['following_count']:,} abonnements")
    print(f"📸 {data['media_count']:,} publications")
    print(f"📄 Bio: {data['biography']}")
else:
    print(f"❌ Erreur: {result['error']}")
```

### Informations d'un utilisateur

```python
# Infos d'un autre utilisateur
url = "https://www.instagram.com/username/"

result = client.get_user_info(url)

if result["success"]:
    data = result["data"]
    print(f"👤 @{data['username']}")
    print(f"🆔 User ID: {data['user_id']}")
    print(f"📝 {data['full_name']}")
    print(f"🔒 {data['account_status']}")
    print(f"👥 {data['follower_count']:,} abonnés")
else:
    print(f"❌ Erreur: {result['error']}")
```

### Informations d'un post

```python
# Infos d'un média
url = "https://www.instagram.com/p/ABC123/"

result = client.get_media_info(url)

if result["success"]:
    data = result["data"]
    print(f"📸 Post {data['code']}")
    print(f"🆔 Media ID: {data['id']}")
    print(f"❤️ {data['like_count']:,} likes")
    print(f"💬 {data['comment_count']:,} commentaires")
    print(f"👤 Auteur: @{data['owner']['username']}")
    print(f"📝 Caption: {data['caption']}")
else:
    print(f"❌ Erreur: {result['error']}")
```

---

## 🔍 Recherche et découverte

### Rechercher des utilisateurs

```python
# Recherche par nom/username
query = "photography"
count = 20

result = client.search_users(query, count)

if result["success"]:
    users = result["data"]
    print(f"🔍 {len(users)} utilisateurs trouvés:")
    
    for user in users:
        verified = " ✅" if user['is_verified'] else ""
        private = " 🔒" if user['is_private'] else ""
        print(f"👤 @{user['username']}{verified}{private}")
        print(f"   {user['full_name']} - {user['follower_count']:,} abonnés")
else:
    print(f"❌ Erreur: {result['error']}")
```

### Timeline/Feed

```python
# Récupérer le feed personnel
count = 15

result = client.get_timeline_feed(count)

if result["success"]:
    posts = result["data"]
    print(f"📱 {len(posts)} posts dans votre timeline:")
    
    for post in posts:
        user = post['user']
        print(f"👤 @{user['username']}")
        print(f"❤️ {post['like_count']:,} | 💬 {post['comment_count']:,}")
        if post['caption']:
            print(f"📝 {post['caption'][:100]}...")
        print()
else:
    print(f"❌ Erreur: {result['error']}")
```

### Abonnés et abonnements

```python
# Mes abonnés
result = client.get_followers(count=50)

# Mes abonnements  
result = client.get_following(count=50)

# Abonnés d'un utilisateur
url = "https://www.instagram.com/username/"
result = client.get_followers(url, count=30)

if result["success"]:
    users = result["data"]
    for user in users:
        verified = " ✅" if user['is_verified'] else ""
        print(f"👤 @{user['username']}{verified}")
        print(f"   {user['full_name']}")
```

### Posts d'un utilisateur

```python
# Récupérer les posts d'un utilisateur
url = "https://www.instagram.com/username/"
count = 12

result = client.get_user_media_list(url, count)

if result["success"]:
    posts = result["data"]
    print(f"📸 {len(posts)} derniers posts:")
    
    for post in posts:
        print(f"📷 Post {post['code']}")
        print(f"❤️ {post['like_count']:,} | 💬 {post['comment_count']:,}")
        if post['caption']:
            print(f"📝 {post['caption'][:80]}...")
else:
    print(f"❌ Erreur: {result['error']}")
```

---

## 💬 Interactions avec les posts

### Commentaires d'un post

```python
# Récupérer les commentaires
url = "https://www.instagram.com/p/ABC123/"
count = 30

result = client.get_media_comments(url, count)

if result["success"]:
    comments = result["data"]
    print(f"💬 {len(comments)} commentaires:")
    
    for comment in comments:
        user = comment['user']
        print(f"👤 @{user['username']}")
        print(f"💬 {comment['text']}")
        print(f"🆔 Comment ID: {comment['comment_id']}")
        print()
else:
    print(f"❌ Erreur: {result['error']}")
```

### Utilisateurs qui ont liké

```python
# Récupérer les likers
url = "https://www.instagram.com/p/ABC123/"
count = 50

result = client.get_media_likers(url, count)

if result["success"]:
    likers = result["data"]
    print(f"❤️ {len(likers)} utilisateurs ont liké:")
    
    for user in likers:
        verified = " ✅" if user['is_verified'] else ""
        print(f"👤 @{user['username']}{verified}")
        print(f"   {user['full_name']}")
else:
    print(f"❌ Erreur: {result['error']}")
```

### Supprimer un commentaire

```python
# Supprimer son propre commentaire
url = "https://www.instagram.com/p/ABC123/"
comment_id = "123456789"  # ID récupéré via get_media_comments

result = client.delete_comment(url, comment_id)

if result["success"]:
    print("✅ Commentaire supprimé!")
else:
    print(f"❌ Erreur: {result['error']}")
```

---

## ⚙️ Gestion du compte

### Changer la confidentialité

```python
# Basculer Public ↔ Privé
result = client.toggle_account_privacy()

if result["success"]:
    new_status = result["data"]["new_status"]
    print(f"✅ Compte maintenant: {new_status}")
else:
    print(f"❌ Erreur: {result['error']}")
```

---

## 🔧 Extraction d'IDs

### Extraire Media ID

```python
# Depuis différents formats d'URL
urls = [
    "https://www.instagram.com/p/ABC123/",
    "https://instagr.am/p/ABC123/", 
    "https://vt.tiktok.com/SHORT_LINK/"
]

for url in urls:
    if client.api:
        media_id = client.api.extract_media_id_from_url(url)
        print(f"URL: {url}")
        print(f"MEDIA ID: {media_id}")
        print()
```

### Extraire User ID

```python
# Depuis profils avec recherche similaire
urls = [
    "https://www.instagram.com/username/",
    "https://www.instagram.com/similar_username/",  # Recherche similaire
    "@username"
]

for url in urls:
    if client.api:
        user_id = client.api.extract_user_id_from_url(url)
        print(f"URL: {url}")
        print(f"USER ID: {user_id}")
        print()
```

---

## 🔗 Support des liens courts

La bibliothèque résout automatiquement tous types de liens courts :

```python
# Liens supportés automatiquement
short_links = [
    "https://vt.tiktok.com/ZSSRHS2Mt/",
    "https://bit.ly/3xyz",
    "https://t.co/abcd123",
    "https://instagr.am/p/ABC123/"
]

for link in short_links:
    # Résolution automatique lors de l'extraction
    if client.api:
        # Pour posts
        if '/p/' in link or 'tiktok' in link:
            media_id = client.api.extract_media_id_from_url(link)
            print(f"Lien court: {link}")
            print(f"MEDIA ID: {media_id}")
        
        # Pour profils  
        else:
            user_id = client.api.extract_user_id_from_url(link)
            print(f"USER ID: {user_id}")
```

---

## 🎨 Gestion des erreurs et logs

### Vérifier le succès d'une action

```python
# Pattern standard pour toutes les actions
result = client.like_post(url)

# Vérification simple
if result["success"]:
    print("✅ Action réussie!")
    
    # Accéder aux données si disponibles
    if "data" in result:
        print(f"📊 Données: {result['data']}")
else:
    print(f"❌ Échec: {result['error']}")
    
    # Types d'erreurs courantes:
    error_types = {
        "Ce media a été supprimé": "Média inexistant",
        "Utilisateur introuvable": "Profil non trouvé", 
        "Le compte @user est déconnecté": "Session expirée",
        "Le compte @user est suspendu": "Compte suspendu",
        "Rate limit": "Trop d'actions rapides"
    }
```

### Affichage des IDs

```python
# Afficher Media ID et User ID avec style
def show_media_id(media_id):
    print(f"\033[95mMEDIA ID\033[0m: \033[97m{media_id}\033[0m")

def show_user_id(user_id):
    print(f"\033[95mUSER ID\033[0m: \033[97m{user_id}\033[0m")

# Utilisation
url = "https://www.instagram.com/p/ABC123/"
if client.api:
    media_id = client.api.extract_media_id_from_url(url)
    show_media_id(media_id)
```

### Messages colorés

```python
# Définir les couleurs
class Colors:
    GREEN = '\033[92m'    # Succès
    RED = '\033[91m'      # Erreur  
    PURPLE = '\033[95m'   # IDs
    WHITE = '\033[97m'    # Valeurs
    RESET = '\033[0m'     # Reset

# Fonctions d'affichage
def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")

def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")

# Utilisation dans les actions
result = client.like_post(url)
if result["success"]:
    print_success("Like réussi!")
else:
    print_error(f"Échec: {result['error']}")
```

---

## 🚨 Gestion des exceptions

```python
from insta_kendou import InstagramClient
from insta_kendou.exceptions import *

try:
    client = InstagramClient()
    result = client.login("username", "password")
    
except LicenseError:
    print("❌ Code d'accès manquant")
    print("📞 Contact: 0389561802 | https://t.me/Kenny5626")
    
except AuthenticationError as e:
    print(f"❌ Erreur authentification: {e}")
    
except TwoFactorError as e:
    print(f"🔐 Erreur 2FA: {e}")
    print(f"📱 Méthodes: {e.methods}")
    
except MediaError as e:
    print(f"📸 Erreur média: {e}")
    print(f"🆔 Media ID: {e.media_id}")
    
except Exception as e:
    print(f"❌ Erreur inattendue: {e}")
```

---

## 📱 Script d'exemple complet

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemple d'utilisation complète de insta_kendou
"""

from insta_kendou import InstagramClient

# Code d'accès obligatoire
ACCESS_CODE = "MampifalyfelicienKennyNestinFoad56266325$17Mars2004FeliciteGemmellineNestine"

def main():
    """Exemple d'utilisation complète"""
    
    # 1. Initialisation
    client = InstagramClient()
    
    # 2. Connexion ou chargement session
    username = "your_username"
    
    # Essayer de charger session existante
    session_data = client.load_session(username)
    
    if session_data:
        print(f"✅ Session chargée pour @{username}")
    else:
        # Connexion avec 2FA automatique
        password = "your_password"
        result = client.login(username, password)
        
        if result["success"]:
            print(f"✅ Connexion réussie: @{username}")
        else:
            print(f"❌ Erreur: {result['message']}")
            return
    
    # 3. Exemples d'actions
    
    # Like un post
    post_url = "https://www.instagram.com/p/ABC123/"
    result = client.like_post(post_url)
    print("✅ Like réussi!" if result["success"] else f"❌ {result['error']}")
    
    # Follow un utilisateur
    profile_url = "https://www.instagram.com/username/"
    result = client.follow_user(profile_url)
    print("✅ Follow réussi!" if result["success"] else f"❌ {result['error']}")
    
    # Commenter
    comment = "Super post! 👍"
    result = client.comment_post(post_url, comment)
    print("✅ Commentaire ajouté!" if result["success"] else f"❌ {result['error']}")
    
    # Upload story
    story_path = "/path/to/story.jpg"
    if os.path.exists(story_path):
        result = client.upload_story(story_path)
        print("✅ Story publiée!" if result["success"] else f"❌ {result['error']}")
    
    # Upload post avec légende
    post_path = "/path/to/post.jpg"
    caption = "Ma nouvelle publication! #instagram"
    if os.path.exists(post_path):
        result = client.upload_post(post_path, caption)
        print("✅ Post publié!" if result["success"] else f"❌ {result['error']}")
    
    # Informations du compte
    result = client.get_account_info()
    if result["success"]:
        data = result["data"]
        print(f"\n📊 Compte: @{data['username']}")
        print(f"👥 {data['follower_count']:,} abonnés")
        print(f"📸 {data['media_count']:,} publications")
    
    # Rechercher utilisateurs
    result = client.search_users("photography", 10)
    if result["success"]:
        print(f"\n🔍 {len(result['data'])} utilisateurs trouvés")
    
    # Sauvegarder session
    client.dump_session(username)
    print("💾 Session sauvegardée")

if __name__ == "__main__":
    main()
```

---

## 📞 Support et contact

- **Téléphone** : 0389561802
- **Telegram** : https://t.me/Kenny5626
- **GitHub** : @Ken56266325

---

## ⚖️ Licence

Cette bibliothèque est à usage privé et nécessite un code d'accès valide pour fonctionner.

© 2024 Kenny - Tous droits réservés
