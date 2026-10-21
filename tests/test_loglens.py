import json
import tempfile
import unittest
from pathlib import Path
from loglens.core import analyze, parse_line, fingerprint
from loglens.report import html_report
from loglens.__main__ import main

class LogTests(unittest.TestCase):
    def test_timezone_normalized(self):
        item = parse_line("2026-01-01T12:00:00+02:00 INFO api Started")
        self.assertEqual(item.timestamp.hour, 10)
    def test_json_record(self):
        item = parse_line(json.dumps(dict(timestamp="2026-01-01T00:00:00Z",level="warn",service="api",message="Slow")))
        self.assertEqual(item.level, "WARNING")
    def test_naive_time_rejected(self):
        with self.assertRaises(ValueError): parse_line("2026-01-01T00:00:00 INFO api Started")
    def test_bad_record_isolated(self):
        result = analyze(["broken", "2026-01-01T00:00:00Z ERROR api Failed", ""])
        self.assertEqual((result["total"],result["skipped"],result["errors"]),(1,1,1))
        self.assertEqual(result["malformed_lines"],[1])
    def test_exact_default(self):
        rows=[f"2026-01-01T00:00:00Z ERROR api User {n} failed" for n in [1,2]]
        self.assertEqual(len(analyze(rows)["groups"]),2)
        self.assertEqual(len(analyze(rows,True)["groups"]),1)
    def test_separate_service(self):
        result=analyze([f"2026-01-01T00:00:00Z ERROR {s} Failed" for s in ["api","worker"]])
        self.assertEqual(len(result["groups"]),2)
    def test_timeline_sorted(self):
        result=analyze([f"2026-01-01T00:0{n}:10Z ERROR api Failed" for n in [2,1,2]])
        self.assertEqual([x["count"] for x in result["timeline"]],[1,2])
    def test_empty(self):
        self.assertEqual(analyze([])["error_rate"],0)
    def test_html_escaped(self):
        report=html_report(analyze(["2026-01-01T00:00:00Z ERROR api <script>alert(1)</script>"]),"<title>")
        self.assertNotIn("<script>",report)
        self.assertIn("&lt;script&gt;",report)
    def test_uuid(self):
        self.assertEqual(fingerprint("id 123e4567-e89b-12d3-a456-426614174000"),"id <uuid>")
    def test_invalid_field_type(self):
        result=analyze(['{"timestamp":1,"level":"INFO","service":"x","message":"x"}'])
        self.assertEqual(result["skipped"],1)
    def test_long_line(self):
        self.assertEqual(analyze(["a"*65537])["skipped"],1)
    def test_cli_writes_reports(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"test.log";path.write_text("2026-01-01T00:00:00Z INFO api Ready\n")
            self.assertEqual(main([str(path),str(Path(folder)/"out")]),0)
            self.assertTrue((Path(folder)/"out"/"report.html").exists())
    def test_input_protected(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"summary.json";path.write_text("hello")
            self.assertEqual(main([str(path),folder]),2)
            self.assertEqual(path.read_text(),"hello")
    def test_unknown_mode(self):
        self.assertEqual(main(["file","out","unknown"]),2)

if __name__ == "__main__":
    unittest.main()
