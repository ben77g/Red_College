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
- No visible header/title banner (removed on request); a visually hidden h1 stays for screen readers.
- Theme: girly and frilly (pink polka-dot background, script headings, hearts and bows). All CSS is in the `<style>` block.
- Progress bar: each opened school has a grass-green bar with a black outline and a pink SVG unicorn (`UNICORN_SVG`). The bar is TIME based: it fills from `SEASON_START` (Aug 1, 2026, when Common App and the UC application open) to the school's target date in `TARGETS` (McGill, U of T, UBC Jan 15, 2027; Michigan Regular Decision Feb 1, 2027; UCLA Nov 30, 2026). The unicorn moves right as the deadline gets closer, and it is computed from today's date when the page loads. Change a target in `TARGETS`, or use a different start by editing `SEASON_START`. Below the bar is an optional personal checklist (`TASKS`, saved in this browser's localStorage as `red_tasks_v1`); it no longer moves the bar.
- Password gate: a big green dragon fills the screen with the password box in its mouth (`#gate` in the HTML, `PASSWORD` constant in the last script). A wrong password shakes the dragon. A right one (not case sensitive) makes the dragon rumble, fire bursts out of its mouth and floods the screen, then the site appears. The unlock is remembered per browser tab (sessionStorage `red_unlocked`), so a refresh does not ask again, but a new tab or visit does. NOT secure: the password is plain text in index.html and the page content is in the public repo. It only stops casual visitors.
- There is a country filter and a search box.
- To preview locally: open `index.html` in a browser, or run `python3 -m http.server` in this folder.
- To add a school: copy an object in `SCHOOLS`, edit it, commit and push to `main`. Pages redeploys automatically.

## Applicant profile (updated 2026-10-09)
- US and Canadian dual citizen attending a US high school. Each school card has a blue "For you" box (the `you` field) on fee status, aid and tuition.
- Canada: Canadian citizenship gives domestic status at U of T and UBC (UBC unconfirmed). McGill: Red likely qualifies for Quebec resident tuition under Quebec "Situation 8" (Canadian citizen who has never lived in Canada and takes up residence in Quebec; needs a sworn statement, 10-year activity proof and 3 months of Quebec residence). Unconfirmed that living in Quebec only to study counts. Ask McGill Student Accounts. Quebec rate was $103.92/credit vs $432.85/credit out-of-province for 2026-27. Source: https://www.mcgill.ca/legaldocuments/quebec/situation8
- US (Michigan, UCLA): US citizenship means a domestic applicant, FAFSA and need-based aid eligibility, no international rules. Red is a California resident (in-state at UCLA, out-of-state at Michigan) and has never lived in Canada.
- History: the first version assumed a Canadian-only citizen who might be international at Michigan/UCLA. That text was removed when the dual citizenship was confirmed. UBC International Scholars Program, McGill Quebec CEGEP dates and the international fee notes stay out as irrelevant.

## Data notes (compiled 2026-10-09)
- Core deadlines for McGill, U of T, UBC and UCLA were read from official pages.
- Michigan deadlines and the fee came mostly from secondary pages (umich.edu blocked the fetch). Marked unconfirmed on the site.
- Unconfirmed: U of T fee and OUAC form/codes, UCLA and Michigan fees, English exemption wording for U of T and UBC, Michigan English exemption (needs test score), UBC early deadline (Dec 1) and scholarship eligibility, McGill AP credit and undergraduate out-of-province rate.
- Not covered: UTSC/UTM specific dates, UCLA supplemental application deadlines, IB/AP and Canadian-curriculum details, program extras at McGill and UBC.
- Dates change every cycle. Re-check official pages and update before relying on them.

## Gaps / todo
- Verify the unconfirmed items above against official pages.
- Add more schools.
