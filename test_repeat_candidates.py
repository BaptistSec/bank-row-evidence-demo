import csv
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from repeat_candidates import candidates, main, money

class RepeatTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
    def tearDown(self):
        self.temp.cleanup()
    def write(self, name, rows, balance=True, bom=False):
        path = self.root / name
        header = 'Date,Description,Amount' + (',Balance' if balance else '') + '\n'
        path.write_text(header + rows, encoding='utf-8-sig' if bom else 'utf-8')
        return path
    def test_same_file_identical_rows_not_flagged(self):
        a=self.write('a.csv','2026-10-06,Coffee,-3.00,97.00\n'*2)
        self.assertEqual(candidates([a]),[])
    def test_cross_file_same_balance(self):
        a=self.write('a.csv','2026-10-06,Coffee,-3.00,97.00\n')
        b=self.write('b.csv','2026-10-06,Coffee,-3.00,97.00\n')
        self.assertEqual(len(candidates([a,b])),1)
    def test_cross_file_different_balance(self):
        a=self.write('a.csv','2026-10-06,Coffee,-3.00,97.00\n')
        b=self.write('b.csv','2026-10-06,Coffee,-3.00,94.00\n')
        self.assertEqual(candidates([a,b]),[])
    def test_missing_balance_only_candidate(self):
        a=self.write('a.csv','2026-10-06,Coffee,-3.00\n',False)
        b=self.write('b.csv','2026-10-06,Coffee,-3.00,97.00\n')
        self.assertEqual(candidates([a,b])[0]['reason'],'balance unavailable')
    def test_same_path_rejected(self):
        a=self.write('a.csv','2026-10-06,Coffee,-3.00,97.00\n')
        with self.assertRaises(ValueError): candidates([a,a])
    def test_nan_rejected(self):
        a=self.write('a.csv','2026-10-06,Coffee,NaN,97.00\n')
        with self.assertRaises(ValueError): candidates([a])
    def test_three_decimals_rejected(self):
        a=self.write('a.csv','2026-10-06,Coffee,-3.001,97.00\n')
        with self.assertRaises(ValueError): candidates([a])
    def test_ambiguous_date_rejected(self):
        a=self.write('a.csv','06/10/2026,Coffee,-3.00,97.00\n')
        with self.assertRaises(ValueError): candidates([a])
    def test_bom_and_quoted_comma(self):
        a=self.write('a.csv','2026-10-06,"Coffee, station",-3.00,97.00\n',bom=True)
        b=self.write('b.csv','2026-10-06,"Coffee, station",-3.00,97.00\n')
        self.assertEqual(len(candidates([a,b])),1)
    def test_duplicate_headers_rejected(self):
        a=self.root/'a.csv'; a.write_text('Date,Description,Amount,Amount\n')
        with self.assertRaises(ValueError): candidates([a])
    def test_extra_column_rejected(self):
        a=self.write('a.csv','2026-10-06,Coffee,-3.00,97.00,extra\n')
        with self.assertRaises(ValueError): candidates([a])
    def test_original_bytes_unchanged(self):
        a=self.write('a.csv','2026-10-06,Coffee,-3.00,97.00\n')
        before=a.read_bytes(); candidates([a]); self.assertEqual(before,a.read_bytes())

    def test_infinity_rejected(self):
        a=self.write('a.csv','2026-10-06,Coffee,Infinity,97.00\n')
        with self.assertRaises(ValueError): candidates([a])
    def test_blank_description_rejected(self):
        a=self.write('a.csv','2026-10-06,   ,-3.00,97.00\n')
        with self.assertRaises(ValueError): candidates([a])
    def test_blank_balance_rejected(self):
        a=self.write('a.csv','2026-10-06,Coffee,-3.00,\n')
        with self.assertRaises(ValueError): candidates([a])
    def test_missing_column_rejected(self):
        a=self.write('a.csv','2026-10-06,Coffee,-3.00\n')
        with self.assertRaises(ValueError): candidates([a])
    def test_invalid_day_rejected(self):
        a=self.write('a.csv','2026-02-30,Coffee,-3.00,97.00\n')
        with self.assertRaises(ValueError): candidates([a])
    def test_unicode_digits_rejected(self):
        a=self.write('a.csv','2026-10-06,Coffee,-٣.00,97.00\n')
        with self.assertRaises(ValueError): candidates([a])
    def test_description_case_not_normalised(self):
        a=self.write('a.csv','2026-10-06,Coffee,-3.00,97.00\n')
        b=self.write('b.csv','2026-10-06,COFFEE,-3.00,97.00\n')
        self.assertEqual(candidates([a,b]),[])
    def test_multiline_record_number(self):
        a=self.write('a.csv','2026-10-06,"Coffee\nstation",-3.00,97.00\n2026-10-07,Tea,-2.00,95.00\n')
        b=self.write('b.csv','2026-10-07,Tea,-2.00,95.00\n')
        self.assertEqual(candidates([a,b])[0]['earlier']['record'],3)
    def test_cli_success_json_and_unchanged(self):
        a=self.write('a.csv','2026-10-06,Coffee,-3.00,97.00\n')
        b=self.write('b.csv','2026-10-06,Coffee,-3.00,97.00\n')
        before={p:p.read_bytes() for p in (a,b)}
        out,err=io.StringIO(),io.StringIO()
        with contextlib.redirect_stdout(out),contextlib.redirect_stderr(err):
            result=main([str(a),str(b)])
        self.assertEqual(result,0)
        self.assertEqual(len(json.loads(out.getvalue())),1)
        self.assertIn('No rows removed',err.getvalue())
        self.assertNotIn('Coffee',out.getvalue())
        self.assertEqual(before,{p:p.read_bytes() for p in (a,b)})
    def test_cli_bad_input_no_partial_stdout(self):
        a=self.write('a.csv','2026-10-06,Coffee,-3.00,97.00\n')
        b=self.write('b.csv','2026-10-06,Coffee,-3.00,97.00\n2026-10-07,Tea,NaN,95.00\n')
        out,err=io.StringIO(),io.StringIO()
        with contextlib.redirect_stdout(out),contextlib.redirect_stderr(err):
            result=main([str(a),str(b)])
        self.assertEqual(result,2)
        self.assertEqual(out.getvalue(),'')
        self.assertIn('Input rejected',err.getvalue())
    def test_cli_file_missing(self):
        out,err=io.StringIO(),io.StringIO()
        with contextlib.redirect_stdout(out),contextlib.redirect_stderr(err):
            result=main([str(self.root/'absent.csv')])
        self.assertEqual(result,2)
        self.assertEqual(out.getvalue(),'')

    def test_unterminated_quote_rejected(self):
        a=self.write('a.csv','2026-10-06,"Coffee,-3.00,97.00\n')
        with self.assertRaises(csv.Error): candidates([a])
    def test_both_missing_balance(self):
        a=self.write('a.csv','2026-10-06,Coffee,-3.00\n',False)
        b=self.write('b.csv','2026-10-06,Coffee,-3.00\n',False)
        self.assertEqual(candidates([a,b])[0]['reason'],'balance unavailable')

    def test_leading_zero_and_negative_zero_are_allowed(self):
        self.assertEqual(money('003.00'),money('3.00'))
        self.assertEqual(money('-0.00'),money('0.00'))
    def test_full_width_digits_rejected(self):
        with self.assertRaises(ValueError): money('３.00')

if __name__ == '__main__': unittest.main()
