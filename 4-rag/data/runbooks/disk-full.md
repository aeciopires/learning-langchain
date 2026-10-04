# Runbook: disk almost full on log servers

> Fictional runbook used only as sample data for the 4-rag module.

## Symptoms

- Alert `LogServerDiskAlmostFull` fires when free disk space is below 10%.

## Diagnosis

1. Find the largest directories under `/var/log`.
2. Check whether log rotation ran in the last 24 hours.

## Mitigation

- Compress or delete application logs older than 7 days.
- Force a log rotation run.
- If free space is still below 10%, increase the volume size by 50 GiB.
