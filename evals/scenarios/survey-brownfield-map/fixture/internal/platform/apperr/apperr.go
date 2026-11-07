// Package apperr is the one error type modules return across their boundary.
package apperr

import "fmt"

type Kind string

const (
	NotFound     Kind = "not_found"
	Invalid      Kind = "invalid"
	Insufficient Kind = "insufficient_stock"
)

type Error struct {
	Kind Kind
	Msg  string
}

func (e *Error) Error() string { return fmt.Sprintf("%s: %s", e.Kind, e.Msg) }

func E(kind Kind, format string, args ...any) error {
	return &Error{Kind: kind, Msg: fmt.Sprintf(format, args...)}
}
