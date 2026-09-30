# Rifqah — Grounded LLM Tourism Experiment

## LLM provider selection

### Compact request payload

Anchor selection now maximizes total activity relevance subject to the original whole-group budget and distinct daily feasibility constraints. Ties maximize total quality, then minimize cost, then use lexicographically sorted ItemIds. Scores are compared at the existing ten-decimal ranking precision. An exact branch-and-bound search selects the set; date matching assigns its members to days. The cheapest-feasible witness is only an internal feasibility check/search seed and is not forced into either candidate payload. This preserves city eligibility and city scoring. The exact search can take longer on larger, tightly constrained pools.

The India October 15-17 offline regression confirms identical city rankings/scores in Basic and WVS, while Buraydah's compact WVS payload now includes Al-Uqailat Museum (SAR 30 group cost) instead of forcing lower-relevance free anchors. See outputs/anchor_relevance_audit.json for full before/after sets.

Scheduling guidance now explicitly computes finish = start + ceil(DurationMinutes), enforces opening/day boundaries and transfer buffers, and requires omitting any activity without a legal slot. Finishing exactly at closing/day_end is allowed, matching the unchanged validator. Overnight closing is interpreted as next day but never extends the daily planning window.

Every supplied activity has per-date scheduling_windows with schedulable and earliest/latest start times, or a reason it cannot fit. These advisory checks examine each activity alone; they do not guarantee that multiple activities fit together with transfers. They do not remove or rerank candidates. The compact payload view and saved experiment expose these annotations. Timing-only validation failures are explicitly rejected. No repair pass or automatic retry is implemented.

MAX_LLM_ACTIVITIES_PER_CITY defaults to 5. This affects only the provider payload; full retrieval, WVS scores, and diagnostics remain unchanged. The compact subset retains existing daily feasibility witnesses, then fills slots in retrieval order. If trip_days exceeds this cap, the app asks for a larger cap before any API request; it never silently violates the limit.

Only planning fields, essential suitability, resolved WVS affinities, factual inputs and planning constraints are sent. Descriptions, evidence tables, city distributions, mapping diagnostics and score breakdowns remain local. Validation receives the exact compact candidate subset, so omitted IDs cannot be accepted. Saved runs contain both retrieval and llm_candidate_package plus request_size. The UI displays them separately.

Request-size diagnostics report city/activity counts, UTF-8 payload bytes and an approximate input-token estimate (characters/4 including system prompt and schema). This is not provider tokenization or a guarantee of fitting TPM limits; provider accounting may include the unchanged output-token allowance.

Set LLM_PROVIDER=openai or LLM_PROVIDER=groq. If omitted, openai preserves existing behavior. Unsupported values fail with a clear configuration error. Only the selected provider's credentials and model are required:

```dotenv
LLM_PROVIDER=groq
GROQ_API_KEY=
GROQ_MODEL=openai/gpt-oss-120b
OPENAI_API_KEY=
OPENAI_MODEL=
```

Groq mode does not require OPENAI_MODEL or OPENAI_API_KEY. The active provider/model appear in UI diagnostics and experiment records. Missing credentials leave offline retrieval available. No automatic provider fallback is performed.

The Groq adapter uses the existing OpenAI SDK with Groq's official compatible Responses endpoint, https://api.groq.com/openai/v1, as documented in [Groq Responses API](https://console.groq.com/docs/responses-api). No additional SDK dependency is needed. The candidate package, system prompt, strict response schema, retrieval, WVS scoring and independent validator are unchanged. Use a model supporting strict Structured Outputs. OpenAI continues to use its original endpoint. Both adapters disable retries and sanitize exception class, HTTP status, error type/code/message, request ID and Retry-After before UI display or storage; keys are redacted. Provider calls are mocked in tests.

This POC observes how an optional WVS-derived cold-start prior changes grounded candidate retrieval and an LLM's destination/itinerary choices. Deterministic code does **not** make the final destination decision.

## Architecture

```text
Same factual tourist inputs (+ WVS prior in one arm)
                    |
        Candidate filtering and ranking
                    |
       Multiple candidate cities + activities
                    |
             OpenAI Responses API
                    |
         LLM selects destination + itinerary
                    |
       Independent deterministic validator
```

Filtering before the LLM grounds the experiment, reduces context size, applies factual constraints, limits opportunities to invent places, and makes the two arms inspectable. The highest retrieval score is not a final recommendation. Tests explicitly allow the provider to select a lower-ranked supplied city.

Existing tourism cleaning, WVS source loading/eligibility, category mappings, normalized scoring, date/budget feasibility matching, and validation rules are reused. No LLM generates source prices, durations, coordinates, or IDs.

## Run with the existing environment

```powershell
cd D:\Rfqh\smart-saudi-trip-planner-poc
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8501
```

Open http://127.0.0.1:8501. The app binds locally; Streamlit telemetry is disabled. Do not recreate or commit .venv.

Set these variables in the process environment or the existing ignored .env file:

```dotenv
OPENAI_API_KEY=your-own-key
OPENAI_MODEL=your-chosen-responses-model
TOP_CITY_CANDIDATES=4
ACTIVITIES_PER_CITY=8
OPENAI_TIMEOUT_SECONDS=90
OPENAI_MAX_OUTPUT_TOKENS=6000
WVS_SCORING_METHOD=normalized_relative
```

The selected model must support Responses and Structured Outputs. There is no silent model substitution. Process environment values override .env. .env.example contains empty credential/model fields and non-secret defaults. Credentials are never included in candidate packages, saved experiment records, or error messages.

The OpenAI provider follows the official [Structured Outputs guide](https://developers.openai.com/api/docs/guides/structured-outputs): strict JSON schema via Responses text.format. Requests use store=false, no tools/web search, a fixed official API endpoint, and no automatic retries. Incomplete responses, refusals, malformed JSON, and API errors are reported without producing a deterministic replacement itinerary.

## Inputs and experiment modes

The tourist supplies only:

- Birth Country
- Required Start Date and End Date; inclusive trip days are computed automatically
- Total group activity budget
- Number of adults and children
- Optional youngest and oldest traveler ages

There is no destination, city, interest, tourism-category, or indoor/outdoor input. Hybrid mode has been removed from the experiment.

**Basic / No WVS:** factual inputs -> candidate filtering/ranking -> LLM destination and itinerary.

**WVS Cold-Start:** exactly the same facts + WVS prior -> candidate filtering/ranking -> LLM destination and itinerary.

“Run experiment” runs one selected arm. “Compare both modes” runs both with the same immutable facts, candidate limits, provider, model, and prompt. If configured, comparison makes two sequential API requests. Submitted facts and the displayed bounded candidate packages are sent to OpenAI. The app never sends the whole inventory.

Research question: **How does adding a WVS-derived cold-start behavioral prior affect the candidate set and the destination/itinerary generated by the LLM?**

Observed differences do not demonstrate that WVS mode is better. LLM variability, weak/unvalidated WVS mappings, inventory quality and truncation can all affect results. The comparison changes both retrieval ranking and the prior supplied to the LLM; it does not isolate those two mechanisms.

## Candidate retrieval

1. Reuse validated source rows; deduplicate ItemIds and normalized city/activity names deterministically.
2. Apply active status, usable opening hours, required date overlap, age bounds when supplied, adult/child suitability, and whole-group affordability.
3. Build normalized city category/environment/budget profiles. Group fit accounts for both the compatible share of the city's available inventory and the group's mean suitability.
4. Use the existing minimum-cost activity/day matching to require at least one distinct, affordable visit on every requested day. Feasibility is a constraint, not a score bonus. No qualifying city means no LLM request.
5. Rank eligible cities for retrieval relevance. Keep up to TOP_CITY_CANDIDATES (default 4, configurable 1–5).
6. For each city, retain its feasibility-witness activities, then fill remaining slots with its highest-scoring activities. This avoids truncating away the only cheap/date-compatible choices.
7. Limit activities to max(ACTIVITIES_PER_CITY, trip days), default 8 per city, configurable 1–20. Thus a 14-day request can retain at least 14 distinct activities. Maximum supported context is 5 × 20 = 100 activities, never all 821.
8. Send the compact package to the LLM. It contains no selected_destination or prebuilt itinerary.

The exact package is visible and downloadable, with per-city counts and JSON byte size. Fewer than the configured number of cities/activities may be available; the app reports this rather than inventing records. The October 15-17, 2026 India sample (two adults, SAR 1,000) prepares 4 cities and 25 activities per arm.

City scores average compatibility, rather than rewarding inventory counts. Ties use city name; activity ties use ItemId. A city with more equally compatible records does not receive a higher score simply for having more rows.

## Retrieval weights

These weights rank **candidates only**, not the final destination. All components are bounded 0–1; score = 100 × weighted sum.

| Retrieval component | Basic / No WVS | WVS Cold-Start |
| --- | ---: | ---: |
| Budget compatibility | Hard constraint only | Hard constraint only |
| Group suitability | 62.5% | Constraint only |
| Source popularity/rating | 37.5% | 90% |
| WVS category match | 0% | 5% |
| WVS hobby match | 0% | 2.5% |
| WVS environment match | 0% | 2.5% |

The WVS arm is 90% source quality and 10% WVS prior. Group and budget remain eligibility constraints in WVS mode. Basic retains its existing 62.5% group and 37.5% quality ranking. These are POC heuristics, not calibrated performance claims.

- Budget: exclude individually unaffordable activities and cities without an affordable distinct visit for every day. Lower price provides no retrieval score bonus. Minimum-cost feasibility witnesses are retained when bounding context.
- City group fit: 50% fraction passing factual group constraints plus 50% mean adult/child suitability weighted by traveler counts. Individual activity group fit uses its own suitability.
- Quality: 0.6 × PopularityScore + 0.4 × AvgRating / 5. This is source appeal, not evidence confidence.
- WVS category/environment: mean eligible affinity corresponding to each candidate activity.
- WVS category/hobby: deterministic item metadata rules in profiles.py refine broad categories before falling back to category mappings. Mapped domains are averaged independently; weights remain unchanged. These semantic links are POC assumptions, not learned relationships.

Missing optional suitability scores use neutral 0.5. Explicit false/zero suitability is a hard exclusion for a traveler group that is present. Positive source scores are ranking signals; no uncalibrated threshold is invented. Without supplied ages, only categorical adult/child impossibilities can be excluded, and exact age bounds are labeled not fully checked.

## WVS evidence

The loader retains HOBBY_RESULTS, CATEGORY_RESULTS, ENVIRONMENT_RESULTS and the diagnostic STATISTICAL_EFFECTS sheet. Evidence tables preserve absolute signal, global baseline, Relative vs Global (pp), Raw N, Effective N, Question Coverage (%), eligibility and rank.

The raw_affinity option uses relative evidence:

```text
delta = Relative vs Global (pp) / 100
affinity = 0.5 + (coverage / 100) × clamp(delta, -0.5, 0.5)
```

Thus coverage shrinks the relative signal toward neutral. Missing, unmapped, duplicate, or ineligible evidence is neutral 0.5. Used rows must meet the existing source eligibility flag, have positive sample sizes/rank and coverage, valid numeric ranges, and consistent signal-minus-baseline arithmetic. Category aliases collapsing to one tourism category are averaged.

Country of birth (Q266) is not confirmed nationality. WVS group signals are not literal individual preferences or percentages of people preferring a hobby. The prompt enforces these limits. Basic mode receives no WVS profile, rows, or WVS scoring components. Statistical effect sizes are displayed for inspection, not multiplied into scores.

## LLM output and validation

The LLM must choose a supplied city, give brief decision summaries, name a supplied alternative when possible, and return days containing actual ISO calendar dates, ItemIds, start times and short activity reasons. The schema's city/ItemId enums are derived only from the package. Cross-city and factual correctness still require independent validation.

The validator rejects:

- Cities outside the supplied set
- Unknown or unvalidated ItemIds, and existing IDs not supplied to the LLM
- Activities belonging to another city
- Repeated IDs or normalized attraction names
- Inactive records and factual traveler-suitability violations
- Group-budget overruns
- Missing/duplicate/out-of-range trip days, date/day mismatches, calendar dates outside the trip range, or more than three activities per day
- Invalid start times, overlaps, insufficient buffers, opening-hour violations and unusable travel dates

All names, durations, prices and calculated end times displayed in a validated itinerary come from source records. Invalid outputs are retained with violation details for research, but are never displayed as an accepted final itinerary or silently repaired.

Planning assumptions: one city; 09:00–22:00 daily window; maximum three visits/day; 30-minute transfer allowance. It is not a driving-route optimizer. Overnight closing can mean the next day, but visits must end within the daily window. Early-morning continuation from a prior day's opening is not modeled.

GroupCost = source Price × (adults + children), assumed SAR per traveler without child discounts. Hotels, meals and transport are excluded. Start Date and End Date are required. Trip days = (End Date - Start Date).days + 1. End Date must not precede Start Date. The existing 14-day planning limit remains. No live price, opening-hour or booking verification is performed.

## Side-by-side results and storage

Every submitted run is stored as a unique JSON file under outputs/experiments/ and remains downloadable in the UI. That directory is ignored by Git. Records contain:

- Same factual tourist inputs and mode-specific candidate packages
- Candidate cities, activities, retrieval components, limits and package sizes
- City/item candidate overlap (Jaccard plus differing IDs)
- Raw LLM-selected destination, selected IDs and output metadata, when available
- Itinerary overlap, duplicate IDs/names, invalid/unsupplied IDs and constraint violations
- Validated category/environment counts, total cost and scheduled duration
- Retrieval, LLM and total latency; provider/model, prompt version, response ID and usage

Unavailable LLM results and overlap metrics are null, not fabricated empty or zero results. Invalid LLM outputs remain distinguishable from validated outputs. No API key is stored. These local records do contain the submitted facts; do not publish them unintentionally.

## Without an API key

Candidate filtering/ranking, WVS inspection, full package downloads, side-by-side candidate-set comparison, source audits, and tests remain available.

Real destination selection and itineraries require both OPENAI_API_KEY and OPENAI_MODEL plus working API access. Missing credentials/configuration or provider errors do not trigger a runtime mock. The only stubs live under tests/ and are explicitly marked TEST MOCK.

## Tests and offline source audit

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -B -m scripts.build_audit
.\.venv\Scripts\python.exe -B scripts\inspect_sources.py
```

All automated provider calls are mocked, including Streamlit tests. Tests verify multiple candidate cities, no deterministic final decision, both retrieval modes, relative WVS influence, context bounds, lower-ranked LLM city choice, invalid/unsupplied IDs, duplicates, factual constraints, sanitized API failures, optional ages and required date ranges, persistence and comparison.

build_audit is offline and never loads API credentials. It writes source quality artifacts and example_candidate_comparison.json using India, two adults, three days starting June 1, 2026, and a SAR 1,000 group budget. It does not generate a final destination or itinerary. Older example_itinerary files, if present from the preceding implementation, are historical deterministic artifacts and are not used by this architecture.

## Source preservation and files

The original tourism CSV, WVS workbook and source DOCX remain read only. Validation still retains 611 of 821 tourism rows, with 210 quarantined and 289 validated active records. Their hashes are recorded in outputs/quality_summary.json. The app reuses trip_planner/data.py and scripts/inspect_sources.py.

| File | Responsibility |
| --- | --- |
| trip_planner/engine.py | Reused factual constraints, feasibility matching and candidate scoring |
| trip_planner/profiles.py | Relative WVS inference and weak retrieval weights |
| trip_planner/retrieval.py | Multiple-city shortlist and bounded candidate packages |
| trip_planner/llm.py | Grounded prompt, strict schema and real OpenAI provider |
| trip_planner/validation.py | Independent post-LLM checks |
| trip_planner/experiment.py | Orchestration, comparison metrics and persisted records |
| trip_planner/settings.py | Safe environment and .env configuration |
| app.py | Factual-only two-mode UI and side-by-side inspection |
| tests/ | Mocked retrieval/provider/validation/UI regression suite |

The repository is not committed or pushed by any script. .env, .venv, bytecode/caches, Streamlit secrets and private experiment records are ignored.

## Required dates and source normalization

### Semantic crosswalk audit

Mapping uses case-insensitive word-boundary rules on ItemName and ItemDescription. Explicit water activities take precedence over hiking, then broad-category shopping, food/entertainment, and nature/scenery rules. Mountain scenery alone does not imply Hiking. Generic urban/family/leisure/adventure records remain neutral without sufficient metadata. Museums and heritage metadata refine cultural hobby matches. Mixed food/entertainment averages only domains evidenced in the metadata, consistently for category and hobby. These English keyword rules are explainable heuristics; ambiguous, multilingual or incidental descriptions can require further review.

WVS candidate packages and the UI mapping-debug expander show matched category/hobby keys, affinities, environment, normalized tourism category and the rule used. Basic mode does not use WVS mappings. Missing evidence and unmapped records retain neutral 0.5. The mapping-only audit below was performed before the experimental normalized default was enabled.

Run `.\\.venv\\Scripts\\python.exe -B -m scripts.audit_mapping` for the offline India/Canada comparison. `outputs/mapping_audit.json` contains eligible-item mappings, full city score decompositions, candidate activities, and before/after overlap. The October 15-17 sample still has identical four-city and 25-activity candidate membership across Basic, India WVS and Canada WVS after mapping corrections.

The pipeline is source quality/active validation -> stable deduplication -> date overlap -> group/age and usable hours -> budget feasibility -> candidate relevance (WVS prior only in WVS mode) -> bounded candidates -> LLM -> independent validator. Both modes share every factual filter. Budget is not a preference for cheaper activities.

Source columns are AvailableDate, EndDate, StartTime, EndTime and Is_year_Around. AvailableDate contains 41 YYYY-MM-DD values, 735 M/D/YYYY values, 10 M/D/YYYY H:MM values and 35 boolean-like invalid values. All 821 EndDate values parse as M/D/YYYY. There are 74 reversed date intervals, 45 invalid opening-hour records and 14 equal/ambiguous opening-hour records; counts can overlap other quality issues. ISO datetime strings are also accepted by the parser. No boolean, numeric serial, missing value or malformed date is guessed.

Invalid/missing/reversed source date bounds remain quarantined, including rows marked year-round. For otherwise valid rows, Is_year_Around=TRUE explicitly overrides the source date interval with normalized 0001-01-01 through 9999-12-31: available on every supported trip date, still constrained by opening hours and other factual checks. These are calendar bounds, not a live operating guarantee. FALSE retains the inclusive source interval. Invalid year-round flags are quarantined. Raw files are unchanged.

Each candidate carries City, available_from, available_until, opens, closes and availability_policy alongside grounded IDs, category/environment, price, group cost, duration, suitability and scores. The package carries trip_start, trip_end and trip_days. The provider must schedule each supplied activity only on an available date. Validation checks the actual returned date independently and requires it to match the numbered day.

Sample: India, October 15-17, 2026, two adults, no children, SAR 1,000: **821 source -> 611 validated -> 289 active -> 270 distinct before date filtering -> 165 date-overlapping -> 4 candidate cities -> 25 supplied activities**, in both modes. Full format counts and sample statistics are in outputs/date_inspection.json. Regenerate without API calls using:

```powershell
.\.venv\Scripts\python.exe -B -m scripts.inspect_dates
```

The UI requires both dates and displays the computed duration and actual filtering counts after submission. Optional ages remain optional; calendar dates are mandatory. Date-based itinerary CSV exports retain the source-derived details. Tests include exact overlap boundaries, partial/no overlap, malformed and boolean-like dates, year-round behavior, calendar/day validation, same-mode factual filters, and budget checks.

## Experimental WVS scoring default

WVS_SCORING_METHOD accepts normalized_relative (default) or raw_affinity. Set it in .env or the process environment; process settings take precedence. Both WVS methods use 90% quality, 5% category, 2.5% hobby and 2.5% environment. The raw switch restores raw affinity calculation, not the historical group-weighted WVS formula. Basic behavior and every eligibility filter remain unchanged.

normalized_relative is EXPERIMENTAL. WVS remains a weak prior; this method has not been validated against real tourism behavior. Relative-vs-Global is transformed only to improve retrieval separation, not to estimate individual preferences or confidence.

Within each country and source domain, subtract the mean eligible Relative-vs-Global value, divide by the largest absolute centered value, then compute affinity = 0.5 + 0.5 * centered_scaled_signal * coverage/100. Zero spread is neutral. Normalization happens before category alias averaging and item mapping. Source values and raw affinities are retained in evidence diagnostics. Ineligible evidence is still excluded. This transformation amplifies within-country contrasts, discards absolute distance from global, and is sensitive to outliers and small domains (especially three environments).

The UI and saved candidate_package.scoring report method, wvs_weight and experimental status. Full retrieval_weights and normalization parameters are saved alongside evidence. Existing saved experiments retain the settings used when they ran.

Offline confirmation for October 15-17, 2026, SAR 1,000 and two adults: India selects Farasan, Unaizah, Buraydah, Jazan; Canada selects Unaizah, Buraydah, Farasan, Tabuk. Their mean shortlisted source-quality values are 0.89873125 and 0.900825 respectively. Eligibility counts remain 289 active, 270 distinct active, and 165 date-overlapping. See outputs/experimental_default_audit.json.
