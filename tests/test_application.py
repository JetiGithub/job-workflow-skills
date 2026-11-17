import json
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import application
import jobflow

class ApplicationTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name)
  self.con=jobflow.connect(str(self.root/'db'))
  self.id,_=jobflow.add(self.con,{'company':'Sample','title':'Analyst','url':'https://jobs.example.test/1'})
  jobflow.transition(self.con,self.id,'needs_verification'); jobflow.transition(self.con,self.id,'preparing')
  self.profile=self.root/'profile.json'; self.profile.write_text(json.dumps({'name':'Alex Example','summary':'Fictional summary.','facts':['Fictional accomplishment.'],'motivation':'Fictional motivation.'}))
 def tearDown(self): self.con.close(); self.tmp.cleanup()
 def test_packet_uses_only_provided_claims(self):
  p=application.create_packet(self.con,self.id,{'mode':'draft'},self.profile,self.root/'drafts')
  text=p.read_text(); self.assertIn('Fictional accomplishment.',text); self.assertIn('Fictional motivation.',text)
  self.assertEqual(p.stat().st_mode & 0o777,0o600)
 def test_review_mode_and_missing_facts_rejected(self):
  with self.assertRaises(ValueError): application.create_packet(self.con,self.id,{'mode':'review'},self.profile,self.root/'drafts')
  self.profile.write_text('{}')
  with self.assertRaises(ValueError): application.create_packet(self.con,self.id,{'mode':'draft'},self.profile,self.root/'drafts')
if __name__=='__main__': unittest.main()
