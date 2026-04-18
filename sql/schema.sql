DROP TABLE IF EXISTS service_requests;

CREATE TABLE service_requests (
    unique_key BIGINT PRIMARY KEY,
    created_date TIMESTAMP,
    closed_date TIMESTAMP,
    agency TEXT,
    complaint_type TEXT,
    descriptor TEXT,
    location_type TEXT,
    borough TEXT,
    incident_zip TEXT,
    status TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION
);

CREATE INDEX idx_created_date ON service_requests (created_date);
CREATE INDEX idx_borough ON service_requests (borough);
CREATE INDEX idx_complaint_type ON service_requests (complaint_type);
CREATE INDEX idx_agency ON service_requests (agency);