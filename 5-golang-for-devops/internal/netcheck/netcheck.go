// Package netcheck tests TCP connectivity - a scriptable "telnet host port"
// or "nc -zv host port", useful to debug security groups and firewalls.
package netcheck

import (
	"context"
	"net"
	"time"
)

// Result is the outcome of one TCP connection attempt.
type Result struct {
	Address string        `json:"address"`
	Open    bool          `json:"open"`
	Latency time.Duration `json:"latency_ns"`
	Error   string        `json:"error,omitempty"`
}

// CheckTCP tries to open a TCP connection to address ("host:port") and closes
// it right away. Open means something accepted the connection.
func CheckTCP(ctx context.Context, address string, timeout time.Duration) Result {
	dialer := net.Dialer{Timeout: timeout}
	start := time.Now()
	conn, err := dialer.DialContext(ctx, "tcp", address)
	result := Result{Address: address, Latency: time.Since(start)}
	if err != nil {
		result.Error = err.Error()
		return result
	}
	_ = conn.Close()
	result.Open = true
	return result
}
