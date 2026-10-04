// Package logstats summarizes structured (JSON lines) logs: how many lines per
// level and per HTTP status, and the most frequent error messages - the
// "grep | sort | uniq -c" of on-call, but for JSON.
package logstats

import (
	"bufio"
	"cmp"
	"encoding/json"
	"io"
	"slices"
	"strings"
)

// entry holds the fields we care about; other fields in the line are ignored.
type entry struct {
	Level  string `json:"level"`
	Msg    string `json:"msg"`
	Status int    `json:"status"`
}

// Count is a value and how many times it appeared.
type Count struct {
	Value string `json:"value"`
	Count int    `json:"count"`
}

// Summary is the result of reading a whole log stream.
type Summary struct {
	Lines        int            `json:"lines"`
	InvalidLines int            `json:"invalid_lines"`
	ByLevel      map[string]int `json:"by_level"`
	ByStatus     map[int]int    `json:"by_status"`
	TopErrors    []Count        `json:"top_errors"`
}

// Summarize reads JSON lines from r. Lines that are not valid JSON are counted
// in InvalidLines instead of stopping the whole report.
func Summarize(r io.Reader, topN int) (Summary, error) {
	summary := Summary{ByLevel: map[string]int{}, ByStatus: map[int]int{}}
	errorMessages := map[string]int{}

	scanner := bufio.NewScanner(r)
	// Log lines can be long (stack traces): allow up to 1 MiB per line.
	scanner.Buffer(make([]byte, 64*1024), 1024*1024)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" {
			continue
		}
		summary.Lines++

		var e entry
		if err := json.Unmarshal([]byte(line), &e); err != nil {
			summary.InvalidLines++
			continue
		}
		level := strings.ToUpper(e.Level)
		if level == "" {
			level = "UNKNOWN"
		}
		summary.ByLevel[level]++
		if e.Status != 0 {
			summary.ByStatus[e.Status]++
		}
		if level == "ERROR" && e.Msg != "" {
			errorMessages[e.Msg]++
		}
	}
	if err := scanner.Err(); err != nil {
		return summary, err
	}
	summary.TopErrors = top(errorMessages, topN)
	return summary, nil
}

// top returns the n most frequent values, most frequent first (ties sorted
// alphabetically, so the output is stable).
func top(counts map[string]int, n int) []Count {
	result := make([]Count, 0, len(counts))
	for value, count := range counts {
		result = append(result, Count{Value: value, Count: count})
	}
	slices.SortFunc(result, func(a, b Count) int {
		if c := cmp.Compare(b.Count, a.Count); c != 0 {
			return c
		}
		return cmp.Compare(a.Value, b.Value)
	})
	if n >= 0 && len(result) > n {
		result = result[:n]
	}
	return result
}
