package orders

import (
	"context"
	"database/sql"
)

type Repo struct{ db *sql.DB }

func NewRepo(db *sql.DB) *Repo { return &Repo{db: db} }

func (r *Repo) Insert(ctx context.Context, o Order) error {
	_, err := r.db.ExecContext(ctx,
		`INSERT INTO orders (id, sku, qty) VALUES ($1, $2, $3)`, o.ID, o.SKU, o.Qty)
	return err
}
