# insta_kendou

Bibliothèque Instagram complète avec authentification 2FA et gestion des médias.

## Installation

```bash
pip install insta_kendou
```

## Utilisation

```python
from insta_kendou import InstagramClient

# Initialiser le client
client = InstagramClient()

# Se connecter
result = client.login("username", "password")

# Utiliser les fonctionnalités
if result["success"]:
    # Liker un post
    client.like_post("https://instagram.com/p/ABC123/")
    
    # Publier une story
    client.upload_story("/path/to/image.jpg")
```

## Licence

Propriétaire - Contactez le créateur pour les droits d'utilisation.
