import contextlib
import csv
import io
import tempfile
import unittest
from pathlib import Path
import tracker


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = str(Path(self.tmp.name) / 'applications.sqlite3')

    def run_cli(self, *args):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            tracker.main(['--db', self.db, *args])
        return output.getvalue()

    def add(self):
        return self.run_cli('add', '--company', 'Example', '--role', 'CV Intern',
                            '--location', 'Munich', '--url', 'https://example.com/job',
                            '--deadline', '2026-10-12', '--next-action', 'Check eligibility',
                            '--next-date', '2026-10-15')

    def test_workflow_persistence_due_and_export(self):
        self.assertIn('#1', self.add())
        self.assertIn('Example', self.run_cli('due', '--on', '2026-10-12'))
        self.run_cli('update', '1', '--status', 'applied', '--next-action', 'Follow up', '--next-date', '2026-10-28')
        self.assertIn('No applications', self.run_cli('due', '--on', '2026-10-12'))
        self.assertIn('Follow up', self.run_cli('due', '--on', '2026-10-28'))
        with tracker.connect(self.db) as db:
            self.assertEqual(db.execute('SELECT applied_at FROM applications').fetchone()[0], tracker.date.today().isoformat())
        self.run_cli('update', '1', '--status', 'rejected')
        self.assertIn('No applications', self.run_cli('due', '--on', '2027-01-01'))
        path = Path(self.tmp.name) / 'export.csv'
        self.run_cli('export', str(path))
        with path.open() as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(rows[0]['status'], 'rejected')

    def test_duplicate_and_invalid_updates(self):
        self.add()
        for args in [None, ('update','99','--status','applied'),
                     ('update','1','--next-date','2026-10-20'),
                     ('update','1','--status','invalid'),
                     ('due','--on','2026-02-30'), ('export',self.db)]:
            with self.assertRaises(SystemExit) as error:
                self.add() if args is None else self.run_cli(*args)
            self.assertEqual(error.exception.code, 2)
        self.assertIn('saved', self.run_cli('list'))


if __name__ == '__main__':
    unittest.main()
