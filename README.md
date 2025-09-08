# AWS Foundation Platform

Unified AWS Landing Zone and Observability Platform - A simple, testable, and maintainable infrastructure foundation.

## Architecture Overview

```
aws-foundation-platform/
├── foundation/          # Landing zone (accounts, networking, security)
├── observability/       # Monitoring, alerting, dashboards  
├── connectivity/        # Wireguard VPN, data transfer
├── configuration/       # SSM Parameter Store, Secrets Manager
├── tests/              # Unit tests for all constructs
├── pyproject.toml      # Poetry dependencies
└── app.py             # Main CDK application
```

## Components

- **Foundation**: Multi-account setup, VPC networking, security baseline
- **Observability**: CloudWatch dashboards, monitoring all platform components
- **Connectivity**: Wireguard VPN tunnel from home lab (192.168.198.0/24) to AWS
- **Configuration**: Centralized parameter and secrets management

## Quick Start

1. **Install dependencies**:
   ```bash
   poetry install --no-root
   ```

2. **Run tests**:
   ```bash
   poetry run pytest -v
   ```

3. **Deploy platform**:
   ```bash
   poetry run cdk deploy --all
   ```

## Development

- **Test-driven**: Every construct has basic synthesis tests
- **Simple**: Functional over fancy - junior-level friendly
- **Modular**: Each component can be developed and tested independently

## Testing

Run all tests with coverage:
```bash
poetry run pytest --cov
```
