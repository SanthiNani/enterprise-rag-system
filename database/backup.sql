-- Backup command:
-- pg_dump -U rag_user -h localhost rag_db > database/backup.sql

-- Restore command:
-- psql -U rag_user -h localhost rag_db < database/backup.sql

-- Backup with compression:
-- pg_dump -U rag_user -h localhost -Fc rag_db > database/backup.dump

-- Restore from compressed:
-- pg_restore -U rag_user -h localhost -d rag_db database/backup.dump