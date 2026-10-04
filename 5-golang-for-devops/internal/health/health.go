// Package health checks HTTP endpoints concurrently, the way a cron job or a
// CI step checks that services answer after a deploy.
package health

import (
	"context"
	"fmt"
	"net/http"
	"sync"
	"time"
)

// Result is the outcome of checking one URL.
type Result struct {
	URL        string        `json:"url"`
	StatusCode int           `json:"status_code"`
	Duration   time.Duration `json:"duration_ns"`
	Healthy    bool          `json:"healthy"`
	Error      string        `json:"error,omitempty"`
}

// CheckURL sends a GET request to url and reports it as healthy when the
// status code is 2xx or 3xx. The context controls the timeout.
func CheckURL(ctx context.Context, client *http.Client, url string) Result {
	start := time.Now()
	result := Result{URL: url}

	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		result.Error = fmt.Sprintf("invalid request: %v", err)
		return result
	}
	resp, err := client.Do(req)
	result.Duration = time.Since(start)
	if err != nil {
		result.Error = err.Error()
		return result
	}
	// Always close the body, or the connection is never reused (a classic leak).
	defer resp.Body.Close()

	result.StatusCode = resp.StatusCode
	result.Healthy = resp.StatusCode >= 200 && resp.StatusCode < 400
	return result
}

// CheckAll checks every URL at the same time (one goroutine each) and returns
// the results in the same order as the input. Each check has its own timeout.
func CheckAll(ctx context.Context, client *http.Client, urls []string, timeout time.Duration) []Result {
	results := make([]Result, len(urls))
	var wg sync.WaitGroup
	for i, url := range urls {
		// WaitGroup.Go (Go 1.25+) starts the goroutine and tracks it, so
		// Wait() below blocks until every check has finished.
		wg.Go(func() {
			checkCtx, cancel := context.WithTimeout(ctx, timeout)
			defer cancel()
			// Each goroutine writes only its own index: no mutex needed.
			results[i] = CheckURL(checkCtx, client, url)
		})
	}
	wg.Wait()
	return results
}

// AllHealthy reports whether every result is healthy.
func AllHealthy(results []Result) bool {
	for _, r := range results {
		if !r.Healthy {
			return false
		}
	}
	return true
}
