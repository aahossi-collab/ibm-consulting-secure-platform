# ibm-consulting-secure-platform

## Database setup

This project uses SQLite via `Flask-SQLAlchemy` and migration support through `Flask-Migrate`.

The default SQLite database path is `instance/secure_platform.db`.

### Install dependencies

```bash
python -m pip install -r requirements.txt
```

### Create the instance directory

```bash
mkdir -p instance
```

### Initialize migrations

```bash
python manage.py db init
```

### Create a migration

```bash
python manage.py db migrate -m "Initial database schema"
```

### Apply migrations

```bash
python manage.py db upgrade
```

### Run the application

```bash
python run.py
```

### Alternative Flask CLI usage

If you prefer the Flask CLI, set the application environment and use the same migration commands:

```bash
export FLASK_APP=run.py
export FLASK_ENV=development
flask db init
flask db migrate -m "Initial database schema"
flask db upgrade
```

### Notes

- `FlASK_ENV` controls which config class is loaded.
- `instance/` is used for SQLite storage.
- `manage.py` exposes `db` commands through Flask-Script.
