import concurrent.futures
import tempfile
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import jobflow as j

class QueueTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory(); self.path=str(Path(self.tmp.name)/'queue.db'); self.con=j.connect(self.path)
  self.job={'url':'https://jobs.example.test/a?utm_source=x','company':'Example','title':'Analyst'}
 def tearDown(self): self.con.close(); self.tmp.cleanup()
 def test_dedup_and_saved_is_not_submitted(self):
  ident,new=j.add(self.con,self.job); self.assertTrue(new)
  self.assertEqual(j.add(self.con,{**self.job,'url':'https://jobs.example.test/a'}),(ident,False))
  self.con.execute('UPDATE jobs SET saved=1 WHERE id=?',(ident,))
  self.assertEqual(self.con.execute('SELECT status FROM jobs').fetchone()[0], 'discovered')
 def test_confirmation_and_recovery(self):
  ident,_=j.add(self.con,self.job)
  for state in ('needs_verification','preparing','submission_unknown'): j.transition(self.con,ident,state)
  with self.assertRaises(ValueError): j.transition(self.con,ident,'submitted')
  self.assertEqual(self.con.execute('SELECT status FROM jobs').fetchone()[0], 'submission_unknown')
  self.assertTrue(j.transition(self.con,ident,'submitted','Official confirmation observed'))
  self.assertFalse(j.transition(self.con,ident,'submitted','Official confirmation observed'))
  self.assertEqual(self.con.execute("SELECT count(*) FROM events WHERE kind='submitted'").fetchone()[0],1)
 def test_reject_invalid_transition(self):
  ident,_=j.add(self.con,self.job)
  with self.assertRaises(ValueError): j.transition(self.con,ident,'submitted','confirmation')
 def test_concurrent_duplicate_adds(self):
  def worker(_):
   con=j.connect(self.path)
   try: return j.add(con,self.job)
   finally: con.close()
  with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool: results=list(pool.map(worker,range(16)))
  self.assertEqual(sum(created for _,created in results),1)
  self.assertEqual(self.con.execute('SELECT count(*) FROM jobs').fetchone()[0],1)
 def test_failed_evidence_write_rolls_back_status(self):
  ident,_=j.add(self.con,self.job)
  for state in ('needs_verification','preparing','submission_unknown'): j.transition(self.con,ident,state)
  self.con.execute("CREATE TRIGGER reject_confirmation BEFORE INSERT ON events WHEN NEW.kind='submitted' BEGIN SELECT RAISE(ABORT, 'simulated failure'); END")
  with self.assertRaises(Exception): j.transition(self.con,ident,'submitted','Official confirmation observed')
  self.assertEqual(self.con.execute('SELECT status FROM jobs').fetchone()[0], 'submission_unknown')
 def test_reject_url_credentials(self):
  with self.assertRaises(ValueError): j.add(self.con,{**self.job,'url':'https://u:p@example.test/job'})
if __name__=='__main__': unittest.main()
