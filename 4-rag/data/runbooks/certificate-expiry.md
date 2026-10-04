# Runbook: TLS certificate about to expire

> Fictional runbook used only as sample data for the 4-rag module.

## Symptoms

- Alert `TlsCertificateExpiringSoon` fires 21 days before a certificate expires.

## Diagnosis

1. Confirm the expiry date of the certificate served by the endpoint.
2. Check whether automatic renewal failed in the certificate manager logs.

## Mitigation

- Trigger a manual renewal in the certificate manager.
- If renewal fails, open a ticket with the security team with the domain name
  and the renewal error message.
- After renewal, confirm the new expiry date on every load balancer.
