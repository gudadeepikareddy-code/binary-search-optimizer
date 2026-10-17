"""Testing module: compares binary search against brute force on random inputs,
checks validation, the API, and prints a small performance analysis.
Run:  python -m unittest discover -s tests -v   (from the project folder)"""
import os
import random
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["BSO_DB"] = os.path.join(tempfile.mkdtemp(), "test.db")

from solver import days_needed, hours_needed, solve, stops_placed  # noqa: E402
from validation import validate  # noqa: E402
import app as app_module  # noqa: E402


class SolverTests(unittest.TestCase):
    def test_known_examples(self):
        self.assertEqual(solve("capacity", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5)["answer"], 15)
        self.assertEqual(solve("capacity", [3, 2, 2, 4, 1, 4], 3)["answer"], 6)
        self.assertEqual(solve("speed", [3, 6, 7, 11], 8)["answer"], 4)
        self.assertEqual(solve("spacing", [1, 2, 4, 8, 9], 3)["answer"], 3)

    def test_matches_brute_force(self):
        rnd = random.Random(1)
        for _ in range(300):
            n = rnd.randint(2, 9)
            w = [rnd.randint(1, 30) for _ in range(n)]
            d = rnd.randint(1, n)
            exp = next(c for c in range(max(w), sum(w) + 1) if days_needed(w, c) <= d)
            self.assertEqual(solve("capacity", w, d)["answer"], exp)

            h = rnd.randint(n, n + 20)
            exp = next(s for s in range(1, max(w) + 1) if hours_needed(w, s) <= h)
            self.assertEqual(solve("speed", w, h)["answer"], exp)

            pos = rnd.sample(range(1, 60), n)
            k = rnd.randint(2, n)
            sp = sorted(pos)
            exp = max(x for x in range(1, 60) if stops_placed(sp, x) >= k)
            self.assertEqual(solve("spacing", pos, k)["answer"], exp)

    def test_baseline_agrees_and_binary_search_is_cheaper(self):
        r = solve("capacity", list(range(1, 201)), 7)
        self.assertTrue(r["baseline"]["matches"])
        self.assertLess(r["binary_search"]["checks"], r["baseline"]["checks"])

    def test_performance_report(self):
        print("\nchecks needed (binary vs linear):")
        for n in (50, 100, 300, 5000):
            r = solve("capacity", list(range(1, n + 1)), 10)
            lin = r["baseline"].get("checks", "skipped (too slow)")
            print(f"  n={n:5d}  binary={r['binary_search']['checks']:3d}  linear={lin}")


class ValidationTests(unittest.TestCase):
    def bad(self, **kw):
        clean, errs = validate(kw)
        self.assertIsNone(clean)
        self.assertTrue(errs)

    def test_rejects(self):
        self.bad(problem="nope", values="1,2", param=1)
        self.bad(problem="capacity", values="1,abc", param=1)
        self.bad(problem="capacity", values="1,-2", param=1)
        self.bad(problem="capacity", values="1,2", param=5)
        self.bad(problem="speed", values="3,6,7", param=2)
        self.bad(problem="spacing", values="1,1,2", param=2)
        self.bad(problem="capacity", values="1,2", param="")

    def test_accepts(self):
        clean, errs = validate({"problem": "capacity", "values": "1, 2 3", "param": "2"})
        self.assertEqual(clean, ("capacity", [1, 2, 3], 2))
        self.assertEqual(errs, [])


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.c = app_module.app.test_client()

    def test_solve_and_history(self):
        r = self.c.post("/api/solve", json={"problem": "speed", "values": "3,6,7,11", "param": 8})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["result"]["answer"], 4)
        self.assertEqual(self.c.get("/api/history").get_json()[0]["answer"], 4)

    def test_bad_input_400(self):
        r = self.c.post("/api/solve", json={"problem": "speed", "values": "x", "param": 8})
        self.assertEqual(r.status_code, 400)
        self.assertFalse(r.get_json()["ok"])
        self.assertEqual(self.c.post("/api/solve", data="junk").status_code, 400)

    def test_index(self):
        self.assertEqual(self.c.get("/").status_code, 200)


if __name__ == "__main__":
    unittest.main()
