# Employee Management System — SQLite3

This is the existing Flask Employee Management System converted from MySQL to SQLite3 with minimal application changes. The original HTML templates, CSS, images, routes, and features are retained. `init_db.py` is separate from `app.py`.

## Files

- `app.py` — Flask app using SQLite3 (`company.db`).
- `init_db.py` — creates the SQLite database and tables from `schema.sql`.
- `schema.sql` — definitions for the existing `users` and `employee` tables.
- `migrate_mysql_to_sqlite.py` — one-time transfer of existing MySQL records to SQLite.
- `templates/`, `static/` — original design files.

## Run it and preserve existing MySQL data

1. Extract this ZIP and open the extracted folder in VS Code.
2. Install application dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Set the MySQL credentials used by your existing database. The defaults in the migration script match the original project (`localhost`, user `root`, password `root`, database `company`). If yours differ, set these in PowerShell first:

   ```powershell
   $env:MYSQL_HOST="localhost"
   $env:MYSQL_USER="root"
   $env:MYSQL_PASSWORD="YOUR_MYSQL_PASSWORD"
   $env:MYSQL_DATABASE="company"
   pip install mysql-connector-python
   ```

4. Initialize the SQLite database and tables:

   ```powershell
   python init_db.py
   ```

5. Copy your existing MySQL `users` and `employee` records into SQLite:

   ```powershell
   python migrate_mysql_to_sqlite.py
   ```

   The script copies the original IDs and all listed columns. It does not delete or modify MySQL records. It refuses to import if either SQLite table already contains rows, to avoid accidental replacement. Keep a backup of your MySQL database until you verify the migrated records.

6. Start the app:

   ```powershell
   python app.py
   ```

7. Open `http://127.0.0.1:5000/`.

## If you already ran `init_db.py`

That is fine: it creates empty tables. Run the migration script next. Do not run the migration again once records have been copied unless you intentionally prepare an empty SQLite database first.

## Notes

- The app uses SQLite's `?` SQL placeholders.
- SQLite is included with Python; it does not require a separate database server.
- The original app has mail and Flask secret settings. For security, rotate any app password that has been exposed and use environment variables for secrets before publishing the project.
