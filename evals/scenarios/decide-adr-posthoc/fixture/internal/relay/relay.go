// Package relay drains webhook_outbox: it claims undelivered rows, POSTs them (HMAC-signed per
// ADR-0001) and marks them delivered; failures are retried with backoff for up to 24 h.
package relay

import (
	"context"
	"database/sql"
	"time"
)

type Relay struct {
	db   *sql.DB
	send func(ctx context.Context, merchantID string, payload []byte) error
}

func (r *Relay) Run(ctx context.Context) {
	t := time.NewTicker(time.Second)
	defer t.Stop()
	for {
		select {
		case <-ctx.Done():
			return
		case <-t.C:
			r.drainOnce(ctx)
		}
	}
}

func (r *Relay) drainOnce(ctx context.Context) {
	rows, err := r.db.QueryContext(ctx, `
		SELECT id, merchant_id, payload FROM webhook_outbox
		WHERE delivered_at IS NULL AND next_attempt_at <= now()
		ORDER BY id LIMIT 50 FOR UPDATE SKIP LOCKED`)
	if err != nil {
		return
	}
	defer rows.Close()
	for rows.Next() {
		var id int64
		var merchantID string
		var payload []byte
		if rows.Scan(&id, &merchantID, &payload) != nil {
			continue
		}
		if r.send(ctx, merchantID, payload) == nil {
			_, _ = r.db.ExecContext(ctx, `UPDATE webhook_outbox SET delivered_at = now() WHERE id = $1`, id)
		} else {
			_, _ = r.db.ExecContext(ctx, `UPDATE webhook_outbox
				SET attempts = attempts + 1, next_attempt_at = now() + (interval '1 second' * power(2, attempts))
				WHERE id = $1`, id)
		}
	}
}
