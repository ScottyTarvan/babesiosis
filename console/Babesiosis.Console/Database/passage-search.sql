/*
    dbo.search_passages: answers a plain-text question with the closest passages of the papers'
    own text (dbo.article_section), optionally within a shortlist of articles.

    This is the second step of "narrow, then read": dbo.search_articles finds candidate articles
    from their review record; search_passages then finds the paragraphs in those articles that
    answer the question, so the caller never has to read whole papers. The question is embedded
    inside SQL Server by the babesiosis_embedding external model (see semantic-search-setup.sql)
    and compared with article_section.embedding by cosine distance; only passages embedded with
    the same model are compared. Distance runs from 0 (same meaning) to 2.

    Examples:
        EXEC dbo.search_passages @question = N'How was acute kidney injury defined?';
        EXEC dbo.search_passages @question = N'urinary GGT and creatinine ratio',
             @article_codes = N'["CB004","CB010"]', @section_kinds = N'["methods","results"]';
        EXEC dbo.search_passages @question = N'mortality rate', @category_code = 'SEV', @max_per_article = 1;

    @article_codes and @section_kinds are JSON arrays of strings. Section kinds: abstract,
    introduction, methods, results, results_discussion, discussion, conclusion, case,
    limitations, abbreviations, body (text without headings), other. @max_per_article caps the
    passages returned from any one article (NULL = no cap), so a broad question spreads over
    several papers. @category_code matches the primary category or a secondary/comparator tag.
*/
CREATE OR ALTER PROCEDURE dbo.search_passages
    @question        NVARCHAR(4000),
    @top             INT           = 10,
    @article_codes   NVARCHAR(MAX) = NULL,
    @section_kinds   NVARCHAR(400) = NULL,
    @max_per_article INT           = 3,
    @category_code   CHAR(3)       = NULL,
    @from_year       SMALLINT      = NULL,
    @to_year         SMALLINT      = NULL,
    @max_distance    FLOAT         = NULL
AS
BEGIN
    SET NOCOUNT ON;

    IF NULLIF(TRIM(@question), N'') IS NULL
        THROW 50011, 'search_passages: @question is required.', 1;
    IF @top IS NULL OR @top NOT BETWEEN 1 AND 100
        THROW 50012, 'search_passages: @top must be between 1 and 100.', 1;
    IF @article_codes IS NOT NULL AND ISJSON(@article_codes) = 0
        THROW 50013, 'search_passages: @article_codes must be a JSON array of article codes.', 1;
    IF @section_kinds IS NOT NULL AND ISJSON(@section_kinds) = 0
        THROW 50014, 'search_passages: @section_kinds must be a JSON array of section kinds.', 1;
    IF @max_per_article IS NOT NULL AND @max_per_article < 1
        THROW 50015, 'search_passages: @max_per_article must be at least 1, or NULL.', 1;

    DECLARE @category_id INT;
    IF @category_code IS NOT NULL
    BEGIN
        SELECT @category_id = category_id FROM dbo.category WHERE category_code = @category_code;
        IF @category_id IS NULL
            THROW 50016, 'search_passages: unknown @category_code (see dbo.category).', 1;
    END

    DECLARE @model NVARCHAR(256) =
        (SELECT model FROM sys.external_models WHERE name = N'babesiosis_embedding');
    IF @model IS NULL
        THROW 50017, 'search_passages: external model babesiosis_embedding is missing; run semantic-search-setup.sql.', 1;

    DECLARE @query_vector VECTOR(1536) =
        AI_GENERATE_EMBEDDINGS(@question USE MODEL babesiosis_embedding);
    IF @query_vector IS NULL
        THROW 50018, 'search_passages: the embedding endpoint returned no vector.', 1;

    WITH ranked AS
    (
        SELECT s.section_id,
               d.distance,
               ROW_NUMBER() OVER (PARTITION BY s.article_id ORDER BY d.distance) AS article_rank
        FROM dbo.article_section AS s
        JOIN dbo.article AS a ON a.article_id = s.article_id
        CROSS APPLY (SELECT VECTOR_DISTANCE('cosine', s.embedding, @query_vector) AS distance) AS d
        WHERE s.embedding IS NOT NULL
          AND s.embedding_model = @model
          AND (@article_codes IS NULL OR a.article_code IN (SELECT UPPER(value) FROM OPENJSON(@article_codes)))
          AND (@section_kinds IS NULL OR s.section_kind IN (SELECT LOWER(value) FROM OPENJSON(@section_kinds)))
          AND (@from_year IS NULL OR a.pub_year >= @from_year)
          AND (@to_year IS NULL OR a.pub_year <= @to_year)
          AND (@max_distance IS NULL OR d.distance <= @max_distance)
          AND (@category_id IS NULL
               OR a.primary_category_id = @category_id
               OR EXISTS (SELECT 1 FROM dbo.article_category AS ac
                          WHERE ac.article_id = a.article_id AND ac.category_id = @category_id))
    )
    SELECT TOP (@top)
        ROW_NUMBER() OVER (ORDER BY r.distance) AS rank,
        a.article_code,
        a.title,
        a.pub_year,
        c.category_code AS primary_category,
        a.has_full_text,
        s.section_kind,
        s.heading,
        s.chunk_index,
        s.chunk_count,
        CAST(r.distance AS DECIMAL(5, 4)) AS distance,
        s.word_count,
        s.body
    FROM ranked AS r
    JOIN dbo.article_section AS s ON s.section_id = r.section_id
    JOIN dbo.article AS a ON a.article_id = s.article_id
    LEFT JOIN dbo.category AS c ON c.category_id = a.primary_category_id
    WHERE @max_per_article IS NULL OR r.article_rank <= @max_per_article
    ORDER BY r.distance
    OPTION (RECOMPILE);
END
GO
