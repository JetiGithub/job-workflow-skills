"""Scout public Greenhouse boards or local JSON, and prepare local application drafts."""
import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError
import jobflow

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise HTTPError(req.full_url, code, 'Redirect refused', headers, fp)

def load_config(path):
    cfg = json.loads(Path(path).read_text(encoding='utf-8'))
    if cfg.get('mode') not in ('review', 'draft', 'submit'):
        raise ValueError('mode must be review, draft, or submit')
    for key in ('roles', 'locations'):
        if not isinstance(cfg.get(key, []), list) or not all(isinstance(x, str) for x in cfg.get(key, [])):
            raise ValueError(f'{key} must be a list of strings')
    return cfg

def greenhouse_jobs(payload):
    jobs = payload.get('jobs')
    if not isinstance(jobs, list): raise ValueError('Invalid board response')
    result = []
    for item in jobs:
        if not isinstance(item, dict): continue
        loc = item.get('location') or {}
        if not isinstance(loc, dict): continue
        if not all(isinstance(item.get(k), str) and item[k].strip() for k in ('title','absolute_url')): continue
        result.append({'title': item['title'], 'url': item['absolute_url'], 'location': loc.get('name') or ''})
    return result

def fetch_greenhouse(slug):
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,100}', slug): raise ValueError('Invalid board token')
    url = f'https://boards-api.greenhouse.io/v1/boards/{slug}/jobs'
    req = Request(url, headers={'User-Agent':'job-workflow-skills/0.2', 'Accept':'application/json'})
    with build_opener(NoRedirect).open(req, timeout=15) as res:
        data = res.read(5_000_001)
    if len(data)>5_000_000: raise ValueError('Board response exceeds size limit')
    return greenhouse_jobs(json.loads(data))

def matches(job, cfg):
    def any_match(terms, value):
        return not terms or any(term.casefold() in value.casefold() for term in terms if term.strip())
    return any_match(cfg.get('roles', []), job['title']) and any_match(cfg.get('locations', []), job.get('location',''))

def scout(con, records, cfg):
    stats={'read':0,'matched':0,'added':0,'duplicates':0,'invalid':0}
    for record in records:
        stats['read']+=1
        try:
            if not isinstance(record, dict) or not all(isinstance(record.get(k), str) for k in ('title','company','url')) or not isinstance(record.get('location',''),str):
                raise ValueError('Invalid record')
            if not matches(record,cfg): continue
            stats['matched']+=1
            _, created=jobflow.add(con,record)
            stats['added' if created else 'duplicates']+=1
        except (ValueError, KeyError, TypeError): stats['invalid']+=1
    return stats

def unique_write(directory, prefix, content):
    directory=Path(directory); directory.mkdir(parents=True,exist_ok=True,mode=0o700)
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    path=directory/f'{prefix}-{stamp}.md'
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w',encoding='utf-8') as f: f.write(content)
    return path

def report(con, stats, directory):
    rows=con.execute('SELECT id,company,title,location,status,url FROM jobs ORDER BY id').fetchall()
    def cell(x): return str(x).replace('|','/').replace('\n',' ').replace('\r',' ')
    lines=['# Job scout report', '', 'Generated: '+datetime.now(timezone.utc).isoformat(), '',
           'This is a queue snapshot, not proof that a job is open or verified.', '',
           'Run counts: '+', '.join(f'{k}={v}' for k,v in stats.items()), '',
           '| ID | Company | Title | Location | Status | URL |','|---|---|---|---|---|---|']
    lines += ['| '+' | '.join(cell(x) for x in row)+' |' for row in rows]
    return unique_write(directory,'scout-report','\n'.join(lines)+'\n')

def draft(con, job_id, cfg, directory):
    if cfg['mode'] not in ('draft','submit'): raise ValueError('Drafting requires draft or submit mode')
    row=con.execute('SELECT company,title,url,status FROM jobs WHERE id=?',(job_id,)).fetchone()
    if not row: raise ValueError('Job not found')
    company,title,url,status=row
    if status not in ('preparing','waiting_user'): raise ValueError('Move job to preparing or waiting_user before drafting')
    # No resume is parsed or facts invented. The candidate supplies approved details manually.
    text=(f'# Application draft — {company} / {title}\n\nJob: {url}\n\n'
          '## Cover letter outline\n\nDear hiring team,\n\n'
          f'I am interested in the {title} position at {company}.\n\n'
          '[Add a truthful, candidate-approved example of relevant experience.]\n\n'
          '[Explain your interest using verified information about the role.]\n\n'
          'Thank you for your consideration.\n\n[Your name]\n\n'
          '## Review checklist\n\n- [ ] Verify the official posting and role is open.\n'
          '- [ ] Select and review the resume.\n- [ ] Confirm all claims and work authorization answers.\n'
          '- [ ] Review every form response and attachments.\n- [ ] Obtain explicit approval before final submission.\n')
    return unique_write(directory,f'application-{job_id}',text)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--db',default='private/jobs.sqlite3'); p.add_argument('--config',default='config.local.json')
    sub=p.add_subparsers(dest='command',required=True)
    i=sub.add_parser('scout-json'); i.add_argument('file'); i.add_argument('--reports',default='private/reports')
    g=sub.add_parser('scout-greenhouse'); g.add_argument('board'); g.add_argument('--company',required=True); g.add_argument('--reports',default='private/reports')
    d=sub.add_parser('draft'); d.add_argument('id',type=int); d.add_argument('--output',default='private/drafts')
    args=p.parse_args(); cfg=load_config(args.config)
    Path(args.db).parent.mkdir(parents=True,exist_ok=True)
    with jobflow.connect(args.db) as con:
        if args.command=='draft': print(draft(con,args.id,cfg,args.output)); return
        if args.command=='scout-json':
            records=json.loads(Path(args.file).read_text(encoding='utf-8'))
            if not isinstance(records,list): raise ValueError('Input must be a JSON array')
        else:
            records=[{**x,'company':args.company} for x in fetch_greenhouse(args.board)]
        stats=scout(con,records,cfg); path=report(con,stats,args.reports)
        print(json.dumps(stats)); print(path)
if __name__=='__main__': main()
