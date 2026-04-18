WITH borough_totals AS (
    SELECT borough, COUNT(*) AS borough_total
    FROM service_requests
    WHERE borough NOT IN ('', 'Unspecified')
    GROUP BY borough
),
city_totals AS (
    SELECT COUNT(*) AS city_total
    FROM service_requests
    WHERE borough NOT IN ('', 'Unspecified')
),
complaint_counts AS (
    SELECT borough, complaint_type, COUNT(*) AS cnt
    FROM service_requests
    WHERE borough NOT IN ('', 'Unspecified')
    GROUP BY borough, complaint_type
),
city_complaints AS (
    SELECT complaint_type, COUNT(*) AS city_cnt
    FROM service_requests
    WHERE borough NOT IN ('', 'Unspecified')
    GROUP BY complaint_type
)
SELECT
    c.borough,
    c.complaint_type,
    ROUND(c.cnt::numeric / b.borough_total * 100, 2) AS borough_pct,
    ROUND(cc.city_cnt::numeric / ct.city_total * 100, 2) AS city_pct,
    ROUND(
        (c.cnt::numeric / b.borough_total) /
        (cc.city_cnt::numeric / ct.city_total),
        2
    ) AS overrepresentation_ratio
FROM complaint_counts c
JOIN borough_totals b ON c.borough = b.borough
JOIN city_complaints cc ON c.complaint_type = cc.complaint_type
JOIN city_totals ct ON true
WHERE c.cnt > 500
ORDER BY overrepresentation_ratio DESC
LIMIT 25;