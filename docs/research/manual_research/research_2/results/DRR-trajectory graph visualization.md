## 1. Recommended graph design
- **Primary:** Plot **relative excess return** (%) on the yâ€‘axis vs calendar date on the xâ€‘axis. Show one line per horizon (1d, 5d, 10d, 20d, 60d), each colored or patterned by horizon. Place each predicted point at its actual *label_window_end* date. Use actual *excess return* values (model prediction vs realized) rather than raw prices.  This avoids implying price levels or trading targets.
- **Alternatives (max 2):**
  - **Normalized scores:** Convert each horizonâ€™s excess return to a percentile or z-score and plot those, to highlight outliers. (E.g. â€œthis 1d return was in the 90th percentile of all 1d returns.â€)
  - **Rank-encoded lines:** Plot each horizonâ€™s rank or quantile (0â€“1 range) of return instead of the raw value. This emphasizes relative performance across horizons.
- **Rejected:** Plotting actual stock price or cumulative price is unsuitable (confuses trajectory vs actual market path). Likewise, showing future fan charts or buy/sell signals is explicitly out of scope.

## 2. Existing-artifact refinements
- **Use current columns (display-only):**
  - Color-code by `horizon` using the marker tableâ€™s `horizon` field.
  - Use different markers/line styles for â€œpredictedâ€ vs â€œactual realizedâ€ points (the artifact schema already has `prediction` vs `label`).
  - If `label` is present (realized return), plot that point; if not, plot the modelâ€™s `prediction` at the same date as a hollow or dashed marker.
  - Add tooltips or annotations from existing fields (e.g. `ticker`, `percentile`) without needing new data.
- **Requires schema changes:** (only if absolutely needed and approved)
  - If we want an explicit â€œbaseline 0%â€ line or a horizon group label, it might require deriving a fixed line (can be computed in display).
  - Showing percentiles *already available* doesnâ€™t require new columns, since the packet has `percentile_rank` columns for market hurdle and model per horizon.
- **No change needed:** All refinements (colors, markers, annotations) can be done client-side from the existing `trajectory_points` table and Stage 10C report JSON. No new provider or inference data is required.

## 3. Date and horizon alignment rules
- **Marker placement:** A model prediction row has an `as_of_date` and a `horizon_id` (e.g. 5d). Its predicted point should be placed at `label_window_end` (the date corresponding to as_of_date + 5 trading days). The realized label (if available) also falls on `label_window_end`.
- **Alignment of prior predictions:** For each horizon, align all markers along their true calendar date (not offset). For example, a 5d prediction made on Jan 10 goes on Jan 15 (label end), and its actual Jan 15 return is plotted at Jan 15 as well. This visually separates *time of model run* (as_of) from *outcome date* (label end).
- **Validation checks:**
  - For every row, verify `label_window_end == as_of_date + horizon` (respecting trading calendars).
  - Ensure `split_role` is `validation` or `lockbox` (not train/purged). Only display outâ€‘ofâ€‘sample predictions.
  - Check that `prediction` and `label` are on the same rowâ€™s horizon.
  - Confirm no duplicate markers: each (as_of_date,horizon) pair is unique.
  - (Optional test) Each plotted pointâ€™s date matches the stored `label_window_end`.

## 4. Caveat wording
Include a concise caption or legend note, for example:

> *â€œThese lines show historical model outputs (excess returns) by horizon. As-of dates are on the xâ€‘axis; points are placed at each label windowâ€™s end. StageÂ 6 found **no reliable predictive signal** (clean-null result), and provider data gaps limit cross-horizon comparisons (limitation-bearing). This view is **not** a future price forecast or trading recommendation.*â€

This preserves the required elements (historical data only, clean-null, limitation-bearing) and explicitly denies price targets/trading advice.

## 5. Out of scope
Make it explicit in the report or docs (e.g., footnote) that we are **not** showing or implying: projected price paths, fan charts, buy/sell signals, live forecasts, or any fresh provider data fetch. We also do **not** extend schema beyond what StageÂ 10C currently provides. All content must come from the existing trajectory marker tables.
