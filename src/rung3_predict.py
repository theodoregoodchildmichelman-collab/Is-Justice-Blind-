"""Rung 3: ask a general AI model "How would Justice X vote?" for each of the 9 justices.

Every justice gets the same prompt (prompts/rung3/<version>.txt) and the same case materials;
only the justice's name changes. The case outcome is the majority of the 9 predicted votes.

Where the materials come from (D-009: outside material only):
  data/ot2026/packets/<docket>/manifest.json plus one text file per input (see
  docs/rung3_collection_plan.md). With --minimal, a case with no packet uses only the question
  presented and the lower-court summary from cases.csv (a fallback when a decision is close).

Who answers the prompt is a "runner", so it can be swapped later:
  manual  Claude answers inside a Claude Code session: `show` prints a prompt, `record` saves
          the answer. Uses the Pro subscription.
  cli     a fresh, tool-less Claude process per prompt (the Claude Code CLI in print mode).
          Uses the Pro subscription; needs a one-time `claude login`.
  api     placeholder for a pay-as-you-go API runner. Not built: no API budget agreed.

Saving and locking (D-014):
  predictions/rung3/<docket>.json is rewritten after every justice, so a run can stop and resume.
  Once all 9 are in, the file is committed to git and pushed to GitHub right away (D-031):
  GitHub's record of when it got the push is the proof the prediction came first. A committed
  file is never changed again: this script refuses to write to it.

Pipeline tests on past cases go to predictions/rung3_contaminated/ and are labeled
"contaminated": Claude has probably seen those decisions, so they are never accuracy numbers.

Run:
  .venv/bin/python src/rung3_predict.py status
  .venv/bin/python src/rung3_predict.py show <docket> <justice>          # manual runner
  .venv/bin/python src/rung3_predict.py record <docket> <justice> < answer.json
  .venv/bin/python src/rung3_predict.py run <docket> [<docket> ...] --runner cli
Put --contaminated before the command to work on a past case in data/dev_packets/ instead.
"""

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from rung1_baselines import CURRENT_COURT
from scdb import ROOT

PROMPT_VERSION = "v1"
# Stays False until the team approves the prompt (D-002). Until then only --contaminated runs work.
PROMPT_APPROVED = False
PROMPT_FILE = ROOT / f"prompts/rung3/{PROMPT_VERSION}.txt"
CASES_FILE = ROOT / "data/ot2026/cases.csv"
OUTCOMES_FILE = ROOT / "data/ot2026/outcomes.csv"
PACKETS = {False: ROOT / "data/ot2026/packets", True: ROOT / "data/dev_packets"}
OUT_DIRS = {False: ROOT / "predictions/rung3", True: ROOT / "predictions/rung3_contaminated"}

# How each justice is named in the prompt. Only this string differs between the 9 prompts.
JUSTICE_NAMES = {
    "JGRoberts": "Chief Justice John G. Roberts, Jr.",
    "CThomas": "Justice Clarence Thomas",
    "SAAlito": "Justice Samuel A. Alito, Jr.",
    "SSotomayor": "Justice Sonia Sotomayor",
    "EKagan": "Justice Elena Kagan",
    "NMGorsuch": "Justice Neil M. Gorsuch",
    "BMKavanaugh": "Justice Brett M. Kavanaugh",
    "ACBarrett": "Justice Amy Coney Barrett",
    "KBJackson": "Justice Ketanji Brown Jackson",
}

# Rough size limit for one case's materials, in tokens (1 token is about 4 characters).
MAX_PACKET_TOKENS = 60_000

CLI_MODEL = "claude-sonnet-5-5"
CLI_SYSTEM_PROMPT = "You are a careful legal analyst. Follow the user's instructions exactly."
CLI_BINARY = "claude"  # the Claude Code CLI; must be logged in with `claude login`


# ---------- case materials ----------

def load_case(docket: str, contaminated: bool, minimal: bool = False) -> dict:
    """Case details plus its materials as a list of {label, text}."""
    packet_dir = PACKETS[contaminated] / docket
    if (packet_dir / "manifest.json").exists():
        manifest = json.loads((packet_dir / "manifest.json").read_text())
        for item in manifest["inputs"]:
            item["text"] = (packet_dir / item["file"]).read_text().strip()
        case = manifest
    elif minimal and not contaminated:
        case = minimal_packet(docket)
    else:
        sys.exit(f"No packet for {docket} in {packet_dir} (use --minimal for the fallback)")

    tokens = sum(len(i["text"]) for i in case["inputs"]) // 4
    if tokens > MAX_PACKET_TOKENS:
        sys.exit(f"{docket}: materials are ~{tokens} tokens, over the {MAX_PACKET_TOKENS} limit. "
                 "Cut them as described in docs/rung3_collection_plan.md.")
    case["packet_tokens"] = tokens
    return case


def minimal_packet(docket: str) -> dict:
    cases = pd.read_csv(CASES_FILE, dtype=str).set_index("docket")
    if docket not in cases.index:
        sys.exit(f"{docket} is not in {CASES_FILE.name}")
    row = cases.loc[docket]
    if row.status != "rate":
        sys.exit(f"{docket} has status '{row.status}', not predicted")
    petitioner, _, respondent = row.case_name.partition(" v. ")
    return {
        "docket": docket, "case_name": row.case_name,
        "petitioner": petitioner, "respondent": respondent,
        "inputs": [
            {"label": "Question presented", "source": row.qp_source, "file": None,
             "text": row.question_presented},
            {"label": "Lower-court decision (summary)", "source": row.lower_court_link, "file": None,
             "text": f"{row.lower_court} ({row.lower_court_date}): {row.lower_court_summary}"},
        ],
    }


def render_prompt(case: dict, justice: str) -> str:
    materials = "\n\n".join(f"=== {i['label']} ===\n{i['text']}" for i in case["inputs"])
    return PROMPT_FILE.read_text().format(
        justice=JUSTICE_NAMES[justice], docket=case["docket"], case_name=case["case_name"],
        petitioner=case["petitioner"], respondent=case["respondent"],
        inputs_list="; ".join(i["label"] for i in case["inputs"]), materials=materials)


def prompt_hash() -> str:
    return hashlib.sha256(PROMPT_FILE.read_bytes()).hexdigest()[:12]


# ---------- runners ----------

class Runner:
    """Takes a prompt, returns the model's raw text answer."""
    name = "base"
    model = "unknown"

    def answer(self, prompt: str) -> str:
        raise NotImplementedError


class CliRunner(Runner):
    """A fresh Claude process per prompt: no tools, no web, no project files, no memory."""
    name = "cli"
    model = CLI_MODEL

    def answer(self, prompt: str) -> str:
        cmd = [CLI_BINARY, "-p", "--model", self.model, "--tools", "", "--no-session-persistence",
               "--strict-mcp-config", "--setting-sources", "", "--system-prompt", CLI_SYSTEM_PROMPT,
               "--output-format", "json"]
        # Run from an empty folder so no project file or memory can reach the model.
        with tempfile.TemporaryDirectory() as empty:
            done = subprocess.run(cmd, input=prompt, capture_output=True, text=True, cwd=empty,
                                  timeout=600)
        reply = json.loads(done.stdout)
        if reply.get("is_error"):
            raise RuntimeError(f"CLI error: {reply.get('result')}")
        return reply["result"]


class ApiRunner(Runner):
    """Placeholder: the same job through the Anthropic API. Needs an API key and an agreed budget."""
    name = "api"

    def answer(self, prompt: str) -> str:
        raise NotImplementedError("No API budget agreed yet (see MASTER.md open questions).")


RUNNERS = {"cli": CliRunner, "api": ApiRunner}


def parse_answer(text: str) -> dict:
    """Pull the JSON object out of the model's reply and check every field."""
    start, end = text.find("{"), text.rfind("}")
    if start < 0:
        raise ValueError(f"No JSON in answer: {text[:200]!r}")
    a = json.loads(text[start:end + 1])
    if a.get("vote") not in ("petitioner", "respondent"):
        raise ValueError(f"vote must be petitioner or respondent, got {a.get('vote')!r}")
    a["confidence"] = float(a["confidence"])
    if not 0.5 <= a["confidence"] <= 1:
        raise ValueError(f"confidence must be 0.5-1, got {a['confidence']}")
    if not isinstance(a.get("reason"), str) or not a["reason"].strip():
        raise ValueError("reason is missing")
    a["inputs_relied_on"] = list(a.get("inputs_relied_on", []))
    a["outcome_known"] = bool(a.get("outcome_known", False))
    return {k: a[k] for k in ["reason", "vote", "confidence", "inputs_relied_on", "outcome_known"]}


# ---------- saving and locking ----------

def out_path(docket: str, contaminated: bool) -> Path:
    return OUT_DIRS[contaminated] / f"{docket}.json"


def is_committed(path: Path) -> bool:
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", str(path)], cwd=ROOT,
                             capture_output=True)
    return tracked.returncode == 0


def already_decided(docket: str) -> bool:
    if not OUTCOMES_FILE.exists():
        return False
    return docket in set(pd.read_csv(OUTCOMES_FILE, dtype=str).docket)


def load_record(case: dict, runner: Runner, contaminated: bool) -> dict:
    """The saved file for this case, or a fresh one. Refuses anything locked or already decided."""
    path = out_path(case["docket"], contaminated)
    if not contaminated:
        if not PROMPT_APPROVED:
            sys.exit(f"Prompt {PROMPT_VERSION} is not approved yet: only --contaminated test runs allowed.")
        if is_committed(path):
            sys.exit(f"{path.relative_to(ROOT)} is committed and locked. Never change it.")
        if already_decided(case["docket"]):
            sys.exit(f"{case['docket']} is already decided: a prediction now would not count.")
    if path.exists():
        record = json.loads(path.read_text())
        for key, now in [("prompt_version", PROMPT_VERSION), ("prompt_sha256", prompt_hash()),
                         ("model", runner.model)]:
            if record[key] != now:
                sys.exit(f"{path.name} was started with {key}={record[key]}, now {now}. "
                         "Finish it with the same setup or delete the uncommitted file.")
        return record
    return {
        "docket": case["docket"], "case_name": case["case_name"], "rung": 3,
        "contaminated": contaminated,
        "prompt_version": PROMPT_VERSION, "prompt_sha256": prompt_hash(),
        "runner": runner.name, "model": runner.model,
        "inputs_provided": [{"label": i["label"], "source": i["source"]} for i in case["inputs"]],
        "packet_tokens": case["packet_tokens"],
        "justices": {},
    }


def save(record: dict, contaminated: bool) -> Path:
    votes = [j["vote"] for j in record["justices"].values()]
    if len(votes) == len(CURRENT_COURT):
        pet = votes.count("petitioner")
        record["case_prediction"] = {"winner": "petitioner" if pet > len(votes) / 2 else "respondent",
                                     "votes_petitioner": pet, "votes_respondent": len(votes) - pet}
    path = out_path(record["docket"], contaminated)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2) + "\n")
    return path


def commit(path: Path, record: dict) -> None:
    """Lock a finished case in git. The commit time is the proof it came before the decision."""
    if len(record["justices"]) < len(CURRENT_COURT):
        return
    subprocess.run(["git", "add", str(path)], cwd=ROOT, check=True)
    msg = (f"Rung 3 prediction: {record['docket']} {record['case_name']} "
           f"(prompt {record['prompt_version']}, {record['model']})")
    subprocess.run(["git", "commit", "-m", msg, "--", str(path)], cwd=ROOT, check=True)
    print(f"Committed and locked {path.relative_to(ROOT)}")
    push()


def push() -> None:
    """Send local commits to GitHub. If that fails, the local lock still stands; push by hand soon."""
    done = subprocess.run(["git", "push", "origin", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    if done.returncode == 0:
        print("Pushed to GitHub")
    else:
        print(f"WARNING: push to GitHub failed, run `git push` as soon as you can.\n{done.stderr.strip()}")


def is_pushed(path: Path) -> bool:
    """True if GitHub's copy of main (as last fetched or pushed) has this file."""
    rel = str(path.relative_to(ROOT))
    return subprocess.run(["git", "cat-file", "-e", f"origin/main:{rel}"], cwd=ROOT,
                          capture_output=True).returncode == 0


def add_answer(record: dict, justice: str, answer: dict) -> None:
    answer["predicted_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    record["justices"][justice] = answer


# ---------- commands ----------

def cmd_run(args, runner: Runner) -> None:
    for docket in args.dockets:
        case = load_case(docket, args.contaminated, args.minimal)
        record = load_record(case, runner, args.contaminated)
        for justice in CURRENT_COURT:
            if justice in record["justices"]:
                continue  # resume: this one is already saved
            answer = parse_answer(runner.answer(render_prompt(case, justice)))
            add_answer(record, justice, answer)
            save(record, args.contaminated)
            print(f"{docket} {justice}: {answer['vote']} ({answer['confidence']:.2f})")
        if not args.contaminated:
            commit(out_path(docket, False), record)


class ManualRunner(Runner):
    name = "manual"

    def __init__(self, model: str):
        self.model = model


def cmd_show(args) -> None:
    print(render_prompt(load_case(args.docket, args.contaminated, args.minimal), args.justice))


def cmd_record(args) -> None:
    case = load_case(args.docket, args.contaminated, args.minimal)
    record = load_record(case, ManualRunner(args.model), args.contaminated)
    if args.justice in record["justices"]:
        sys.exit(f"{args.justice} is already recorded for {args.docket}")
    add_answer(record, args.justice, parse_answer(sys.stdin.read()))
    path = save(record, args.contaminated)
    print(f"Saved {args.justice} to {path.relative_to(ROOT)} ({len(record['justices'])}/9)")
    if not args.contaminated:
        commit(path, record)


def cmd_status(args) -> None:
    cases = pd.read_csv(CASES_FILE, dtype=str)
    for docket in cases.loc[cases.status == "rate", "docket"]:
        path = out_path(docket, False)
        done = len(json.loads(path.read_text())["justices"]) if path.exists() else 0
        lock = ("locked, pushed" if is_pushed(path) else "locked, NOT PUSHED") if is_committed(path) else ""
        packet = "packet" if (PACKETS[False] / docket / "manifest.json").exists() else "no packet"
        print(f"{docket:8} {done}/9  {packet:9} {lock}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--contaminated", action="store_true", help="past case for pipeline tests only")
    p.add_argument("--minimal", action="store_true", help="no packet: use only the QP and lower-court summary")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    s = sub.add_parser("show")
    s.add_argument("docket")
    s.add_argument("justice", choices=CURRENT_COURT)
    r = sub.add_parser("record")
    r.add_argument("docket")
    r.add_argument("justice", choices=CURRENT_COURT)
    r.add_argument("--model", default="claude-opus-5-5", help="model answering in the session")
    u = sub.add_parser("run")
    u.add_argument("dockets", nargs="+")
    u.add_argument("--runner", choices=RUNNERS, default="cli")
    args = p.parse_args()

    if args.cmd == "status":
        cmd_status(args)
    elif args.cmd == "show":
        cmd_show(args)
    elif args.cmd == "record":
        cmd_record(args)
    else:
        cmd_run(args, RUNNERS[args.runner]())


if __name__ == "__main__":
    main()
