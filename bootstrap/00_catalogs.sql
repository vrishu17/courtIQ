-- One-time bootstrap, run as workspace admin in the SQL editor.
-- Catalogs use the workspace's default storage (no location needed on serverless).
CREATE CATALOG IF NOT EXISTS courtiq_dev  COMMENT 'CourtIQ development environment';
CREATE CATALOG IF NOT EXISTS courtiq_prod COMMENT 'CourtIQ production environment';

SHOW CATALOGS LIKE 'courtiq*';
