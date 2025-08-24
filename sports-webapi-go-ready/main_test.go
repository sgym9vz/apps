package main

import (
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestHealth(t *testing.T) {
	seedData()
	req := httptest.NewRequest(http.MethodGet, "/health", nil)
	rr := httptest.NewRecorder()
	healthHandler(rr, req)
	if rr.Code != http.StatusOK {
		t.Fatalf("status=%d body=%s", rr.Code, rr.Body.String())
	}
}

func TestPlayersPerPage(t *testing.T) {
	seedData()
	req := httptest.NewRequest(http.MethodGet, "/api/players?per_page=2", nil)
	rr := httptest.NewRecorder()
	playersListHandler(rr, req)
	if rr.Code != http.StatusOK {
		t.Fatalf("status=%d body=%s", rr.Code, rr.Body.String())
	}
	// not parsing JSON here to keep it minimal; status 200 is enough smoke test
}
