from django.db import migrations, models


def create_table_engine_aware(apps, schema_editor):
    vendor = schema_editor.connection.vendor  # 'sqlite', 'mysql', 'postgresql', etc.
    with schema_editor.connection.cursor() as cursor:
        if vendor == "mysql":
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `zendesk_agents` (
                  `id` int NOT NULL AUTO_INCREMENT,
                  `email` text COLLATE utf8mb3_unicode_ci NOT NULL,
                  `password` text COLLATE utf8mb3_unicode_ci NOT NULL,
                  `employee_id` text COLLATE utf8mb3_unicode_ci DEFAULT NULL,
                  `first_name` text COLLATE utf8mb3_unicode_ci NOT NULL,
                  `last_name` text COLLATE utf8mb3_unicode_ci NOT NULL,
                  `username` text COLLATE utf8mb3_unicode_ci NOT NULL,
                  `session_id` text COLLATE utf8mb3_unicode_ci DEFAULT NULL,
                  `date_created` datetime DEFAULT NULL,
                  `status` text COLLATE utf8mb3_unicode_ci DEFAULT NULL,
                  `salt` text COLLATE utf8mb3_unicode_ci DEFAULT NULL,
                  `country` text COLLATE utf8mb3_unicode_ci DEFAULT NULL,
                  PRIMARY KEY (`id`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_unicode_ci;
            """)
        elif vendor == "sqlite":
            # SQLite syntax: INTEGER PRIMARY KEY AUTOINCREMENT; no collations/engines
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS "zendesk_agents" (
                  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                  "email" TEXT NOT NULL,
                  "password" TEXT NOT NULL,
                  "employee_id" TEXT NULL,
                  "first_name" TEXT NOT NULL,
                  "last_name" TEXT NOT NULL,
                  "username" TEXT NOT NULL,
                  "session_id" TEXT NULL,
                  "date_created" DATETIME NULL,
                  "status" TEXT NULL,
                  "salt" TEXT NULL,
                  "country" TEXT NULL
                );
            """)
        else:
            # Generic fallback using Django schema API (portable)
            # This won't set engine/collation specifics but works on most vendors.
            # If the table exists already, this will no-op due to IF NOT EXISTS equivalent
            # not being available via SchemaEditor; so we try a safe CREATE and ignore errors.
            try:
                cursor.execute("""
                    CREATE TABLE zendesk_agents (
                      id SERIAL PRIMARY KEY,
                      email TEXT NOT NULL,
                      password TEXT NOT NULL,
                      employee_id TEXT NULL,
                      first_name TEXT NOT NULL,
                      last_name TEXT NOT NULL,
                      username TEXT NOT NULL,
                      session_id TEXT NULL,
                      date_created TIMESTAMP NULL,
                      status TEXT NULL,
                      salt TEXT NULL,
                      country TEXT NULL
                    );
                """)
            except Exception:
                # Table probably already exists; ignore.
                pass


def drop_table_engine_aware(apps, schema_editor):
    vendor = schema_editor.connection.vendor
    with schema_editor.connection.cursor() as cursor:
        if vendor in ("sqlite", "mysql", "postgresql"):
            cursor.execute('DROP TABLE IF EXISTS "zendesk_agents";')
        else:
            try:
                cursor.execute('DROP TABLE IF EXISTS "zendesk_agents";')
            except Exception:
                pass


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        # 1) Create the physical table in a vendor-aware way.
        migrations.RunPython(
            code=create_table_engine_aware,
            reverse_code=drop_table_engine_aware,
        ),
        # 2) Register the model in Django's state so future migrations understand it exists.
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.CreateModel(
                    name="ZendeskAgent",
                    fields=[
                        ("id", models.AutoField(primary_key=True, serialize=False)),
                        ("email", models.TextField()),
                        ("password", models.TextField()),
                        ("employee_id", models.TextField(blank=True, null=True)),
                        ("first_name", models.TextField()),
                        ("last_name", models.TextField()),
                        ("username", models.TextField()),
                        ("session_id", models.TextField(blank=True, null=True)),
                        ("date_created", models.DateTimeField(blank=True, null=True)),
                        ("status", models.TextField(blank=True, null=True)),
                        ("salt", models.TextField(blank=True, null=True)),
                        ("country", models.TextField(blank=True, null=True)),
                    ],
                    options={"db_table": "zendesk_agents"},
                )
            ],
        ),
    ]
