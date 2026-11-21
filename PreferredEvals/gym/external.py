"""Launch plans for pinned, external evaluation frameworks.

Native agents and graders remain in their upstream harness. A plan never
claims success or grants access to private tasks. Execution is opt-in and
requires the runner already installed locally.

Prime 0.4.1: vf-run, verifiers.v1, in-process light runner.
Thinking Machines Inkling Verify: python -m inkling_verify.benchmarks.*.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

SUPPORTED = {
    "prime-v041": {"type": "prime_v1", "release": "v0.4.1", "runner": "vf-run",
                   "requires": "installed taskset and harness plugins; local subprocess runtime"},
    "inkling-deepswe": {"type":"inkling", "module":"deepswe", "requires":"Linux x86-64, rootless Podman, pinned images"},
    "inkling-hle": {"type":"inkling", "module":"hle", "requires":"prepared HLE dataset and selected judge model"},
    "inkling-niah": {"type":"inkling", "module":"niah", "requires":"prepared dataset, pinned tokenizer"},
    "inkling-mmmu-pro": {"type":"inkling", "module":"mmmu_pro", "requires":"prepared images; optional Podman tools"},
    "inkling-mmau": {"type":"inkling", "module":"mmau", "requires":"audio-capable model endpoint"},
}


CODE_HARNESSES = {"bash", "mini_swe_agent", "terminus_2", "opencode", "codex", "claude_code", "openclaw",
                  "hermes_agent", "kimi_code", "pi", "prime_agent", "rlm", "deepseek", "browser_use"}


def plan(profile, *, model, base_url, out, limit=4, rollouts=1, taskset=None,
         runtime="subprocess", judge_model=None, subset=None, tokenizer=None,
         api_key_env="PREFERRED_EVALS_API_KEY", harness=None, max_tokens=None, temperature=None,
         data_dir=None, concurrency=None, extra_args=None):
    if profile not in SUPPORTED:
        raise ValueError("unknown external profile: " + str(profile))
    if not model or not base_url:
        raise ValueError("model and base_url required")
    uri = urlparse(base_url)
    if uri.scheme not in ("http", "https") or not uri.hostname:
        raise ValueError("OpenAI-compatible base URL must be http(s)")
    if type(limit) is not int or not 1 <= limit <= 100000:
        raise ValueError("limit must be in 1..100000")
    if type(rollouts) is not int or not 1 <= rollouts <= 100:
        raise ValueError("rollouts must be in 1..100")
    if runtime not in ("subprocess", "docker", "prime"):
        raise ValueError("runtime must be subprocess, docker or prime")
    if max_tokens is not None and (type(max_tokens) is not int or max_tokens < 1):
        raise ValueError("max_tokens must be a positive integer")
    if concurrency is not None and (type(concurrency) is not int or concurrency < 1):
        raise ValueError("concurrency must be a positive integer")
    meta = SUPPORTED[profile]
    prepare = None
    notes = [meta["requires"], "Upstream native runner owns scoring; preserve its original traces and version hash.",
             "Model endpoint must be reachable from the executing host/runtime."]
    if meta["type"] == "inkling":
        mod = "inkling_verify.benchmarks." + meta["module"]
        prepare = [sys.executable, "-m", mod, "prepare"]
        if meta["module"] == "niah":
            if not tokenizer:
                notes.append("NIAH prepare requires --tokenizer for meaningful prompts")
                prepare = None
            else:
                prepare += ["--tokenizer", tokenizer]
        if meta["module"] == "mmmu_pro" and subset:
            prepare += ["--subset", subset]
        command = [sys.executable, "-m", mod, "run", "--api", "openai-completions",
                   "--model", model, "--base-url", base_url,
                   "--api-key-env", api_key_env, "--limit", str(limit),
                   "--samples-per-problem", str(rollouts), "--output", str(out)]
        if subset and meta["module"] in ("mmmu_pro", "mmau"):
            command += ["--subset", subset]
        if data_dir:
            command += ["--data-dir", str(data_dir)]
            if prepare:
                prepare += ["--data-dir", str(data_dir)]
        if max_tokens is not None:
            command += ["--max-output-tokens", str(max_tokens)]
        if temperature is not None:
            command += ["--temperature", str(temperature)]
        if concurrency is not None:
            command += ["--concurrency", str(concurrency)]
        if judge_model and meta["module"] == "hle":
            command += ["--judge-model", judge_model]
        if meta["module"] == "hle" and judge_model is None:
            notes.append("HLE default model-self-judging is a fragile metric; specify --judge-model for scientific use")
    else:
        if not taskset:
            raise ValueError("Prime 0.4.1 requires explicit installed --taskset id")
        if subset or judge_model or tokenizer:
            raise ValueError("Prime profile does not accept Inkling-specific flags")
        if not harness or not isinstance(harness, str):
            raise ValueError("Prime 0.4.1 needs an explicit harness: 'taskset' (the taskset's own default) "
                             "or a harness id such as 'null' (chat only)")
        command = ["vf-run", "--env.taskset.id", taskset, "-m", model,
                   "-n", str(limit), "-r", str(rollouts),
                   "--env.agent.runtime.type", runtime]
        if harness != "taskset":
            command += ["--env.agent.harness.id", harness]
        command += ["--client.base_url", base_url,
                   "--client.api_key_var", api_key_env,
                   "--output_dir", str(out)]
        if max_tokens is not None:
            command += ["--sampling.max_tokens", str(max_tokens)]
        if temperature is not None:
            command += ["--sampling.temperature", str(temperature)]
        if concurrency is not None:
            command += ["-c", str(concurrency)]
        if data_dir:
            raise ValueError("Prime profile does not take --data-dir")
        prepare = command + ["--dry-run"]
        notes.append("vf-run v0.4.1 is local/in-process; full hosted Prime evaluations use prime-rl")
        notes.append("verifiers 0.4.1 resolves an unpinned harness to the taskset's exported harness, and to its "
                     "bash harness (a shell for the model) when the taskset exports none; pin 'null' for "
                     "chat-only tasksets such as gsm8k.")
        if harness == "taskset":
            notes.append("Harness left to the taskset default: check the resolved run.json for the harness id.")
        if harness in CODE_HARNESSES and runtime == "subprocess":
            notes.append(f"Harness {harness} executes model-written code in a local subprocess, not a sandbox.")
        if runtime == "prime":
            notes.append("Paid Prime runtime requested; requires --allow-paid on execution")
    if extra_args:
        if not all(isinstance(a, str) for a in extra_args):
            raise ValueError("extra native arguments must be strings")
        command = command + list(extra_args)
        notes.append("Extra native arguments appended verbatim: " + " ".join(extra_args))
    return {"schema":"preferred-evals/native-plan-v1", "profile":profile, "model":model,
            "url_host":uri.hostname, "release":meta.get("release","pin upstream Inkling commit"), "runtime":runtime,
            "command":command, "prepare_command":prepare, "notes":notes,
            "dry_run_only":True}


def run(plan_data, *, workdir, execute=False, do_prepare=False, allow_paid=False,
        allow_downloads=False, allow_remote=False):
    if not execute:
        return {"executed":False, "plan":plan_data}
    if plan_data["profile"] == "prime-v041" and plan_data.get("runtime") == "prime" and not allow_paid:
        raise ValueError("paid Prime runtime requires --allow-paid")
    host = plan_data["url_host"]
    if host.lower() not in ("localhost", "127.0.0.1", "::1") and not allow_remote:
        raise ValueError("remote model endpoint requires --allow-remote")
    cmd = plan_data["command"]
    executable = cmd[0]
    if executable != sys.executable and shutil.which(executable) is None:
        raise FileNotFoundError(f"native evaluation runner not installed: {executable}")
    cwd = str(Path(workdir).resolve())
    if do_prepare:
        if plan_data["profile"] != "prime-v041" and not allow_downloads:
            raise ValueError("data preparation may download task data; pass --allow-downloads")
        if not plan_data["prepare_command"]:
            raise ValueError("this profile needs additional preparation parameters")
        before = subprocess.run(plan_data["prepare_command"], cwd=cwd, check=False)
        if before.returncode != 0:
            return {"executed":True,"stage":"prepare","returncode":before.returncode}
    after = subprocess.run(cmd, cwd=cwd, check=False)
    return {"executed":True,"stage":"run","returncode":after.returncode,
            "result_scoring":"inspect native saved traces and summary; CLI exit is not a task-success score"}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--list", action="store_true", help="Print supported native eval profiles")
    ap.add_argument("--profile", choices=SUPPORTED)
    ap.add_argument("--model")
    ap.add_argument("--base-url", default="http://127.0.0.1:18127/v1")
    ap.add_argument("--out", type=Path, default=Path("preferred-evals-results"))
    ap.add_argument("--limit", type=int, default=4)
    ap.add_argument("--rollouts", type=int, default=1)
    ap.add_argument("--taskset", help="Installed Prime v0.4.1 taskset ID, e.g. gsm8k")
    ap.add_argument("--runtime", choices=("subprocess","docker","prime"), default="subprocess")
    ap.add_argument("--harness",
                    help="Prime profile, required: 'taskset' (the taskset's own harness) or a harness id "
                         "('null' is chat only; bash and agent harnesses run model-written code)")
    ap.add_argument("--max-tokens", type=int, help="output token budget passed to the native runner")
    ap.add_argument("--temperature", type=float)
    ap.add_argument("--data-dir", type=Path, help="Inkling prepared-data directory")
    ap.add_argument("--concurrency", type=int)
    ap.add_argument("--native-arg", action="append", default=[],
                    help="argument appended verbatim to the native command (repeatable; use --native-arg=--flag)")
    ap.add_argument("--judge-model")
    ap.add_argument("--subset")
    ap.add_argument("--tokenizer")
    ap.add_argument("--api-key-env", default="PREFERRED_EVALS_API_KEY")
    ap.add_argument("--workdir", type=Path, default=Path("."))
    ap.add_argument("--write-plan", type=Path)
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--prepare", action="store_true")
    ap.add_argument("--allow-downloads", action="store_true")
    ap.add_argument("--allow-paid", action="store_true")
    ap.add_argument("--allow-remote", action="store_true")
    args = ap.parse_args()
    if args.list:
        print(json.dumps(SUPPORTED,indent=2,sort_keys=True))
        return
    if not args.profile or not args.model:
        ap.error("--profile and --model required unless --list")
    p=plan(args.profile,model=args.model,base_url=args.base_url,out=args.out,
           limit=args.limit,rollouts=args.rollouts,taskset=args.taskset,
           runtime=args.runtime,judge_model=args.judge_model,subset=args.subset,
           tokenizer=args.tokenizer,api_key_env=args.api_key_env,harness=args.harness,
           max_tokens=args.max_tokens,temperature=args.temperature,data_dir=args.data_dir,
           concurrency=args.concurrency,extra_args=args.native_arg)
    if args.write_plan:
        args.write_plan.parent.mkdir(parents=True,exist_ok=True)
        args.write_plan.write_text(json.dumps(p,indent=2,sort_keys=True)+"\n")
    result=run(p,workdir=args.workdir,execute=args.execute,do_prepare=args.prepare,
               allow_paid=args.allow_paid,allow_downloads=args.allow_downloads,
               allow_remote=args.allow_remote)
    print(json.dumps(result,indent=2,sort_keys=True))
    if args.execute and result.get("returncode",0):
        raise SystemExit(result["returncode"])


if __name__=="__main__":
    main()
