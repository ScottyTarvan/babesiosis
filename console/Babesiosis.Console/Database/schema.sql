/*
  Babesiosis article store - schema for babesiosis-db (SQL Server 2025).

  Run this script once before the loader. It is safe to run again: tables are
  created only when missing, and the category seed is merged.

  Source: core/articles.jsonl (structured fields), the .md files in
          core/articles (narrative sections), core/data/terms (terms) and
          core/data/markdown (the papers' own text, in passages).
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

-- name is the formal category name; label is the short plain-language name the
-- web app shows (with the code beside it and the formal name on hover).
MERGE dbo.category AS t
USING (VALUES
  ('ERY', N'Erythrocyte injury, haemolysis, anaemia and immune-mediated processes', N'Red cells and anaemia',                  1),
  ('INF', N'Inflammation, innate/adaptive immunity and immunopathology',             N'Inflammation and immunity',              2),
  ('END', N'Endothelium, microcirculation, perfusion and tissue hypoxia',            N'Endothelium and perfusion',              3),
  ('COA', N'Coagulation, platelets, immunothrombosis and DIC',                       N'Coagulation and platelets',              4),
  ('REN', N'Renal injury and renal function',                                        N'Kidney',                                 5),
  ('PUL', N'Pulmonary injury and gas exchange',                                      N'Lung and gas exchange',                  6),
  ('NEU', N'Neurological and cerebral disease',                                      N'Brain and nervous system',               7),
  ('CAR', N'Cardiac injury and haemodynamics',                                       N'Heart and haemodynamics',                8),
  ('MET', N'Hepatic, metabolic, endocrine and acid-base disturbances',               N'Liver, metabolism and acid-base',        9),
  ('OXO', N'Oxidative stress, host-parasite interaction, omics and virulence',      N'Oxidative stress, omics and virulence', 10),
  ('SEV', N'Multisystem clinical phenotype, severity and outcome',                  N'Severity, phenotype and outcome',       11)
) AS s (category_code, name, label, sort_order)
ON t.category_code = s.category_code
WHEN MATCHED AND (t.name <> s.name OR t.sort_order <> s.sort_order OR ISNULL(t.label, N'') <> s.label) THEN
  UPDATE SET name = s.name, label = s.label, sort_order = s.sort_order
WHEN NOT MATCHED BY TARGET THEN
  INSERT (category_code, name, label, sort_order) VALUES (s.category_code, s.name, s.label, s.sort_order);

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

    -- The paper's own text (data/markdown/<ID>.md, loaded into dbo.article_section by SectionLoader)
    has_full_text               BIT            NULL,      -- 1 = full text (JATS XML or PDF) with usable text; 0 = abstract only or no text
    text_quality                VARCHAR(20)    NULL,      -- ok / review / abstract_only / no_text (front matter "quality")
    text_flags                  JSON           NULL,      -- front matter quality_flags, e.g. ["garbled_text"]
    text_language               VARCHAR(30)    NULL,      -- language of the paper (en, tr, ru, ...); passages are English when text_translated = 1
    text_translated             BIT            NULL,      -- 1 = passages come from the LLM translation <ID>.en.md
    text_word_count             INT            NULL,
    text_file                   NVARCHAR(200)  NULL,      -- data/markdown/CB058.en.md
    text_hash                   BINARY(32)     NULL,      -- SHA-256 of the embedded passage texts; sections reload when it changes
    text_loaded_at              DATETIME2(0)   NULL,

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

-- Databases created before the full-text columns were added to the CREATE TABLE above.
IF COL_LENGTH(N'dbo.article', N'text_hash') IS NULL
  ALTER TABLE dbo.article ADD
    has_full_text   BIT           NULL,
    text_quality    VARCHAR(20)   NULL,
    text_flags      JSON          NULL,
    text_language   VARCHAR(30)   NULL,
    text_translated BIT           NULL,
    text_word_count INT           NULL,
    text_file       NVARCHAR(200) NULL,
    text_hash       BINARY(32)    NULL,
    text_loaded_at  DATETIME2(0)  NULL;

/* Derived columns for the web app's overview. Computed and persisted, so they
   follow every reload of the article without a loader change.

   country_normalised: country is free text (183 spellings). Take the text before
   the first "(", ";", "," or "/", trimmed; map Türkiye to Turkey, Republic of
   Korea to South Korea and United States to USA; empty values and values that
   start "not ", "unspecified" or "unclear" are NULL (not stated).

   category_confidence / category_source: how the primary category was assigned,
   from the articles.jsonl record (high / low from the NLP step; NULL with source
   "agent ..." when NLP found no category and the extraction agent's label was kept). */
IF COL_LENGTH(N'dbo.article', N'country_normalised') IS NULL
  ALTER TABLE dbo.article ADD country_normalised AS
    CAST(CASE
      WHEN LTRIM(RTRIM(LEFT(ISNULL(country, N''), PATINDEX(N'%[(;,/]%', ISNULL(country, N'') + N'(') - 1))) = N''
        OR LTRIM(RTRIM(LEFT(ISNULL(country, N''), PATINDEX(N'%[(;,/]%', ISNULL(country, N'') + N'(') - 1))) LIKE N'not %'
        OR LTRIM(RTRIM(LEFT(ISNULL(country, N''), PATINDEX(N'%[(;,/]%', ISNULL(country, N'') + N'(') - 1))) LIKE N'unspecified%'
        OR LTRIM(RTRIM(LEFT(ISNULL(country, N''), PATINDEX(N'%[(;,/]%', ISNULL(country, N'') + N'(') - 1))) LIKE N'unclear%' THEN NULL
      WHEN LTRIM(RTRIM(LEFT(ISNULL(country, N''), PATINDEX(N'%[(;,/]%', ISNULL(country, N'') + N'(') - 1))) = N'Türkiye' THEN N'Turkey'
      WHEN LTRIM(RTRIM(LEFT(ISNULL(country, N''), PATINDEX(N'%[(;,/]%', ISNULL(country, N'') + N'(') - 1))) = N'Republic of Korea' THEN N'South Korea'
      WHEN LTRIM(RTRIM(LEFT(ISNULL(country, N''), PATINDEX(N'%[(;,/]%', ISNULL(country, N'') + N'(') - 1))) = N'United States' THEN N'USA'
      ELSE LTRIM(RTRIM(LEFT(ISNULL(country, N''), PATINDEX(N'%[(;,/]%', ISNULL(country, N'') + N'(') - 1)))
    END AS NVARCHAR(100)) PERSISTED;

IF COL_LENGTH(N'dbo.article', N'category_confidence') IS NULL
  ALTER TABLE dbo.article ADD
    category_confidence AS CAST(JSON_VALUE(source_json, '$.category_confidence') AS VARCHAR(10)) PERSISTED,
    category_source     AS CAST(JSON_VALUE(source_json, '$.category_source') AS VARCHAR(60)) PERSISTED;

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

/* ---------------------------------------------------------------------------
   article_section - the paper's own text in passages, from data/markdown/<ID>.md
   (or the English translation <ID>.en.md). Loaded by SectionLoader.

   A passage is one H2 section of the Markdown, or part of one when the
   section is long (chunk_index 1..chunk_count, split at paragraph breaks,
   about 500 words each). section_kind normalises the heading so the agent
   can ask for "results" or "methods" whatever the paper called them.
   Abstract-only articles have a single abstract passage. Each passage has
   its own embedding (title + heading + body) for dbo.search_passages.
--------------------------------------------------------------------------- */
IF OBJECT_ID(N'dbo.article_section', N'U') IS NULL
BEGIN
  CREATE TABLE dbo.article_section
  (
    section_id      INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_article_section PRIMARY KEY,
    article_id      INT            NOT NULL CONSTRAINT FK_article_section_article REFERENCES dbo.article (article_id) ON DELETE CASCADE,
    section_order   SMALLINT       NOT NULL,                 -- reading order within the article, from 1
    section_kind    VARCHAR(20)    NOT NULL CONSTRAINT CK_article_section_kind CHECK (section_kind IN
                      ('abstract', 'introduction', 'methods', 'results', 'results_discussion', 'discussion',
                       'conclusion', 'case', 'limitations', 'abbreviations', 'body', 'other')),
    heading         NVARCHAR(300)  NULL,                     -- "Results" or "Results > Pooled prevalence"; NULL when the text has no headings
    chunk_index     SMALLINT       NOT NULL,                 -- 1-based part number within the H2 section
    chunk_count     SMALLINT       NOT NULL,                 -- parts in the H2 section
    body            NVARCHAR(MAX)  NOT NULL,                 -- Markdown: paragraphs, lists, pipe tables
    word_count      INT            NOT NULL,

    -- Embedding (same model and dimensions as article.embedding)
    embedding       VECTOR(1536)   NULL,
    embedding_model VARCHAR(100)   NULL,
    embedded_at     DATETIME2(0)   NULL,

    CONSTRAINT UQ_article_section_order UNIQUE (article_id, section_order)
  );

  CREATE INDEX IX_article_section_kind ON dbo.article_section (article_id, section_kind, section_order);
END;

/* ---------------------------------------------------------------------------
   synthesis_section - the narrative syntheses in core/search/synthesis, split
   by heading: one document per category (<CODE>.md, sections such as
   "Question this direction asks" and "Evidence base"), CROSS.md (one section
   per numbered theme) and QUESTIONS.md (one section per "## " heading).
   The text is stored as written (Markdown). Loaded by SynthesisLoader
   (console --synthesis-only), which replaces a document's rows as a whole.
--------------------------------------------------------------------------- */
IF OBJECT_ID(N'dbo.synthesis_section', N'U') IS NULL
BEGIN
  CREATE TABLE dbo.synthesis_section
  (
    synthesis_section_id INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_synthesis_section PRIMARY KEY,
    document_code        VARCHAR(10)    NOT NULL,                  -- ERY .. SEV, CROSS, QUESTIONS
    section_order        SMALLINT       NOT NULL,                  -- reading order within the document, from 1
    section_key          VARCHAR(60)    NOT NULL,                  -- intro, question, evidence-base, theme-1, q1, summary-table, ...
    heading              NVARCHAR(400)  NOT NULL,                  -- as written, Markdown emphasis kept
    body                 NVARCHAR(MAX)  NOT NULL,                  -- Markdown, as written
    source_file          NVARCHAR(200)  NOT NULL,                  -- search/synthesis/REN.md
    file_modified_at     DATETIME2(0)   NOT NULL,                  -- UTC, the file's last write time
    loaded_at            DATETIME2(0)   NOT NULL CONSTRAINT DF_synthesis_section_loaded_at DEFAULT SYSUTCDATETIME(),

    CONSTRAINT UQ_synthesis_section_order UNIQUE (document_code, section_order),
    CONSTRAINT UQ_synthesis_section_key   UNIQUE (document_code, section_key)
  );
END;

COMMIT TRANSACTION;

/* ===========================================================================
   Experiments: per-subject measurements from the downloaded datasets, and the
   results of analyses run over them.

   Source: core/data/tidy/<dataset>.json              (deleted on 2026-11-12; the dataset tables are empty)
           experiments/<package>/out/db/<code>.json   (see experiments/run-instructions.md)
   Loaded by DatasetLoader and ExperimentLoader (console --datasets-only).

   Measurements are stored long (one row per subject x variable x time point)
   so a new dataset adds rows, not columns, and variables can later be mapped
   to a canonical code across datasets. Results the UI must sort or filter
   (associations, cluster labels) are relational; the full, method-specific
   output is kept as JSON in experiment_result.
=========================================================================== */

SET XACT_ABORT ON;
BEGIN TRANSACTION;

/* ---------------------------------------------------------------------------
   dataset - one row per downloaded dataset (datasets.jsonl dataset_id)
--------------------------------------------------------------------------- */
IF OBJECT_ID(N'dbo.dataset', N'U') IS NULL
BEGIN
  CREATE TABLE dbo.dataset
  (
    dataset_id         INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_dataset PRIMARY KEY,
    dataset_code       VARCHAR(20)    NOT NULL CONSTRAINT UQ_dataset_code UNIQUE,   -- DS05, S-CB050
    title              NVARCHAR(500)  NOT NULL,
    article_code       VARCHAR(10)    NULL,                                        -- linked article, e.g. CB126
    article_id         INT            NULL CONSTRAINT FK_dataset_article REFERENCES dbo.article (article_id),
    repository         NVARCHAR(200)  NULL,
    source_record      NVARCHAR(400)  NULL,                                        -- DOI or accession of the record
    licence            NVARCHAR(400)  NULL,
    independent_source VARCHAR(10)    NULL,                                        -- SRC-F
    species            NVARCHAR(400)  NULL,
    design             NVARCHAR(MAX)  NULL,
    source_file        NVARCHAR(300)  NULL,                                        -- path under core/
    source_sha256      CHAR(64)       NULL,                                        -- from data/manifest.jsonl
    n_subjects         INT            NOT NULL CONSTRAINT DF_dataset_n_subjects DEFAULT 0,
    notes              JSON           NULL,                                        -- ["..."] cleaning notes from the tidy script
    extracted_at       DATETIME2(0)   NULL,                                        -- when the tidy file was written
    loaded_at          DATETIME2(0)   NOT NULL CONSTRAINT DF_dataset_loaded_at DEFAULT SYSUTCDATETIME()
  );
END;

/* ---------------------------------------------------------------------------
   variable - one row per measured or recoded column of a dataset
   data_type: N numeric, O ordinal (integer score, ranked like a number),
              C categorical, D date, T free text (never tested)
--------------------------------------------------------------------------- */
IF OBJECT_ID(N'dbo.variable', N'U') IS NULL
BEGIN
  CREATE TABLE dbo.variable
  (
    variable_id     INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_variable PRIMARY KEY,
    dataset_id      INT            NOT NULL CONSTRAINT FK_variable_dataset REFERENCES dbo.dataset (dataset_id) ON DELETE CASCADE,
    variable_code   VARCHAR(60)    NOT NULL,                                       -- haematocrit, breed_group
    name            NVARCHAR(200)  NOT NULL,                                       -- display name
    source_name     NVARCHAR(200)  NULL,                                           -- header as it appears in the file
    canonical_code  VARCHAR(60)    NULL,                                           -- same measurement across datasets (filled when a second dataset is mapped)
    unit            NVARCHAR(50)   NULL,
    data_type       CHAR(1)        NOT NULL CONSTRAINT CK_variable_data_type CHECK (data_type IN ('N', 'O', 'C', 'D', 'T')),
    domain          VARCHAR(30)    NULL,                                           -- signalment, clinical, haematology, biochemistry, pathogen, time
    derived         BIT            NOT NULL CONSTRAINT DF_variable_derived DEFAULT 0,        -- a grade or class computed from another variable
    derived_from    JSON           NULL,                                           -- ["haemoglobin","rcc"]: arithmetic parents; a pair with a parent is trivial
    include_default BIT            NOT NULL CONSTRAINT DF_variable_include DEFAULT 1,        -- part of the default test set
    ref_low         FLOAT          NULL,
    ref_high        FLOAT          NULL,
    description     NVARCHAR(1000) NULL,
    levels          JSON           NULL,                                           -- categorical: {"level": count}
    sort_order      SMALLINT       NOT NULL CONSTRAINT DF_variable_sort_order DEFAULT 0,
    CONSTRAINT UQ_variable_dataset_code UNIQUE (dataset_id, variable_code)
  );
END;

/* ---------------------------------------------------------------------------
   subject - one row per animal (or sample where animals are not identified)
--------------------------------------------------------------------------- */
IF OBJECT_ID(N'dbo.subject', N'U') IS NULL
BEGIN
  CREATE TABLE dbo.subject
  (
    subject_id    INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_subject PRIMARY KEY,
    dataset_id    INT            NOT NULL CONSTRAINT FK_subject_dataset REFERENCES dbo.dataset (dataset_id) ON DELETE CASCADE,
    subject_code  VARCHAR(60)    NOT NULL,                                        -- the dataset's own identifier, e.g. BET001
    group_label   NVARCHAR(100)  NULL,                                            -- study group as the dataset defines it
    outcome_label NVARCHAR(100)  NULL,                                            -- survival or severity class where one exists
    CONSTRAINT UQ_subject_dataset_code UNIQUE (dataset_id, subject_code)
  );
END;

/* ---------------------------------------------------------------------------
   observation - long table of values. time_point is '' for single-visit data.
--------------------------------------------------------------------------- */
IF OBJECT_ID(N'dbo.observation', N'U') IS NULL
BEGIN
  CREATE TABLE dbo.observation
  (
    observation_id BIGINT IDENTITY(1,1) NOT NULL CONSTRAINT PK_observation PRIMARY KEY,
    subject_id     INT            NOT NULL CONSTRAINT FK_observation_subject  REFERENCES dbo.subject (subject_id) ON DELETE CASCADE,
    variable_id    INT            NOT NULL CONSTRAINT FK_observation_variable REFERENCES dbo.variable (variable_id),
    time_point     VARCHAR(30)    NOT NULL CONSTRAINT DF_observation_time_point DEFAULT '',
    value_num      FLOAT          NULL,
    value_text     NVARCHAR(400)  NULL,
    value_date     DATE           NULL,
    CONSTRAINT UQ_observation UNIQUE (subject_id, variable_id, time_point)
  );

  CREATE INDEX IX_observation_variable ON dbo.observation (variable_id) INCLUDE (subject_id, value_num, value_text);
END;

/* ---------------------------------------------------------------------------
   experiment - one row per analysis run
--------------------------------------------------------------------------- */
IF OBJECT_ID(N'dbo.experiment', N'U') IS NULL
BEGIN
  CREATE TABLE dbo.experiment
  (
    experiment_id   INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_experiment PRIMARY KEY,
    experiment_code VARCHAR(60)    NOT NULL CONSTRAINT UQ_experiment_code UNIQUE,  -- EXP01-DS05-pairwise
    name            NVARCHAR(200)  NOT NULL,
    description     NVARCHAR(MAX)  NULL,
    method          VARCHAR(50)    NOT NULL,                                       -- pairwise_association, clustering, ...
    dataset_id      INT            NULL CONSTRAINT FK_experiment_dataset REFERENCES dbo.dataset (dataset_id),
    parameters      JSON           NULL,                                           -- the run's settings, verbatim
    script          NVARCHAR(200)  NULL,                                           -- scripts/experiment_pairwise.py
    script_version  VARCHAR(64)    NULL,                                           -- SHA-256 prefix of the script file
    run_at          DATETIME2(0)   NULL,
    n_subjects      INT            NULL,
    n_variables     INT            NULL,
    n_tests         INT            NULL,
    summary         NVARCHAR(MAX)  NULL,                                           -- short plain-text summary written by the script
    loaded_at       DATETIME2(0)   NOT NULL CONSTRAINT DF_experiment_loaded_at DEFAULT SYSUTCDATETIME()
  );
END;

/* ---------------------------------------------------------------------------
   association - one row per tested variable pair. The UI sorts and filters here.
--------------------------------------------------------------------------- */
IF OBJECT_ID(N'dbo.association', N'U') IS NULL
BEGIN
  CREATE TABLE dbo.association
  (
    association_id INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_association PRIMARY KEY,
    experiment_id  INT           NOT NULL CONSTRAINT FK_association_experiment REFERENCES dbo.experiment (experiment_id) ON DELETE CASCADE,
    variable_a_id  INT           NOT NULL CONSTRAINT FK_association_variable_a REFERENCES dbo.variable (variable_id),
    variable_b_id  INT           NOT NULL CONSTRAINT FK_association_variable_b REFERENCES dbo.variable (variable_id),
    test           VARCHAR(30)   NOT NULL,                                         -- spearman, kruskal_wallis, chi_square
    estimate       FLOAT         NULL,                                             -- rho, eta_squared, cramers_v
    estimate_label VARCHAR(30)   NULL,
    n              INT           NOT NULL,
    p_value        FLOAT         NULL,                                             -- permutation p
    p_adjusted     FLOAT         NULL,                                             -- Benjamini-Hochberg across the run
    significant    BIT           NOT NULL CONSTRAINT DF_association_significant DEFAULT 0,
    trivial        BIT           NOT NULL CONSTRAINT DF_association_trivial DEFAULT 0,  -- one variable is arithmetically derived from the other
    direction      NVARCHAR(200) NULL,                                             -- "positive", or the group with the higher median
    detail         JSON          NULL                                              -- group medians, contingency table, statistic
  );

  CREATE INDEX IX_association_experiment ON dbo.association (experiment_id, p_adjusted) INCLUDE (variable_a_id, variable_b_id, estimate, significant, trivial);
  CREATE INDEX IX_association_variable_a ON dbo.association (variable_a_id);
  CREATE INDEX IX_association_variable_b ON dbo.association (variable_b_id);
END;

/* ---------------------------------------------------------------------------
   cluster_assignment - subject-level groupings from clustering experiments
--------------------------------------------------------------------------- */
IF OBJECT_ID(N'dbo.cluster_assignment', N'U') IS NULL
BEGIN
  CREATE TABLE dbo.cluster_assignment
  (
    experiment_id INT          NOT NULL CONSTRAINT FK_cluster_experiment REFERENCES dbo.experiment (experiment_id) ON DELETE CASCADE,
    subject_id    INT          NOT NULL CONSTRAINT FK_cluster_subject    REFERENCES dbo.subject (subject_id),
    cluster_label VARCHAR(30)  NOT NULL,
    score         FLOAT        NULL,                                               -- silhouette or membership strength
    CONSTRAINT PK_cluster_assignment PRIMARY KEY (experiment_id, subject_id)
  );
END;

/* ---------------------------------------------------------------------------
   experiment_result - the full, method-specific outputs as JSON
   (correlation matrix, variable clusters, top findings, figure data)
--------------------------------------------------------------------------- */
IF OBJECT_ID(N'dbo.experiment_result', N'U') IS NULL
BEGIN
  CREATE TABLE dbo.experiment_result
  (
    result_id     INT IDENTITY(1,1) NOT NULL CONSTRAINT PK_experiment_result PRIMARY KEY,
    experiment_id INT           NOT NULL CONSTRAINT FK_result_experiment REFERENCES dbo.experiment (experiment_id) ON DELETE CASCADE,
    result_kind   VARCHAR(40)   NOT NULL,                                          -- spearman_matrix, variable_clusters, top_associations
    title         NVARCHAR(200) NULL,
    payload       JSON          NOT NULL,
    sort_order    SMALLINT      NOT NULL CONSTRAINT DF_result_sort_order DEFAULT 0
  );

  CREATE INDEX IX_experiment_result_experiment ON dbo.experiment_result (experiment_id, sort_order);
END;

COMMIT TRANSACTION;
