# Red_College ("Red's")

A static dashboard of first-year undergrad application deadlines and requirements for US and Canadian schools.
Live site (GitHub Pages): https://ben77g.github.io/Red_College/

## Current schools (Fall 2027 entry)
McGill, University of Toronto (St. George), UBC Vancouver, University of Michigan, UCLA.

## How it works
- Everything is in one file, `index.html` (no build step, no dependencies).
- School data is the `SCHOOLS` array near the bottom of the file. Each school has deadlines (`l` label, `d` ISO date, `u:1` if unconfirmed), fee, test policy, documents, English requirement and an official URL.
- The page shows the next 12 deadlines across schools (with days left), plus a card per school. There is a country filter and a search box.
- To preview locally: open `index.html` in a browser, or run `python3 -m http.server` in this folder.
- To add a school: copy an object in `SCHOOLS`, edit it, commit and push to `main`. Pages redeploys automatically.

## Data notes (compiled 2026-10-09)
- Core deadlines for McGill, U of T, UBC and UCLA were read from official pages.
- Michigan deadlines and the fee came mostly from secondary pages (umich.edu blocked the fetch). Marked unconfirmed on the site.
- Unconfirmed: U of T fee, UCLA and Michigan fees, English score minimums for McGill, U of T, UCLA, UBC early deadline (Dec 1), McGill Quebec CEGEP dates.
- Not covered: UTSC/UTM specific dates, UCLA supplemental application deadlines, IB/AP and Canadian-curriculum details, program extras at McGill and UBC.
- Dates change every cycle. Re-check official pages and update before relying on them.

## Gaps / todo
- Verify the unconfirmed items above against official pages.
- Add more schools.
