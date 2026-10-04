package health

import (
	"context"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"
)

// newServer starts a local HTTP server (httptest) that answers with the given
// status code after an optional delay - no real network or service needed.
func newServer(t *testing.T, status int, delay time.Duration) *httptest.Server {
	t.Helper()
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		time.Sleep(delay)
		w.WriteHeader(status)
	}))
	t.Cleanup(server.Close)
	return server
}

func TestCheckURL(t *testing.T) {
	// Table-driven test: one row per scenario, the idiomatic Go style.
	tests := []struct {
		name        string
		status      int
		wantHealthy bool
	}{
		{"ok", http.StatusOK, true},
		{"redirect", http.StatusFound, true},
		{"not found", http.StatusNotFound, false},
		{"server error", http.StatusServiceUnavailable, false},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			server := newServer(t, tt.status, 0)
			// A client that does not follow redirects, so 302 is seen as-is.
			client := &http.Client{CheckRedirect: func(*http.Request, []*http.Request) error {
				return http.ErrUseLastResponse
			}}
			got := CheckURL(context.Background(), client, server.URL)
			if got.Healthy != tt.wantHealthy || got.StatusCode != tt.status {
				t.Fatalf("CheckURL() = %+v, want healthy=%v status=%d", got, tt.wantHealthy, tt.status)
			}
		})
	}
}

func TestCheckURLInvalidURL(t *testing.T) {
	got := CheckURL(context.Background(), http.DefaultClient, "://bad url")
	if got.Healthy || got.Error == "" {
		t.Fatalf("expected an error for an invalid URL, got %+v", got)
	}
}

func TestCheckAllKeepsOrderAndAppliesTimeout(t *testing.T) {
	fast := newServer(t, http.StatusOK, 0)
	slow := newServer(t, http.StatusOK, 500*time.Millisecond)

	results := CheckAll(context.Background(), http.DefaultClient, []string{fast.URL, slow.URL}, 100*time.Millisecond)

	if results[0].URL != fast.URL || !results[0].Healthy {
		t.Errorf("fast server: got %+v", results[0])
	}
	if results[1].URL != slow.URL || results[1].Healthy || results[1].Error == "" {
		t.Errorf("slow server should time out: got %+v", results[1])
	}
	if AllHealthy(results) {
		t.Error("AllHealthy() = true, want false")
	}
	if !AllHealthy(results[:1]) {
		t.Error("AllHealthy(fast only) = false, want true")
	}
}
