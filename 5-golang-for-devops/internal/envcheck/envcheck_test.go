package envcheck

import (
	"reflect"
	"testing"
)

func TestMissing(t *testing.T) {
	env := map[string]string{"AWS_REGION": "us-east-1", "EMPTY": "  "}
	lookup := func(name string) (string, bool) {
		value, ok := env[name]
		return value, ok
	}
	got := Missing([]string{"AWS_REGION", "EMPTY", "DB_PASSWORD", " "}, lookup)
	want := []string{"EMPTY", "DB_PASSWORD"}
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("Missing() = %v, want %v", got, want)
	}
}

func TestMask(t *testing.T) {
	tests := map[string]string{"": "", "abc": "***", "abcdef1234": "ab******34"}
	for in, want := range tests {
		if got := Mask(in); got != want {
			t.Errorf("Mask(%q) = %q, want %q", in, got, want)
		}
	}
}
