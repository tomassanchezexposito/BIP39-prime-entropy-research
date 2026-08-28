#!/usr/bin/env python3
from pathlib import Path
import hashlib, json
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "generated_phrases"
EXCLUDED = {"MANIFEST.tsv"}

def sha256_file(path, chunk=1024*1024):
    h=hashlib.sha256()
    with path.open('rb') as f:
        while True:
            b=f.read(chunk)
            if not b: break
            h.update(b)
    return h.hexdigest()

def count_nonempty_lines(path):
    n=0
    with path.open('r',encoding='utf-8-sig',errors='replace') as f:
        for line in f:
            if line.strip(): n+=1
    return n

files=[]
for p in sorted(DATA.rglob('*.txt')):
    if p.name in EXCLUDED or 'private' in p.parts or p.name.endswith('.private.txt'):
        continue
    rel=p.relative_to(ROOT).as_posix()
    stat=p.stat()
    files.append({
        'path':rel,
        'nonempty_lines':count_nonempty_lines(p),
        'bytes':stat.st_size,
        'sha256':sha256_file(p),
        'modified_utc':datetime.fromtimestamp(stat.st_mtime,timezone.utc).isoformat(),
    })
now=datetime.now(timezone.utc).isoformat()
manifest=DATA/'MANIFEST.tsv'
with manifest.open('w',encoding='utf-8',newline='') as f:
    f.write('path\tnonempty_lines\tbytes\tsha256\tmodified_utc\n')
    for r in files:
        f.write(f"{r['path']}\t{r['nonempty_lines']}\t{r['bytes']}\t{r['sha256']}\t{r['modified_utc']}\n")
status={
    'updated_at_utc':now,
    'corpus_files':len(files),
    'nonempty_lines':sum(x['nonempty_lines'] for x in files),
    'total_bytes':sum(x['bytes'] for x in files),
    'files':files,
}
(DATA/'DATASET_STATUS.json').write_text(json.dumps(status,indent=2)+"\n",encoding='utf-8')
(DATA/'STATUS.md').write_text(
    '# Dataset status\n\n'
    f"- **Last indexed (UTC):** {now}\n"
    f"- **Corpus files:** {status['corpus_files']:,}\n"
    f"- **Non-empty phrase lines:** {status['nonempty_lines']:,}\n"
    f"- **Total corpus bytes:** {status['total_bytes']:,}\n\n"
    'Anything listed here must be treated as public test data and never used to custody funds.\n',
    encoding='utf-8'
)
print(f"Indexed {len(files)} files, {status['nonempty_lines']:,} non-empty lines.")
