-- Skrypt do utworzenia tabeli w bazie Neon PostgreSQL
-- Uruchom ten skrypt tylko raz, aby utworzyć strukturę bazy danych

-- Tworzenie tabeli dla logów aktywności
CREATE TABLE IF NOT EXISTS activity_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    online_users INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tworzenie indeksu na timestamp dla szybszych zapytań
CREATE INDEX IF NOT EXISTS idx_activity_logs_timestamp ON activity_logs(timestamp);

-- Wyświetlenie struktury tabeli
\d activity_logs;
