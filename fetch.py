#!/usr/bin/env python3
"""Fetch one shard of ICLR 2027 submission PDFs from OpenReview with your own OpenReview account.

    python fetch.py 7          fetch shard 7 (resumes if you stop and restart it)
    python fetch.py --list     show all shards and how many PDFs you already have
    python fetch.py --test     log in and download one PDF, to check that everything works

Needs Python 3.8 or newer and nothing else (standard library only). Your password is used once to log in and is never saved.
OpenReview allows about 25 PDF downloads per hour per account, so a 100-paper shard takes about 4-5 hours. Leave it running;
it waits by itself when OpenReview says "too many requests". When the shard is finished it writes shard_XXX.zip: send that file to Nitin.
"""
import os, sys, json, time, shutil, zipfile, hashlib, getpass, datetime, urllib.request, urllib.error

API = "https://api2.openreview.net"
HERE = os.path.dirname(os.path.abspath(__file__))
GAP = 150            # seconds between downloads (about 24 per hour, just under OpenReview's limit)
UA = "iclr27-pdf-shards/1.0 (python urllib)"


def shard_ids(n):
    p = os.path.join(HERE, "shards", f"shard_{n:03d}.txt")
    if not os.path.exists(p):
        sys.exit(f"No shard {n}. Run 'python fetch.py --list' to see the shard numbers.")
    return [l.strip() for l in open(p) if l.strip()]


def all_shards():
    d = os.path.join(HERE, "shards")
    return sorted(int(f[6:9]) for f in os.listdir(d) if f.startswith("shard_") and f.endswith(".txt"))


def out_dir(n):
    d = os.path.join(HERE, "pdfs", f"shard_{n:03d}"); os.makedirs(d, exist_ok=True); return d


def have_pdf(path):
    try:
        with open(path, "rb") as f: return f.read(4) == b"%PDF" and os.path.getsize(path) > 1000
    except OSError: return False


def read_status(d):
    """ids that are permanently unavailable (404/403), so a restart does not retry them forever"""
    p = os.path.join(d, "_status.tsv"); s = {}
    if os.path.exists(p):
        for l in open(p):
            a = l.rstrip("\n").split("\t")
            if len(a) >= 2: s[a[0]] = a[1]
    return s


def note_status(d, i, msg):
    with open(os.path.join(d, "_status.tsv"), "a") as f: f.write(f"{i}\t{msg}\n")


def login():
    user = os.environ.get("OPENREVIEW_USERNAME") or input("OpenReview login e-mail: ").strip()
    pw = os.environ.get("OPENREVIEW_PASSWORD") or getpass.getpass("OpenReview password (not shown, not saved): ")
    req = urllib.request.Request(f"{API}/login", data=json.dumps({"id": user, "password": pw}).encode(),
                                 headers={"Content-Type": "application/json", "User-Agent": UA}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r: tok = json.load(r)["token"]
    except urllib.error.HTTPError as e:
        sys.exit(f"Login failed (HTTP {e.code}). Check the e-mail and password you use on openreview.net.")
    except Exception as e:
        sys.exit(f"Could not reach OpenReview: {e}")
    print("Logged in to OpenReview.")
    return tok


def download(i, tok):
    """returns (status, bytes or wait-seconds or message)"""
    req = urllib.request.Request(f"{API}/pdf?id={i}", headers={"Authorization": f"Bearer {tok}", "User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=180) as r: return "ok", r.read()
    except urllib.error.HTTPError as e:
        if e.code == 429:
            wait = 1800
            try:
                reset = json.loads(e.read().decode())["details"]["resetTime"][:19]
                t = datetime.datetime.strptime(reset, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=datetime.timezone.utc)
                wait = max(60, (t - datetime.datetime.now(datetime.timezone.utc)).total_seconds() + 30)
            except Exception: pass
            return "wait", wait
        if e.code in (401,): return "relogin", None
        if e.code in (403, 404): return "missing", f"http {e.code}"
        return "retry", f"http {e.code}"
    except Exception as e:
        return "retry", str(e)[:80]


def fmt(s):
    s = int(max(0, s)); h, m = divmod(s // 60, 60)
    return f"{h}h{m:02d}m" if h else f"{m}m{s % 60:02d}s"


def bar(n, done, missing, note=""):
    k = done + missing; w = 30; f = int(w * k / max(n, 1))
    eta = (n - k) * GAP
    line = f"\r[{'#' * f}{'.' * (w - f)}] {k}/{n} ({100 * k // max(n, 1)}%)  PDFs {done}  unavailable {missing}  ETA ~{fmt(eta)}  {note}"
    w = max(40, shutil.get_terminal_size((100, 20)).columns - 1)
    sys.stdout.write(line[:w].ljust(w)); sys.stdout.flush()


def wait_with_countdown(sec, n, done, missing, why):
    end = time.time() + sec
    while time.time() < end:
        bar(n, done, missing, f"{why}: next try in {fmt(end - time.time())}"); time.sleep(min(5, max(0.1, end - time.time())))


def pack(n, ids, d):
    z = os.path.join(HERE, f"shard_{n:03d}.zip"); st = read_status(d); rows = []
    with zipfile.ZipFile(z, "w", zipfile.ZIP_STORED) as zf:
        for i in ids:
            p = os.path.join(d, f"{i}.pdf")
            if have_pdf(p):
                b = open(p, "rb").read(); rows.append(f"{i}\tok\t{len(b)}\t{hashlib.sha256(b).hexdigest()}")
                zf.write(p, f"shard_{n:03d}/{i}.pdf")
            else: rows.append(f"{i}\t{st.get(i, 'not fetched')}\t0\t-")
        zf.writestr(f"shard_{n:03d}/manifest.tsv", "id\tstatus\tbytes\tsha256\n" + "\n".join(rows) + "\n")
    print(f"\nWrote {z} ({os.path.getsize(z) / 1e6:.0f} MB). Please send this file to Nitin.")


def run(n, test=False):
    ids = shard_ids(n); d = out_dir(n); st = read_status(d)
    todo = [i for i in ids if not have_pdf(os.path.join(d, f"{i}.pdf")) and i not in st]
    if test: todo = todo[:1]
    done = sum(have_pdf(os.path.join(d, f"{i}.pdf")) for i in ids); missing = len(st)
    print(f"Shard {n}: {len(ids)} papers, {done} already here, {len(todo)} to fetch. Saving into {d}")
    print("You can stop with Ctrl+C at any time and run the same command later; it continues where it stopped.")
    if not todo:
        if not test: pack(n, ids, d)
        return
    tok = login(); t_login = time.time(); tries = {}
    q = list(todo)
    while q:
        i = q[0]; t0 = time.time()
        if time.time() - t_login > 3000: tok = login(); t_login = time.time()
        bar(len(ids), done, missing, f"downloading {i}")
        kind, val = download(i, tok)
        if kind == "ok" and val[:4] == b"%PDF":
            tmp = os.path.join(d, f"{i}.pdf.part")
            with open(tmp, "wb") as f: f.write(val)
            os.replace(tmp, os.path.join(d, f"{i}.pdf")); done += 1; q.pop(0)
        elif kind == "wait":
            wait_with_countdown(val, len(ids), done, missing, "OpenReview rate limit (normal)"); continue
        elif kind == "relogin":
            tok = login(); t_login = time.time(); continue
        elif kind == "missing" or tries.get(i, 0) >= 4:
            note_status(d, i, val if kind == "missing" else f"failed: {val}"); missing += 1; q.pop(0)
        else:
            tries[i] = tries.get(i, 0) + 1; q.append(q.pop(0))        # try it again later
        if test: break
        if q: wait_with_countdown(GAP - (time.time() - t0), len(ids), done, missing, "pacing")
    bar(len(ids), done, missing, "finished"); print()
    if test:
        print("Test OK: one PDF downloaded." if done else "Test did not download a PDF; see the message above.")
        return
    pack(n, ids, d)


def main():
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"): print(__doc__); return
    if a[0] == "--list":
        print("shard  papers  PDFs here")
        for n in all_shards():
            ids = shard_ids(n); d = os.path.join(HERE, "pdfs", f"shard_{n:03d}")
            h = sum(have_pdf(os.path.join(d, f"{i}.pdf")) for i in ids) if os.path.isdir(d) else 0
            print(f"{n:5d}  {len(ids):6d}  {h:9d}")
        return
    if a[0] == "--test": run(all_shards()[-1], test=True); return
    try: n = int(a[0])
    except ValueError: sys.exit("Usage: python fetch.py <shard number>   (for example: python fetch.py 7)")
    try: run(n)
    except KeyboardInterrupt: print("\nStopped. Run the same command again to continue.")


if __name__ == "__main__":
    main()
