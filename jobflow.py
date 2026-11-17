"""Offline, local job queue. No browser or network access."""
import argparse
import json
import sqlite3
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

STATES = {'discovered', 'needs_verification', 'preparing', 'waiting_user', 'submitted', 'submission_unknown', 'closed', 'skipped'}
TRANSITIONS = {
 'discovered': {'needs_verification', 'closed', 'skipped'},
 'needs_verification': {'preparing', 'waiting_user', 'closed', 'skipped'},
 'preparing': {'waiting_user', 'submission_unknown', 'closed', 'skipped'},
 'waiting_user': {'needs_verification', 'preparing', 'submission_unknown', 'closed', 'skipped'},
 'submission_unknown': {'submitted'},
 'submitted': {'closed'}, 'closed': set(), 'skipped': {'needs_verification'},
}

def canonical_url(value):
    p = urlsplit(value.strip())
    if p.scheme not in ('https', 'http') or not p.hostname or p.username or p.password:
        raise ValueError('Expected an HTTP(S) posting URL without credentials')
    # Preserve non-tracking parameters: some sites use them to identify jobs.
    q = [(k,v) for k,v in parse_qsl(p.query, keep_blank_values=True) if not k.lower().startswith('utm_')]
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path.rstrip('/') or '/', urlencode(sorted(q)), ''))

def connect(path):
    con = sqlite3.connect(path, timeout=30, isolation_level=None)
    con.execute('PRAGMA foreign_keys=ON')
    con.executescript('''CREATE TABLE IF NOT EXISTS jobs (
      id INTEGER PRIMARY KEY, url TEXT NOT NULL UNIQUE, company TEXT NOT NULL, title TEXT NOT NULL,
      location TEXT NOT NULL DEFAULT '', status TEXT NOT NULL DEFAULT 'discovered',
      saved INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
      updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, job_id INTEGER NOT NULL REFERENCES jobs(id),
      kind TEXT NOT NULL, detail TEXT NOT NULL DEFAULT '', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);''')
    return con

def add(con, job):
    url = canonical_url(job['url'])
    company, title = job['company'].strip(), job['title'].strip()
    if not company or not title: raise ValueError('company and title are required')
    con.execute('BEGIN IMMEDIATE')
    try:
        cur = con.execute('INSERT OR IGNORE INTO jobs(url,company,title,location) VALUES(?,?,?,?)', (url, company, title, job.get('location','')))
        job_id = con.execute('SELECT id FROM jobs WHERE url=?', (url,)).fetchone()[0]
        if cur.rowcount: con.execute("INSERT INTO events(job_id,kind) VALUES(?, 'discovered')", (job_id,))
        con.commit()
        return job_id, bool(cur.rowcount)
    except BaseException:
        con.rollback(); raise

def transition(con, job_id, target, evidence=''):
    if target not in STATES: raise ValueError('Unknown status')
    con.execute('BEGIN IMMEDIATE')
    try:
        row = con.execute('SELECT status FROM jobs WHERE id=?', (job_id,)).fetchone()
        if not row: raise ValueError('Job not found')
        current = row[0]
        if current == target:
            con.commit(); return False
        if target not in TRANSITIONS[current]: raise ValueError(f'Invalid transition: {current} -> {target}')
        if target == 'submitted' and not evidence.strip(): raise ValueError('Submission confirmation evidence is required')
        con.execute('UPDATE jobs SET status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?', (target, job_id))
        con.execute('INSERT INTO events(job_id,kind,detail) VALUES(?,?,?)', (job_id,target,evidence.strip()))
        con.commit(); return True
    except BaseException:
        con.rollback(); raise

def resolve_not_submitted(con, job_id, evidence):
    """Record an explicit reconciliation before permitting another attempt."""
    if not evidence.strip(): raise ValueError('Reconciliation evidence is required')
    con.execute('BEGIN IMMEDIATE')
    try:
        row = con.execute('SELECT status FROM jobs WHERE id=?', (job_id,)).fetchone()
        if not row or row[0] != 'submission_unknown': raise ValueError('Job must be submission_unknown')
        con.execute("UPDATE jobs SET status='preparing', updated_at=CURRENT_TIMESTAMP WHERE id=?", (job_id,))
        con.execute("INSERT INTO events(job_id,kind,detail) VALUES(?, 'reconciled_not_submitted', ?)", (job_id,evidence.strip()))
        con.commit()
    except BaseException:
        con.rollback(); raise

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--db',default='private/jobs.sqlite3')
    sub=p.add_subparsers(dest='cmd',required=True)
    a=sub.add_parser('add'); a.add_argument('json_file')
    sub.add_parser('list')
    t=sub.add_parser('status'); t.add_argument('id',type=int); t.add_argument('status',choices=sorted(STATES)); t.add_argument('--evidence',default='')
    s=sub.add_parser('save'); s.add_argument('id',type=int)
    r=sub.add_parser('resolve-not-submitted'); r.add_argument('id',type=int); r.add_argument('--evidence',required=True)
    args=p.parse_args(); Path(args.db).parent.mkdir(parents=True,exist_ok=True)
    with connect(args.db) as con:
        if args.cmd=='add':
            data=json.loads(Path(args.json_file).read_text()); data=data if isinstance(data,list) else [data]
            for j in data: print(*add(con,j))
        elif args.cmd=='list':
            con.row_factory=sqlite3.Row
            print(json.dumps([dict(x) for x in con.execute('SELECT * FROM jobs ORDER BY id')],indent=2))
        elif args.cmd=='resolve-not-submitted':
            resolve_not_submitted(con,args.id,args.evidence); print('reconciled')
        elif args.cmd=='save':
            cur=con.execute('UPDATE jobs SET saved=1 WHERE id=?',(args.id,))
            if not cur.rowcount: raise ValueError('Job not found')
        else: print('updated' if transition(con,args.id,args.status,args.evidence) else 'unchanged')
if __name__=='__main__': main()
