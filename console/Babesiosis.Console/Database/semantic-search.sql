/*
    dbo.search_articles: answers a plain-text question with the closest articles by meaning.

    The question is embedded inside SQL Server by the babesiosis_embedding external model
    (see semantic-search-setup.sql) and compared with article.embedding by cosine distance.
    Only rows embedded with the same model are compared, so a model change can't silently
    mix vector spaces. Distance runs from 0 (same meaning) to 2; under about 0.6 is usually
    on-topic for text-embedding-3-small.

    Examples:
        EXEC dbo.search_articles @question = N'Which studies measured cardiac troponin?';
        EXEC dbo.search_articles @question = N'acute kidney injury markers', @top = 5, @from_year = 2015;
        EXEC dbo.search_articles @question = N'treatment with imidocarb', @category_code = 'INF';

    @category_code matches the primary category or a secondary/comparator tag.
*/
CREATE OR ALTER PROCEDURE dbo.search_articles
    @question      NVARCHAR(4000),
    @top           INT      = 10,
    @category_code CHAR(3)  = NULL,
    @from_year     SMALLINT = NULL,
    @to_year       SMALLINT = NULL,
    @max_distance  FLOAT    = NULL
AS
BEGIN
    SET NOCOUNT ON;

    IF NULLIF(TRIM(@question), N'') IS NULL
        THROW 50001, 'search_articles: @question is required.', 1;
    IF @top IS NULL OR @top NOT BETWEEN 1 AND 100
        THROW 50002, 'search_articles: @top must be between 1 and 100.', 1;

    DECLARE @category_id INT;
    IF @category_code IS NOT NULL
    BEGIN
        SELECT @category_id = category_id FROM dbo.category WHERE category_code = @category_code;
        IF @category_id IS NULL
            THROW 50003, 'search_articles: unknown @category_code (see dbo.category).', 1;
    END

    DECLARE @model NVARCHAR(256) =
        (SELECT model FROM sys.external_models WHERE name = N'babesiosis_embedding');
    IF @model IS NULL
        THROW 50004, 'search_articles: external model babesiosis_embedding is missing; run semantic-search-setup.sql.', 1;

    DECLARE @query_vector VECTOR(1536) =
        AI_GENERATE_EMBEDDINGS(@question USE MODEL babesiosis_embedding);
    IF @query_vector IS NULL
        THROW 50005, 'search_articles: the embedding endpoint returned no vector.', 1;

    SELECT TOP (@top)
        ROW_NUMBER() OVER (ORDER BY d.distance) AS rank,
        a.article_code,
        a.title,
        a.pub_year,
        a.journal,
        c.category_code AS primary_category,
        CAST(d.distance AS DECIMAL(5, 4)) AS distance,
        a.one_sentence_finding,
        a.doi
    FROM dbo.article AS a
    CROSS APPLY (SELECT VECTOR_DISTANCE('cosine', a.embedding, @query_vector) AS distance) AS d
    LEFT JOIN dbo.category AS c ON c.category_id = a.primary_category_id
    WHERE a.embedding IS NOT NULL
      AND a.embedding_model = @model
      AND (@from_year IS NULL OR a.pub_year >= @from_year)
      AND (@to_year IS NULL OR a.pub_year <= @to_year)
      AND (@max_distance IS NULL OR d.distance <= @max_distance)
      AND (@category_id IS NULL
           OR a.primary_category_id = @category_id
           OR EXISTS (SELECT 1 FROM dbo.article_category AS ac
                      WHERE ac.article_id = a.article_id AND ac.category_id = @category_id))
    ORDER BY d.distance
    OPTION (RECOMPILE);
END
GO
