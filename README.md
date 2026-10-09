# Red_College ("Red's")

A static dashboard of first-year undergrad application deadlines and requirements, written for one applicant profile: a Canadian citizen attending a US high school (US curriculum, AP, SAT/ACT available).
Live site (GitHub Pages): https://ben77g.github.io/Red_College/

## Current schools (Fall 2027 entry)
McGill, University of Toronto (St. George), UBC Vancouver, University of Michigan, UCLA.

## How it works
- Everything is in one file, `index.html` (no build step, no dependencies).
- School data is the `SCHOOLS` array near the bottom of the file. Each school has deadlines (`l` label, `d` ISO date, `u:1` if unconfirmed), fee, test policy, documents, English requirement and an official URL.
- Layout: deadlines list on the left (all upcoming deadlines across schools, with days left; clicking one opens that school), school icons on the right. Clicking an icon expands it to full width and shows its details (deadlines, fee, tests, documents, English, a "For you" box). Click again to close. Stacks to one column on narrow screens.
- Icons are colored monogram badges (the `BRAND` object in the script), not official logos. Add an entry there for each new school id.
- There is a country filter and a search box.
- To preview locally: open `index.html` in a browser, or run `python3 -m http.server` in this folder.
- To add a school: copy an object in `SCHOOLS`, edit it, commit and push to `main`. Pages redeploys automatically.

## Applicant profile (set 2026-10-09)
- Canadian citizen, US high school. Each school card has a blue "For you" box (the `you` field) on fee status, aid and tuition.
- Canada: U of T and UBC give domestic status to Canadian citizens abroad (UBC unconfirmed); McGill would use the out-of-province Canadian rate.
- US (Michigan, UCLA): a Canadian citizen who is not a US citizen or permanent resident, or who needs a visa, is likely international: no FAFSA or need-based aid, nonresident tuition. Red's actual US status was not given, so the page says to confirm with each school. If Red is a US permanent resident, update the `you` text and add back FAFSA dates (UCLA Mar 2, Michigan Early Decision aid Nov 15).
- Removed as irrelevant for this profile: UBC International Scholars Program (Nov 15), McGill Quebec CEGEP dates, UCLA FAFSA/Cal Grant date.

## Data notes (compiled 2026-10-09)
- Core deadlines for McGill, U of T, UBC and UCLA were read from official pages.
- Michigan deadlines and the fee came mostly from secondary pages (umich.edu blocked the fetch). Marked unconfirmed on the site.
- Unconfirmed: U of T fee and OUAC form/codes, UCLA and Michigan fees, English exemption wording for U of T and UBC, Michigan English exemption (needs test score), UBC early deadline (Dec 1) and scholarship eligibility, McGill AP credit and undergraduate out-of-province rate.
- Not covered: UTSC/UTM specific dates, UCLA supplemental application deadlines, IB/AP and Canadian-curriculum details, program extras at McGill and UBC.
- Dates change every cycle. Re-check official pages and update before relying on them.

## Gaps / todo
- Verify the unconfirmed items above against official pages.
- Add more schools.
