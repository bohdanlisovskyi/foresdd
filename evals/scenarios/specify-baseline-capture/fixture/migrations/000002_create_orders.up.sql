CREATE TABLE orders (
    id         TEXT PRIMARY KEY,
    sku        TEXT NOT NULL REFERENCES stock (sku),
    qty        INTEGER NOT NULL CHECK (qty > 0),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
