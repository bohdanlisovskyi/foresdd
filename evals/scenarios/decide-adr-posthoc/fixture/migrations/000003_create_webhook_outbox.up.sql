CREATE TABLE webhook_outbox (
    id              BIGSERIAL PRIMARY KEY,
    merchant_id     TEXT        NOT NULL,
    payload         JSONB       NOT NULL,
    attempts        INTEGER     NOT NULL DEFAULT 0,
    next_attempt_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    delivered_at    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX webhook_outbox_pending ON webhook_outbox (next_attempt_at) WHERE delivered_at IS NULL;
