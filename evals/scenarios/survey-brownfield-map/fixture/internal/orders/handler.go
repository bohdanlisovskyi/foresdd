package orders

import (
	"encoding/json"
	"errors"
	"net/http"

	"example.com/stockroom/internal/platform/apperr"
)

// RegisterRoutes is how every module wires itself into the mux (called from cmd/server).
func RegisterRoutes(mux *http.ServeMux, svc *Service) {
	mux.HandleFunc("POST /orders", func(w http.ResponseWriter, r *http.Request) {
		var in struct {
			SKU string `json:"sku"`
			Qty int    `json:"qty"`
		}
		if err := json.NewDecoder(r.Body).Decode(&in); err != nil {
			http.Error(w, "bad json", http.StatusBadRequest)
			return
		}
		o, err := svc.Place(r.Context(), in.SKU, in.Qty)
		if err != nil {
			writeErr(w, err)
			return
		}
		w.WriteHeader(http.StatusCreated)
		_ = json.NewEncoder(w).Encode(o)
	})
}

func writeErr(w http.ResponseWriter, err error) {
	var ae *apperr.Error
	if errors.As(err, &ae) {
		switch ae.Kind {
		case apperr.Invalid:
			http.Error(w, ae.Msg, http.StatusBadRequest)
		case apperr.Insufficient:
			http.Error(w, ae.Msg, http.StatusConflict)
		default:
			http.Error(w, ae.Msg, http.StatusNotFound)
		}
		return
	}
	http.Error(w, "internal", http.StatusInternalServerError)
}
