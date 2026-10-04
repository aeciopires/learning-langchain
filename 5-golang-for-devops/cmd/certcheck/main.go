// Command certcheck reports how many days are left before the TLS certificate
// of each endpoint expires, and exits with code 1 if any expires within the
// warning window.
//
// Usage:
//
//	go run ./cmd/certcheck -warn-days 21 example.com:443 go.dev:443
package main

import (
	"context"
	"flag"
	"fmt"
	"os"
	"time"

	"github.com/aeciopires/learning-langchain/5-golang-for-devops/internal/certs"
)

func main() {
	warnDays := flag.Int("warn-days", 21, "fail when a certificate expires in fewer days than this")
	timeout := flag.Duration("timeout", 5*time.Second, "timeout for each connection")
	insecure := flag.Bool("insecure", false, "skip verification (only to read dates of self-signed certificates)")
	flag.Parse()

	addresses := flag.Args()
	if len(addresses) == 0 {
		fmt.Fprintln(os.Stderr, "usage: certcheck [-warn-days 21] [-timeout 5s] [-insecure] HOST:PORT [HOST:PORT...]")
		os.Exit(2)
	}

	ok := true
	now := time.Now()
	for _, address := range addresses {
		info, err := certs.Inspect(context.Background(), address, certs.Options{Insecure: *insecure, Timeout: *timeout}, now)
		switch {
		case err != nil:
			ok = false
			fmt.Printf("[ERROR] %-30s %v\n", address, err)
		case info.DaysLeft < *warnDays:
			ok = false
			fmt.Printf("[WARN ] %-30s expires %s (%d days left)\n", address, info.NotAfter.Format(time.DateOnly), info.DaysLeft)
		default:
			fmt.Printf("[OK   ] %-30s expires %s (%d days left)\n", address, info.NotAfter.Format(time.DateOnly), info.DaysLeft)
		}
	}
	if !ok {
		os.Exit(1)
	}
}
