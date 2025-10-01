#!/bin/bash
###############################################################################
# Skrypt instalacyjny Skool Activity Scraper dla VPS
# Automatycznie instaluje i konfiguruje scraper na serwerze Linux
###############################################################################

set -e  # Zatrzymaj przy pierwszym błędzie

echo "=================================================="
echo "🚀 Instalacja Skool Activity Scraper"
echo "=================================================="
echo ""

# Sprawdź czy uruchamiasz jako root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Uruchom skrypt jako root (sudo ./install.sh)"
    exit 1
fi

# Katalog instalacji
INSTALL_DIR="/opt/skool_scraper"

echo "📦 Aktualizacja systemu..."
apt-get update -qq

echo "📦 Instalacja zależności systemowych..."
apt-get install -y python3 python3-pip python3-venv git

echo "📁 Tworzenie katalogu instalacji: $INSTALL_DIR"
mkdir -p $INSTALL_DIR

echo "📋 Kopiowanie plików..."
# Zakładam, że skrypt jest uruchamiany z głównego katalogu projektu
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cp $SCRIPT_DIR/scraper.py $INSTALL_DIR/
cp $SCRIPT_DIR/view_data.py $INSTALL_DIR/
cp $SCRIPT_DIR/create_table.py $INSTALL_DIR/
cp $SCRIPT_DIR/requirements.txt $INSTALL_DIR/
cp $SCRIPT_DIR/update_cookies.sh $INSTALL_DIR/
chmod +x $INSTALL_DIR/update_cookies.sh

# Kopiuj pliki systemd
echo "📝 Kopiowanie plików systemd..."
cp $SCRIPT_DIR/systemd/skool-scraper.service /etc/systemd/system/
cp $SCRIPT_DIR/systemd/skool-scraper.timer /etc/systemd/system/

# Sprawdź czy config.json istnieje
if [ ! -f "$SCRIPT_DIR/config.json" ]; then
    echo "⚠️  Nie znaleziono config.json - kopiuję config.json.example"
    if [ -f "$SCRIPT_DIR/config.json.example" ]; then
        cp $SCRIPT_DIR/config.json.example $INSTALL_DIR/config.json
        echo "⚠️  WAŻNE: Edytuj $INSTALL_DIR/config.json i dodaj swoje credentials!"
    else
        echo "❌ Nie znaleziono ani config.json ani config.json.example"
        exit 1
    fi
else
    cp $SCRIPT_DIR/config.json $INSTALL_DIR/
    echo "✅ Skopiowano config.json"
fi

echo "🐍 Tworzenie wirtualnego środowiska Python..."
cd $INSTALL_DIR
python3 -m venv venv

echo "📦 Instalacja zależności Python..."
source venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo "🔄 Przeładowanie systemd..."
systemctl daemon-reload

echo "✅ Włączanie timera..."
systemctl enable skool-scraper.timer
systemctl start skool-scraper.timer

echo ""
echo "=================================================="
echo "✅ Instalacja zakończona pomyślnie!"
echo "=================================================="
echo ""
echo "📋 Użyteczne komendy:"
echo "  • Status timera:        systemctl status skool-scraper.timer"
echo "  • Zatrzymaj timer:      systemctl stop skool-scraper.timer"
echo "  • Uruchom timer:        systemctl start skool-scraper.timer"
echo "  • Zobacz logi:          tail -f /var/log/skool-scraper.log"
echo "  • Zobacz błędy:         tail -f /var/log/skool-scraper-error.log"
echo "  • Uruchom ręcznie:      systemctl start skool-scraper.service"
echo "  • Zobacz dane z bazy:   cd $INSTALL_DIR && source venv/bin/activate && python view_data.py"
echo ""
echo "⏱️  Scraper będzie uruchamiany automatycznie co minutę"
echo ""
