/*
  Babesiosis article store - schema for babesiosis-db (SQL Server 2025).

  Run this script once before the loader. It is safe to run again: tables are
  created only when missing, and the category seed is merged.

  Source: core/articles.jsonl (structured fields), the .md files in
          core/articles (narrative sections), and core/data/terms (terms).
*/

SET XACT_ABORT ON;
BEGIN TRANSACTION;

/* ---------------------------------------------------------------------------
   category - the 11 pathophysiology categories defined in index.md
--------------------------------------------------------------------------- */
IF OBJECT_ID(N'dbo.category', N'U') IS NULL
BEGIN
  CREATE TABLE dbo.category
  (
    category_id   INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_category PRIMARY KEY,
    category_code CHAR(3)       NOT NULL CONSTRAINT UQ_category_code UNIQUE,
    name          NVARCHAR(100) NOT NULL CONSTRAINT UQ_category_name UNIQUE,
    label         NVARCHAR(100) NULL,      -- short display label for charts, e.g. Haemolysis
    sort_order    TINYINT       NOT NULL
  );
END;

-- Databases created before label was added to the CREATE TABLE above.
IF COL_LENGTH(N'dbo.category', N'label') IS NULL
  ALTER TABLE dbo.category ADD label NVARCHAR(100) NULL;

MERGE dbo.category AS t
USING (VALUES
  ('ERY', N'Erythrocyte injury, haemolysis, anaemia and immune-mediated processes', 1),
  ('INF', N'Inflammation, innate/adaptive immunity and immunopathology',             2),
  ('END', N'Endothelium, microcirculation, perfusion and tissue hypoxia',            3),
  ('COA', N'Coagulation, platelets, immunothrombosis and DIC',                       4),
  ('REN', N'Renal injury and renal function',                                        5),
  ('PUL', N'Pulmonary injury and gas exchange',                                      6),
  ('NEU', N'Neurological and cerebral disease',                                      7),
  ('CAR', N'Cardiac injury and haemodynamics',                                       8),
  ('MET', N'Hepatic, metabolic, endocrine and acid-base disturbances',               9),
  ('OXO', N'Oxidative stress, host-parasite interaction, omics and virulence',      10),
  ('SEV', N'Multisystem clinical phenotype, severity and outcome',                  11)
) AS s (category_code, name, sort_order)
ON t.category_code = s.category_code
WHEN MATCHED AND (t.name <> s.name OR t.sort_order <> s.sort_order) THEN
  UPDATE SET name = s.name, sort_order = s.sort_order
WHEN NOT MATCHED BY TARGET THEN
  INSERT (category_code, name, sort_order) VALUES (s.category_code, s.name, s.sort_order);

/* ---------------------------------------------------------------------------
   article - one row per article file
--------------------------------------------------------------------------- */
IF OBJECT_ID(N'dbo.article', N'U') IS NULL
BEGIN
  CREATE TABLE dbo.article
  (
    article_id                  INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_article PRIMARY KEY,

    -- Keys
    article_code                VARCHAR(10)    NOT NULL CONSTRAINT UQ_article_code UNIQUE,  -- e.g. CB001
    source_key                  VARCHAR(100)   NOT NULL CONSTRAINT UQ_article_source_key UNIQUE,  -- e.g. PMID:28074976; REF:<slug> keys reach 64 characters
    file_name                   NVARCHAR(200)  NOT NULL,

    -- Bibliographic
    title                       NVARCHAR(500)  NOT NULL,
    authors                     NVARCHAR(1000) NULL,      -- display string, "Abdoli A, Olfatifar M, ..."
    journal                     NVARCHAR(300)  NULL,
    volume_issue_pages          NVARCHAR(150)  NULL,
    doi                         VARCHAR(100)   NULL,
    pmid                        VARCHAR(20)    NULL,
    pmcid                       VARCHAR(20)    NULL,
    language                    NVARCHAR(100)  NULL,      -- as recorded; values are not normalised
    corrections                 NVARCHAR(400)  NULL,

    -- Dates. first_pub_date is YYYY, YYYY-MM or YYYY-MM-DD in the source, so it
    -- is stored as the first day of the period plus its precision.
    pub_date                    DATE           NULL,
    pub_date_precision          CHAR(1)        NULL CONSTRAINT CK_article_pub_date_precision CHECK (pub_date_precision IN ('D', 'M', 'Y')),
    pub_year                    SMALLINT       NULL,
    first_pub_date_text         VARCHAR(10)    NULL,
    online_date_text            NVARCHAR(200)  NULL,      -- free text in the source
    issue_date_text             NVARCHAR(200)  NULL,      -- free text in the source
    date_note                   NVARCHAR(800)  NULL,

    -- Study
    scope_label                 NVARCHAR(50)   NULL,
    include_type                VARCHAR(20)    NULL,
    study_type                  NVARCHAR(300)  NULL,      -- older-format records only
    older_foundational          BIT            NULL,
    design                      NVARCHAR(1000) NULL,
    evidence_type               NVARCHAR(150)  NULL,
    host                        NVARCHAR(400)  NULL,
    country                     NVARCHAR(300)  NULL,
    species_summary             NVARCHAR(200)  NULL,      -- species_short
    species                     JSON           NULL,      -- [{name, status, method}]
    sample_size                 NVARCHAR(400)  NULL,
    n_infected_dogs             INT            NULL,
    n_controls                  INT            NULL,
    cohort_id                   VARCHAR(10)    NULL,

    -- Category. NULL when the source has no category code (43 articles) or
    -- holds free text instead of a code.
    primary_category_id         INT            NULL CONSTRAINT FK_article_category REFERENCES dbo.category (category_id),

    -- Narrative, from the article .md file
    one_sentence_finding        NVARCHAR(1000) NULL,
    abstract_summary            NVARCHAR(MAX)  NULL,
    authors_conclusion          NVARCHAR(MAX)  NULL,
    reviewer_interpretation     NVARCHAR(MAX)  NULL,
    key_limitations             NVARCHAR(MAX)  NULL,
    relevance                   NVARCHAR(MAX)  NULL,      -- human comparator and background articles
    evidence_basis              NVARCHAR(MAX)  NULL,      -- whole section, markdown
    markdown                    NVARCHAR(MAX)  NOT NULL,  -- whole file, verbatim

    -- Sources and data availability
    abstract_available          BIT            NULL,
    abstract_source             NVARCHAR(400)  NULL,
    fulltext_checked            BIT            NULL,
    fulltext_url                NVARCHAR(400)  NULL,
    supplement_checked          BIT            NULL,
    repository_checked          BIT            NULL,
    data_availability_statement NVARCHAR(600)  NULL,
    dataset_status_code         TINYINT        NULL,
    dataset_status              NVARCHAR(100)  NULL,
    dataset_ids                 JSON           NULL,      -- ["S-CB005"]
    source_links                JSON           NULL,
    access_date                 DATE           NULL,
    verification_notes          NVARCHAR(2000) NULL,
    text_source                 VARCHAR(20)    NULL,      -- abstract / jats_xml / pdf, from data/terms/<ID>.json (TermLoader)

    -- Embedding (Azure OpenAI text-embedding-3-small)
    embedding                   VECTOR(1536)   NULL,
    embedding_model             VARCHAR(100)   NULL,
    embedded_at                 DATETIME2(0)   NULL,

    -- Audit
    source_json                 JSON           NOT NULL,  -- the articles.jsonl record, verbatim
    content_hash                BINARY(32)     NOT NULL,  -- SHA-256 of the embedded text; re-embed when it changes
    loaded_at                   DATETIME2(0)   NOT NULL CONSTRAINT DF_article_loaded_at DEFAULT SYSUTCDATETIME()
  );

  CREATE INDEX IX_article_primary_category ON dbo.article (primary_category_id);
  CREATE INDEX IX_article_pub_year         ON dbo.article (pub_year);
END;

-- Databases created before text_source was added to the CREATE TABLE above.
IF COL_LENGTH(N'dbo.article', N'text_source') IS NULL
  ALTER TABLE dbo.article ADD text_source VARCHAR(20) NULL;

/* ---------------------------------------------------------------------------
   article_category - secondary tags and comparator categories
   (the primary category stays on article.primary_category_id)
--------------------------------------------------------------------------- */
IF OBJECT_ID(N'dbo.article_category', N'U') IS NULL
BEGIN
  CREATE TABLE dbo.article_category
  (
    article_id  INT         NOT NULL CONSTRAINT FK_article_category_article  REFERENCES dbo.article (article_id) ON DELETE CASCADE,
    category_id INT         NOT NULL CONSTRAINT FK_article_category_category REFERENCES dbo.category (category_id),
    tag_type    VARCHAR(10) NOT NULL CONSTRAINT CK_article_category_tag_type CHECK (tag_type IN ('secondary', 'comparator')),
    CONSTRAINT PK_article_category PRIMARY KEY (article_id, category_id, tag_type)
  );

  CREATE INDEX IX_article_category_category ON dbo.article_category (category_id, tag_type);
END;

/* ---------------------------------------------------------------------------
   term - UMLS disorder concepts from data/terms/<ID>.json, with the curated
   display map data/terms/term_display.csv (hidden, display_name, note).
   Loaded by TermLoader.
--------------------------------------------------------------------------- */
IF OBJECT_ID(N'dbo.term', N'U') IS NULL
BEGIN
  CREATE TABLE dbo.term
  (
    term_id       INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_term PRIMARY KEY,
    cui           VARCHAR(10)   NOT NULL CONSTRAINT UQ_term_cui UNIQUE,   -- UMLS CUI, e.g. C0002871
    concept       NVARCHAR(200) NOT NULL,                                 -- UMLS preferred name
    semantic_type NVARCHAR(100) NULL,                                     -- semantic type names, '; '-separated
    display_name  NVARCHAR(200) NULL,                                     -- merges CUIs under one label; NULL = concept
    hidden        BIT           NOT NULL CONSTRAINT DF_term_hidden DEFAULT 0,
    note          NVARCHAR(400) NULL
  );
END;

/* ---------------------------------------------------------------------------
   article_term - one row per article x term with at least one affirmed mention.
   studied = affirmed mention in title, results, case or conclusion (or in the
   abstract for abstract-only articles).
--------------------------------------------------------------------------- */
IF OBJECT_ID(N'dbo.article_term', N'U') IS NULL
BEGIN
  CREATE TABLE dbo.article_term
  (
    article_id        INT          NOT NULL CONSTRAINT FK_article_term_article REFERENCES dbo.article (article_id) ON DELETE CASCADE,
    term_id           INT          NOT NULL CONSTRAINT FK_article_term_term    REFERENCES dbo.term (term_id),
    mentions          INT          NOT NULL,
    mentions_affirmed INT          NOT NULL,
    mentions_negated  INT          NOT NULL,
    studied           BIT          NOT NULL,
    sections          JSON         NULL,      -- {"abstract": 4, "title": 1}
    forms             JSON         NULL,      -- {"anaemia": 3, "anemia": 1}
    best_score        DECIMAL(4,3) NULL,
    CONSTRAINT PK_article_term PRIMARY KEY (article_id, term_id)
  );

  CREATE INDEX IX_article_term_term ON dbo.article_term (term_id) INCLUDE (studied);
END;

COMMIT TRANSACTION;
