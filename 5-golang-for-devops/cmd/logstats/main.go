// Command logstats summarizes JSON-lines logs read from files or stdin.
//
// Usage:
//
//	go run ./cmd/logstats -top 5 testdata/app.log
//	kubectl logs deploy/checkout-api | go run ./cmd/logstats
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"os"

	"github.com/aeciopires/learning-langchain/5-golang-for-devops/internal/logstats"
)

func main() {
	topN := flag.Int("top", 5, "how many of the most frequent error messages to show")
	flag.Parse()

	// No file arguments: read from stdin, so the command works in a pipe.
	var input io.Reader = os.Stdin
	if flag.NArg() > 0 {
		readers := make([]io.Reader, 0, flag.NArg())
		for _, path := range flag.Args() {
			file, err := os.Open(path)
			if err != nil {
				fmt.Fprintln(os.Stderr, "error:", err)
				os.Exit(1)
			}
			defer file.Close()
			readers = append(readers, file)
		}
		input = io.MultiReader(readers...)
	}

	summary, err := logstats.Summarize(input, *topN)
	if err != nil {
		fmt.Fprintln(os.Stderr, "error:", err)
		os.Exit(1)
	}
	encoder := json.NewEncoder(os.Stdout)
	encoder.SetIndent("", "  ")
	_ = encoder.Encode(summary)
}
