#!/bin/bash
# Script de build automatique pour insta_kendou
# Build, obfuscation et publication sur GitHub
set -e  # Arrêter en cas d'erreur

echo "🚀 Build automatique d'insta_kendou"
echo "=================================="

# Variables
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="$PROJECT_ROOT/build"
DIST_DIR="$PROJECT_ROOT/dist"

cd "$PROJECT_ROOT"

# Détection de l'environnement Python (Windows compatible)
if command -v python &> /dev/null; then
    PYTHON_CMD="python"
elif command -v py &> /dev/null; then
    PYTHON_CMD="py"
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    echo "❌ Python non trouvé!"
    exit 1
fi

echo "🐍 Utilisation de: $PYTHON_CMD"

# Étape 1: Nettoyage
echo "🧹 Nettoyage des fichiers précédents..."
$PYTHON_CMD build_tools/obfuscate.py clean

# Étape 2: Vérification des dépendances
echo "📋 Vérification des dépendances..."

# Installer les dépendances de build si nécessaire
$PYTHON_CMD -m pip install --upgrade pip setuptools wheel > /dev/null 2>&1

# Étape 3: Tests de base (vérification syntaxe)
echo "🔍 Vérification de la syntaxe Python..."
find insta_kendou -name "*.py" -exec $PYTHON_CMD -m py_compile {} \;
echo "✅ Syntaxe Python validée"

# Étape 4: Obfuscation et build
echo "🔒 Obfuscation et création du package..."
$PYTHON_CMD build_tools/obfuscate.py build

# Étape 5: Vérification du package
echo "🔍 Vérification du package créé..."
WHEEL_FILE=$(find "$DIST_DIR" -name "*.whl" -type f | head -1)
if [ -z "$WHEEL_FILE" ]; then
    echo "❌ Aucun fichier wheel trouvé!"
    exit 1
fi

echo "✅ Package créé: $(basename "$WHEEL_FILE")"

# Étape 6: Test d'installation
echo "🧪 Test d'installation du package..."
TEMP_ENV=$(mktemp -d)
$PYTHON_CMD -m venv "$TEMP_ENV" > /dev/null 2>&1

# Activation du virtual environment (compatible Windows/MINGW)
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    # Windows/MINGW
    source "$TEMP_ENV/Scripts/activate"
else
    # Linux/macOS
    source "$TEMP_ENV/bin/activate"
fi

pip install "$WHEEL_FILE" > /dev/null 2>&1

$PYTHON_CMD -c "import insta_kendou; print('✅ Import réussi')" 2>/dev/null || {
    echo "❌ Échec du test d'import"
    deactivate
    rm -rf "$TEMP_ENV"
    exit 1
}

deactivate
rm -rf "$TEMP_ENV"

# Étape 7: Préparer pour GitHub (optionnel)
echo "📦 Package prêt pour GitHub"
echo "   Fichier: $WHEEL_FILE"
echo "   Taille: $(du -h "$WHEEL_FILE" | cut -f1)"

# Étape 8: Instructions finales
echo ""
echo "✨ BUILD TERMINÉ AVEC SUCCÈS!"
echo "========================="
echo ""
echo "📋 Prochaines étapes:"
echo "   1. Commit des changements: git add . && git commit -m 'Update package'"
echo "   2. Push vers GitHub: git push origin main"
echo "   3. Installation: pip install git+https://github.com/Ken56266325/insta_kendou.git"
echo ""
echo "📞 Support: 0389561802 | https://t.me/Kenny5626"
echo ""

exit 0
