CREATE TABLE IF NOT EXISTS clients (
    org varchar(255),
    repo varchar(255),
    onboarded_by varchar(255),
    correlation_id varchar(255),
    ts TIMESTAMPTZ,
    PRIMARY KEY(org, repo)
);

CREATE TABLE IF NOT EXISTS clients_audit (
    actn varchar(16),
    org varchar(255),
    repo varchar(255),
    onboarded_by varchar(255),
    correlation_id varchar(48),
    ts TIMESTAMPTZ,
    PRIMARY KEY(correlation_id, org, repo)
);

-- TODO:

-- CREATE TABLE IF NOT EXISTS requirements (
--     id int,
--     parent varchar(255),
--     s3key varchar(255),
--     author varchar(255)
-- );

-- CREATE TABLE IF NOT EXISTS scoring (
--     id int NOT NULL,
--     product varchar(255),
--     requirement varchar(255),
--     score int,
--     PRIMARY KEY(id)
-- );

-- CREATE TABLE IF NOT EXISTS applicability (
--     id int NOT NULL,
--     producttype varchar(255),
--     requirementlevel varchar(255),
--     PRIMARY KEY(id)
-- );
