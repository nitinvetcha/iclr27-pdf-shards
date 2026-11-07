# ICLR 2027 PDF shards

This repo helps us download ICLR 2027 submission PDFs from OpenReview. The papers are split into **147 small shards of 100 papers each**.
Each person runs one shard with their own OpenReview account and sends back one zip file. All further processing happens on Nitin's server.

## How to run a shard (3 steps)

1. Get the code (needs Python 3.8 or newer; nothing to install):
   ```
   git clone https://github.com/nitinvetcha/iclr27-pdf-shards.git
   cd iclr27-pdf-shards
   ```
2. Run the shard number Nitin gave you, for example shard 7:
   ```
   python fetch.py 7
   ```
   It asks for your OpenReview e-mail and password. The password is used only to log in. It is never saved or sent anywhere else.
3. When it finishes, it writes **`shard_007.zip`** in this folder. Send that file to Nitin.

While it runs, you see a progress line like this:
```
[#########.....................] 31/100 (31%)  PDFs 30  unavailable 1  ETA ~2h52m  pacing: next try in 1m48s
```

## Good to know

- **It is slow on purpose.** OpenReview allows about 25 PDFs per hour per account, so one shard takes **about 4–5 hours**. Just leave it running.
- **"OpenReview rate limit (normal)"** means OpenReview asked us to wait. The script waits by itself and continues.
- **You can stop it at any time** (Ctrl+C, closing the laptop, losing Wi-Fi). Run the same command again, and it continues where it stopped.
- **"unavailable"** counts papers that OpenReview no longer serves (for example, withdrawn). That is fine; they are listed in the zip.
- **To check that it works** before a long run: `python fetch.py --test` (logs in and downloads one PDF).
- **To see all shards** and how many PDFs you already have: `python fetch.py --list`.
- On Windows, use `py fetch.py 7` if `python` is not found. On a Mac or Linux, `python3 fetch.py 7`.
- To run without typing the password each time, set `OPENREVIEW_USERNAME` and `OPENREVIEW_PASSWORD` in your shell first.

## Shards

- **Shard 1** is fetched by Nitin's server. Please do not take it.
- Please **take the shard number Nitin gives you**, so two people do not download the same papers.
- Each shard file in `shards/` is just a list of OpenReview submission ids, one per line.

## Please keep this private

ICLR 2027 is still under review. Please do not share this repo, the PDFs or the zip files outside our group, and do not put them on any public site.
