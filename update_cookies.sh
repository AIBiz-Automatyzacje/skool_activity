#!/bin/bash
###############################################################################
# Skrypt pomocniczy do aktualizacji cookies
# Uruchom ten skrypt gdy cookies wygasną
###############################################################################

echo "🔧 Aktualizacja cookies dla Skool Scraper"
echo "=========================================="
echo ""
echo "INSTRUKCJA:"
echo "1. Zaloguj się na https://www.skool.com w przeglądarce"
echo "2. Otwórz DevTools (F12) → Application → Cookies"
echo "3. Skopiuj wartości cookies"
echo ""
echo "Edytuję config.json..."
echo ""

if [ "$EUID" -ne 0 ]; then
    nano config.json
else
    nano /opt/skool_scraper/config.json
fi

echo ""
echo "✅ Plik zapisany!"
echo ""
echo "Czy chcesz uruchomić timer ponownie? (y/n)"
read -r response

if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
    echo "🚀 Uruchamiam timer..."
    sudo systemctl start skool-scraper.timer
    sudo systemctl status skool-scraper.timer
    echo ""
    echo "✅ Timer uruchomiony!"
    echo ""
    echo "Sprawdź logi:"
    echo "  tail -f /var/log/skool-scraper.log"
else
    echo "⏸️  Timer nie został uruchomiony."
    echo "Aby uruchomić ręcznie:"
    echo "  sudo systemctl start skool-scraper.timer"
fi
