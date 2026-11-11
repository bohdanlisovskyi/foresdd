.PHONY: build test lint migrate

build:
	go build ./...

test:
	go test ./...

lint:
	golangci-lint run ./...

# golang-migrate CLI; files are NNNNNN_name.up.sql / .down.sql
migrate:
	migrate -path migrations -database "$$DATABASE_URL" up
