-- Governed reporting mart: one row per as_of_date x lob x segment.
-- All aggregation happens here or upstream. reportkit only selects and filters.
select as_of_date, lob, segment, exposure_mm, revenue_mm, raroc, hurdle
from {{ ref('int_client_profitability_monthly') }}
