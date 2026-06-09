const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");

// ── Icons ──
const { FaUserCircle, FaShieldAlt, FaBoxOpen, FaSignature, FaLock, FaServer,
         FaProjectDiagram, FaStar, FaSkull, FaExclamationTriangle, FaArrowRight,
         FaCheckCircle, FaTimesCircle, FaLayerGroup, FaTools, FaKey, FaTags,
         FaClipboardList, FaShip } = require("react-icons/fa");

function renderIconSvg(IconComponent, color = "#000000", size = 256) {
  return ReactDOMServer.renderToStaticMarkup(
    React.createElement(IconComponent, { color, size: String(size) })
  );
}
async function iconToBase64Png(IconComponent, color, size = 256) {
  const svg = renderIconSvg(IconComponent, color, size);
  const pngBuffer = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + pngBuffer.toString("base64");
}

// ── Palette ──
const C = {
  darkBg:    "0F172A",
  darkText:  "E2E8F0",
  accent:    "0891B2",
  accent2:   "0284C7",
  warmAccent:"F59E0B",
  danger:    "DC2626",
  success:   "10B981",
  contentBg: "FFFFFF",
  cardBg:    "F1F5F9",
  text:      "1E293B",
  textMuted: "64748B",
  border:    "CBD5E1",
  white:     "FFFFFF",
};

const FONT_TITLE = "Calibri";
const FONT_BODY  = "Calibri";

// ── Helpers ──
const mkShadow = () => ({ type: "outer", color: "000000", blur: 6, offset: 2, angle: 135, opacity: 0.10 });

function addSectionTitle(slide, title) {
  slide.addShape("rect", { x: 0, y: 0, w: 10, h: 1.1, fill: { color: C.darkBg } });
  slide.addText(title, {
    x: 0.8, y: 0, w: 8.4, h: 1.1,
    fontSize: 24, fontFace: FONT_TITLE, color: C.white, valign: "middle", bold: true,
    margin: 0,
  });
}

function addCard(slide, x, y, w, h, opts = {}) {
  slide.addShape("rect", {
    x, y, w, h,
    fill: { color: opts.fill || C.cardBg },
    shadow: opts.shadow !== false ? mkShadow() : undefined,
    rectRadius: opts.radius || 0,
  });
}

// ── Build ──
async function build() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9";
  pres.author = "Kavish Punchoo";
  pres.title = "Rebuilding Trust in the Software Supply Chain on Kubernetes";
  pres.subject = "CNCF Meetup Talk";

  // Pre-render icons
  const icons = {};
  const iconDefs = [
    ["user", FaUserCircle, "#0891B2"],
    ["shield", FaShieldAlt, "#10B981"],
    ["box", FaBoxOpen, "#0891B2"],
    ["signature", FaSignature, "#F59E0B"],
    ["lock", FaLock, "#10B981"],
    ["server", FaServer, "#0284C7"],
    ["diagram", FaProjectDiagram, "#0891B2"],
    ["star", FaStar, "#F59E0B"],
    ["skull", FaSkull, "#DC2626"],
    ["warning", FaExclamationTriangle, "#F59E0B"],
    ["arrow", FaArrowRight, "#0891B2"],
    ["check", FaCheckCircle, "#10B981"],
    ["times", FaTimesCircle, "#DC2626"],
    ["layers", FaLayerGroup, "#0891B2"],
    ["tools", FaTools, "#64748B"],
    ["key", FaKey, "#F59E0B"],
    ["tags", FaTags, "#0891B2"],
    ["clipboard", FaClipboardList, "#0891B2"],
    ["ship", FaShip, "#0891B2"],
  ];
  for (const [name, comp, color] of iconDefs) {
    icons[name] = await iconToBase64Png(comp, "#" + color);
  }

  // ════════════════════════════════════════════
  // SLIDE 1: TITLE
  // ════════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.darkBg };
    // Decorative accent line
    s.addShape("rect", { x: 0.8, y: 1.2, w: 0.08, h: 2.2, fill: { color: C.accent } });
    s.addText("Rebuilding Trust\nin the Software Supply Chain\non Kubernetes", {
      x: 1.2, y: 1.2, w: 8, h: 2.4,
      fontSize: 34, fontFace: FONT_TITLE, color: C.white, bold: true, valign: "top",
      lineSpacingMultiple: 1.1,
      margin: 0,
    });
    s.addText("Kavish Punchoo  |  DevOps Architect", {
      x: 1.2, y: 3.8, w: 8, h: 0.5,
      fontSize: 14, fontFace: FONT_BODY, color: C.accent, valign: "middle", margin: 0,
    });
    s.addText("CNCF Meetup  •  June 2026", {
      x: 1.2, y: 4.3, w: 8, h: 0.4,
      fontSize: 12, fontFace: FONT_BODY, color: C.textMuted, valign: "middle", margin: 0,
    });
  }

  // ════════════════════════════════════════════
  // SLIDE 2: ABOUT ME
  // ════════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.contentBg };
    addSectionTitle(s, "About Me");

    addCard(s, 0.6, 1.5, 8.8, 3.6);

    s.addImage({ data: icons.user, x: 0.9, y: 1.8, w: 0.55, h: 0.55 });

    s.addText([
      { text: "Kavish Punchoo", options: { bold: true, fontSize: 20, color: C.text, breakLine: true } },
      { text: "DevOps Architect — Bertelsmann / Arvato Systems Malaysia", options: { fontSize: 13, color: C.accent, breakLine: true } },
      { text: "", options: { fontSize: 8, breakLine: true } },
      { text: "Building and securing Kubernetes platforms in production. CKA certified. ", options: { fontSize: 13, color: C.text, breakLine: true } },
      { text: "Currently focused on containerization strategy across 10+ teams, Kubernetes", options: { fontSize: 13, color: C.text, breakLine: true } },
      { text: "operator development, and DevSecOps pipeline standardization.", options: { fontSize: 13, color: C.text, breakLine: true } },
    ], { x: 1.0, y: 1.8, w: 7.6, h: 2.0, valign: "top", fontFace: FONT_BODY, margin: 0 });

    // Quick stat boxes
    const stats = [
      { label: "CKA", sub: "Certified", x: 1.0 },
      { label: "10+", sub: "Teams", x: 4.0 },
      { label: "60%", sub: "Fewer incidents", x: 7.0 },
    ];
    for (const st of stats) {
      addCard(s, st.x, 4.0, 2.2, 0.9, { fill: C.darkBg });
      s.addText(st.label, { x: st.x, y: 4.0, w: 2.2, h: 0.55, fontSize: 20, fontFace: FONT_TITLE, color: C.accent, bold: true, align: "center", valign: "bottom", margin: 0 });
      s.addText(st.sub, { x: st.x, y: 4.5, w: 2.2, h: 0.35, fontSize: 11, fontFace: FONT_BODY, color: C.textMuted, align: "center", valign: "top", margin: 0 });
    }
  }

  // ════════════════════════════════════════════
  // SLIDE 3: SHAI-HULUD ATTACKS
  // ════════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.contentBg };
    addSectionTitle(s, "The Attack That Shook npm");

    // Left card: Shai-Hulud
    addCard(s, 0.6, 1.4, 4.2, 3.8, { fill: C.cardBg });
    s.addImage({ data: icons.skull, x: 1.0, y: 1.7, w: 0.4, h: 0.4 });
    s.addText("Shai-Hulud", { x: 1.0, y: 2.2, w: 3.4, h: 0.35, fontSize: 16, fontFace: FONT_TITLE, color: C.danger, bold: true, margin: 0 });
    s.addText([
      { text: "Self-replicating worm hidden inside", options: { breakLine: true } },
      { text: "npm packages", options: { bold: true, breakLine: true } },
      { text: "", options: { fontSize: 6, breakLine: true } },
      { text: "Compromised 500+ packages", options: { breakLine: true } },
      { text: "Injected malicious postInstall scripts", options: { breakLine: true } },
      { text: "Exfiltrated CI/CD secrets & credentials", options: { breakLine: true } },
      { text: "Injected GitHub Actions workflows", options: { breakLine: true } },
      { text: "", options: { fontSize: 6, breakLine: true } },
      { text: "Sep 2025 — CISA alert", options: { italic: true, color: C.textMuted, fontSize: 11, breakLine: true } },
      { text: "Nov 2025 — Shai-Hulud 2.0", options: { italic: true, color: C.textMuted, fontSize: 11 } },
    ], { x: 1.0, y: 2.6, w: 3.6, h: 2.4, fontSize: 12, fontFace: FONT_BODY, color: C.text, valign: "top", margin: 0 });

    // Right card: Mini Shai-Hulud
    addCard(s, 5.2, 1.4, 4.2, 3.8, { fill: C.cardBg });
    s.addImage({ data: icons.warning, x: 5.6, y: 1.7, w: 0.4, h: 0.4 });
    s.addText("Mini Shai-Hulud", { x: 5.6, y: 2.2, w: 3.4, h: 0.35, fontSize: 16, fontFace: FONT_TITLE, color: C.warmAccent, bold: true, margin: 0 });
    s.addText([
      { text: "317 packages compromised in a", options: { breakLine: true } },
      { text: "single wave", options: { bold: true, breakLine: true } },
      { text: "", options: { fontSize: 6, breakLine: true } },
      { text: "Affected popular packages:", options: { breakLine: true } },
      { text: "  size-sensor (4.2M downloads/mo)", options: { breakLine: true } },
      { text: "  echarts-for-react (3.8M)", options: { breakLine: true } },
      { text: "  @antv/scale (2.2M)", options: { breakLine: true } },
      { text: "", options: { fontSize: 6, breakLine: true } },
      { text: "May 2026 — latest wave", options: { italic: true, color: C.textMuted, fontSize: 11 } },
    ], { x: 5.6, y: 2.6, w: 3.4, h: 2.4, fontSize: 12, fontFace: FONT_BODY, color: C.text, valign: "top", margin: 0 });
  }

  // ════════════════════════════════════════════
  // SLIDE 4: HOW IT HAPPENS
  // ════════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.contentBg };
    addSectionTitle(s, "How Supply Chain Attacks Happen");

    // Flow diagram: 4 steps
    const steps = [
      { label: "Developer updates\na dependency", icon: icons.user, x: 0.6 },
      { label: "Malicious version\npublished to npm", icon: icons.ship, x: 2.8 },
      { label: "CI/CD pulls it\nautomatically", icon: icons.tools, x: 5.0 },
      { label: "postInstall executes\npayload", icon: icons.skull, x: 7.2 },
    ];
    for (const st of steps) {
      addCard(s, st.x, 1.5, 2.0, 2.0);
      s.addImage({ data: st.icon, x: st.x + 0.75, y: 1.7, w: 0.5, h: 0.5 });
      s.addText(st.label, { x: st.x, y: 2.3, w: 2.0, h: 0.9, fontSize: 12, fontFace: FONT_BODY, color: C.text, align: "center", valign: "top", margin: 0 });
      if (st.x < 7.2) {
        s.addImage({ data: icons.arrow, x: st.x + 2.0, y: 2.25, w: 0.5, h: 0.5 });
      }
    }

    // Bottom emphasis
    addCard(s, 0.6, 3.8, 8.8, 1.4, { fill: "FEF3C7" });
    s.addText([
      { text: "No malicious code in the repo. No compromised credentials.", options: { bold: true, breakLine: true, color: "92400E" } },
      { text: "One routine dependency bump — and the entire supply chain is poisoned.", options: { color: "92400E" } },
    ], { x: 1.0, y: 3.95, w: 8.0, h: 1.0, fontSize: 13, fontFace: FONT_BODY, valign: "middle", margin: 0 });
  }

  // ════════════════════════════════════════════
  // SLIDE 5: THE IMPACT
  // ════════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.contentBg };
    addSectionTitle(s, "The Damage");

    // Big number callouts
    const impacts = [
      { num: "500+", label: "Packages compromised\nin single campaign", x: 0.6, color: C.danger },
      { num: "2.2M", label: "Weekly downloads of one\naffected package (@ctrl/tinycolor)", x: 3.6, color: C.warmAccent },
      { num: "~50%", label: "of npm ecosystem could\nbe reached transitively", x: 6.6, color: C.accent },
    ];
    for (const imp of impacts) {
      addCard(s, imp.x, 1.5, 2.8, 1.6);
      s.addText(imp.num, { x: imp.x, y: 1.6, w: 2.8, h: 0.7, fontSize: 32, fontFace: FONT_TITLE, color: imp.color, bold: true, align: "center", valign: "bottom", margin: 0 });
      s.addText(imp.label, { x: imp.x, y: 2.3, w: 2.8, h: 0.7, fontSize: 11, fontFace: FONT_BODY, color: C.text, align: "center", valign: "top", margin: 0 });
    }

    // Consequences list
    addCard(s, 0.6, 3.5, 8.8, 1.8);
    s.addText("What was at risk:", { x: 1.0, y: 3.65, w: 8.0, h: 0.35, fontSize: 14, fontFace: FONT_TITLE, color: C.danger, bold: true, margin: 0 });
    s.addText([
      { text: "CI/CD secrets and cloud credentials exfiltrated to attacker-controlled servers", options: { bullet: true, breakLine: true, fontSize: 12 } },
      { text: "GitHub Actions workflows injected with malicious pipelines for persistence", options: { bullet: true, breakLine: true, fontSize: 12 } },
      { text: "Downstream users unknowingly deploying compromised code to production", options: { bullet: true, breakLine: true, fontSize: 12 } },
      { text: "Trust in the open source ecosystem eroded — one update at a time", options: { bullet: true, fontSize: 12 } },
    ], { x: 1.0, y: 4.0, w: 8.0, h: 1.2, fontFace: FONT_BODY, color: C.text, valign: "top", margin: 0 });
  }

  // ════════════════════════════════════════════
  // SLIDE 6: FROM NPM TO KUBERNETES
  // ════════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.contentBg };
    addSectionTitle(s, "From npm to Your Cluster");

    s.addText("The attack chain doesn't stop at the developer machine.", {
      x: 0.8, y: 1.4, w: 8.4, h: 0.4, fontSize: 14, fontFace: FONT_BODY, color: C.textMuted, italic: true, margin: 0,
    });

    // Chain — 5 cards fitting within 10" slide
    const chainW = 1.5, chainGap = 0.3, chainStart = 0.65;
    const chainPositions = [0, 1, 2, 3, 4].map(i => chainStart + i * (chainW + chainGap));
    const chain = [
      { label: "Malicious\nnpm package", icon: icons.ship },
      { label: "npm install\npostInstall runs", icon: icons.box },
      { label: "Container image\nbuilt with payload", icon: icons.server },
      { label: "Image pushed\nto registry", icon: icons.tags },
      { label: "Deployed to\nKubernetes", icon: icons.diagram },
    ];
    for (let i = 0; i < chain.length; i++) {
      const cx = chainPositions[i];
      addCard(s, cx, 2.0, chainW, 1.7);
      s.addImage({ data: chain[i].icon, x: cx + (chainW - 0.5) / 2, y: 2.2, w: 0.5, h: 0.5 });
      s.addText(chain[i].label, { x: cx, y: 2.8, w: chainW, h: 0.8, fontSize: 11, fontFace: FONT_BODY, color: C.text, align: "center", valign: "top", margin: 0 });
      if (i < chain.length - 1) {
        s.addImage({ data: icons.arrow, x: cx + chainW, y: 2.55, w: chainGap, h: 0.35 });
      }
    }

    // Key question
    addCard(s, 0.6, 4.1, 8.8, 1.2, { fill: C.darkBg });
    s.addText([
      { text: "How do we know what's inside that image?", options: { bold: true, breakLine: true, color: C.white, fontSize: 16 } },
      { text: "How do we trust it wasn't tampered with? How do we enforce that trust at admission time?", options: { color: C.textMuted, fontSize: 13 } },
    ], { x: 1.0, y: 4.2, w: 8.0, h: 1.0, fontFace: FONT_BODY, valign: "middle", margin: 0 });
  }

  // ════════════════════════════════════════════
  // NO SLIDES FOR DEMO — SPEAKER NOTES IN RESULT
  // ════════════════════════════════════════════

  // ════════════════════════════════════════════
  // SLIDE 7: KEY CONCEPTS
  // ════════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.contentBg };
    addSectionTitle(s, "Key Concepts");

    const concepts = [
      { title: "SBOM", body: "Software Bill of Materials —\na machine-readable inventory\nof every component in your image", icon: icons.clipboard, x: 0.8 },
      { title: "Provenance", body: "Cryptographic proof of where,\nwhen, and how an artifact\nwas built", icon: icons.key, x: 3.65 },
      { title: "Signatures", body: "Digital signatures verify the\nimage was signed by a trusted\nkey — prevents tampering", icon: icons.signature, x: 6.5 },
      { title: "Admission Control", body: "Kubernetes policy engine\nthat enforces trust before\nany pod can run", icon: icons.lock, x: 0.8, y: 3.35 },
      { title: "Attestations", body: "Cryptographically signed\nmetadata (SBOM, policy\nresults) attached to images", icon: icons.tags, x: 3.65, y: 3.35 },
      { title: "Traceability", body: "From source commit to\nrunning pod — every step\nis recorded and verifiable", icon: icons.diagram, x: 6.5, y: 3.35 },
    ];

    for (const c of concepts) {
      const cy = c.y || 1.5;
      addCard(s, c.x, cy, 2.7, 1.6);
      s.addImage({ data: c.icon, x: c.x + 0.15, y: cy + 0.15, w: 0.35, h: 0.35 });
      s.addText(c.title, { x: c.x + 0.6, y: cy + 0.15, w: 2.0, h: 0.35, fontSize: 14, fontFace: FONT_TITLE, color: C.accent, bold: true, valign: "middle", margin: 0 });
      s.addText(c.body, { x: c.x + 0.15, y: cy + 0.6, w: 2.4, h: 0.8, fontSize: 11, fontFace: FONT_BODY, color: C.text, valign: "top", margin: 0 });
    }
  }

  // ════════════════════════════════════════════
  // SLIDE 8: THE LAYERED APPROACH
  // ════════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.contentBg };
    addSectionTitle(s, "Defense in Depth");

    // Build time
    addCard(s, 0.6, 1.4, 4.2, 1.6, { fill: C.darkBg });
    s.addText("BUILD TIME", { x: 0.8, y: 1.5, w: 3.8, h: 0.3, fontSize: 11, fontFace: FONT_TITLE, color: C.accent, bold: true, margin: 0, charSpacing: 3 });
    s.addText([
      { text: "SBOM generation (Syft)", options: { bullet: true, breakLine: true } },
      { text: "Dependency policy checks", options: { bullet: true, breakLine: true } },
      { text: "Provenance creation", options: { bullet: true, breakLine: true } },
      { text: "Signing & attestation (Cosign)", options: { bullet: true } },
    ], { x: 0.8, y: 1.8, w: 3.8, h: 1.1, fontSize: 12, fontFace: FONT_BODY, color: C.white, valign: "top", margin: 0 });

    // GitOps time
    addCard(s, 5.2, 1.4, 4.2, 1.6, { fill: C.darkBg });
    s.addText("GITOPS", { x: 5.4, y: 1.5, w: 3.8, h: 0.3, fontSize: 11, fontFace: FONT_TITLE, color: C.warmAccent, bold: true, margin: 0, charSpacing: 3 });
    s.addText([
      { text: "Git as single source of truth", options: { bullet: true, breakLine: true } },
      { text: "ArgoCD syncs desired state", options: { bullet: true, breakLine: true } },
      { text: "Immutable image tags (digests)", options: { bullet: true, breakLine: true } },
      { text: "Audit trail via git history", options: { bullet: true } },
    ], { x: 5.4, y: 1.8, w: 3.8, h: 1.1, fontSize: 12, fontFace: FONT_BODY, color: C.white, valign: "top", margin: 0 });

    // Runtime
    addCard(s, 0.6, 3.3, 8.8, 1.8, { fill: C.cardBg });
    s.addText("RUNTIME — ADMISSION CONTROL", { x: 0.8, y: 3.4, w: 8.4, h: 0.3, fontSize: 11, fontFace: FONT_TITLE, color: C.danger, bold: true, margin: 0, charSpacing: 2 });
    s.addText([
      { text: "Kyverno ImageValidatingPolicy verifies image signatures at pod creation", options: { bullet: true, breakLine: true, fontSize: 13 } },
      { text: "Unsigned or tampered images are rejected before they ever run", options: { bullet: true, breakLine: true, fontSize: 13 } },
      { text: "Attestations can be verified at admission time for deeper policy checks", options: { bullet: true, fontSize: 13 } },
    ], { x: 0.8, y: 3.75, w: 8.4, h: 1.2, fontFace: FONT_BODY, color: C.text, valign: "top", margin: 0 });

    // Bottom separator
    s.addShape("rect", { x: 0.6, y: 5.2, w: 8.8, h: 0.03, fill: { color: C.accent } });
    s.addText([
      { text: "Supply chain security isn't about preventing every compromise. It's about making compromises ", options: { fontSize: 11, fontFace: FONT_BODY, color: C.textMuted, italic: true } },
      { text: "detectable, making trust explicit, and making policy enforceable.", options: { fontSize: 11, fontFace: FONT_BODY, color: C.accent, bold: true } },
    ], {
      x: 0.8, y: 5.25, w: 8.4, h: 0.3, valign: "middle", margin: 0,
    });
  }

  // ════════════════════════════════════════════
  // SLIDE 9: CNCF PROJECTS
  // ════════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.contentBg };
    addSectionTitle(s, "CNCF Projects in This Stack");

    const projects = [
      { name: "Argo Workflows", role: "Pipeline orchestration", desc: "Multi-step build pipeline with\nSBOM generation, policy checks,\nsigning, and GitOps update", icon: icons.diagram, x: 0.8 },
      { name: "Argo CD", role: "GitOps deployment", desc: "Syncs desired state from git.\nRolls out signed images\nor rejects unsigned ones", icon: icons.ship, x: 3.65 },
      { name: "Kyverno", role: "Admission control", desc: "ImageValidatingPolicy verifies\ncosign signatures at pod\ncreation time", icon: icons.shield, x: 6.5, y: 1.5 },
      { name: "Sigstore / Cosign", role: "Signing & attestation", desc: "Signs container images.\nAttaches attestations (SBOM,\npolicies, provenance)", icon: icons.signature, x: 0.8, y: 3.35 },
      { name: "Syft (Anchore)", role: "SBOM generation", desc: "Generates CycloneDX SBOM\nfrom source. Enables dependency\npolicy enforcement", icon: icons.clipboard, x: 3.65, y: 3.35 },
      { name: "cert-manager", role: "Certificate lifecycle", desc: "Manages TLS certificates\nfor webhooks and\ninternal services", icon: icons.key, x: 6.5, y: 3.35 },
    ];

    for (const p of projects) {
      const py = p.y || 1.5;
      addCard(s, p.x, py, 2.7, 1.6);
      s.addImage({ data: p.icon, x: p.x + 0.15, y: py + 0.15, w: 0.35, h: 0.35 });
      s.addText(p.name, { x: p.x + 0.6, y: py + 0.1, w: 2.0, h: 0.3, fontSize: 14, fontFace: FONT_TITLE, color: C.accent, bold: true, valign: "middle", margin: 0 });
      s.addText(p.role, { x: p.x + 0.6, y: py + 0.4, w: 2.0, h: 0.25, fontSize: 10, fontFace: FONT_BODY, color: C.textMuted, italic: true, valign: "middle", margin: 0 });
      s.addText(p.desc, { x: p.x + 0.15, y: py + 0.7, w: 2.4, h: 0.7, fontSize: 11, fontFace: FONT_BODY, color: C.text, valign: "top", margin: 0 });
    }
  }

  // ════════════════════════════════════════════
  // SLIDE 10: KEY TAKEAWAYS (CLOSING)
  // ════════════════════════════════════════════
  {
    const s = pres.addSlide();
    s.background = { color: C.darkBg };
    s.addShape("rect", { x: 0.8, y: 0.8, w: 0.08, h: 3.0, fill: { color: C.accent } });

    s.addText("Key Takeaways", {
      x: 1.2, y: 0.8, w: 8, h: 0.5,
      fontSize: 24, fontFace: FONT_TITLE, color: C.white, bold: true, valign: "middle", margin: 0,
    });

    const takeawayCards = [
      { text: "Supply chain attacks are real\nand they're hitting the npm\necosystem right now", x: 0.8 },
      { text: "Trust must be earned at\nevery layer — build, registry,\nadmission, runtime", x: 3.6 },
      { text: "CNCF tools give you the\nbuilding blocks to make\ntrust explicit and enforceable", x: 6.4 },
    ];
    for (const tc of takeawayCards) {
      addCard(s, tc.x, 1.6, 2.6, 2.0, { fill: "1E293B" });
      s.addText(tc.text, { x: tc.x + 0.2, y: 1.75, w: 2.2, h: 1.7, fontSize: 12, fontFace: FONT_BODY, color: C.white, valign: "top", margin: 0 });
    }

    s.addText([
      { text: "Thank you", options: { fontSize: 28, bold: true, color: C.white, breakLine: true } },
      { text: "Questions?", options: { fontSize: 16, color: C.accent, breakLine: true } },
      { text: "", options: { fontSize: 10 } },
      { text: "github.com/kavish-p   |   kavish.punchoo@gmail.com", options: { fontSize: 11, color: C.textMuted } },
    ], { x: 0.8, y: 3.9, w: 8.4, h: 1.5, fontFace: FONT_BODY, align: "center", valign: "middle", margin: 0 });
  }

  // ── Write ──
  await pres.writeFile({ fileName: "/home/kavish/PERSO/microservices-demo/presentation/Rebuilding-Trust-Supply-Chain-Kubernetes.pptx" });
  console.log("Done: presentation written.");
}

build().catch(e => { console.error(e); process.exit(1); });
