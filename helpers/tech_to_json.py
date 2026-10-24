import glob
import json
import logging
import os
import sys

import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TACTICS_ENUM = {
    "Reconnaissance": "TA01",
    "Resource Development": "TA02",
    "Initial Access": "TA03",
    "Execution": "TA04",
    "Persistence": "TA05",
    "Privilege Escalation": "TA06",
    "Defense Evasion": "TA07",
    "Credential Access": "TA08",
    "Lateral Movement": "TA09",
    "Collection": "TA10",
    "Exfiltration": "TA11",
    "Impact": "TA12",
}

SITE_BASE = os.environ.get("OSCAR_SITE_BASE", "https://poisonedpipeline.com")


def main(path, dest="matrix.json"):
    j = {}

    for filename in glob.glob(os.path.join(path, "*.yaml")):
        logger.info("Reading file: %s", filename)
        with open(filename, "r") as f:
            y = yaml.load(f, Loader=yaml.SafeLoader)

        tactic = y["tactic"]
        if tactic not in j:
            j[tactic] = {
                "items": [],
                "amount": 0,
                "tooltip": tactic,
                "tacticid": TACTICS_ENUM.get(tactic, ""),
            }

        y.setdefault("subTechniques", [])
        sub = [] if y["subTechniques"] == [None] else (y["subTechniques"] or [])

        item = {
            "id": y["id"],
            "tags": y.get("realm") or [],
            "name": y["summary"],
            "tooltip": y["summary"],
            "url": f"{SITE_BASE}/techniques/{y['id']}.html",
            "description": y.get("description") or "",
            "subTechniques": sub,
            "subTechniquesAmount": len(sub),
        }
        j[tactic]["items"].append(item)
        j[tactic]["amount"] += 1

    j = dict(sorted(j.items(), key=lambda item: item[1].get("tacticid") or item[0]))
    for tactic in j:
        j[tactic]["items"] = sorted(j[tactic]["items"], key=lambda k: k["id"])
        j[tactic]["amount"] = len(j[tactic]["items"])

    with open(dest, "w") as f:
        json.dump(j, f, indent=4)
        f.write("\n")


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "content/oscar/techniques"
    dest = sys.argv[2] if len(sys.argv) > 2 else "matrix.json"
    main(src, dest)
