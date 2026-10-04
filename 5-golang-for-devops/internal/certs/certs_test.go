package certs

import (
	"context"
	"crypto/x509"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"
)

func TestDaysUntil(t *testing.T) {
	now := time.Date(2026, 10, 1, 0, 0, 0, 0, time.UTC)
	tests := []struct {
		name string
		t    time.Time
		want int
	}{
		{"in 30 days", now.Add(30 * 24 * time.Hour), 30},
		{"in 12 hours", now.Add(12 * time.Hour), 0},
		{"expired 2 days ago", now.Add(-48 * time.Hour), -2},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := DaysUntil(tt.t, now); got != tt.want {
				t.Fatalf("DaysUntil() = %d, want %d", got, tt.want)
			}
		})
	}
}

// httptest.NewTLSServer serves a self-signed test certificate; trusting it
// through RootCAs lets the test verify the chain without Insecure.
func TestInspectTrustedServer(t *testing.T) {
	server := httptest.NewTLSServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {}))
	defer server.Close()

	pool := x509.NewCertPool()
	pool.AddCert(server.Certificate())
	address := strings.TrimPrefix(server.URL, "https://")
	now := time.Now()

	info, err := Inspect(context.Background(), address, Options{RootCAs: pool, Timeout: time.Second}, now)
	if err != nil {
		t.Fatalf("Inspect() error = %v", err)
	}
	if !info.NotAfter.Equal(server.Certificate().NotAfter) {
		t.Errorf("NotAfter = %v, want %v", info.NotAfter, server.Certificate().NotAfter)
	}
	if info.DaysLeft != DaysUntil(server.Certificate().NotAfter, now) {
		t.Errorf("DaysLeft = %d", info.DaysLeft)
	}
}

func TestInspectUntrustedServerFailsUnlessInsecure(t *testing.T) {
	server := httptest.NewTLSServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {}))
	defer server.Close()
	address := strings.TrimPrefix(server.URL, "https://")

	if _, err := Inspect(context.Background(), address, Options{Timeout: time.Second}, time.Now()); err == nil {
		t.Fatal("expected a verification error for a self-signed certificate")
	}
	if _, err := Inspect(context.Background(), address, Options{Insecure: true, Timeout: time.Second}, time.Now()); err != nil {
		t.Fatalf("Insecure: Inspect() error = %v", err)
	}
}

func TestInspectRejectsAddressWithoutPort(t *testing.T) {
	if _, err := Inspect(context.Background(), "example.com", Options{}, time.Now()); err == nil {
		t.Fatal("expected an error for an address without a port")
	}
}
