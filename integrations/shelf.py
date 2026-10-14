#!/usr/bin/env python3
"""The shared shelf: registry of vendor adapters plus a workflow runner.

Usage:
  python3 -m integrations.shelf list
  python3 -m integrations.shelf run onboarding
  python3 -m integrations.shelf run order_to_cash
"""

import json
import sys

from integrations import ADAPTERS, AdapterError


def get_shelf():
    """Metadata for every vendor on the shelf."""
    return [cls().describe() for cls in ADAPTERS]


def by_ticker(ticker):
    for cls in ADAPTERS:
        if cls.ticker == ticker:
            return cls()
    raise AdapterError("no adapter for ticker %s" % ticker)


def run_step(step):
    """Execute one workflow step: {adapter, action}. Prints the vendor."""
    adapter = by_ticker(step["adapter"])
    result = adapter.run()
    line = {"step": step["step"], "action": step["action"],
            "ticker": result["ticker"], "vendor": result["vendor"],
            "category": result["category"], "product": result["product"],
            "mode": result["mode"], "result": result["result"]}
    print("[%s] %s handled by %s (%s)" % (result["mode"].upper(),
                                          step["action"], result["vendor"],
                                          result["ticker"]))
    return line


def run_workflow(workflow):
    """Run a workflow dict {name, description, steps}. Returns transcript."""
    print("Workflow: %s" % workflow["name"])
    print("%s" % workflow["description"])
    print("-" * 60)
    transcript = {"name": workflow["name"],
                  "description": workflow["description"], "steps": []}
    for step in workflow["steps"]:
        transcript["steps"].append(run_step(step))
    vendors = sorted({s["ticker"] for s in transcript["steps"]})
    modes = sorted({s["mode"] for s in transcript["steps"]})
    print("-" * 60)
    print("Done: %d steps, %d vendors (%s), modes: %s"
          % (len(transcript["steps"]), len(vendors),
             ", ".join(vendors), ", ".join(modes)))
    transcript["vendors"] = vendors
    transcript["modes"] = modes
    return transcript


def main(argv):
    from workflows import onboarding, order_to_cash
    workflows = {"onboarding": onboarding.WORKFLOW,
                 "order_to_cash": order_to_cash.WORKFLOW}
    if len(argv) < 2 or argv[1] not in ("list", "run"):
        print(__doc__)
        return 1
    if argv[1] == "list":
        print(json.dumps(get_shelf(), indent=2))
        return 0
    name = argv[2] if len(argv) > 2 else ""
    if name not in workflows:
        print("unknown workflow: %s (choose: %s)"
              % (name, ", ".join(workflows)))
        return 1
    run_workflow(workflows[name])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
