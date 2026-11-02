"""Tests for the SRIM -> LAMMPS stopping-table converter."""
import importlib.util
import unittest
from pathlib import Path

POT = Path(__file__).resolve().parents[2] / "client" / "potentials"
_spec = importlib.util.spec_from_file_location("srim_to_lammps", POT / "srim_to_lammps.py")
srim = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(srim)

HEAD = " Stopping Units =  eV/Angstrom \n"
ROWS = ("9.99999 eV    6.856E-01  5.815E+00       2 A         1 A         1 A   \n"
        "  1.00 keV   5.000E+00  1.000E+02       8 A         6 A         4 A   \n"
        "  2.00 keV   7.000E+00  1.500E+02      10 A         8 A         5 A   \n")
JUNK = "  2.00 keV   7.000E+00  1.500E+02      10 A         8 A         5 A   \n  1.50 keV   6.0E+00  1.2E+02  9 A    A   40 A\n   5.00"


class TestSrimToLammps(unittest.TestCase):
    def test_keeps_electronic_column_in_ev(self):
        self.assertEqual(srim.convert(HEAD + ROWS, 2000.0), [(9.99999, 0.6856), (1000.0, 5.0), (2000.0, 7.0)])

    def test_trailing_wine_junk_is_dropped(self):
        self.assertEqual(len(srim.convert(HEAD + ROWS + JUNK, 2000.0)), 3)

    def test_truncated_table_or_wrong_units_rejected(self):
        with self.assertRaises(ValueError):
            srim.convert(HEAD + ROWS, 20000.0)
        with self.assertRaises(ValueError):
            srim.convert(ROWS, 2000.0)

    def test_repo_table_is_the_converted_srim_output(self):
        rows = srim.convert((POT / "srim2013_W_in_W.txt").read_text(), 20000.0)
        data = [tuple(map(float, l.split())) for l in (POT / "stopping_W.dat").read_text().splitlines() if not l.startswith("#")]
        self.assertEqual(len(data), len(rows))
        self.assertAlmostEqual(data[-1][1], 30.66)


if __name__ == "__main__":
    unittest.main()
