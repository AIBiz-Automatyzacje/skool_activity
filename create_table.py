#!/usr/bin/env python3
"""
Skrypt do utworzenia tabeli w bazie danych Neon
Uruchom ten skrypt tylko raz!
"""

import psycopg2

# Connection string do Neon
DATABASE_URL = "postgresql://neondb_owner:npg_dXxhIZ0JEc7w@ep-super-flower-adzmzyqq-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"

def create_table():
    """Tworzy tabelę activity_logs w bazie danych"""
    try:
        print("🔌 Łączenie z bazą danych Neon...")
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        print("📝 Tworzenie tabeli activity_logs...")

        # Tworzenie tabeli
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_logs (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL,
                online_users INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Tworzenie indeksu
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_activity_logs_timestamp
            ON activity_logs(timestamp);
        """)

        conn.commit()
        print("✅ Tabela utworzona pomyślnie!")

        # Sprawdzenie struktury tabeli
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'activity_logs'
            ORDER BY ordinal_position;
        """)

        print("\n📋 Struktura tabeli activity_logs:")
        print("-" * 50)
        for row in cursor.fetchall():
            print(f"  {row[0]:<15} | {row[1]:<20} | nullable: {row[2]}")
        print("-" * 50)

        cursor.close()
        conn.close()
        print("\n✅ Gotowe! Możesz teraz uruchomić scraper.")

    except Exception as e:
        print(f"❌ Błąd: {e}")
        exit(1)

if __name__ == "__main__":
    create_table()
