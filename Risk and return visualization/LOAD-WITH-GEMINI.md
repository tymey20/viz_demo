# Loading your real data with Gemini

You don't have to share your data with anyone. You give Gemini your export
(CSV / Excel / whatever) **plus the prompt below**, and it returns a finished
`deals-data.js`. Drop that file into this folder, replacing the one that's
here, and open the dashboard. Done — it runs offline, no internet needed.

---

## Step 1 — Get your data ready
Any tabular export works (CSV is easiest). One row per deal. You need, at
minimum, columns for: line of business, industry, net income, and blended
capital. Exposure and risk rating are strongly recommended. Tenor, spread,
and product mix are optional bonuses.

## Step 2 — Paste this prompt into Gemini, then attach your file

> You are converting a portfolio export into a JavaScript data file for a
> dashboard. I will attach my deal-level data.
>
> Produce a single file named `deals-data.js`. It must contain exactly one
> statement: `window.DEALS = [ ... ];` — an array with **one object per deal**.
>
> Map my columns to these object fields:
> - `lob` (required): the line of business name as a string. Use your own
>   internal LOB names exactly as they appear in my data — the dashboard picks
>   up whatever LOBs are present and gives each its own filter, series, and
>   color. Just keep the naming consistent (don't write the same LOB two
>   different ways).
> - `industry` (required): the industry/sector name as a string.
> - `netIncome` (required): net income in absolute dollars (number, no `$` or commas).
> - `blendedCapital` (required): blended/total capital in absolute dollars.
> - `exposure` (recommended): exposure/EAD/commitment in absolute dollars.
> - `rating` (recommended): risk rating as a number on a 1–10 scale where 1 is
>   best and 10 is worst. If my scale is different, convert it to 1–10.
> - `id` (optional): a deal identifier string if I have one.
> - `robc` (optional): Return on Blended Capital in percent, only if my data
>   already has it; otherwise omit it and it will be derived.
> - `tenor` (optional): tenor in years as a number.
> - `spread` (optional): spread in basis points as a number.
> - `mix` (optional): if I have product/revenue mix, output it as
>   `mix: { lending, deposits, ep, capmkts }` with numeric shares (any units;
>   they'll be normalized). `lending` = lending balances, `deposits` =
>   deposits/DDA, `ep` = electronic payments, `capmkts` = capital markets.
>   Omit entirely if I don't have it.
>
> Rules:
> - Output ONLY the contents of `deals-data.js` in one code block. No commentary.
> - All dollar fields are absolute dollars, not millions. Strip `$` and commas.
> - Omit any optional field you can't fill rather than guessing.
> - Keep going until every row in my file is included.
>
> Here is my data:  *(attach your CSV/Excel)*

## Step 3 — Save the result
Copy Gemini's output into a file called `deals-data.js` and put it in this
folder, replacing the existing `deals-data.js`.

## Step 4 — Open the dashboard
Open `Risk Return Dashboard.dc.html`. The header badge should turn green and
read **"Live data · N deals"**. If it still says "Sample data", the array
didn't load — check that the file is named exactly `deals-data.js` and that it
starts with `window.DEALS = [`.

---

### Tips
- **Large files are fine** — thousands of deals load instantly.
- **Don't rename the file.** The dashboard loads `./deals-data.js` by name.
- If a chart looks off, the most common cause is the same LOB written two
  different ways (e.g. "Inst. Banking" vs "Institutional Banking"), which makes
  it show up as two separate lines of business — open `deals-data.js` and make
  the `lob` values consistent.
- The schema is also documented at the top of `deals-data.js` itself.
