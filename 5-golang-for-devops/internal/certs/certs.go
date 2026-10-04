// Package certs reads the TLS certificate an endpoint serves and reports how
// many days are left before it expires - an expired certificate is one of
// the most common (and most avoidable) outages.
package certs

import (
	"context"
	"crypto/tls"
	"crypto/x509"
	"errors"
	"fmt"
	"net"
	"time"
)

// Info describes the leaf certificate served by an endpoint.
type Info struct {
	Address  string    `json:"address"`
	Subject  string    `json:"subject"`
	Issuer   string    `json:"issuer"`
	NotAfter time.Time `json:"not_after"`
	DaysLeft int       `json:"days_left"`
}

// Options controls how the TLS connection is made.
type Options struct {
	// ServerName overrides the name checked against the certificate (SNI);
	// empty means the host part of the address.
	ServerName string
	// RootCAs are the trusted CAs; nil means the system's CA pool.
	RootCAs *x509.CertPool
	// Insecure skips certificate verification. Only for reading the dates of
	// self-signed or internal certificates - never for sending data.
	Insecure bool
	Timeout  time.Duration
}

// Inspect connects to address ("host:port"), completes the TLS handshake and
// returns the leaf certificate's details. now is passed in so tests (and
// reports) can compute DaysLeft against a fixed moment.
func Inspect(ctx context.Context, address string, opts Options, now time.Time) (Info, error) {
	serverName := opts.ServerName
	if serverName == "" {
		host, _, err := net.SplitHostPort(address)
		if err != nil {
			return Info{}, fmt.Errorf("address must be host:port: %w", err)
		}
		serverName = host
	}

	dialer := tls.Dialer{
		NetDialer: &net.Dialer{Timeout: opts.Timeout},
		Config: &tls.Config{
			ServerName:         serverName,
			RootCAs:            opts.RootCAs,
			InsecureSkipVerify: opts.Insecure, // opt-in, see the field comment
			MinVersion:         tls.VersionTLS12,
		},
	}
	conn, err := dialer.DialContext(ctx, "tcp", address)
	if err != nil {
		return Info{}, err
	}
	defer conn.Close()

	tlsConn, ok := conn.(*tls.Conn)
	if !ok {
		return Info{}, errors.New("not a TLS connection")
	}
	peers := tlsConn.ConnectionState().PeerCertificates
	if len(peers) == 0 {
		return Info{}, errors.New("the server sent no certificate")
	}
	leaf := peers[0]
	return Info{
		Address:  address,
		Subject:  leaf.Subject.String(),
		Issuer:   leaf.Issuer.String(),
		NotAfter: leaf.NotAfter,
		DaysLeft: DaysUntil(leaf.NotAfter, now),
	}, nil
}

// DaysUntil returns the whole days between now and t (negative if t is past).
func DaysUntil(t, now time.Time) int {
	return int(t.Sub(now).Hours() / 24)
}
