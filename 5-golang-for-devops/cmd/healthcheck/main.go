// Command healthcheck checks HTTP endpoints concurrently and exits with code 1
// if any of them is unhealthy - ready for cron jobs and CI/CD smoke tests.
//
// Usage:
//
//	go run ./cmd/healthcheck -timeout 3s https://example.com https://go.dev
//	go run ./cmd/healthcheck -json https://example.com
package main

import (
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"net/http"
	"os"
	"time"

	"github.com/aeciopires/learning-langchain/5-golang-for-devops/internal/health"
)

func main() {
	timeout := flag.Duration("timeout", 5*time.Second, "timeout for each request")
	asJSON := flag.Bool("json", false, "print the results as JSON")
	flag.Parse()

	urls := flag.Args()
	if len(urls) == 0 {
		fmt.Fprintln(os.Stderr, "usage: healthcheck [-timeout 5s] [-json] URL [URL...]")
		os.Exit(2)
	}

	results := health.CheckAll(context.Background(), http.DefaultClient, urls, *timeout)

	if *asJSON {
		encoder := json.NewEncoder(os.Stdout)
		encoder.SetIndent("", "  ")
		_ = encoder.Encode(results)
	} else {
		for _, r := range results {
			state := "OK  "
			if !r.Healthy {
				state = "FAIL"
			}
			fmt.Printf("[%s] %-40s status=%-3d time=%-8s %s\n",
				state, r.URL, r.StatusCode, r.Duration.Round(time.Millisecond), r.Error)
		}
	}

	if !health.AllHealthy(results) {
		os.Exit(1)
	}
}
