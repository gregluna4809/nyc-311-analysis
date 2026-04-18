SELECT
    DATE_TRUNC('month', created_date)::date AS month,
    borough,
    COUNT(*) AS complaint_count
FROM service_requests
WHERE created_date IS NOT NULL
  AND borough IS NOT NULL
  AND borough <> ''
GROUP BY 1, 2
ORDER BY 1, 3 DESC;