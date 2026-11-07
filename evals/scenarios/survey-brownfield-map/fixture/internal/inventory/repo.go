package inventory

import (
	"context"
	"database/sql"
)

type Repo struct{ db *sql.DB }

func NewRepo(db *sql.DB) *Repo { return &Repo{db: db} }

// Decrement reserves qty units of sku; returns false when stock is short.
func (r *Repo) Decrement(ctx context.Context, sku string, qty int) (bool, error) {
	res, err := r.db.ExecContext(ctx,
		`UPDATE stock SET on_hand = on_hand - $1 WHERE sku = $2 AND on_hand >= $1`, qty, sku)
	if err != nil {
		return false, err
	}
	n, err := res.RowsAffected()
	return n == 1, err
}
