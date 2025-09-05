#!/bin/bash
# -*- coding: utf-8 -*-
"""
Script de build automatisé pour insta_kendou
Obfuscation, packaging et publication sur GitHub
"""

set -e  # Arrêter en cas d'erreur

# Variables de configuration
PROJECT_NAME="insta_kendou"
GITHUB_REPO="Ken56266325/insta_kendou"
BUILD_DIR="build"
DIST_DIR="dist"
OBFUSCATED_DIR="obfuscated"

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

echo_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

echo_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

echo_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Fonction de nettoyage
cleanup() {
    echo_info "Nettoyage des fichiers temporaires..."
    rm -rf $BUILD_DIR
    rm -rf $DIST_DIR
    rm -rf *.egg-info
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -delete 2>/dev/null || true
}

# Fonction de vérification des dépendances
check_dependencies() {
    echo_info "Vérification des dépendances..."
    
    # Vérifier Python
    if ! command -v python &> /dev/null; then
        echo_error "Python n'est pas installé"
        exit 1
    fi
    
    # Vérifier pip
    if ! command -v pip &> /dev/null; then
        echo_error "pip n'est pas installé"
        exit 1
    fi
    
    # Installer les dépendances de build
    pip install --upgrade setuptools wheel twine build
    
    echo_success "Dépendances vérifiées"
}

# Fonction d'obfuscation
obfuscate_code() {
    echo_info "Obfuscation du code source..."
    
    # Créer le répertoire obfusqué
    mkdir -p $OBFUSCATED_DIR
    
    # Copier la structure
    cp -r $PROJECT_NAME $OBFUSCATED_DIR/
    cp setup.py $OBFUSCATED_DIR/
    cp README.md $OBFUSCATED_DIR/
    cp requirements.txt $OBFUSCATED_DIR/
    cp MANIFEST.in $OBFUSCATED_DIR/
    
    # Obfusquer les fichiers Python
    python build_tools/obfuscate.py $PROJECT_NAME $OBFUSCATED_DIR/$PROJECT_NAME
    
    echo_success "Code obfusqué avec succès"
}

# Fonction de build du package
build_package() {
    echo_info "Construction du package..."
    
    cd $OBFUSCATED_DIR
    
    # Nettoyer avant build
    rm -rf build dist *.egg-info
    
    # Build du package
    python -m build
    
    # Vérifier que les fichiers ont été créés
    if [ ! -d "dist" ] || [ -z "$(ls -A dist/)" ]; then
        echo_error "Échec de la construction du package"
        cd ..
        exit 1
    fi
    
    cd ..
    
    echo_success "Package construit avec succès"
}

# Fonction de test du package
test_package() {
    echo_info "Test du package..."
    
    # Installer le package en mode test
    pip install $OBFUSCATED_DIR/dist/*.whl --force-reinstall
    
    # Test basique d'import
    python -c "
try:
    import $PROJECT_NAME
    print('✅ Import réussi')
    
    # Test de base
    from $PROJECT_NAME import InstagramClient
    print('✅ Client import réussi')
    
    client = InstagramClient()
    print('✅ Client créé avec succès')
    
except Exception as e:
    print(f'❌ Erreur test: {e}')
    exit(1)
"
    
    echo_success "Package testé avec succès"
}

# Fonction de publication sur GitHub
publish_github() {
    echo_info "Publication sur GitHub..."
    
    # Vérifier si git est configuré
    if ! git config user.name &> /dev/null; then
        echo_warning "Configuration Git manquante, configuration automatique..."
        git config user.name "Kenny"
        git config user.email "mampifaly56266325@gmail.com"
    fi
    
    # Créer une release
    VERSION=$(python -c "import sys; sys.path.insert(0, '$OBFUSCATED_DIR'); from $PROJECT_NAME import __version__; print(__version__)")
    
    # Copier les fichiers de distribution
    mkdir -p release
    cp -r $OBFUSCATED_DIR/dist/* release/
    
    # Ajouter les changements
    git add release/
    git commit -m "Release v$VERSION - Code obfusqué" || true
    
    # Créer un tag
    git tag -a "v$VERSION" -m "Version $VERSION" || true
    
    # Pousser vers GitHub
    git push origin main || echo_warning "Erreur push - vérifiez la configuration Git"
    git push origin "v$VERSION" || echo_warning "Erreur push tag - vérifiez la configuration Git"
    
    echo_success "Publication sur GitHub terminée"
}

# Fonction principale
main() {
    echo_info "🚀 BUILD AUTOMATISÉ DE $PROJECT_NAME"
    echo "================================================"
    
    # Étape 1: Nettoyage
    cleanup
    
    # Étape 2: Vérification
    check_dependencies
    
    # Étape 3: Obfuscation
    obfuscate_code
    
    # Étape 4: Build
    build_package
    
    # Étape 5: Test
    test_package
    
    # Étape 6: Publication
    if [ "$1" = "--publish" ]; then
        publish_github
    else
        echo_info "Pour publier sur GitHub, utilisez: $0 --publish"
    fi
    
    echo "================================================"
    echo_success "🎉 BUILD TERMINÉ AVEC SUCCÈS!"
    echo_info "Package disponible dans: $OBFUSCATED_DIR/dist/"
}

# Gestion des arguments
case "$1" in
    --clean)
        cleanup
        echo_success "Nettoyage terminé"
        ;;
    --publish)
        main --publish
        ;;
    --help)
        echo "Usage: $0 [--clean|--publish|--help]"
        echo "  --clean    : Nettoyer les fichiers temporaires"
        echo "  --publish  : Builder et publier sur GitHub"
        echo "  --help     : Afficher cette aide"
        ;;
    *)
        main
        ;;
esac
