package inventory

import (
	"context"

	"example.com/stockroom/internal/platform/apperr"
)

type store interface {
	Decrement(ctx context.Context, sku string, qty int) (bool, error)
}

type Service struct{ repo store }

func NewService(repo store) *Service { return &Service{repo: repo} }

// Reserve is called directly by the orders module (in-process, no events).
func (s *Service) Reserve(ctx context.Context, sku string, qty int) error {
	ok, err := s.repo.Decrement(ctx, sku, qty)
	if err != nil {
		return err
	}
	if !ok {
		return apperr.E(apperr.Insufficient, "sku %s: need %d", sku, qty)
	}
	return nil
}
