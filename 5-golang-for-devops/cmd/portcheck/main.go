// Command portcheck tests TCP connectivity to one or more host:port pairs and
// exits with code 1 if any is closed - handy to debug firewalls and security
// groups from inside a container or a bastion host.
//
// Usage:
//
//	go run ./cmd/portcheck -timeout 2s db.internal:5432 cache.internal:6379
package main

import (
	"context"
	"flag"
	"fmt"
	"os"
	"time"

	"github.com/aeciopires/learning-langchain/5-golang-for-devops/internal/netcheck"
)

func main() {
	timeout := flag.Duration("timeout", 3*time.Second, "timeout for each connection")
	flag.Parse()

	addresses := flag.Args()
	if len(addresses) == 0 {
		fmt.Fprintln(os.Stderr, "usage: portcheck [-timeout 3s] HOST:PORT [HOST:PORT...]")
		os.Exit(2)
	}

	allOpen := true
	for _, address := range addresses {
		r := netcheck.CheckTCP(context.Background(), address, *timeout)
		if r.Open {
			fmt.Printf("[OPEN  ] %-30s %s\n", r.Address, r.Latency.Round(time.Millisecond))
		} else {
			allOpen = false
			fmt.Printf("[CLOSED] %-30s %s\n", r.Address, r.Error)
		}
	}
	if !allOpen {
		os.Exit(1)
	}
}
