# Lemlist `/database/people` & `/database/companies` Filters

Live spec from `GET /database/filters` (verified 2026-05-06).
Full schema with values: `database-filters-spec.json` next to this file.

## Filter Object Shape
```json
{ "filterId": "<id>", "in": ["..."], "out": ["..."] }
```
Both `in` and `out` accept arrays. `out` required-but-can-be-empty `[]`. Combining two filterIds is AND. Values within one filter's `in` are OR.

## Pagination & Response Shape
`page` (1-indexed), `size` (1-100, max 100 per Lemlist limit).

Response (verified 2026-05-21):
```json
{ "results": [...], "total": 0, "took": 175, "page": 1, "size": 5,
  "search": "lsh_...", "limitation": 4997, "team": "tea_..." }
```
- `results` is the leads array (NOT `people`/`data`); `total` = full match count.
- `search` = per-query handle (prefix `lsh_`), minted fresh on every POST.
- `took` = query duration in ms.
- `limitation` = remaining daily-search quota (body-level counterpart to the `x-daily-search-limit` header).
- Discovery results carry **NO email** — email requires the paid enrichment endpoints (`findEmail` etc., cost credits).

## Filter Catalog (39 total)

### Lead Identity
| filterId | Type | Notes |
|---|---|---|
| `leadsByIds` | elasticId | Lookup by lemlist `_id` |
| `username` | text | Full name |
| `leadLinkedInUrl` | text | Contact LinkedIn URL |
| `leadLinkedInSlug` | text | Slug only |

### Role / Title
| filterId | Type | Notes |
|---|---|---|
| `currentTitle` | autocomplete | Substring match on current job title |
| `currentTitleWithExactMatch` | autocomplete | Exact match (use for narrow titles) |
| `pastTitle` | autocomplete | Past role |
| `seniority` | select | **Enum (7):** `Entry-Level`, `Mid-Level (Individual Contributor)`, `Upper Mid-Level / Experienced IC`, `People Management / Leadership`, `Department Leadership`, `Executive Leadership`, `Ownership / Firm Leadership` |
| `department` | select | Enum (~30): `Accounting`, `Administrative`, `Arts and Design`, `Business Development`, `Community and Social Services`, `Consulting`, `Education`, `Engineering`, `Entrepreneurship`, `Finance`, `Healthcare Services`, `Human Resources`, `Information Technology`, `Legal`, `Marketing`, `Media and Communication`, `Operations`, `Product Management`, `Program and Project Management`, `Purchasing`, `Quality Assurance`, `Real Estate`, `Research`, `Sales`, … |
| `currentPositionTenure` | select | `Less than 6 months`, `6 months to 1 year`, `1 to 3 years`, `3 to 5 years`, `More than 5 years` |
| `yearsOfExperience` | select | `less than 1 year`, `1 to 2 years`, `2 to 5 years`, `5 to 10 years`, `More than 10 years` |

### Profile / Personal
| filterId | Type | Notes |
|---|---|---|
| `keyword` | text | Free text — matches headline + summary + skills |
| `skill` | autocomplete | Specific LinkedIn skill |
| `interest` | autocomplete | Interests |
| `numberOfConnections` | select | Connection count buckets |
| `schoolName` | text | University / school |
| `schoolDegree` | text | Degree |
| `location` | autocomplete | City / state of person |

### Geo
| filterId | Type | Notes |
|---|---|---|
| `country` | autocomplete | Lead country |
| `region` | select | `Europe`, `Western Europe`, `Southern Europe`, `Northern Europe`, `Eastern Europe`, `Balkans`, `DACH`, `America`, `North America`, …, `Asia`, `East Asia`, `Southeast Asia`, `South Asia`, `Middle East`, `Oceania` |

### Company Filters (apply to lead's current company)
| filterId | Type | Notes |
|---|---|---|
| `currentCompany` | autocomplete | Specific company name |
| `currentCompanyByIds` | text | by lemlist company `_id` |
| `currentCompanyHeadcount` | select | `1-10`, `11-50`, `51-200`, `201-500`, `501-1000`, `1001-5000`, `5001-10000`, `10001+` |
| `currentCompanySubIndustry` | level | Hierarchical industry tree (20 top-level: `Manufacturing`, `Technology, Information and Media`, `Financial Services`, `Hospitals and Health Care`, `Construction`, `Retail`, `Wholesale`, `Education`, `Transportation, Logistics, Supply Chain and Storage`, `Oil, Gas, and Mining`, `Utilities`, `Professional Services`, `Government Administration`, `Real Estate and Equipment Rental Services`, `Consumer Services`, `Entertainment Providers`, `Holding Companies`, `Farming, Ranching, Forestry`, `Administrative and Support Services`, `Accommodation Services`). Sub-levels accepted as values. |
| `currentCompanyRevenue` | select | `$0 - $500K`, `$500K - $1M`, `$1M - $3M`, `$3M - $5M`, `$5M - $10M`, `$10M - $20M`, `$20M - $30M`, `$30M+` |
| `currentCompanySizeGrowth` | slider | 6m growth % range |
| `currentCompanyFounded` | slider | Founded year range |
| `currentCompanyMarket` | select | `B2C`, `B2B`, `B2B/B2C` |
| `currentCompanyType` | select | `Public Company`, `Privately Held`, `Nonprofit`, `Educational Institution`, `Educational`, `Partnership`, `Self Employed`, `Self Owned`, `Government Agency`, `Sole Proprietorship` |
| `currentCompanyTechnologies` | autocomplete | Tech stack tag |
| `currentCompanyLastFundingRoundAt` | select | Time since last funding round buckets |
| `currentCompanyCountry` | autocomplete | Company country |
| `currentCompanyRegion` | select | Same enum as `region` |
| `currentCompanyLocation` | autocomplete | Company city / state |
| `currentCompanyLinkedInUrl` | text | exact URL |
| `currentCompanyWebsiteUrl` | text | exact URL |
| `keywordInCompany` | text | Free text — matches company description / about |

### Companies-Only Mode
| filterId | Type | Notes |
|---|---|---|
| `companiesByIds` | elasticId | by company `_id` |
| `numberOfLeadsPerCompany` | slider | Filter companies by lead-count in DB |

## Critical Pitfalls

1. **Seniority enum changed.** Old labels (`CxO`, `Director`, `Vice President`, `Owner/Partner`, `Experienced Manager`, `Manager`, `Senior`, `Entry level`, `in Training`) **no longer match**. Use the 7 levels above.
2. **Industry filter exists** — `currentCompanySubIndustry` (level type, hierarchical). Don't fold industries into `keyword` — that's substring match and hits unrelated profiles (the "Samsung-fridge vs AirArabia-fridge" problem).
3. **`keyword` matches profile-level** (headline + summary + skills). For company-level keyword match use `keywordInCompany`.
4. **`out[]` must be present** in every filter object even if empty.
5. **Combining filters is AND across filterIds, OR within `in[]`.**
6. **`pastTitle`** lets you target people who used to be at competitor companies — useful for poach-style outreach.
7. **`currentPositionTenure`** lets you target newly hired execs (< 6 months) — strong buying-trigger signal.
8. **Legacy LinkedIn industry strings are DEAD** (verified 2026-05-21). `currentCompanySubIndustry` uses LinkedIn's *current* taxonomy. Old values like `Computer Software`, `Internet`, `Industrial Manufacturing` silently match nothing. Verified-live equivalents: `Technology, Information and Internet`, `Technology, Information and Media`, `Business Consulting and Services`, `Software Development`, `Machinery Manufacturing`, `Industrial Machinery Manufacturing`, `Motor Vehicle Manufacturing`, `Pharmaceutical Manufacturing`. **Never guess subIndustry strings — look them up via `GET /database/filters` (tree at `filters[].filterId == "currentCompanySubIndustry"`).**
9. **Off-taxonomy values fail SILENTLY — no error.** An invalid filter value returns HTTP `200` with `{"results":[],"total":0}`, not a `400`/`422`. Because filterIds are AND-ed, a single stale value zeroes the entire result set with zero feedback. When a search unexpectedly returns 0, isolate each filter (run them one at a time) to find the dead value before trusting an "empty market" conclusion.
