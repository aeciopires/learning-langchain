package logstats

import (
	"reflect"
	"strings"
	"testing"
)

const sampleLogs = `
{"time":"2026-10-01T10:00:00Z","level":"INFO","msg":"request","status":200}
{"time":"2026-10-01T10:00:01Z","level":"error","msg":"db timeout","status":500}
{"time":"2026-10-01T10:00:02Z","level":"ERROR","msg":"db timeout","status":500}
{"time":"2026-10-01T10:00:03Z","level":"ERROR","msg":"cache miss storm","status":503}
{"time":"2026-10-01T10:00:04Z","level":"WARN","msg":"slow request","status":200}
this line is not JSON
{"time":"2026-10-01T10:00:05Z","msg":"no level"}
`

func TestSummarize(t *testing.T) {
	got, err := Summarize(strings.NewReader(sampleLogs), 1)
	if err != nil {
		t.Fatal(err)
	}
	if got.Lines != 7 || got.InvalidLines != 1 {
		t.Errorf("Lines=%d InvalidLines=%d, want 7 and 1", got.Lines, got.InvalidLines)
	}
	wantLevels := map[string]int{"INFO": 1, "ERROR": 3, "WARN": 1, "UNKNOWN": 1}
	if !reflect.DeepEqual(got.ByLevel, wantLevels) {
		t.Errorf("ByLevel = %v, want %v", got.ByLevel, wantLevels)
	}
	wantStatus := map[int]int{200: 2, 500: 2, 503: 1}
	if !reflect.DeepEqual(got.ByStatus, wantStatus) {
		t.Errorf("ByStatus = %v, want %v", got.ByStatus, wantStatus)
	}
	wantTop := []Count{{Value: "db timeout", Count: 2}}
	if !reflect.DeepEqual(got.TopErrors, wantTop) {
		t.Errorf("TopErrors = %v, want %v", got.TopErrors, wantTop)
	}
}

func TestTopBreaksTiesAlphabetically(t *testing.T) {
	got := top(map[string]int{"b": 1, "a": 1, "c": 5}, -1)
	want := []Count{{"c", 5}, {"a", 1}, {"b", 1}}
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("top() = %v, want %v", got, want)
	}
}
