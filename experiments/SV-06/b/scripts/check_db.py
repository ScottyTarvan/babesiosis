"""Run the check query of run-instructions.md step 3 for this part's code."""
import pyodbc, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from write_db import odbc_conn_str
c = pyodbc.connect(odbc_conn_str()).cursor()
c.execute("""SELECT e.experiment_code, e.method, e.run_at, COUNT(r.result_id) AS results,
       SUM(CASE WHEN r.result_kind = 'interpretation' THEN 1 ELSE 0 END) AS interpretation
FROM dbo.experiment AS e LEFT JOIN dbo.experiment_result AS r ON r.experiment_id = e.experiment_id
WHERE e.experiment_code = 'SV-06-02-ds07-candidate-tests'
GROUP BY e.experiment_code, e.method, e.run_at""")
for row in c.fetchall(): print(" | ".join(str(x) for x in row))
