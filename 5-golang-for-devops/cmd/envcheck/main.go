// Command envcheck fails (exit code 1) when any required environment variable
// is unset or empty - a guard at the start of a deploy script or container.
//
// Usage:
//
//	go run ./cmd/envcheck AWS_REGION DB_HOST DB_PASSWORD
//	go run ./cmd/envcheck -show AWS_REGION DB_PASSWORD   # prints masked values
package main

import (
	"flag"
	"fmt"
	"os"

	"github.com/aeciopires/learning-langchain/5-golang-for-devops/internal/envcheck"
)

func main() {
	show := flag.Bool("show", false, "print every required variable with its value masked")
	flag.Parse()

	required := flag.Args()
	if len(required) == 0 {
		fmt.Fprintln(os.Stderr, "usage: envcheck [-show] VAR [VAR...]")
		os.Exit(2)
	}

	if *show {
		for _, name := range required {
			fmt.Printf("%s=%s\n", name, envcheck.Mask(os.Getenv(name)))
		}
	}

	missing := envcheck.Missing(required, os.LookupEnv)
	if len(missing) > 0 {
		fmt.Fprintf(os.Stderr, "missing required variables: %v\n", missing)
		os.Exit(1)
	}
	fmt.Println("all required variables are set")
}
