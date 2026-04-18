SELECT
    agency,
    ROUND(
        PERCENTILE_CONT(0.5) WITHIN GROUP (
            ORDER BY (EXTRACT(EPOCH FROM (closed_date - created_date)) / 3600) / 24
        )::numeric,
        2
    ) AS median_response_days
FROM service_requests
WHERE created_date IS NOT NULL
  AND closed_date IS NOT NULL
  AND closed_date >= created_date
  AND (closed_date - created_date) < INTERVAL '30 days'
GROUP BY agency
ORDER BY median_response_days DESC;