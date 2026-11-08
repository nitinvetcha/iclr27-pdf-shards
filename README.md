# ICLR 2027 PDF shards

This repo helps us download ICLR 2027 submission PDFs from OpenReview. The papers are split into **small shards of 100 papers each** (re-cut 8 Nov 2026: 135 shards; shards 1-20 are Nitin's server, the rest are assigned by name in `assignments.txt`, most important first, with no overlap).
Each person runs one shard with their own OpenReview account and sends back one zip file. All further processing happens on Nitin's server.

## How to run a shard (3 steps)

1. Get the code (needs Python 3.8 or newer; nothing to install):
   ```
   git clone https://github.com/nitinvetcha/iclr27-pdf-shards.git
   cd iclr27-pdf-shards
   ```
2. Run it with **your name as it appears in [`assignments.txt`](assignments.txt)**, for example:
   ```
   python fetch.py alice
   ```
   It fetches every shard assigned to you, one after another. (To run a single shard instead: `python fetch.py 7`.)
   It asks for your OpenReview e-mail and password. The password is used only to log in. It is never saved or sent anywhere else.
3. Each finished shard becomes a zip in this folder, for example **`shard_007.zip`**. Send those files to Nitin.

While it runs, you see a progress line like this:
```
[#########.....................] 31/100 (31%)  PDFs 30  unavailable 1  ETA ~2h52m  pacing: next try in 1m48s
```

## Where the files go

- While a shard runs, its PDFs are saved in `iclr27-pdf-shards/pdfs/shard_007/`.
- When the shard is complete, the script packs them into **`iclr27-pdf-shards/shard_007.zip`**, checks the zip, and then deletes the
  loose PDFs (they are all inside the zip). It then starts your next shard by itself.
- **Send Nitin the `shard_XXX.zip` files** (for example, by Google Drive). You can send each one as soon as it appears; no need to wait
  for all of them. Once Nitin confirms receipt, you may delete the zip.
- About 300-500 MB per zip.

## Running it in tmux (so it keeps going when you close the terminal)

```
tmux new -s iclr
python fetch.py yourname        # type the e-mail and password once
```
Press **Ctrl+b, then d** to leave it running in the background. Come back later with `tmux attach -t iclr` to see the progress line.
You type the password only once per run: the script keeps it in memory (never on disk) for re-logins and for the next shards.

## Good to know

- **It is slow on purpose.** OpenReview allows about 25 PDFs per hour per account, so one shard takes **about 4–5 hours**. Just leave it running.
- **"OpenReview rate limit (normal)"** means OpenReview asked us to wait. The script waits by itself and continues.
- **You can stop it at any time** (Ctrl+C, closing the laptop, losing Wi-Fi). Run the same command again, and it continues where it stopped.
- **"unavailable"** counts papers that OpenReview no longer serves (for example, withdrawn). That is fine; they are listed in the zip.
- **To check that it works** before a long run: `python fetch.py --test` (logs in and downloads one PDF).
- **To see all shards** and how many PDFs you already have: `python fetch.py --list`.
- On Windows, use `py fetch.py 7` if `python` is not found. On a Mac or Linux, `python3 fetch.py 7`.
- To run without typing the password each time, set `OPENREVIEW_USERNAME` and `OPENREVIEW_PASSWORD` in your shell first.

## Who does which shard: `assignments.txt`

- **Nitin assigns shards** by editing [`assignments.txt`](assignments.txt) on GitHub: open the file, click the pencil icon, write a
  name after the shard number (for example `7 alice`), and click "Commit changes". One word per name, no spaces.
- Give one person several shards by writing their name on several lines.
- The script fetches the latest `assignments.txt` each time it starts, so new assignments take effect without re-cloning.
- **Shard 1** is fetched by Nitin's server. The server also skips every shard that has a name next to it.
- Each shard file in `shards/` is just a list of OpenReview submission ids, one per line.

## Please keep this private

ICLR 2027 is still under review. Please do not share this repo, the PDFs or the zip files outside our group, and do not put them on any public site.
