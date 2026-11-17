"""Create local application materials from candidate-approved facts."""
import argparse
import json
from pathlib import Path
import jobflow
import workflow


def load_profile(path):
    profile = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(profile, dict): raise ValueError('Profile must be an object')
    for k in ('name', 'summary', 'motivation'):
        if not isinstance(profile.get(k), str) or not profile[k].strip(): raise ValueError(f'{k} is required')
    facts = profile.get('facts')
    if not isinstance(facts, list) or not facts or not all(isinstance(x, str) and x.strip() for x in facts):
        raise ValueError('facts must be a non-empty list of approved statements')
    return profile


def create_packet(con, job_id, cfg, profile, directory):
    if cfg['mode'] not in ('draft', 'submit'): raise ValueError('Packet creation requires draft or submit mode')
    row = con.execute('SELECT company,title,url,status FROM jobs WHERE id=?', (job_id,)).fetchone()
    if not row: raise ValueError('Job not found')
    company, title, url, status = row
    if status not in ('preparing', 'waiting_user'): raise ValueError('Job must be preparing or waiting_user')
    profile = load_profile(profile)
    facts = '\n'.join('- '+f.replace('\n', ' ') for f in profile['facts'])
    # Copy claims verbatim; do not infer qualifications, employer facts, or authorization.
    content = (f'# Application packet: {title} — {company}\n\nJob: {url}\n\n'
        '## Candidate-approved resume content\n\n'
        f"{profile['name']}\n\n{profile['summary']}\n\n{facts}\n\n"
        '## Cover letter draft\n\nDear hiring team,\n\n'
        f"I am applying for the {title} position at {company}. {profile['summary']}\n\n"
        f"Relevant experience I would bring includes:\n\n{facts}\n\n"
        f"{profile['motivation']}\n\nThank you for considering my application.\n\n{profile['name']}\n\n"
        '## Final review\n\n- Verify every statement and the official job posting.\n'
        '- Review resume formatting and select the correct file.\n'
        '- Answer authorization and availability questions only with confirmed information.\n'
        '- Review all form fields and obtain explicit authorization before submitting.\n')
    return workflow.unique_write(directory, f'packet-{job_id}', content)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('id',type=int); parser.add_argument('--profile',required=True)
    parser.add_argument('--db',default='private/jobs.sqlite3'); parser.add_argument('--config',default='config.local.json')
    parser.add_argument('--output',default='private/drafts')
    args=parser.parse_args(); cfg=workflow.load_config(args.config)
    with jobflow.connect(args.db) as con: print(create_packet(con,args.id,cfg,args.profile,args.output))
if __name__=='__main__': main()
