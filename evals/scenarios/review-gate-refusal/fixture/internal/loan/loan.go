package loan

import (
	"errors"
	"time"
)

// ErrNotFound is returned when a loan id is unknown.
var ErrNotFound = errors.New("loan.not_found")

// Loan is one book lent to one member.
type Loan struct {
	ID       string
	MemberID string
	BookID   string
	DueAt    time.Time
}

// Store holds loans in memory.
type Store struct {
	loans map[string]Loan
}

func NewStore() *Store { return &Store{loans: map[string]Loan{}} }

func (s *Store) Put(l Loan) { s.loans[l.ID] = l }

func (s *Store) Get(id string) (Loan, error) {
	l, ok := s.loans[id]
	if !ok {
		return Loan{}, ErrNotFound
	}
	return l, nil
}
