package orders

import (
	"context"
	"testing"
)

type fakeStore struct{ got []Order }

func (f *fakeStore) Insert(_ context.Context, o Order) error { f.got = append(f.got, o); return nil }

type fakeInv struct{}

func (fakeInv) Reserve(context.Context, string, int) error { return nil }

// Table-driven unit tests with hand-written fakes; no DB in unit tests.
func TestPlace(t *testing.T) {
	cases := []struct {
		name    string
		qty     int
		wantErr bool
	}{
		{"positive qty", 2, false},
		{"zero qty rejected", 0, true},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			fs := &fakeStore{}
			_, err := NewService(fs, fakeInv{}).Place(context.Background(), "SKU-1", tc.qty)
			if (err != nil) != tc.wantErr {
				t.Fatalf("err = %v, wantErr %v", err, tc.wantErr)
			}
		})
	}
}
