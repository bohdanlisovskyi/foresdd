package orders

import (
	"context"
	"database/sql"
	"encoding/json"
)

type Service struct{ db *sql.DB }

// Place inserts the order AND its order.placed outbox row in ONE transaction, so a webhook can
// only exist for a committed order. Delivery happens later in internal/relay — never in this
// request path. (Replaced the synchronous POST described in sad.md §4.)
func (s *Service) Place(ctx context.Context, id, merchantID string) error {
	tx, err := s.db.BeginTx(ctx, nil)
	if err != nil {
		return err
	}
	defer tx.Rollback()

	if _, err := tx.ExecContext(ctx,
		`INSERT INTO orders (id, merchant_id) VALUES ($1, $2)`, id, merchantID); err != nil {
		return err
	}
	payload, _ := json.Marshal(map[string]string{"type": "order.placed", "order_id": id})
	if _, err := tx.ExecContext(ctx,
		`INSERT INTO webhook_outbox (merchant_id, payload) VALUES ($1, $2)`, merchantID, payload); err != nil {
		return err
	}
	return tx.Commit()
}
