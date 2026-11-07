package loan

import (
	"testing"
	"time"
)

func TestStoreGet(t *testing.T) {
	s := NewStore()
	s.Put(Loan{ID: "l1", MemberID: "m1", BookID: "b1", DueAt: time.Now()})
	if _, err := s.Get("l1"); err != nil {
		t.Fatalf("expected loan, got %v", err)
	}
	if _, err := s.Get("nope"); err != ErrNotFound {
		t.Fatalf("expected ErrNotFound, got %v", err)
	}
}
