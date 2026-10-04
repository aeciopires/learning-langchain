# Runbook: high CPU on checkout-api

> Fictional runbook used only as sample data for the 4-rag module.

## Symptoms

- Alert `CheckoutApiHighCpu` fires when average CPU stays above 85% for 10 minutes.
- p95 latency of `checkout-api` grows above 800 ms.

## Diagnosis

1. Check whether a deploy happened in the last hour (`deploy-history` dashboard).
2. Compare requests per second with the same hour of the previous week.
3. Look for slow queries in the `checkout-db` slow query log.

## Mitigation

- If a deploy happened in the last hour, roll back to the previous version.
- If traffic is above normal, scale `checkout-api` from 3 to 6 replicas.
- Escalate to the `#team-checkout` channel if CPU stays high for 30 minutes.
