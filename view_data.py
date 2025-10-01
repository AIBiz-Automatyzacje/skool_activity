#!/usr/bin/env python3
"""
Skrypt do wyświetlania danych z bazy
"""

import json
import psycopg2
from datetime import datetime


def load_config():
    """Wczytuje konfigurację z pliku config.json"""
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)


def view_recent_data(database_url, limit=10):
    """
    Wyświetla ostatnie wpisy z bazy danych

    Args:
        database_url (str): Connection string do bazy danych
        limit (int): Liczba rekordów do wyświetlenia
    """
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()

        # Pobierz ostatnie rekordy
        cursor.execute("""
            SELECT id, timestamp, online_users, created_at
            FROM activity_logs
            ORDER BY timestamp DESC
            LIMIT %s;
        """, (limit,))

        records = cursor.fetchall()

        print("=" * 80)
        print(f"📊 Ostatnie {limit} wpisów z bazy danych")
        print("=" * 80)
        print()

        if not records:
            print("⚠️  Brak danych w bazie")
        else:
            print(f"{'ID':<6} {'Timestamp':<20} {'Online':<10} {'Utworzono':<20}")
            print("-" * 80)
            for record in records:
                id_val, timestamp, online_users, created_at = record
                timestamp_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
                created_str = created_at.strftime('%Y-%m-%d %H:%M:%S')
                print(f"{id_val:<6} {timestamp_str:<20} {online_users:<10} {created_str:<20}")

        print()
        print("=" * 80)

        # Statystyki
        cursor.execute("""
            SELECT
                COUNT(*) as total_records,
                AVG(online_users) as avg_users,
                MIN(online_users) as min_users,
                MAX(online_users) as max_users
            FROM activity_logs;
        """)

        stats = cursor.fetchone()
        total, avg, min_val, max_val = stats

        print("📈 Statystyki:")
        print(f"  • Wszystkich rekordów: {total}")
        print(f"  • Średnio użytkowników: {avg:.2f}")
        print(f"  • Minimum: {min_val}")
        print(f"  • Maximum: {max_val}")
        print("=" * 80)

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Błąd: {e}")


if __name__ == "__main__":
    config = load_config()
    database_url = config.get('database_url')

    if not database_url:
        print("❌ Błąd: Brak database_url w pliku config.json")
        exit(1)

    view_recent_data(database_url, limit=20)
