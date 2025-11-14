-- Migration ICP - À exécuter sur votre base Render
-- Copier-coller ce fichier complet dans le Shell Render ou psql

-- Vérifier combien de lignes avant migration
SELECT COUNT(*) AS total_rows_before FROM links;

-- Ajouter la colonne ICP (ignore si elle existe déjà)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'links' AND column_name = 'icp'
    ) THEN
        ALTER TABLE links ADD COLUMN icp VARCHAR(255);
        RAISE NOTICE 'Colonne ICP ajoutée avec succès';
    ELSE
        RAISE NOTICE 'Colonne ICP existe déjà - aucune action';
    END IF;
END $$;

-- Vérifier combien de lignes après migration
SELECT COUNT(*) AS total_rows_after FROM links;

-- Vérifier que la colonne existe
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'links' AND column_name = 'icp';

-- Afficher un résumé
SELECT
    'Migration terminée ✅' AS status,
    COUNT(*) AS total_links,
    COUNT(icp) AS links_with_icp,
    COUNT(*) - COUNT(icp) AS links_without_icp
FROM links;
