package netcheck

import (
	"context"
	"net"
	"testing"
	"time"
)

func TestCheckTCPOpenPort(t *testing.T) {
	// Port 0 asks the OS for any free port, so the test never collides.
	listener, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		t.Fatal(err)
	}
	defer listener.Close()

	got := CheckTCP(context.Background(), listener.Addr().String(), time.Second)
	if !got.Open {
		t.Fatalf("expected open port, got %+v", got)
	}
}

func TestCheckTCPClosedPort(t *testing.T) {
	// Grab a free port and close it: nothing listens there anymore.
	listener, err := net.Listen("tcp", "127.0.0.1:0")
	if err != nil {
		t.Fatal(err)
	}
	address := listener.Addr().String()
	listener.Close()

	got := CheckTCP(context.Background(), address, time.Second)
	if got.Open || got.Error == "" {
		t.Fatalf("expected closed port with an error, got %+v", got)
	}
}
