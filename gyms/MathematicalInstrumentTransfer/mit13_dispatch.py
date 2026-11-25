"""MIT-13 blind dispatcher for a llama-server OpenAI-compatible endpoint.

Sends only the prompt text in a fresh single-turn chat under one fixed system prompt. Reads prompts.jsonl
(id, prompt, max_tokens); never reads private.jsonl. Resumable: appends one response row per finished id."""
import argparse, json, re, time
from pathlib import Path
from random import Random
from urllib import request

SYSTEM = 'You are a careful mathematician. Reply with a single JSON object and nothing else.'
CHAT_OVERHEAD = 24  # template tokens added around system + user text


def http_post(base_url, path, payload, timeout=1800):
    req = request.Request(base_url.rstrip('/') + path, json.dumps(payload).encode(), {'Content-Type': 'application/json'})
    with request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def extract_json(content):
    """First JSON object in content after removing reasoning blocks. Returns (obj, error)."""
    text = re.sub(r'<think>.*?</think>', '', content or '', flags=re.S)
    if '<think>' in text:
        text = text.split('<think>')[0]
    dec = json.JSONDecoder()
    for m in re.finditer(r'\{', text):
        try:
            obj, _ = dec.raw_decode(text[m.start():])
        except ValueError:
            continue
        if isinstance(obj, dict):
            return obj, None
    return None, 'no_json_object'


def run_row(post, row, retries=1, temperature=0.0, seed=0, budget=None, system=SYSTEM):
    """One dispatch row. post(path, payload) -> dict. All attempts share one total token budget."""
    budget = budget or row['max_tokens']
    est_in = len(post('/tokenize', {'content': system + '\n' + row['prompt']})['tokens']) + CHAT_OVERHEAD
    used, in_tok, attempts, obj, err = 0, est_in, [], None, 'not_attempted'
    for k in range(retries + 1):
        cap = budget - used - in_tok
        if cap < 16:
            err = 'budget_exhausted' if attempts else 'prompt_exceeds_budget'
            break
        t0 = time.perf_counter()
        att = dict(attempt=k, max_tokens=cap)
        try:
            resp = post('/v1/chat/completions', dict(
                model='local', messages=[{'role': 'system', 'content': system}, {'role': 'user', 'content': row['prompt']}],
                max_tokens=cap, temperature=temperature, seed=seed + k, cache_prompt=False, stream=False))
            msg = resp['choices'][0]['message']
            usage = resp.get('usage') or {}
            content = msg.get('content') or ''
            reasoning = msg.get('reasoning_content') or ''
            pt, ct = usage.get('prompt_tokens'), usage.get('completion_tokens')
            att.update(raw=content, reasoning_len=len(reasoning), finish_reason=resp['choices'][0].get('finish_reason'),
                       usage_reported=pt is not None and ct is not None)
            if pt is None or ct is None:  # tokenizer cross-check substitutes for missing usage
                pt = est_in - CHAT_OVERHEAD
                ct = len(post('/tokenize', {'content': content + reasoning})['tokens'])
            att.update(tokens_in=pt, tokens_out=ct)
            obj, err = extract_json(content)
        except Exception as e:  # network or protocol failure counts as a failed attempt
            att.update(raw='', reasoning_len=0, tokens_in=0, tokens_out=0, error=f'{type(e).__name__}: {e}')
            obj, err = None, 'request_error'
        att['wall_ms'] = round((time.perf_counter() - t0) * 1000)
        att['parse_error'] = err
        attempts.append(att)
        used += att['tokens_in'] + att['tokens_out']
        in_tok = max(in_tok, att['tokens_in'])
        if obj is not None:
            break
    tin, tout = sum(a['tokens_in'] for a in attempts), sum(a['tokens_out'] for a in attempts)
    return dict(row_id=row['id'], tokens_in=tin, tokens_out=tout, response=obj, attempts=attempts,
                wall_ms=sum(a['wall_ms'] for a in attempts), raw=[a['raw'] for a in attempts],
                parse_error=None if obj is not None else err, over_budget=tin + tout > budget,
                reasoning_len=sum(a['reasoning_len'] for a in attempts), budget=budget, xcheck_prompt_tokens=est_in - CHAT_OVERHEAD)


def read_jsonl(path):
    p = Path(path)
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def dispatch(base_url, prompts, out, seed, retries, temperature, budget=None, post=None, limit=None):
    post = post or (lambda path, payload: http_post(base_url, path, payload))
    rows = read_jsonl(prompts)
    order = list(range(len(rows)))
    Random(seed).shuffle(order)
    out = Path(out)
    out.with_suffix('.meta.json').write_text(json.dumps(dict(shuffle_seed=seed, retries=retries, temperature=temperature,
                                                             system_prompt=SYSTEM, budget=budget, base_url=base_url), indent=2))
    done = {r['row_id'] for r in read_jsonl(out)}
    n = 0
    with out.open('a') as f:
        for i in order:
            row = rows[i]
            if row['id'] in done:
                continue
            if limit is not None and n >= limit:
                break
            f.write(json.dumps(run_row(post, row, retries, temperature, seed, budget), sort_keys=True) + '\n')
            f.flush()
            n += 1
    return n


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base-url', required=True)
    p.add_argument('--prompts', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--seed', type=int, default=13)
    p.add_argument('--retries', type=int, default=1)
    p.add_argument('--temperature', type=float, default=0.0)
    p.add_argument('--budget', type=int, default=None, help='override the per-row total token budget')
    p.add_argument('--limit', type=int, default=None)
    a = p.parse_args()
    print('dispatched', dispatch(a.base_url, a.prompts, a.output, a.seed, a.retries, a.temperature, a.budget, limit=a.limit))


if __name__ == '__main__':
    main()
