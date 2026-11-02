# External Integrations & Services

This document details external providers, payment gateways, and third-party APIs.

## Configured Integrations

| Name | Kind / Category | Provider | Description |
| :--- | :--- | :--- | :--- |
| **activity_log** | `audit_log` | `activity_log` | - |
| **mailgun** | `mail` | `mailgun` | - |
| **s3** | `storage` | `s3` | - |

## Configuration & Secrets Guidance

### activity_log (`audit_log`)
- **Provider / Package**: `activity_log`
- **Environment Variables**: Configure in `.env` securely.
- **Resilience**: Retries with exponential backoff and timeout.

### mailgun (`mail`)
- **Provider / Package**: `mailgun`
- **Environment Variables**: Configure in `.env` securely.
- **Resilience**: Retries with exponential backoff and timeout.

### s3 (`storage`)
- **Provider / Package**: `s3`
- **Environment Variables**: Configure in `.env` securely.
- **Resilience**: Retries with exponential backoff and timeout.
