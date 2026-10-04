// Package envcheck validates that required environment variables are set
// before an application or a deploy script starts - failing fast with a
// clear message beats failing later with a confusing one.
package envcheck

import "strings"

// Missing returns the names in required that are unset or empty, using
// lookup (os.LookupEnv in production, a map in tests).
func Missing(required []string, lookup func(string) (string, bool)) []string {
	var missing []string
	for _, name := range required {
		name = strings.TrimSpace(name)
		if name == "" {
			continue
		}
		if value, ok := lookup(name); !ok || strings.TrimSpace(value) == "" {
			missing = append(missing, name)
		}
	}
	return missing
}

// Mask hides most of a secret's value for safe logging: "abcdef1234" -> "ab******34".
func Mask(value string) string {
	if len(value) <= 4 {
		return strings.Repeat("*", len(value))
	}
	return value[:2] + strings.Repeat("*", len(value)-4) + value[len(value)-2:]
}
