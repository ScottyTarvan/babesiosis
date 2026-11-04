/*
    Semantic search setup for babesiosis-db (SQL Server 2025).

    Lets SQL Server embed a plain-text question itself, through AI_GENERATE_EMBEDDINGS and an
    external model that calls the same Azure OpenAI deployment the loader used.

    Run it through Setup-SemanticSearch.ps1, which fills the sqlcmd variables below from
    appsettings.Local.json, so the API key is never written to this file or a command line.
    Safe to re-run: a re-run replaces the stored key and the model definition (use it after
    regenerating the Azure key).

    Needs a sysadmin login: sp_configure requires ALTER SETTINGS.

    sqlcmd variables:
        BABESIOSIS_AOAI_ENDPOINT        https://<resource>.cognitiveservices.azure.com/  (trailing slash)
        BABESIOSIS_AOAI_DEPLOYMENT      embedding deployment name
        BABESIOSIS_AOAI_KEY             API key (single quotes doubled)
        BABESIOSIS_EMBEDDING_MODEL      model name stored in article.embedding_model
        BABESIOSIS_EMBEDDING_DIMENSIONS 1536
        BABESIOSIS_MASTER_KEY_PASSWORD  used only when the database has no master key yet
*/
:on error exit
SET NOCOUNT ON;
GO

-- AI_GENERATE_EMBEDDINGS goes through sp_invoke_external_rest_endpoint, which is off by default.
EXECUTE sp_configure 'external rest endpoint enabled', 1;
RECONFIGURE WITH OVERRIDE;
GO

-- The database master key encrypts the scoped credential that holds the API key.
IF NOT EXISTS (SELECT 1 FROM sys.symmetric_keys WHERE name = '##MS_DatabaseMasterKey##')
BEGIN
    CREATE MASTER KEY ENCRYPTION BY PASSWORD = N'$(BABESIOSIS_MASTER_KEY_PASSWORD)';
    PRINT 'Created the database master key.';
END
GO

-- The credential name must be the endpoint URL; SQL Server matches it to the model LOCATION.
IF EXISTS (SELECT 1 FROM sys.database_scoped_credentials WHERE name = N'$(BABESIOSIS_AOAI_ENDPOINT)')
BEGIN
    ALTER DATABASE SCOPED CREDENTIAL [$(BABESIOSIS_AOAI_ENDPOINT)]
        WITH IDENTITY = 'HTTPEndpointHeaders', SECRET = '{"api-key":"$(BABESIOSIS_AOAI_KEY)"}';
    PRINT 'Replaced the API key in the existing credential.';
END
ELSE
BEGIN
    CREATE DATABASE SCOPED CREDENTIAL [$(BABESIOSIS_AOAI_ENDPOINT)]
        WITH IDENTITY = 'HTTPEndpointHeaders', SECRET = '{"api-key":"$(BABESIOSIS_AOAI_KEY)"}';
    PRINT 'Created the credential.';
END
GO

IF EXISTS (SELECT 1 FROM sys.external_models WHERE name = N'babesiosis_embedding')
    DROP EXTERNAL MODEL babesiosis_embedding;
GO

CREATE EXTERNAL MODEL babesiosis_embedding
WITH (
    LOCATION   = '$(BABESIOSIS_AOAI_ENDPOINT)openai/deployments/$(BABESIOSIS_AOAI_DEPLOYMENT)/embeddings?api-version=2024-02-01',
    API_FORMAT = 'Azure OpenAI',
    MODEL_TYPE = EMBEDDINGS,
    MODEL      = '$(BABESIOSIS_EMBEDDING_MODEL)',
    CREDENTIAL = [$(BABESIOSIS_AOAI_ENDPOINT)],
    PARAMETERS = '{"dimensions":$(BABESIOSIS_EMBEDDING_DIMENSIONS),"sql_rest_options":{"retry_count":3}}'
);
PRINT 'Created external model babesiosis_embedding.';
GO

-- Smoke test: one live call to Azure, compared against the stored article vectors.
DECLARE @probe VECTOR($(BABESIOSIS_EMBEDDING_DIMENSIONS)) =
    AI_GENERATE_EMBEDDINGS(N'Babesia infection in dogs' USE MODEL babesiosis_embedding);

IF @probe IS NULL
    THROW 50000, 'Smoke test failed: the embedding endpoint returned no vector.', 1;

SELECT TOP (3) article_code, VECTOR_DISTANCE('cosine', embedding, @probe) AS distance, title
FROM dbo.article
WHERE embedding IS NOT NULL
ORDER BY distance;
GO
