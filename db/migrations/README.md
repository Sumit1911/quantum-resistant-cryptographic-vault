# Database Migrations

This directory stores schema migration scripts.

Current project state:

- Baseline schema is defined in `db/schema.sql`.
- Initial migration is provided in `db/migrations/0001_initial.sql`.

When schema changes are introduced, add a new incremental migration file:

- `0002_<description>.sql`
- `0003_<description>.sql`
- etc.
