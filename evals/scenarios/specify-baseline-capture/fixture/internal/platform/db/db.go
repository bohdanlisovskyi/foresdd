// Package db opens the shared Postgres handle every module repo receives.
package db

import "database/sql"

func Open(dsn string) (*sql.DB, error) {
	return sql.Open("postgres", dsn)
}
