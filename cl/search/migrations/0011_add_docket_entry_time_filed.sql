BEGIN;
--
-- Add field time_filed to docketentry
--
ALTER TABLE "search_docketentry" ADD COLUMN "time_filed" time NULL;
--
-- Alter field date_filed on docketentry
--
COMMIT;
