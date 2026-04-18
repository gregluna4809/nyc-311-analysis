WITH ranked_complaints AS (
    SELECT
        borough,
        complaint_type,
        COUNT(*) AS complaint_count,
        ROW_NUMBER() OVER (
            PARTITION BY borough
            ORDER BY COUNT(*) DESC
        ) AS rn
    FROM service_requests
    WHERE borough IS NOT NULL
      AND borough <> ''
      AND borough <> 'Unspecified'
      AND complaint_type IS NOT NULL
      AND complaint_type <> ''
    GROUP BY borough, complaint_type
)
SELECT
    borough,
    complaint_type,
    complaint_count
FROM ranked_complaints
WHERE rn <= 10
ORDER BY borough, complaint_count DESC;