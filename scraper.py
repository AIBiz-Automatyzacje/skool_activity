#!/usr/bin/env python3
"""
Skool Activity Scraper
Pobiera liczbę aktywnych użytkowników z grupy Skool i zapisuje do bazy danych
"""

import json
import requests
import psycopg2
import subprocess
import sys
from bs4 import BeautifulSoup
from datetime import datetime


def load_config():
    """Wczytuje konfigurację z pliku config.json"""
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Błąd: Nie znaleziono pliku config.json")
        print("Utwórz plik config.json i dodaj swoje cookies")
        exit(1)
    except json.JSONDecodeError:
        print("❌ Błąd: Nieprawidłowy format JSON w config.json")
        exit(1)


def send_error_webhook(webhook_url):
    """
    Wysyła powiadomienie na webhook o błędzie autoryzacji

    Args:
        webhook_url (str): URL webhooka do powiadomienia

    Returns:
        bool: True jeśli wysłano pomyślnie, False w przeciwnym razie
    """
    try:
        print(f"📨 Wysyłanie powiadomienia na webhook...")
        response = requests.get(webhook_url, timeout=10)

        if response.status_code == 200:
            print("✅ Webhook wywołany pomyślnie")
            return True
        else:
            print(f"⚠️  Webhook odpowiedział kodem: {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️  Błąd wysyłania webhooka: {e}")
        return False


def stop_timer():
    """
    Zatrzymuje systemd timer

    Returns:
        bool: True jeśli zatrzymano pomyślnie, False w przeciwnym razie
    """
    try:
        print("🛑 Zatrzymywanie timera...")
        result = subprocess.run(
            ['systemctl', 'stop', 'skool-scraper.timer'],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("✅ Timer zatrzymany pomyślnie")
            return True
        else:
            print(f"⚠️  Nie udało się zatrzymać timera: {result.stderr}")
            return False
    except Exception as e:
        print(f"⚠️  Błąd zatrzymywania timera: {e}")
        return False


def handle_auth_error(webhook_url):
    """
    Obsługuje błąd autoryzacji - wysyła webhook i zatrzymuje timer

    Args:
        webhook_url (str): URL webhooka do powiadomienia
    """
    print()
    print("=" * 70)
    print("🚨 BŁĄD AUTORYZACJI - COOKIES WYGASŁY")
    print("=" * 70)
    print()

    # Wyślij webhook
    if webhook_url:
        send_error_webhook(webhook_url)
    else:
        print("⚠️  Brak URL webhooka w konfiguracji")

    # Zatrzymaj timer
    stop_timer()

    print()
    print("=" * 70)
    print("📝 CO DALEJ:")
    print("1. Zaloguj się ponownie na Skool w przeglądarce")
    print("2. Pobierz nowe cookies z DevTools")
    print("3. Zaktualizuj plik /opt/skool_scraper/config.json")
    print("4. Uruchom timer ponownie:")
    print("   sudo systemctl start skool-scraper.timer")
    print("=" * 70)
    print()


def get_active_users(url, cookies):
    """
    Pobiera liczbę aktywnych użytkowników ze strony Skool

    Args:
        url (str): URL do grupy Skool
        cookies (dict): Słownik z cookies do autoryzacji

    Returns:
        tuple: (liczba_użytkowników: int|None, auth_error: bool)
               auth_error=True oznacza błąd autoryzacji (wygasłe cookies)
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
    }

    try:
        print(f"📡 Łączenie z {url}...")
        response = requests.get(url, cookies=cookies, headers=headers, timeout=30)

        if response.status_code == 200:
            print("✅ Połączono pomyślnie")

            soup = BeautifulSoup(response.content, 'lxml')

            # Szukamy linka z href zawierającym "/members?t=online"
            # To jest link do strony z użytkownikami online
            online_link = soup.find('a', href=lambda x: x and '/members?t=online' in x)

            if online_link:
                print(f"🔍 Znaleziono link do użytkowników online")

                # W linku szukamy divów z klasą styled__TypographyWrapper-sc-70zmwu-0
                number_divs = online_link.find_all('div', class_='styled__TypographyWrapper-sc-70zmwu-0')

                # Pierwszy div powinien zawierać liczbę, drugi tekst "Online"
                for div in number_divs:
                    text = div.get_text(strip=True)
                    if text.isdigit():
                        active_count = int(text)
                        print(f"✨ Znaleziono liczbę użytkowników online: {active_count}")
                        return (active_count, False)

            # Fallback - jeśli nie znaleziono przez link, spróbuj szukać przez tekst "Online"
            print("⚠️  Nie znaleziono przez link, próbuję alternatywnej metody...")
            elements = soup.find_all('div', class_='styled__TypographyWrapper-sc-70zmwu-0')

            for i, elem in enumerate(elements):
                text = elem.get_text(strip=True)
                if text.lower() == 'online':
                    # Sprawdź poprzedni element - powinien zawierać liczbę
                    if i > 0:
                        prev_elem = elements[i - 1]
                        prev_text = prev_elem.get_text(strip=True)
                        if prev_text.isdigit():
                            active_count = int(prev_text)
                            print(f"✨ Znaleziono liczbę użytkowników online: {active_count}")
                            return (active_count, False)

            print("❌ Nie znaleziono liczby aktywnych użytkowników")
            print("🔧 Sprawdź strukturę HTML strony lub cookies")
            return (None, False)

        elif response.status_code == 401 or response.status_code == 403:
            print(f"❌ Błąd autoryzacji (kod: {response.status_code})")
            print("🔧 Cookies wygasły lub są nieprawidłowe")
            return (None, True)  # auth_error = True
        else:
            print(f"❌ Błąd HTTP: {response.status_code}")
            return (None, False)

    except requests.exceptions.Timeout:
        print("❌ Przekroczono czas oczekiwania na odpowiedź")
        return (None, False)
    except requests.exceptions.ConnectionError:
        print("❌ Błąd połączenia - sprawdź połączenie internetowe")
        return (None, False)
    except Exception as e:
        print(f"❌ Nieoczekiwany błąd: {e}")
        return (None, False)


def save_to_database(database_url, timestamp, online_users):
    """
    Zapisuje dane do bazy danych PostgreSQL

    Args:
        database_url (str): Connection string do bazy danych
        timestamp (datetime): Timestamp pomiaru
        online_users (int): Liczba użytkowników online

    Returns:
        bool: True jeśli zapis się powiódł, False w przeciwnym razie
    """
    try:
        print("💾 Zapisywanie do bazy danych...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()

        # Wstawienie danych do tabeli
        cursor.execute("""
            INSERT INTO activity_logs (timestamp, online_users)
            VALUES (%s, %s)
            RETURNING id;
        """, (timestamp, online_users))

        record_id = cursor.fetchone()[0]
        conn.commit()

        print(f"✅ Zapisano do bazy (ID: {record_id})")

        cursor.close()
        conn.close()
        return True

    except Exception as e:
        print(f"❌ Błąd zapisu do bazy: {e}")
        return False


def main():
    """Główna funkcja programu"""
    print("=" * 50)
    print("🚀 Skool Activity Scraper")
    print("=" * 50)
    print()

    # Wczytaj konfigurację
    config = load_config()
    url = config.get('url')
    cookies = config.get('cookies', {})
    database_url = config.get('database_url')
    error_webhook = config.get('error_webhook')

    if not url:
        print("❌ Błąd: Brak URL w pliku config.json")
        exit(1)

    if not cookies:
        print("❌ Błąd: Brak cookies w pliku config.json")
        exit(1)

    if not database_url:
        print("❌ Błąd: Brak database_url w pliku config.json")
        exit(1)

    # Pobierz dane
    timestamp = datetime.now()
    print(f"🕐 Czas: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    active_users, auth_error = get_active_users(url, cookies)

    # Obsługa błędu autoryzacji
    if auth_error:
        handle_auth_error(error_webhook)
        exit(2)  # Exit code 2 = błąd autoryzacji

    if active_users is not None:
        print()
        print("=" * 50)
        print(f"📊 WYNIK: {active_users} użytkowników online")
        print("=" * 50)
        print()

        # Zapisz do bazy danych
        if save_to_database(database_url, timestamp, active_users):
            print()
            print("✅ Operacja zakończona pomyślnie!")
        else:
            print()
            print("⚠️  Dane pobrane, ale nie zapisano do bazy")
            exit(1)
    else:
        print()
        print("=" * 50)
        print("❌ Nie udało się pobrać danych")
        print("=" * 50)
        exit(1)


if __name__ == "__main__":
    main()
