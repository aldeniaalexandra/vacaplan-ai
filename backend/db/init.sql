-- VacaPlan AI — Database Schema

CREATE TABLE IF NOT EXISTS bookings (
    id              SERIAL PRIMARY KEY,
    session_id      UUID NOT NULL,
    confirmation_id VARCHAR(20) NOT NULL UNIQUE,
    amount_usd      NUMERIC(10, 2) NOT NULL,
    status          VARCHAR(20) DEFAULT 'confirmed',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS booking_audit_log (
    id              SERIAL PRIMARY KEY,
    session_id      UUID NOT NULL,
    event           VARCHAR(100) NOT NULL,
    details         JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_bookings_session ON bookings(session_id);
CREATE INDEX idx_audit_session ON booking_audit_log(session_id);
