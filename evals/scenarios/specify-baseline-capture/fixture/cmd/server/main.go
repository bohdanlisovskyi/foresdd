package main

import (
	"log"
	"net/http"
	"os"

	"example.com/stockroom/internal/inventory"
	"example.com/stockroom/internal/orders"
	"example.com/stockroom/internal/platform/db"
)

func main() {
	pool, err := db.Open(os.Getenv("DATABASE_URL"))
	if err != nil {
		log.Fatal(err)
	}

	inv := inventory.NewService(inventory.NewRepo(pool))
	ord := orders.NewService(orders.NewRepo(pool), inv)

	mux := http.NewServeMux()
	orders.RegisterRoutes(mux, ord)

	log.Fatal(http.ListenAndServe(":8080", mux))
}
