# Microservices Demo Error Documentation

This document tracks the errors found in the microservices demo and their solutions.

## Error Categories

### Application Errors

| Service | Error Description | Error Type | Managed to identify the error? | Correct solution suggested? | Status | Ground truth solution | Reference |
|---------|------------------|------------|-------------------------------|-----------------------------|--------|------------------------|-----------|
| Cart Service | Unable to add loafers to cart | Application | ✅ | ✅ | ✅ Fixed | Remove exception when loafers are added to cart | [Slack Thread](https://fuzzy-labs.slack.com/archives/C08M5SMJ0KW/p1744896330504309) |
| Payment Service | Order placement with valid credit card | Application | ❌ | ❌ | ❌ Fail to provide solution | Exception should be thrown for valid credit cards | No message, stuck in loop |
| Currency Service | GBP currency conversion | Application | ✅ | ✅ | ✅ Fixed | Add conversion rate for GBP | [Slack Thread](https://fuzzy-labs.slack.com/archives/C08M5SMJ0KW/p1744896844011919) |
| Product Catalog | Negative price for ducks | Application | ✅ | ✅ | ✅ Fixed | Fix duck's unit price in `products.json` | [Slack Thread](https://fuzzy-labs.slack.com/archives/C08M5SMJ0KW/p1744897001392409) |
| Infrastructure | Node crash due to k8s misconfiguration allowing too much memory for service | System | ❌ | ❌ | ❌ Fail to provide solution | Terminate the EC2 instance of the node | [Slack Thread](https://fuzzy-labs.slack.com/archives/C08M5SMJ0KW/p1745404588383829) |


### System Errors

| Error Description | Status | Solution | Reference |
|------------------|--------|----------|-----------|
| Node crash due to k8s memory misconfiguration in checkout service manifest| ❌ Fail to provide solution | Terminate crashed node's EC2 instance | [Slack Thread](https://fuzzy-labs.slack.com/archives/C08M5SMJ0KW/p1745404588383829) |

## Status Legend
- ✅ Fixed: Error has been identified and resolved
- ❌ Unresolved: Agent is unable to identify or provide a correct solution to the problem.
- Pending: Error is under investigation

## Notes
- Each error includes a reference link to relevant discussion threads where available
- Solutions are documented with specific implementation details
- System errors are tracked separately from application errors for better organization