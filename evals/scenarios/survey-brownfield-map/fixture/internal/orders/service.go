package orders

import (
	"context"
	"crypto/rand"
	"encoding/hex"

	"example.com/stockroom/internal/platform/apperr"
)

type Order struct {
	ID  string
	SKU string
	Qty int
}

type store interface {
	Insert(ctx context.Context, o Order) error
}

type reserver interface {
	Reserve(ctx context.Context, sku string, qty int) error
}

type Service struct {
	repo store
	inv  reserver
}

func NewService(repo store, inv reserver) *Service { return &Service{repo: repo, inv: inv} }

func (s *Service) Place(ctx context.Context, sku string, qty int) (Order, error) {
	if qty <= 0 {
		return Order{}, apperr.E(apperr.Invalid, "qty must be positive, got %d", qty)
	}
	if err := s.inv.Reserve(ctx, sku, qty); err != nil {
		return Order{}, err
	}
	o := Order{ID: newID(), SKU: sku, Qty: qty}
	return o, s.repo.Insert(ctx, o)
}

// newID: random 16-byte hex ids, generated in the app (no DB sequence).
func newID() string {
	b := make([]byte, 16)
	_, _ = rand.Read(b)
	return hex.EncodeToString(b)
}
