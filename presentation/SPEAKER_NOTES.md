# Speaker Notes — Rebuilding Trust in the Software Supply Chain on Kubernetes
## CNCF Meetup Talk (~30 min)

---

## OPENING (~5 min)

### Slide 1: Title (~30 sec)

"Good evening everyone. Today I want to talk about something that affects every single one of us who builds software on Kubernetes — trust in our supply chain. My talk is called 'Rebuilding Trust in the Software Supply Chain on Kubernetes.'"

[Let the title breathe for a moment.]

### Slide 2: About Me (~1 min)

"I'm Kavish — I'm a DevOps Architect at Bertelsmann / Arvato Systems in Malaysia. I spend my days building and securing Kubernetes platforms in production — containerization strategy, Kubernetes operators, DevSecOps pipelines. I'm CKA certified and I've been in this space for a while.

The reason I'm here today is that this topic — supply chain security — stopped being theoretical for me when the Shai-Hulud attacks hit. Let me tell you about them."

### Slide 3: The Attack That Shook npm (~1.5 min)

[Point to the left card first.]

"In September 2025, researchers identified a self-replicating worm hiding inside npm packages. They called it Shai-Hulud — after the sandworm from Dune. Why? Because it burrowed deep into the supply chain and grew.

It compromised over 500 packages. It injected malicious postInstall scripts that exfiltrated CI/CD secrets. It even injected GitHub Actions workflows into repositories for persistence. By the time CISA issued an alert, thousands of credentials had already been compromised.

[Point to the right card.]

And then in May — just a few weeks ago — Mini Shai-Hulud struck again. 317 packages in a single wave. These weren't obscure packages — things like size-sensor with 4.2 million weekly downloads, echarts-for-react, @antv/scale."

### Slide 4: How Supply Chain Attacks Happen (~1 min)

"So how does this actually happen? Let me walk through the chain.

[Walk through each step visually.]

It starts with a developer doing something perfectly routine — updating a dependency. The malicious version has already been published to npm. CI/CD pulls it automatically. And then the postInstall script executes during npm install — that's the hook. No code in your repo, no compromised credentials. One routine dependency bump, and your entire supply chain is poisoned."

### Slide 5: The Damage (~1 min)

[Point to the big numbers.]

"500+ packages compromised in the initial campaign. One of the affected packages — @ctrl/tinycolor — had 2.2 million weekly downloads. And researchers estimated that through transitive dependencies, roughly half the npm ecosystem could be reached.

[Point to the list below.]

What was at risk? CI/CD secrets. Cloud credentials. GitHub Actions workflows injected with malicious pipelines. Downstream users deploying compromised code to production. And most importantly — trust. Trust in the open source ecosystem, eroded one update at a time."

### Slide 6: From npm to Your Cluster (~1 min)

[Walk through the chain from left to right.]

"And here's why this matters to us as a Kubernetes community. The attack chain doesn't stop at the developer machine. It extends all the way into your cluster.

Malicious npm package → postInstall runs during build → container image is built with the payload inside → image gets pushed to your registry → deployed to Kubernetes.

[Gesture to the question box.]

So the questions we have to ask ourselves are: How do we know what's inside that image? How do we trust it wasn't tampered with? And most importantly — how do we enforce that trust at admission time?"

---

## DEMO (~15 min)

[Say:] "Let me show you what this looks like in practice."

### Demo Setup Context

"I have a microservices application running on this cluster — it's the Google microservices-demo. I've set up a complete pipeline using CNCF tools: Argo Workflows for CI, Argo CD for GitOps, Syft for SBOMs, Cosign for signing, and Kyverno for admission control.

I'm running a malicious dependency scenario. I have a private npm package called @kavish-p/build-canary. Version 1.0.0 is benign. Version 1.0.3 is the one with the postInstall payload."

### Demo Step 1: The PR (~1 min)

**Action:** Show a GitHub PR that bumps @kavish-p/build-canary from 1.0.0 to 1.0.3.

**Key point to make:**
"This is a dependency bump PR. Looks completely routine. A developer or a bot opened it. Nothing in this PR suggests anything malicious — the code diff is just a version number change."

**Approve and merge the PR.**

### Demo Step 2: The Argo Workflow (~2 min)

**Action:** Show the Argo Workflow UI running `build-paymentservice-trusted`.

**Key points:**
- "Argo Workflows picks up the change and runs our pipeline"
- Walk through the DAG steps as they execute:
  1. **Clone** — pulls the repo
  2. **Build and push** — builds the container image with `buildctl`, pushes to the registry. During npm install, the malicious postInstall runs. In this demo, it sends a hit to a canary receiver endpoint.
  3. **Resolve digest** — gets the SHA256 digest
  4. **Generate SBOM** — Syft scans the source directory and produces a CycloneDX JSON SBOM
  5. **Check dependency policy** — checks if @kavish-p/build-canary@1.0.3 is in the SBOM

**Action:** The workflow will fail at the dependency check step.

**Say:** "The SBOM caught it. Syft found @kavish-p/build-canary@1.0.3 in the dependency tree, and our policy blocks it."

### Demo Step 3: The Canary Receiver (~1.5 min)

**Action:** Before revealing, say: "But here's the thing — the build already happened. npm install already ran. And during that npm install..."

**Action:** Show the canary receiver logs. Show the hit that was recorded during the build.

**Say:** "I had a canary receiver running in the cluster. During the build, the postInstall script sent an HTTP request to it. In this demo it's a harmless ping. But in a real attack, that same mechanism could exfiltrate the NPM_TOKEN, GitHub tokens, any secret mounted in the build environment."

**Action:** Show the malicious dependency's postInstall.js to the audience.

**Say:** "This is the actual postInstall script. It's not complex — that's the scary part. A few lines of JavaScript that runs during npm install. No one reviews npm dependencies the way they review code."

### Demo Step 4: SBOM Approach (~1.5 min)

**Action:** Run the workflow again with `dependency-policy-mode: enforce`.

[This was what happened in step 2. Recap it.]

**Say:** "So what can we do? Generating an SBOM and checking it at build time gives us visibility. Syft creates a CycloneDX JSON of every dependency. We can check for specific versions, known malicious packages, anything we want.

But — and this is important — the build already happened. The SBOM check prevents the compromised image from reaching production, but the payload already executed. For preventing the actual damage from a Shai-Hulud-style attack, something like `npm ci --ignore-scripts` would prevent the postInstall from running entirely. SBOMs are about detection and visibility, not prevention."

**This is the honest moment in the talk. Own it. It makes everything more credible.**

### Demo Step 5: Skip SBOM, Skip Signing (~2 min)

**Action:** Run the workflow with `dependency-policy-mode: skip`. This skips both the SBOM check AND the signing step.

**Say:** "Now let me show what happens when we skip the checks. This time, the workflow runs without the dependency policy check, and also without signing the image. The image gets built, pushed, and Argo Workflows updates the kustomization in the repo with the new digest."

**Action:** Show the ArgoCD UI detecting the change.

**Say:** "ArgoCD picks up the change. It sees the new image digest in the kustomization, and it tries to deploy."

**Action:** Show the deployment failing. Show the error message:
`admission webhook "ivpol.validate.kyverno.svc-fail" denied the request: Policy verify-paymentservice-signature failed: paymentservice image signature verification failed`

**Say with emphasis:** "This is the key moment. Kyverno's ImageValidatingPolicy checked the image signature at admission time. The image wasn't signed by our trusted key, so it was rejected. The pod never ran.

This is admission control in action. Even though the image made it through the build pipeline, through the registry, through GitOps — Kyverno was the last line of defense. And it worked."

### Demo Step 6: Skip Check, Still Sign (~2 min)

**Action:** Run the workflow with `dependency-policy-mode: skip-policy`. This skips the dependency check but still signs and attests.

**Say:** "Now you might ask: what if the attacker also signed the image? What if the malicious dependency is in a signed image?"

[Pause for effect.]

"And that's a fair question. Because signing alone isn't enough. Let me show you what happens when the image IS signed but still contains the malicious dependency."

**Action:** Show the workflow running with `skip-policy` — SBOM check is skipped, but signing and attestation happen. The image gets deployed because it's signed.

**Say:** "The image deployed. Because it was signed with our key. And now we have a signed image running in production with a malicious dependency."

**Transition to the concepts slides:** "So what's the takeaway here? One tool isn't enough. Signing catches unsigned images. SBOMs catch known bad dependencies. Admission control is the enforcement point. But you need all of them working together."

### Demo Step 7 (Optional): cosign verify-attestation

**If time permits:** "I can also show the attestations attached to this image. With `cosign verify-attestation`, we can see what claims were made about this image — the SBOM hash, the provenance, the policy results. All stored as OCI artifacts alongside the image."

**If time is tight, skip this and move to slides.**

---

## CLOSING (~10 min)

### Slide 7: Key Concepts (~2.5 min)

"I want to quickly walk through the key concepts that make up this defense stack.

[Point to each concept as you explain it.]

- **SBOM** — A machine-readable inventory of every component in your image. CycloneDX or SPDX format. Know what's inside.
- **Provenance** — Cryptographic proof of where, when, and how an artifact was built. SLSA framework.
- **Signatures** — Digital signatures verify the image was signed by a trusted key. Prevents tampering.
- **Admission Control** — The enforcement point. Policy engines like Kyverno check signatures before any pod runs.
- **Attestations** — Cryptographically signed metadata attached to images. SBOM, policy results, provenance — all as OCI artifacts.
- **Traceability** — From source commit to running pod. Every step recorded and verifiable."

### Slide 8: Defense in Depth (~2.5 min)

[Explain each layer, pointing to it.]

**Build Time:** "At build time, we generate SBOMs with Syft. We check dependency policies — is that version of a package known to be malicious? We create provenance records. And we sign and attest the image with Cosign."

**GitOps:** "GitOps gives us an audit trail. The image is referenced by immutable digest, not a mutable tag. ArgoCD syncs the desired state."

**Runtime:** "And at runtime, Kyverno's ImageValidatingPolicy verifies the signature at pod creation time. Unsigned or tampered images are rejected before they ever run."

[Point to the bottom quote.]

"And this is the philosophy I want to leave you with: Supply chain security isn't about preventing every compromise. That's impossible. It's about making compromises detectable, making trust explicit, and making policy enforceable."

### Slide 9: CNCF Projects (~2 min)

[Quick run through each project.]

"All the tools I showed today are CNCF projects or in the CNCF ecosystem:

- **Argo Workflows** — Multi-step pipeline orchestration
- **Argo CD** — GitOps deployment
- **Kyverno** — Kubernetes-native policy engine
- **Sigstore / Cosign** — Signing and attestation
- **Syft** — SBOM generation
- **cert-manager** — Certificate lifecycle for webhooks

The beautiful thing is — this whole stack is open source, cloud-native, and integrates natively with Kubernetes."

### Slide 10: Key Takeaways (~1 min)

[Speak directly to the audience.]

"Three things I want you to take away from this talk:

First: Supply chain attacks are real and they're happening right now. Shai-Hulud wasn't a theoretical exercise — it compromised 500+ packages.

Second: Trust must be earned at every layer. Build time, registry, admission, runtime. No single tool is enough.

Third: The CNCF ecosystem gives us the building blocks. SBOMs, signatures, provenance, admission control — they're all available now, open source, and production-ready.

The question isn't whether you can implement this. The question is whether you can afford not to."

[Beat.]

"Thank you. Questions?"

---

## PRESENTATION TIPS

### Timing guide
- Opening (slides 1-6): ~5-6 min
- Demo: ~13-15 min (don't rush, this is the star)
- Closing (slides 7-10): ~7-8 min
- Buffer: ~2 min for questions/transitions

### Demo tips
- **Pre-stage everything** — Have the PR open, Argo Workflows UI ready, Kyverno logs ready
- **Don't type commands live** — Use terminal recordings or pre-opened windows
- **Have a backup plan** — If the workflow takes too long, have screenshots ready
- **The canary reveal is your hook** — Draw it out. Say "something happened during the build" before showing what
- **The Kyverno denial is your climax** — Let the error message speak for itself. Pause after showing it.

### Handling questions
**"Doesn't `npm ci --ignore-scripts` fix this?"**
Yes! For Shai-Hulud specifically, that would prevent postInstall execution. But it breaks legitimate packages that need postInstall. And it doesn't help with malicious package contents in the code itself. Defense in depth.

**"Why not use OPA/Gatekeeper instead of Kyverno?"**
Both work! Kyverno has native image verification support (verifyImageSignatures) which made the demo simpler. OPA/Gatekeeper with external data would also work.

**"How do you manage the Cosign keys?"**
In production, use a KMS provider (AWS KMS, Google Cloud KMS, Azure Key Vault) instead of raw keys. Cosign supports KMS-based key management natively.

**"Does this work with Helm?"**
Yes. Kyverno policies apply to pods regardless of how they're created — Helm, operators, raw YAML. And you can add image verification policies at the cluster level.
