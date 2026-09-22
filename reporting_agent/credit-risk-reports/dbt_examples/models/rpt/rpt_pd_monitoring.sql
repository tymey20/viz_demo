-- One row per as_of_date x portfolio x segment. Metrics computed upstream in Python/dbt.
select as_of_date, portfolio, segment, n_obligors, gini, ks, psi, predicted_dr, observed_dr
from {{ ref('int_pd_monitoring_metrics') }}
