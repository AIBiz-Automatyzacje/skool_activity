# Skool Activity Scraper

Automatyczny scraper do monitorowania aktywności użytkowników w grupach Skool. Pobiera liczbę użytkowników online co minutę i zapisuje do bazy danych PostgreSQL.

## 🎯 Funkcje

- ✅ Automatyczne pobieranie liczby użytkowników online z grupy Skool
- ✅ Zapis danych do bazy PostgreSQL (Neon)
- ✅ Uruchamianie co minutę przez systemd timer
- ✅ Logowanie do plików
- ✅ Automatyczny restart przy błędzie
- ✅ Wyświetlanie statystyk z bazy danych

## 📋 Wymagania

- Python 3.9+
- PostgreSQL (zalecamy [Neon.tech](https://neon.tech) - darmowy tier)
- Linux VPS z systemd (Ubuntu/Debian polecane)
- Dostęp do grupy Skool (zalogowany użytkownik)

## 🚀 Instalacja na VPS

### Krok 1: Przygotowanie bazy danych

1. Załóż konto na [Neon.tech](https://neon.tech)
2. Utwórz nową bazę danych
3. Skopiuj connection string (będzie wyglądać tak: `postgresql://user:pass@host/db`)

### Krok 2: Przygotowanie cookies

1. Zaloguj się na Skool w przeglądarce
2. Otwórz DevTools (F12) → Application/Storage → Cookies
3. Skopiuj wartości wszystkich cookies z domeny `.skool.com` i `www.skool.com`

### Krok 3: Transfer plików na VPS

**Opcja A - Git (polecana):**
```bash
# Lokalnie
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/twoj-user/skool-scraper.git
git push -u origin main

# Na VPS
ssh user@twoj-vps.com
git clone https://github.com/twoj-user/skool-scraper.git
cd skool-scraper
```

**Opcja B - SCP:**
```bash
# Z lokalnego komputera
scp -r /sciezka/do/skool_activity user@twoj-vps.com:/tmp/
```

### Krok 4: Konfiguracja

1. Skopiuj przykładową konfigurację:
```bash
cp config.json.example config.json
```

2. Edytuj `config.json` i wklej swoje dane:
```bash
nano config.json
```

```json
{
  "cookies": {
    "auth_token": "TWOJ_AUTH_TOKEN",
    "client_id": "TWOJ_CLIENT_ID",
    ...
  },
  "url": "https://www.skool.com/twoja-grupa",
  "database_url": "postgresql://user:pass@host/db"
}
```

### Krok 5: Instalacja

```bash
sudo ./install.sh
```

Skrypt automatycznie:
- Zainstaluje Python i zależności
- Utworzy wirtualne środowisko
- Zainstaluje paczki Python
- Skonfiguruje systemd timer
- Uruchomi scraper

## 📊 Użycie

### Sprawdzanie statusu

```bash
# Status timera
systemctl status skool-scraper.timer

# Status ostatniego uruchomienia
systemctl status skool-scraper.service

# Logi scraper
tail -f /var/log/skool-scraper.log

# Logi błędów
tail -f /var/log/skool-scraper-error.log
```

### Zarządzanie scraperem

```bash
# Zatrzymaj
sudo systemctl stop skool-scraper.timer

# Uruchom
sudo systemctl start skool-scraper.timer

# Restart
sudo systemctl restart skool-scraper.timer

# Uruchom raz ręcznie
sudo systemctl start skool-scraper.service
```

### Wyświetlanie danych z bazy

```bash
cd /opt/skool_scraper
source venv/bin/activate
python view_data.py
```

## 🚨 Automatyczna obsługa błędów autoryzacji

Scraper automatycznie wykrywa wygasłe cookies i:
1. ✅ Wysyła powiadomienie na webhook (n8n)
2. ✅ Zatrzymuje timer automatycznie
3. ✅ Wyświetla instrukcję naprawy w logach

**Gdy cookies wygasną, scraper sam się zatrzyma!**

### Jak zaktualizować wygasłe cookies i uruchomić ponownie?

**Opcja A - Automatyczny skrypt (ŁATWY SPOSÓB):**
```bash
ssh user@twoj-vps.com
cd /opt/skool_scraper
sudo ./update_cookies.sh
```
Skrypt automatycznie otworzy edytor, poprosi o wklejenie nowych cookies i uruchomi timer.

**Opcja B - Ręcznie:**

1. **Pobierz nowe cookies:**
   - Otwórz przeglądarkę i zaloguj się na [Skool](https://www.skool.com)
   - Otwórz DevTools (F12) → Application/Storage → Cookies
   - Skopiuj wszystkie cookies z domeny `.skool.com` i `www.skool.com`

2. **Zaktualizuj config.json na VPS:**
   ```bash
   ssh user@twoj-vps.com
   sudo nano /opt/skool_scraper/config.json
   # Wklej nowe cookies
   ```

3. **Uruchom timer ponownie:**
   ```bash
   sudo systemctl start skool-scraper.timer
   sudo systemctl status skool-scraper.timer
   ```

4. **Sprawdź czy działa:**
   ```bash
   tail -f /var/log/skool-scraper.log
   ```

## 🛠️ Rozwiązywanie problemów

### Scraper nie pobiera danych (ogólne błędy)

1. Sprawdź logi:
```bash
tail -f /var/log/skool-scraper-error.log
```

2. Uruchom ręcznie aby zobaczyć błąd:
```bash
cd /opt/skool_scraper
source venv/bin/activate
python scraper.py
```

### Błąd połączenia z bazą danych

1. Sprawdź connection string w `config.json`
2. Sprawdź czy baza Neon nie jest zawieszona (auto-suspend po braku aktywności)
3. Przetestuj połączenie ręcznie:
```bash
cd /opt/skool_scraper
source venv/bin/activate
python create_table.py
```

### Timer się nie uruchamia

```bash
# Sprawdź status timera
systemctl status skool-scraper.timer

# Sprawdź czy jest włączony
systemctl list-timers --all | grep skool

# Włącz ponownie
sudo systemctl enable skool-scraper.timer
sudo systemctl start skool-scraper.timer
```

## 📁 Struktura plików

```
/opt/skool_scraper/
├── venv/                      # Wirtualne środowisko Python
├── scraper.py                 # Główny skrypt
├── view_data.py               # Wyświetlanie danych
├── create_table.py            # Tworzenie tabeli (jednorazowo)
├── requirements.txt           # Zależności Python
├── config.json                # Konfiguracja (NIE commituj!)
├── update_cookies.sh          # Skrypt pomocniczy do aktualizacji cookies
└── systemd/
    ├── skool-scraper.service  # Definicja service
    └── skool-scraper.timer    # Definicja timera

/var/log/
├── skool-scraper.log          # Logi główne
└── skool-scraper-error.log    # Logi błędów

/etc/systemd/system/
├── skool-scraper.service      # Zainstalowany service
└── skool-scraper.timer        # Zainstalowany timer
```

## 🔒 Bezpieczeństwo

- ⚠️ **NIE commituj** `config.json` do repozytorium (zawiera credentials)
- ✅ Użyj `.gitignore` aby wykluczyć `config.json`
- ✅ Ogranicz uprawnienia do `config.json`: `chmod 600 /opt/skool_scraper/config.json`
- ✅ Connection string do bazy zawiera hasło - przechowuj bezpiecznie

## 📈 Dane w bazie

### Struktura tabeli `activity_logs`

| Kolumna       | Typ       | Opis                           |
|---------------|-----------|--------------------------------|
| id            | SERIAL    | ID rekordu (auto-increment)    |
| timestamp     | TIMESTAMP | Czas pomiaru                   |
| online_users  | INTEGER   | Liczba użytkowników online     |
| created_at    | TIMESTAMP | Czas utworzenia rekordu w DB   |

### Przykładowe zapytania SQL

```sql
-- Ostatnie 10 pomiarów
SELECT * FROM activity_logs ORDER BY timestamp DESC LIMIT 10;

-- Średnia użytkowników online w ciągu ostatniej godziny
SELECT AVG(online_users) FROM activity_logs
WHERE timestamp > NOW() - INTERVAL '1 hour';

-- Maksimum użytkowników dzisiaj
SELECT MAX(online_users) FROM activity_logs
WHERE DATE(timestamp) = CURRENT_DATE;

-- Średnia użytkowników online dla każdej godziny
SELECT
    DATE_TRUNC('hour', timestamp) as hour,
    AVG(online_users) as avg_users,
    MAX(online_users) as max_users
FROM activity_logs
GROUP BY hour
ORDER BY hour DESC;
```

## 🤝 Wsparcie

W razie problemów:
1. Sprawdź logi: `/var/log/skool-scraper-error.log`
2. Sprawdź status: `systemctl status skool-scraper.timer`
3. Przetestuj ręcznie: `cd /opt/skool_scraper && source venv/bin/activate && python scraper.py`

## 📝 Licencja

MIT
