import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import jobflow
import workflow

class WorkflowTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(); self.root=Path(self.temp.name); self.con=jobflow.connect(str(self.root/'db'))
  self.config={'roles':['data analyst'],'locations':['remote'],'mode':'draft'}
  self.jobs=[{'company':'Example','title':'Data Analyst','location':'Remote','url':'https://example.test/1'}, {'company':'Example','title':'Manager','location':'Remote','url':'https://example.test/2'}]
 def tearDown(self): self.con.close(); self.temp.cleanup()
 def test_scout_filter_repeat_and_reports(self):
  first=workflow.scout(self.con,self.jobs,self.config); second=workflow.scout(self.con,self.jobs,self.config)
  self.assertEqual((first['added'],second['duplicates']),(1,1))
  a=workflow.report(self.con,first,self.root/'reports'); b=workflow.report(self.con,second,self.root/'reports')
  self.assertNotEqual(a,b); self.assertIn('added=1',a.read_text()); self.assertIn('duplicates=1',b.read_text())
 def test_fixture_board_parsing(self):
  payload={'jobs':[{'title':'Data Analyst','absolute_url':'https://example.test/job','location':{'name':'Remote'}},{'title':None}]}
  self.assertEqual(len(workflow.greenhouse_jobs(payload)),1)
  with self.assertRaises(ValueError): workflow.fetch_greenhouse('../bad')
 def test_draft_mode_and_placeholder(self):
  ident,_=jobflow.add(self.con,self.jobs[0]); jobflow.transition(self.con,ident,'needs_verification'); jobflow.transition(self.con,ident,'preparing')
  with self.assertRaises(ValueError): workflow.draft(self.con,ident,{**self.config,'mode':'review'},self.root/'drafts')
  output=workflow.draft(self.con,ident,self.config,self.root/'drafts')
  self.assertIn('candidate-approved',output.read_text()); self.assertEqual(output.stat().st_mode & 0o777,0o600)
 def test_unknown_requires_explicit_reconciliation(self):
  ident,_=jobflow.add(self.con,self.jobs[0])
  for state in ('needs_verification','preparing','submission_unknown'): jobflow.transition(self.con,ident,state)
  with self.assertRaises(ValueError): jobflow.transition(self.con,ident,'waiting_user')
  with self.assertRaises(ValueError): jobflow.resolve_not_submitted(self.con,ident,'')
  jobflow.resolve_not_submitted(self.con,ident,'Checked official portal; no application found')
  self.assertEqual(self.con.execute('SELECT status FROM jobs').fetchone()[0],'preparing')
if __name__=='__main__': unittest.main()
