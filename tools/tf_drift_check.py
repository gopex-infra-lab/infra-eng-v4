import json
import sys

# local_file entries are recreated on every fresh runner workspace, so they are never drift
IGNORED_TYPES = {"local_file"}

plan = json.load(sys.stdin)

changes = []
for c in plan.get("resource_changes", []):
    actions = c["change"]["actions"]
    if actions in (["no-op"], ["read"]):
        continue
    if c["type"] in IGNORED_TYPES:
        continue
    changes.append(c)

info = [d["address"] for d in plan.get("resource_drift", []) if d["type"] not in IGNORED_TYPES]
if info:
    print("INFO: refreshed values differ from the stored state for:", info)

if changes:
    print("DRIFT: configuration and real infrastructure differ:")
    for c in changes:
        print("  ", c["address"], c["change"]["actions"])
        if c["type"].startswith("proxmox_"):
            before = c["change"].get("before") or {}
            after = c["change"].get("after") or {}
            for k in sorted(set(before) | set(after)):
                if before.get(k) != after.get(k):
                    print("      ", k, ":", json.dumps(before.get(k))[:200], "->", json.dumps(after.get(k))[:200])
    sys.exit(1)

print("no drift (local files ignored)")
