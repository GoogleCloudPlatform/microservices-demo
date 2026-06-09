# Demo Flow Improvements & Suggestions

Based on reviewing your Argo WorkflowTemplate, Kyverno policy, and the complete setup, here are my suggestions:

## Suggested Rename: Workflow Parameters

The current naming of `dependency-policy-mode` values is confusing for a live audience:

| Current | Suggested | What it does |
|---------|-----------|--------------|
| `skip` | `skip-all` | Skip SBOM check AND skip signing |
| `skip-policy` | `no-policy` | Skip SBOM check, BUT still sign |
| `enforce` | (keep) | Run SBOM check, fail if blocked dep found |

When presenting, simpler names = less confusion. You could also use a separate parameter `signing-mode: enforce | skip` and keep `dependency-policy-mode: enforce | skip`.

## Stronger Demo: Add an Attestation-Checking Kyverno Rule

Currently your Kyverno policy only verifies the cosign **signature**. It doesn't check the **attestations** attached to the image. You could add a second validation rule that extracts the dependency-policy attestation and verifies the blocked version is NOT present.

This would create a much stronger chain:

1. **Build time**: Syft generates SBOM → fails if blocked dep found
2. **Signing time**: Attestation is created recording PASS (dep not found) and attached to the image
3. **Admission time**: Kyverno verifies BOTH the signature AND the attestation content

This way, even if the SBOM check is bypassed (or the blocked version changes between build and admission), Kyverno catches it.

**To implement this**, add to your ImageValidatingPolicy:

```yaml
validations:
  # Existing: verify signature
  - expression: images.containers.map(image, verifyImageSignatures(image, [attestors.cosignkey])).all(e, e > 0)
    message: paymentservice image signature verification failed
  # NEW: verify attestation
  - expression: |
      images.containers
        .map(image, verifyImageAttestations(image, [attestors.cosignkey], "custom"))
        .all(e, e.exists(att, att.predicate.data.service == "paymentservice"
                           && att.predicate.data.result == "pass"))
    message: paymentservice attestation check failed — dependency policy must pass
```

This means: verify that every container image has at least one `custom` attestation signed by our key, where the attestation says `result == "pass"`.

## Demo Flow Refined (Recommended Sequence)

With the attestation check added, the demo flows naturally:

### Run 1: `enforce` mode (SBOM check + signing)
- Build → SBOM → policy **fails** (blocked dep detected)
- Pipeline stops. Demo point: SBOM catches what's inside.
- **Show canary receiver** — reveal the postInstall already fired during build.

### Run 2: `skip-all` mode (no SBOM, no signing)
- Build → push → ArgoCD deploys
- Kyverno **denies** — "image signature verification failed"
- Demo point: Admission control catches unsigned images even if pipeline failed.

### Run 3: `no-policy` mode (no SBOM, but signs)
- Build → sign → push → ArgoCD deploys
- Kyverno **accepts** (signature valid)
- BUT if you had the attestation-checking rule, Kyverno would still **deny** because the attestation wouldn't be attached (or would show `result: skip`)
- Demo point: Even signed images aren't automatically trusted — attestations provide the proof.

## Ordering: Canary Reveal Timing

Put the canary reveal **before** showing the successful SBOM block. Here's why:

1. Build runs → you see it building
2. Show canary logs — "During that build, something happened"
3. Show postInstall.js — the attacker's code
4. Then show the SBOM check failing — "But at least we caught it"

This creates a tension arc: tension (something bad happened) → relief (but we caught it) → tension again (but the canary already fired).

## Other Tips

### Pre-stage these windows
- GitHub PR page (with the dep bump)
- Argo Workflows UI (running workflow)
- Canary receiver logs (pre-populated from a test run)
- Kyverno deny message (from the event or admission report)
- Terminal with `cosign verify-attestation` output

### Terminal commands to have ready
```bash
# Show signatures on registry
curl -s http://localhost:5000/v2/microservices-demo/paymentservice/referrers/sha256:DIGEST

# Show attestations
cosign verify-attestation --key cosign.pub host.docker.internal:5000/microservices-demo/paymentservice@sha256:DIGEST

# Show Kyverno events  
kubectl get events -n online-boutique --sort-by='.lastTimestamp' | grep -i paymentservice
```

### Timing note
At ~15 min, the demo is the bulk of the talk. Don't rush it. The slides before set context, the slides after reinforce. The demo IS the talk.
