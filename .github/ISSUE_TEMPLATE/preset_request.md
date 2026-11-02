---
name: Preset Request
about: Propose a new domain-specific architectural preset or integration pattern
title: '[PRESET] '
labels: ['enhancement', 'preset']
assignees: ''
---

### Preset Name & Identifier
- **Display Name**: [e.g. Stripe Subscriptions & Billing Portal]
- **Suggested Identifier**: [e.g. `stripe-billing`]

### Use Case & Problem Statement
Describe what architectural problem this preset solves and why developers need it.

### Target Ecosystem & Dependencies
- **Key Composer Packages**: [e.g. `laravel/cashier:^15.0`]
- **External Services / APIs**: [e.g. Stripe Webhooks, Customer Portal]
- **Minimum Framework Versions**: Laravel 11/12+, Filament v3/v4

### Proposed Spec Extensions
How would this preset configure `spec/spec.json`?
```json
{
  "project": {
    "presets": ["stripe-billing"]
  },
  "models": [
    // Proposed model or field extensions
  ],
  "integrations": [
    // Integration definitions
  ]
}
```

### Architectural & Security Invariants
- What edge cases or pitfalls must be addressed? (e.g., webhook signature verification, replay protection, customer ID mapping, tax calculation).
- What policies and Filament resources should be scaffolded?

### Willingness to Contribute
- [ ] Yes, I would like to submit a PR authoring this preset.
- [ ] No, I am requesting this feature for community consideration.
