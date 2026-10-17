# Route / Score Optimizer Using Binary Search

Python + Flask web app that finds optimal answers with **binary search on the answer** and compares it to a linear-scan baseline.

## Problems supported
| Type | Question | Search direction |
|---|---|---|
| `capacity` | Smallest daily capacity to ship packages (in order) within D days | minimize |
| `speed` | Slowest speed to finish all tasks within H hours | minimize |
| `spacing` | Largest possible minimum distance between K chosen stops | maximize |

Each has a monotonic feasibility check, so binary search needs O(log R) checks versus O(R) for the baseline (R = size of the search range).

## Run
```
pip install -r requirements.txt
python app.py          # open http://127.0.0.1:5000
python -m unittest discover -s tests -v
```

## Modules
1. Input and Validation: `validation.py`
2. Binary Search Algorithm: `solver.py` (`binary_search`, `linear_search`)
3. Optimization / Result Calculation: `solver.py` (`build_problem`, `solve`)
4. Frontend Dashboard: `templates/index.html`, `static/`
5. Backend API: `app.py` (`POST /api/solve`, `GET /api/history`), SQLite `history.db`
6. Testing and Performance Analysis: `tests/test_all.py` (brute-force cross-check, validation, API, checks-count report)

## Example
Packages `1,2,3,4,5,6,7,8,9,10`, 5 days, gives capacity **15**.
The baseline is skipped automatically when the range is too large to scan quickly.
