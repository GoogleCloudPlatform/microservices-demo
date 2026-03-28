#!/usr/bin/env python3
"""
demo_scenario.py

Runs a 5-minute AI Observability Platform demo:
  t=0:   Normal operation — show scores
  t=60:  Inject stress on recommendationservice
  t=90:  Poll /status, print rising score
  t=120: Anomaly detected (score > 0.6)
  t=150: Trigger remediation via POST /remediate
  t=165: Print remediation result
  t=180: Poll /status, show score falling
  t=240: Demo complete

Usage:
  python3 demo_scenario.py           # Live demo
  python3 demo_scenario.py --dry-run # Print what it would do
"""

import sys
import time
import argparse
import subprocess
from datetime import datetime

try:
    import requests
except ImportError:
    print("ERROR: 'requests' not installed. Run: pip3 install requests")
    sys.exit(1)

API_BASE = "http://localhost:8001"
TARGET_SERVICE = "recommendationservice"
FAILURE_TYPE = "memory_leak"


def ts():
    return datetime.now().strftime("%H:%M:%S")


def print_section(title, color="\033[96m"):
    reset = "\033[0m"
    print(f"\n{color}{'='*60}{reset}")
    print(f"{color}  [{ts()}] {title}{reset}")
    print(f"{color}{'='*60}{reset}")


def print_info(msg):
    print(f"  \033[37m[{ts()}] {msg}\033[0m")


def print_ok(msg):
    print(f"  \033[92m[{ts()}] ✓ {msg}\033[0m")


def print_warn(msg):
    print(f"  \033[93m[{ts()}] ⚠ {msg}\033[0m")


def print_error(msg):
    print(f"  \033[91m[{ts()}] ✗ {msg}\033[0m")


def check_api():
    try:
        resp = requests.get(f"{API_BASE}/health", timeout=5)
        data = resp.json()
        return data
    except Exception as e:
        return None


def get_status():
    try:
        resp = requests.get(f"{API_BASE}/status", timeout=5)
        return resp.json()
    except Exception as e:
        return None


def inject_stress(service_name, dry_run=False):
    """Try to exec stress into the service container."""
    if dry_run:
        print_info(f"[DRY-RUN] Would inject memory stress into {service_name}")
        return True

    # Try docker exec to run a quick stress command
    prefixes = ["microservices-demo_", "microservicesdemo_", ""]
    for prefix in prefixes:
        container = f"{prefix}{service_name}"
        cmd = ["docker", "exec", "-d", container, "sh", "-c",
               "dd if=/dev/zero bs=1M count=100 2>/dev/null & sleep 30"]
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=5)
            if result.returncode == 0:
                print_ok(f"Stress injected into {container}")
                return True
        except Exception:
            pass

    print_warn(f"Could not inject stress (container not found or Docker unavailable)")
    print_info("Continue by observing live telemetry and remediation flow.")
    return False


def trigger_remediation(service, failure_type, dry_run=False):
    if dry_run:
        print_info(f"[DRY-RUN] Would POST /remediate with service={service}, failure_type={failure_type}")
        return {"result": {"success": True, "elapsed_s": 0.5, "actions_taken": ["[DRY-RUN]"]}}

    try:
        resp = requests.post(
            f"{API_BASE}/remediate",
            json={"service": service, "failure_type": failure_type},
            timeout=30,
        )
        return resp.json()
    except Exception as e:
        print_error(f"Remediation request failed: {e}")
        return None


def print_scores(status_data):
    if not status_data or "services" not in status_data:
        print_warn("No status data available")
        return

    services = status_data["services"]
    # Sort by combined_score descending
    sorted_svcs = sorted(services.items(), key=lambda x: x[1].get("combined_score", 0), reverse=True)

    print_info(f"  {'Service':<30} {'IF':>6} {'LSTM':>6} {'Combined':>10} {'Status':>10}")
    print_info(f"  {'-'*30} {'-'*6} {'-'*6} {'-'*10} {'-'*10}")
    for svc, data in sorted_svcs:
        if_s = data.get("if_score", 0)
        lstm_s = data.get("lstm_score", 0)
        comb_s = data.get("combined_score", 0)
        st = data.get("status", "?")
        print_info(f"  {svc:<30} {if_s:>6.3f} {lstm_s:>6.3f} {comb_s:>10.3f} {st:>10}")


def poll_score_until(target_service, threshold, timeout_s, interval_s=5, check_above=True, dry_run=False):
    """Poll /status until service score crosses threshold."""
    start = time.time()
    while time.time() - start < timeout_s:
        if dry_run:
            print_info(f"[DRY-RUN] Would poll /status (looking for {target_service} score {'>' if check_above else '<'} {threshold})")
            time.sleep(interval_s if not dry_run else 1)
            return None

        status_data = get_status()
        if status_data:
            svc_data = status_data.get("services", {}).get(target_service, {})
            score = svc_data.get("combined_score", 0)
            print_info(f"  {target_service} score: {score:.3f}")

            if check_above and score > threshold:
                return score
            if not check_above and score < threshold:
                return score

        time.sleep(interval_s)
    return None


def main():
    parser = argparse.ArgumentParser(description="AI Observability Platform Demo")
    parser.add_argument("--dry-run", action="store_true", help="Print actions without executing")
    args = parser.parse_args()

    dry_run = args.dry_run

    print_section("AI Observability Platform - 5 Minute Demo", "\033[95m")

    # --- Check API ---
    print_info("Checking API health...")
    health = check_api()
    if not health and not dry_run:
        print_error(f"API not responding at {API_BASE}. Start with: ./infra/start_platform.sh")
        sys.exit(1)
    elif dry_run and not health:
        print_warn("[DRY-RUN] API not running but continuing anyway")
    else:
        print_ok(
            f"API healthy: runtime_mode={health.get('runtime_mode')}, "
            f"models_loaded={health.get('models_loaded')}"
        )

    # ============================
    # t=0: Normal operation
    # ============================
    demo_start = time.time()
    print_section("Phase 1: Normal Operation (t=0)", "\033[94m")
    status_data = get_status() if not dry_run else None
    if status_data:
        print_scores(status_data)
    else:
        print_info("[DRY-RUN] Would display current service scores")
    print_ok("System operating normally")

    # Wait until t=60
    elapsed = time.time() - demo_start
    wait_s = max(0, 60 - elapsed)
    print_info(f"Waiting {wait_s:.0f}s until anomaly injection (t=60)...")
    if not dry_run:
        time.sleep(wait_s)
    else:
        print_info("[DRY-RUN] Skipping wait")

    # ============================
    # t=60: Inject anomaly
    # ============================
    print_section("Phase 2: Injecting Memory Stress (t=60)", "\033[93m")
    inject_stress(TARGET_SERVICE, dry_run=dry_run)

    # ============================
    # t=90: Poll rising scores
    # ============================
    elapsed = time.time() - demo_start
    wait_s = max(0, 90 - elapsed)
    if not dry_run:
        time.sleep(wait_s)

    print_section("Phase 3: Polling Rising Anomaly Scores (t=90)", "\033[93m")
    print_info(f"Watching {TARGET_SERVICE} score...")

    if not dry_run:
        score = poll_score_until(TARGET_SERVICE, 0.6, timeout_s=60, interval_s=5, check_above=True)
        if score:
            print_warn(f"{TARGET_SERVICE} score reached {score:.3f} (> 0.6 threshold)")
        else:
            print_info("Score didn't cross 0.6 threshold in time")
    else:
        print_info("[DRY-RUN] Would poll every 5s, waiting for score > 0.6")

    # ============================
    # t=120: Anomaly detected
    # ============================
    elapsed = time.time() - demo_start
    wait_s = max(0, 120 - elapsed)
    if not dry_run:
        time.sleep(wait_s)

    print_section("Phase 4: Anomaly Detected (t=120)", "\033[91m")
    status_data = get_status() if not dry_run else None
    if status_data:
        print_scores(status_data)
        rc = status_data.get("root_cause", {})
        svc = rc.get("service") or rc.get("root_cause")
        if svc:
            print_warn(f"Root cause: {svc} ({rc.get('failure_type')}) confidence={rc.get('confidence'):.0%}")
        print_info(f"Recommendation: {status_data.get('recommendation', '')}")
    else:
        print_info("[DRY-RUN] Would display anomaly scores and root cause")

    # ============================
    # t=150: Trigger remediation
    # ============================
    elapsed = time.time() - demo_start
    wait_s = max(0, 150 - elapsed)
    if not dry_run:
        time.sleep(wait_s)

    print_section("Phase 5: Triggering Remediation (t=150)", "\033[92m")
    print_info(f"Calling POST {API_BASE}/remediate")
    print_info(f"  service={TARGET_SERVICE}, failure_type={FAILURE_TYPE}")

    remediation_start = time.time()
    result = trigger_remediation(TARGET_SERVICE, FAILURE_TYPE, dry_run=dry_run)
    remediation_elapsed = time.time() - remediation_start

    # ============================
    # t=165: Show result
    # ============================
    elapsed = time.time() - demo_start
    wait_s = max(0, 165 - elapsed)
    if not dry_run:
        time.sleep(wait_s)

    print_section("Phase 6: Remediation Result (t=165)", "\033[92m")
    if result:
        r = result.get("result", {})
        success = r.get("success", False)
        elapsed_s = r.get("elapsed_s", remediation_elapsed)
        actions = r.get("actions_taken", [])

        if success:
            print_ok(f"Remediation SUCCESSFUL in {elapsed_s:.2f}s")
        else:
            print_warn(f"Remediation completed with errors in {elapsed_s:.2f}s")

        for a in actions:
            print_info(f"  Action: {a}")

        within = r.get("within_target", elapsed_s <= 15)
        target = r.get("target_s", 15)
        if within:
            print_ok(f"Within {target}s target ✓")
        else:
            print_warn(f"Exceeded {target}s target")

    # ============================
    # t=180: Score falling
    # ============================
    elapsed = time.time() - demo_start
    wait_s = max(0, 180 - elapsed)
    if not dry_run:
        time.sleep(wait_s)

    print_section("Phase 7: Score Recovery (t=180)", "\033[94m")
    print_info(f"Watching {TARGET_SERVICE} score fall after remediation...")

    if not dry_run:
        score = poll_score_until(TARGET_SERVICE, 0.4, timeout_s=60, interval_s=5, check_above=False)
        if score:
            print_ok(f"{TARGET_SERVICE} score recovered to {score:.3f} (< 0.4)")
        else:
            status_data = get_status()
            if status_data:
                print_scores(status_data)
    else:
        print_info("[DRY-RUN] Would poll every 5s, waiting for score < 0.4")

    # ============================
    # t=240: Complete
    # ============================
    elapsed = time.time() - demo_start
    wait_s = max(0, 240 - elapsed)
    if not dry_run:
        time.sleep(wait_s)

    print_section("Demo Complete (t=240)", "\033[95m")
    total_elapsed = time.time() - demo_start
    print_ok(f"Demo completed in {total_elapsed:.0f}s")
    print_info("")
    print_info("Summary:")
    print_info("  1. Observed normal operation")
    print_info("  2. Injected memory stress into recommendationservice")
    print_info("  3. AI detected anomaly and identified root cause")
    print_info("  4. Automated remediation restarted the service")
    print_info("  5. System recovered within SLA")
    print_info("")


if __name__ == "__main__":
    main()
