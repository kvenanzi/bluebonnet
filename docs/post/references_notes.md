# Citation check

Each source cited in `README.md` was checked on 6 November 2026 by Claude agents: the DOI and metadata against Crossref, whether the source supports the sentence that cites it (with the supporting passage quoted), and whether that was judged from the full text, the abstract only, or a secondary description. The post was then corrected to match. The sentences quoted under "Post" are from the draft before correction.

## Citation check, group A: results

Checked 6 November 2026. All metadata was checked against the Crossref API (`https://api.crossref.org/works/<doi>`). Some publisher sites (Wiley/ESA, AMS, OUP, Allen Press/KGL Meridian, ScienceDirect) returned HTTP 403 or a Cloudflare challenge to automated fetching. I did not try to get around those blocks. Where that happened, the evidence level below is what I could actually read.

## Summary

| item | metadata OK | support | evidence level | action needed |
|---|---|---|---|---|
| A1 Went 1949 | Yes | **Not verified** (25 mm / 10 mm not found in this paper) | Metadata only; no text of the paper read. Secondary sources only, and they conflict | Get the full text before keeping the numbers, or reword (see below) |
| A2 Beatley 1974 | Yes | Yes (minor: "usually") | Abstract only | Optional: add "usually" |
| A3 Davis et al 1991 | Yes (Crossref says "Jerry Persons"; the paper copy says "Jerry Parsons", which matches the post) | **Partly** | Full text (reproduction on plantanswers.com, the co-author's site; its abstract matches Crossref word for word) | Reword: "only some sprout in any one autumn" is not in the paper; 85–95% applies to 3 of 4 lots; it is a greenhouse emergence study |
| A4 Turner et al 2018 | Yes (online 12 Dec 2017, issue 2018) | **Partly** | Abstract only | Reword: "much of what people see" is not supported, and the authors hedge on cause ("may be explained by") |
| A5 Ropelewski & Halpert 1986 | Yes | **Partly** | Abstract only | Reword: the abstract names "parts of the southeastern United States and northern Mexico", not Texas |
| A6 Phillips et al 2009 | Yes | **Partly** | Full text (author-distributed PDF at whoi.edu) | Narrow "standard correction": the paper is about choosing background points for distribution models, not dividing counts |
| A7 Callaghan et al 2021 | Yes (Sci Rep 11:19073) | **No** (as worded) | Full text (Europe PMC, PMC8463711) | Reword: the paper is about birds and found **no evidence** that colorful species were over-represented |
| W1 LBJWC 2025 forecast | URL resolves (25 Feb 2025) | **Partly** | Full page | Reword: it is a forecast of a "mixed" season, thin in the west and strong in the east |
| W2 Fox 7, 18 Mar 2026 | URL resolves; date correct | Yes | Full page | None (optional small wording note) |
| W3 LBJWC plant page | URL resolves | **Partly** | Full page | Reword: the page does not say "sprouts in autumn", "flat" or "early May" |
| W4 CPC ENSO discussion, Sept 2026 | Found: issued **10** (not 11) September 2026 | **Partly** | Full page | Reword: El Niño was already under way (an Advisory was in force), and the >90% was for a **very strong** event |

---

## A1. Went 1949

**Post:** "In the Mojave Desert, about 25 mm of rain at the right time produced heavy germination of winter annuals while about 10 mm produced little (Went 1949)"

**Metadata (Crossref):** Went, F. W. "Ecology of Desert Plants. II. The Effect of Rain and Temperature on Germination and Growth". *Ecology* 30(1):1–13, January 1949. doi:10.2307/1932273 resolves to this work. All fields in the post are correct.

**Support:** Not verified. I could not read any text of this paper. Wiley/ESA returned 403, JSTOR is not free for 1949, and OpenAlex, Unpaywall, Europe PMC and Internet Archive had no open copy. The paper also has no abstract in Crossref or OpenAlex.

What I found from secondary sources (not checked against the original):
- A web-search summary of a ScienceDirect review (*Journal of Arid Environments*, pii S0140196318311832, "Responses of Chihuahuan Desert herbaceous annuals to rainfall augmentation"; the page itself returned 403) credits the 10 mm vs 25 mm contrast to **Went 1948**, not 1949: rains "slightly over 10 mm did not initiate germination, whereas rains of over 25 mm were completely effective". It credits Went 1949 only for the general suggestion of about 25 mm. I saw this only as a search-engine summary, so it is not a reliable quote.
- A UNLV course page (https://landau.faculty.unlv.edu/adaptations.htm) says: "Went noted that no seedlings of any species germinated in the Sonoran Desert following a 10 mm rainfall; extensive germination occurred only after a rainfall of 25 mm." It gives no year, and it says **Sonoran**, not Mojave.
- Went 1948 is "Ecology of Desert Plants. I. Observations on Germination in the Joshua Tree National Monument, California", *Ecology* 29(3):242–253, doi:10.2307/1930988 (metadata checked on Crossref). Joshua Tree lies where the Mojave and Colorado (Sonoran) deserts meet.

**Evidence level:** Metadata only. I found no support for the 25 mm and 10 mm figures in Went 1949 itself.

**Action:** Either (a) get the PDF of Went 1949 (and probably Went 1948) through a library or JSTOR login and confirm the numbers, the desert and the year, or (b) replace the sentence with one that a source I did read supports. Beatley 1974's abstract (see A2) supports this:

> "In the Mojave Desert, the growth of winter annuals usually follows a heavy rain of more than 25 mm in autumn (Beatley 1974)"

That drops the 10 mm comparison, which I could not verify from any primary source.

## A2. Beatley 1974

**Post:** "germination there [Mojave] depends on a large enough fall rain inside a seasonal window (Beatley 1974)"

**Metadata (Crossref):** Beatley, Janice C. "Phenological Events and Their Environmental Triggers in Mojave Desert Ecosystems". *Ecology* 55(4):856–863, July 1974. doi:10.2307/1934421. Correct.

**Support:** Yes. The abstract (from OpenAlex) says, word for word:

> "Phenological events in Mojave desert systems are triggered by heavy rains (>25 mm [1 in]). The most predictable and consequential of these is a regional rain between late September and early December. This rainfall event is usually the precursor of successful vegetative and reproductive growth of shrubs the next spring, and is usually necessary for all growth phenomena of herbaceous perennials and winter annuals during the following winter and spring."

It also says: "Under certain conditions rainfall during other seasons may trigger growth and reproduction of the primary producers". The study area is the Mojave Desert of southern Nevada (13 years of records).

**Evidence level:** Abstract only. Wiley/ESA returned 403.

**Action:** Optional. To match the abstract's "usually": "germination there usually depends on a large enough fall rain inside a seasonal window (Beatley 1974)".

## A3. Davis et al 1991

**Post:** "Its seeds have a hard coat that keeps out water, so only some of them sprout in any one autumn. In one study, untreated seed lots sprouted at 16–71%, and treating the coat with acid raised that to 85–95% (Davis et al 1991)"

**Metadata (Crossref):** Davis, Tim D.; George, Steven W.; Upadhyaya, Abha; "Persons", Jerry. "Improvement of Seedling Emergence of Lupinus texensis Hook. Following Seed Scarification Treatments". *Journal of Environmental Horticulture* 9(1):17–21, March 1991. doi:10.24266/0738-2898-9.1.17. The full-text copy prints "Jerry Parsons", which matches the post. The Crossref spelling looks like a Crossref error, so keep "Parsons". Everything else is correct.

**Support:** Partly.
- Hard coat that keeps out water. Supported: "acid scarification improved emergence by removing a physical barrier (i.e. the hard seed coat that is impermeable to water) rather than by removing a chemical inhibitor from the seed."
- 16–71%. Supported: "Only 16 and 23% of the non-scarified seeds emerged after one month for the A and C lots, respectively (Table 2). In contrast, 50 and 71% of the non-scarified seeds emerged after one month for the B and D lots, respectively."
- 85–95%. Supported, but only for 3 of the 4 lots: "Emergence was promoted by acid scarification in three of the four seedlots. For the lots that responded to acid scarification, the optimal scarification time was 30-60 minutes which resulted in 85-95% emergence one month after planting." For lot D: "acid scarification for any length of time did not significantly increase seedling emergence compared to non-scarified seed" (its best was 80%).
- "so only some of them sprout in any one autumn". **Not supported.** This was a greenhouse study of commercial seed lots, with emergence counted after one week and one month. It says nothing about the field, about autumn, or about germination being spread across years.
- The study measured seedling "emergence", not sprouting as such. It used concentrated sulfuric acid.

**Evidence level:** Full text. The copy is at https://plantanswers.com/research_lupinus.htm, a reproduction on PLANTanswers, the site of co-author Jerry Parsons. Its abstract matches the Crossref abstract word for word, and it includes Tables 2–4. I did not see the publisher's PDF (403/Cloudflare), so I could not check the page numbers against a printed copy, but Crossref gives 17–21.

**Proposed rewording:**

> "Its seeds have a hard coat that keeps out water, which slows sprouting. In one greenhouse study of four commercial seed lots, 16–71% of untreated seeds came up within a month, and soaking the seeds in acid raised that to 85–95% in the three lots that responded (Davis et al 1991)"

If the post needs the "only some sprout in any one autumn" idea, it needs a separate field-ecology source. I did not find or check one.

## A4. Turner et al 2018

**Post:** "Much of what people see along Texas roads was sown by the state transportation department and the public, which has made wild populations more genetically alike (Turner et al 2018)"

**Metadata (Crossref):** Turner, Kathryn G; Huang, Daisie I; Cronk, Quentin C B; Rieseberg, Loren H. "Homogenization of Populations in the Wildflower, Texas Bluebonnet (Lupinus texensis)". *Journal of Heredity* 109(2):152–161. Published online 12 Dec 2017; issue dated 14 Feb 2018. doi:10.1093/jhered/esx094. Correct. Citing it as 2018 for volume 109 is fine.

**Support:** Partly. The abstract says, word for word:

> "Wildflower seeds are routinely spread along highways and thoroughfares throughout North America as part of federal beautification policy, but the genetic effect of the introduction of these cultivated populations on wild populations of the same species is unknown." ... "the Texas bluebonnet (Lupinus texensis), a species popular in commercially available wildflower seed mixes used by both the Texas Department of Transportation and the public." ... "We find a striking lack of population structure both between wild and seeded populations and amongst wild populations. STRUCTURE analyses indicate that all populations are apparently panmictic. This pattern may be explained by extensive swamping of wild populations by seeded germplasm and increased dispersal of semi-domesticated seed across this species' core native range by humans."

- "Much of what people see along Texas roads was sown". Not in the abstract.
- "which has made wild populations more genetically alike". The authors offer this as a possible explanation ("may be explained by"), not as an established cause. They also name a second factor: human dispersal of semi-domesticated seed.
- (A related fact from W2's Fox 7 article: TxDOT sows "approximately 30,000 pounds of wildflower seed annually". That is wildflower seed in general, not bluebonnet alone.)

**Evidence level:** Abstract only. The OUP page showed the abstract and "You do not currently have access to this article". The paper is not in PMC, and I found no preprint.

**Proposed rewording:**

> "The state transportation department and the public sow this species along Texas roads. A genetic study found almost no difference between sown and wild populations, and the authors suggest that sown seed may have swamped the wild populations (Turner et al 2018)"

## A5. Ropelewski & Halpert 1986

**Post:** "El Niño winters tend to be wet in Texas (Ropelewski & Halpert 1986)"

**Metadata (Crossref):** Ropelewski, C. F.; Halpert, M. S. "North American Precipitation and Temperature Patterns Associated with the El Niño/Southern Oscillation (ENSO)". *Monthly Weather Review* 114(12):2352–2362, December 1986. doi:10.1175/1520-0493(1986)114<2352:NAPATP>2.0.CO;2. Correct.

**Support:** Partly. The abstract (from OpenAlex) says, word for word:

> "The analysis shows that above normal precipitation was associated with ENSO in 18 out of 22 cases (81%)in the "season" starting with October of the ENSO year to March of the following year for an area of North America that includes parts of the southeastern United States and northern Mexico."

The abstract does not name Texas. A secondary source in a web-search summary (Kurtzman & Scanlon 2007, *Water Resources Research*, doi:10.1029/2007WR005863; the page returned 403, so I did not read it) describes the paper's Gulf of Mexico region as running from Texas to Florida. I could not confirm that from the paper's map.

A supporting web source I did read is NOAA CPC, "North American Winter Features" (https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/ensocycle/nawinter.shtml): "This shift results in an exceptionally stormy winter and increased precipitation across California and the southern U.S, and less stormy conditions across the northern part of the country."

**Evidence level:** Abstract only. The AMS PDF returned 403 or an empty response.

**Proposed rewording:**

> "El Niño winters tend to be wet in parts of the southeastern United States and northern Mexico (Ropelewski & Halpert 1986)"

Or, to keep Texas, add the CPC link: "El Niño winters tend to be wet across the southern United States (Ropelewski & Halpert 1986; NOAA Climate Prediction Center)". "Southern U.S." is the CPC's wording; the paper's abstract says "southeastern".

## A6. Phillips et al 2009

**Post:** "So I divided the bluebonnet count by the count of photos of any plant taken in the same county on the same days. ... This is a standard correction for this kind of data (Phillips et al 2009)"

**Metadata (Crossref):** Phillips, Steven J.; Dudík, Miroslav; Elith, Jane; Graham, Catherine H.; Lehmann, Anthony; Leathwick, John; Ferrier, Simon. "Sample selection bias and presence-only distribution models: implications for background and pseudo-absence data". *Ecological Applications* 19(1):181–197, January 2009. doi:10.1890/07-2153.1. Correct.

**Support:** Partly. The paper supports the idea behind the correction: records of a broad group of species gathered the same way can stand in for observer effort, and "vascular plants" is named as a suitable group. Word for word:

> "if presence records are derived from natural history collections, records for a broad set of species could be used to estimate survey effort. The set of species should be chosen so as to represent the specimen collection or observation activities of collectors of the target species. In general, the groups should contain species that are all collected or observed using the same methods or equipment; such groups of species are called target groups (Ponder et al. 2001, Anderson 2003). Broad biological groups (birds, vascular plants, and so on) are likely to be suitable. The sites for all records from all species in the target group then make up the full set of available information on survey effort and can be used as background data; we call such a set of sites target-group background."

From the abstract: "We find that target-group background improves average performance for all the modeling methods we consider".

However:
- The method in the paper picks background (pseudo-absence) points for presence-only species distribution models (Maxent, GLM, GAM, boosted regression trees). It does not divide one species' count by an all-species count per county and day. The post's ratio uses the same idea, but it is a different procedure.
- The paper proposes and tests the method. It does not show that the method is "standard". Calling it standard would need later reviews, which I did not check.

**Evidence level:** Full text (17-page PDF of the published article, https://www.whoi.edu/cms/files/Phillips_EcolApp_2009_53454.pdf).

**Proposed rewording:**

> "This uses the same idea as the 'target-group' method, which treats records of a broad group of species collected the same way, such as all plants, as a measure of how hard people were looking (Phillips et al 2009)"

## A7. Callaghan et al 2021

**Post:** "it has a known weakness: showy species get photographed out of proportion to how common they are (Callaghan et al 2021)"

**Metadata (Crossref):** Callaghan, Corey T.; Poore, Alistair G. B.; Hofmann, Max; Roberts, Christopher J.; Pereira, Henrique M. "Large-bodied birds are over-represented in unstructured citizen science data". *Scientific Reports* 11, article 19073, published 24 Sep 2021. doi:10.1038/s41598-021-98584-7. Correct.

**Support:** No, as worded. The paper compares iNaturalist and eBird records of **birds** in the continental US. On color, its finding is the opposite of the post's sentence. From the abstract, word for word:

> "We found strong evidence that large-bodied birds were over-represented in the unstructured citizen science dataset; moderate evidence that common species were over-represented in the unstructured dataset; strong evidence that species in large groups were over-represented; and no evidence that colorful species were over-represented in unstructured citizen science data."

> "Importantly, in programs like iNaturalist the detectability process is two-fold—first, an individual organism needs to be detected, and second, it needs to be photographed, which is likely easier for many large-bodied species."

The paper mentions bias toward "charismatic" species, and toward colorful insects, only when citing other studies. From the Introduction: "Even within citizen science projects focused on specific taxa, there can be strong taxonomic biases towards particularly charismatic species or those that are readily identified" (its refs 20–23). From the Discussion: "In other taxa, more colorful insect species are more commonly reported" (ref 68: Caley et al 2020, *J Pest Sci* 93:543–550, doi:10.1007/s10340-019-01115-7, not checked). It says nothing about plants.

**Evidence level:** Full text (Europe PMC, PMC8463711, CC-BY).

**Proposed rewording (fully supported by this paper):**

> "it has a known weakness: some species are recorded out of proportion to how common they are. In birds, for example, large species are over-represented on iNaturalist compared with a more structured survey, probably partly because they are easier to photograph (Callaghan et al 2021)"

**Possible plant-specific source (not verified for content):** Carbone LM, Massi C, Actis Alesina F, Tavella J (2026). "Citizen science contribution to plant diversity knowledge: Insights from iNaturalist in central Argentina". *Flora* 338:152972. doi:10.1016/j.flora.2026.152972. I checked the metadata on Crossref. A web-search summary says it finds iNaturalist plant records biased toward families with abundant and conspicuous species. I could not read the abstract (ScienceDirect 403; no abstract on Crossref or OpenAlex), so **do not cite it without reading it**.

## W1. Lady Bird Johnson Wildflower Center, 2025 forecast

**Post:** "In 2025 the Lady Bird Johnson Wildflower Center attributed a thin bloom to the previous fall's drought"
**URL:** https://www.wildflower.org/pressroom/2025-wildflower-forecast. It resolves to "2025 Wildflower Forecast", dated Feb 25, 2025.

**Support:** Partly. It is a forecast made before the season, not an account of a bloom that had happened. It predicts a mixed season, poor in the west and strong in the east. Word for word:

> "Experts at the Lady Bird Johnson Wildflower Center are predicting a mixed season for spring blooms this year due to the continuing drought in the Edwards Plateau and Trans Pecos according to the Center's Annual Wildflower forecast released today. However, eastern parts of the state are tracking to have a strong showing."

> "The late fall drought will likely hinder this year's early-blooming wildflowers such as Texas bluebonnets ( Lupinus texensis ) and Texas paintbrush ( Castilleja indivisa ) in the western part of the state, says DeLong-Amaya. "Last fall's drought influenced the number of little wildflower plants we have growing out there.""

**Evidence level:** Full page.

**Proposed rewording:**

> "In 2025 the Lady Bird Johnson Wildflower Center predicted fewer bluebonnets in the drier western part of the state and blamed the previous fall's drought"

## W2. Fox 7 Austin, 18 March 2026

**Post:** "in 2026 its staff said a dry fall and a warm winter had produced a moderate, short season"
**URL:** https://www.fox7austin.com/news/texas-experts-predict-moderate-bluebonnet-season-due-dry-fall-warm-winter. It resolves to "Texas experts predict 'moderate' bluebonnet season due to dry fall and warm winter", published March 18, 2026.

**Support:** Yes. Word for word:

> ""Rainfall is a major contributor to the moderate bluebonnet season we're experiencing, but in more ways than one," said Kyle Cheesborough, Director of Gardens at the Wildflower Center. "Most importantly, last fall and winter's low rainfall resulted in fewer plants sprouting.""

> "A warm winter accelerated the growth process, which experts say has shortened the overall window for blooms."

> "The Source: Information in this article is from the Lady Bird Johnson Wildflower Center website, and Kyle Cheesborough, Director of Gardens, Lady Bird Johnson Wildflower Center."

Small note: the "shortened window" point is the reporter's summary of what "experts say", not a direct quote from staff. The staff quote blames low rainfall in both fall and winter.

**Evidence level:** Full page.

**Action:** None needed.

## W3. LBJWC plant database, Lupinus texensis

**Post:** "The Texas bluebonnet (Lupinus texensis) sprouts in autumn, spends the winter as a flat rosette of leaves, and flowers from March to early May"
**URL:** https://www.wildflower.org/plants/result.php?id_plant=lute. It resolves to the species page.

**Support:** Partly. Word for word:

> "Duration: Annual"
> "Bloom Time: Mar , Apr , May"
> "this famous wildflower forms attractive rosettes in winter."
> "Propagate by sowing seed or planting seedlings in fall."
> "Seed Treatment: Scarification will hasten germination."

The page does not say the plant sprouts in autumn (it says to sow in fall), does not call the rosette "flat", and gives May, not "early May".

The W2 Fox 7 article does say: "Bluebonnets typically germinate in the fall and grow their leaf clusters, known as rosettes, throughout the winter."

**Evidence level:** Full page.

**Proposed rewording (supported by the plant page alone):**

> "The Texas bluebonnet (Lupinus texensis) is an annual. It is sown in fall, forms a rosette of leaves in winter, and flowers from March to May"

Or keep "sprouts in autumn" and "spends the winter as a rosette" and add the Fox 7 link for that part. Either way, drop "flat" and "early".

## W4. CPC ENSO Diagnostic Discussion, September 2026

**Post:** "A strong El Niño was expected (the Climate Prediction Center gave it more than a 90% probability)", stated as of 25 September 2026.

**Source found:** https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso_disc_sep2026/ensodisc.shtml. "EL NIÑO/SOUTHERN OSCILLATION (ENSO) DIAGNOSTIC DISCUSSION issued by CLIMATE PREDICTION CENTER/NCEP/NWS **10 September 2026**". It was issued on the 10th, not the 11th. The next discussion was scheduled for 8 October 2026, so this was the latest one on 25 September.

**Support:** Partly. Word for word:

> "ENSO Alert System Status: El Niño Advisory"
> "Synopsis: El Niño is strengthening, with a greater than 90% chance of a very strong event during the Northern Hemisphere fall and winter 2026-27."
> "During the October-December 2026 season, there is a 75% chance of a historic event that would exceed the strength of previous El Niño events dating back to 1950 (+2.5°C or more for a 3-month RONI value )."

- The probability: "greater than 90%" matches "more than 90%".
- Strength: CPC said "**very strong**", not just "strong".
- "Expected": an El Niño Advisory was already in force, meaning El Niño conditions were already present, with Niño-3.4 at +1.8°C in August. The event was under way and expected to strengthen. It was not just expected.

(For reference, the 8 October 2026 discussion, now at the current-discussion URL, says "a strong-to-very strong El Niño likely through January-March 2027 (remaining greater than an 83% chance)".)

**Evidence level:** Full page.

**Proposed rewording:**

> "An El Niño was already under way, and the Climate Prediction Center gave a greater than 90% chance that it would become a very strong event during the fall and winter of 2026–27"


## Group B citation check: methods and software

Checked 2026-11-06. Metadata was checked against the Crossref REST API (`api.crossref.org/works/<doi>`). For JMLR and NeurIPS it was checked against the official proceedings pages. Open copies were found through OpenAlex and downloaded. PDFs were turned into text with pypdf and searched directly, so the quotes below are copied from the source text unless a note says otherwise. Where the only copy available was a WebFetch summary, that is stated.

## Summary

| Ref | Metadata OK | Support | Evidence level | Action needed |
|---|---|---|---|---|
| B1 McMaster & Wilhelm 1997 | Yes (Crossref lists only McMaster as author; the publisher repository lists both) | **Partly** | Abstract only (UNL repository page; PDF blocked) | **Reword**: the paper is about calculating GDD for crops, not about predicting flowering |
| B2 Nosek et al 2018 | Yes | Partly (slight overstatement) | Full text of the author preprint (OSF); key sentences of the published version via PMC (WebFetch) | Optional: "The way" -> "One effective way" |
| B3 Gelman & Hill 2007 | Yes (Crossref print date is 18 Dec 2006; the book is usually cited as 2007) | Yes, but book text not seen | Secondary descriptions only for the book. Full text (preprint) of Gelman 2006, which uses the same radon example | None required. Could add Gelman 2006 as a checkable source |
| B4 Abril-Pla et al 2023 | Yes (14 authors) | Yes | Full text (Europe PMC XML) | None |
| B5 Hoffman & Gelman 2014 | Yes (JMLR 15:1593–1623) | Yes | Full text (JMLR PDF) | None |
| B6 Vehtari et al 2021 | Yes (pages 667–718 include the discussion) | **Partly** | Full text (arXiv v5, 22 Jun 2021, final version) | **Reword**: tie the citation to the 1.01 R-hat threshold, not to "no divergent transitions" |
| B7 Barber et al 2021 | Yes | Yes | Full text (arXiv v3) | None (see the coverage caveat) |
| B8 Gneiting & Raftery 2007 | Yes | Yes | Full text (author-hosted PDF of the published JASA article) | None |
| B9 Hoerl & Kennard 1970 | Yes | Yes (names the method) | Abstract only (OpenAlex) | None |
| B9 Zou & Hastie 2005 | Yes | Yes (names the method) | Full text (Hastie's site, published JRSS-B layout) | None |
| B9 Park & Mazer 2018 | Yes | Yes (precedent for the elastic net in flowering phenology) | Abstract only (PubMed) | None |
| B10 Ke et al 2017 | Yes (pages 3146–3154 appear in the archived official BibTeX; the current proceedings page lists no pages) | Yes | Full text (official NeurIPS PDF) plus the proceedings abstract page | None. Could drop the page numbers or keep them, citing the archived BibTeX |

---

## B1. McMaster & Wilhelm 1997

**Post:** "For timing, accumulated warmth, measured as growing degree days, is the standard predictor of spring flowering (McMaster & Wilhelm 1997)"

**Metadata.** Crossref for 10.1016/S0168-1923(97)00027-0 gives: "Growing degree-days: one equation, two interpretations", *Agricultural and Forest Meteorology* 87(4):291–300, December 1997. Crossref lists only "G McMaster" as author, which is a gap in the publisher's metadata. The UNL Digital Commons record (digitalcommons.unl.edu/usdaarsfacpub/83) lists "McMaster, Gregory S." and "Wilhelm, Wallace", and its note says "Published in Agricultural and Forest Meteorology 87 (1997) 291-300." **Metadata OK.**

**Support: partly.** The paper is about two ways of computing GDD and how they differ for wheat and corn. It never mentions flowering of wild plants or spring flowering. The nearest passages in the abstract are:

> "Heat units, expressed in growing degree-days (GDD), are frequently used to describe the timing of biological processes."

> "The objective of this paper is to show the differences which can result from using these two methods to estimate GDD, and make researchers and practitioners aware of the need to report clearly which method was used in the calculations."

> "Not recognizing the discrepancy between methods can result in confusion and add error in quantifying relationships between heat unit accumulation and timing of events in crop development and growth, particularly in crop simulation models."

The abstract supports "GDD is frequently used to describe the timing of biological processes". It does not support "the standard predictor of spring flowering". Park & Mazer 2018 (B9), which this post also cites, says in its abstract that many phenology studies "have included only a limited set of climate parameters that are often chosen a priori". It also found that, apart from mean maximum temperature, the best predictors of flowering time "have not commonly been included in phenological models". So "the standard predictor" goes further than the sources the post cites.

**Evidence level:** abstract only. The publisher page (ScienceDirect) returned 403, and the UNL PDF is behind a bot check. I read the abstract on the UNL repository page.

**Proposed rewording (fully supported by the abstract):**

> "For timing, accumulated warmth, measured as growing degree days, is frequently used to describe when biological events happen, such as stages of plant development (McMaster & Wilhelm 1997)."

A shorter version: "For timing, a common measure is accumulated warmth, counted as growing degree days (McMaster & Wilhelm 1997)."

If the post needs the specific claim about predicting flowering, it needs a phenology source. I looked for one (for example Chuine & Régnière 2017, *Annu Rev Ecol Evol Syst* 48:159–182, doi:10.1146/annurev-ecolsys-110316-022706, metadata checked in Crossref). Its abstract does not mention degree days, and its open copy on HAL was behind a bot check, so I cannot say it supports the sentence. I am not recommending it.

---

## B2. Nosek et al 2018

**Post:** "The way to check whether it has learned anything is to write the tests down before running them, then make a prediction before the outcome exists (Nosek et al 2018)"

**Metadata.** Crossref gives Nosek BA, Ebersole CR, DeHaven AC, Mellor DT, "The preregistration revolution", *PNAS* 115(11):2600–2606, 2018 (online 12 Mar, print 13 Mar). **OK.**

**Support: partly (yes in substance, with a small overstatement).** From the author preprint (OSF):

> "Progress in science relies in part on generating hypotheses with existing observations and testing hypotheses with new observations."

> "An effective solution is to define the research questions and analysis plan prior to observing the research outcomes–a process called preregistration."

> "In prediction, data are used to confront the possibility that the prediction is wrong."

> "In prediction, the problem of forking paths is avoided because the analytic pipeline is specified prior to observing the data."

The published PMC version (read through WebFetch) words the abstract sentence as "An effective solution is to define the research questions and analysis plan before observing the research outcomes". It defines preregistration this way: "Preregistration of an analysis plan is committing to analytic steps without advance knowledge of the research outcomes."

Nosek calls this "an effective solution". The post says "The way", which is stronger than the source. The rest of the sentence (fix the tests first, predict before the outcome exists) matches the paper.

**Evidence level:** full text of the author preprint (OSF download, 19 pages). For the published version, the abstract and definitions came from PMC via WebFetch. The preprint wording can differ slightly from the published text ("prior to" vs "before").

**Proposed rewording:**

> "One effective way to check whether it has learned anything is to write the tests down before running them, then make a prediction before the outcome exists (Nosek et al 2018)."

---

## B3. Gelman & Hill 2007

**Post:** "County effects are partially pooled, so a county with few records is drawn toward the average county (Gelman & Hill 2007)"

**Metadata.** Crossref for 10.1017/CBO9780511790942 gives the monograph "Data Analysis Using Regression and Multilevel/Hierarchical Models", Gelman A & Hill J, Cambridge University Press, 1st edition, ISBNs 9780521867061 / 9780521686891. Crossref's print date is 18 Dec 2006. The book carries a 2007 copyright and is almost always cited as 2007. **OK.**

**Support: yes, from secondary sources. I did not see the book's own text.** The book's Chapter 12 ("Multilevel linear models: the basics") uses the Minnesota radon data by county. Secondary descriptions (lecture notes and course pages found by search) say it presents multilevel estimates as a compromise between complete pooling and no pooling, with counties that have small samples pulled toward the overall average. The one open copy of Chapter 12 I found (socialinteractionlab.github.io) now returns 404 and has no Wayback snapshot. So I have not read the book's wording.

The same point, with the same example, is in Gelman's companion paper, which I read in full (preprint, 31 Oct 2004):

> "At the other extreme, the no-pooling model overfits the data, for example giving an implausibly high estimate of the average radon levels in Lac Qui Parle County, in which only two observations were available."

> "... whether they take into account the estimation uncertainty of the [county coefficients], as is done in Figure 1 by shrinking toward the complete-pooling estimate."

The bracketed words replace Greek symbols that did not survive text extraction. The complete-pooling estimate is "a common line for all counties", so shrinking toward it means moving toward the all-county average.

**Evidence level:** secondary descriptions for the book itself. Full text (preprint) of Gelman A (2006), "Multilevel (hierarchical) modeling: what it can and cannot do", *Technometrics* 48(3):432–435, doi:10.1198/004017005000000661 (metadata checked in Crossref).

**Action:** the sentence is a textbook statement and is almost certainly in the book, but the post should not say it was checked against the book's text. Either (a) keep the citation and describe it as checked only against secondary descriptions, or (b) add the paper I could check: "(Gelman & Hill 2007; Gelman 2006)". The sentence itself needs no change.

---

## B4. Abril-Pla et al 2023 (PyMC)

**Post:** "Both were fit in PyMC (Abril-Pla et al 2023)"

**Metadata.** Crossref gives "PyMC: a modern, and comprehensive probabilistic programming framework in Python", *PeerJ Computer Science* 9:e1516, 1 Sep 2023, with 14 authors (Abril-Pla, Andreani, Carroll, Dong, Fonnesbeck, Kochurov, Kumar, Lao, Luhmann, Martin, Osthege, Vieira, Wiecki, Zinkov). **OK.**

**Support: yes.**

> "PyMC is a probabilistic programming library for Python that provides tools for constructing and fitting Bayesian models."

This paper also supports B5's point that PyMC uses NUTS:

> "The default sampler for all continuous distributions is based on the No-U-Turn sampler (Hoffman & Gelman, 2014)"

Its footnote 4 says: "This is the first description of the sampler, but the implementation in PyMC includes several improvements that have been developed since then, for example on mass matrix tuning."

**Evidence level:** full text (Europe PMC full-text XML of PMC10495961).

---

## B5. Hoffman & Gelman 2014 (NUTS)

**Post:** "with the No-U-Turn Sampler (Hoffman & Gelman 2014)"

**Metadata.** The JMLR page jmlr.org/papers/v15/hoffman14a.html and the PDF header ("Journal of Machine Learning Research 15 (2014) 1593-1623 Submitted 11/11; Revised 10/13; Published 4/14") give "The No-U-Turn Sampler: Adaptively Setting Path Lengths in Hamiltonian Monte Carlo", Matthew D. Hoffman and Andrew Gelman. **OK.**

**Support: yes.**

> "We introduce the No-U-Turn Sampler (NUTS), an extension to HMC that eliminates the need to set a number of steps L."

**Evidence level:** full text (official JMLR PDF).

---

## B6. Vehtari et al 2021 (R-hat)

**Post:** "The two forecast fits had maximum R-hat 1.007 and 1.004 and no divergent transitions (Vehtari et al 2021)"

**Metadata.** Crossref gives "Rank-Normalization, Folding, and Localization: An Improved R̂ for Assessing Convergence of MCMC (with Discussion)", Vehtari, Gelman, Simpson, Carpenter, Bürkner, *Bayesian Analysis* 16(2):667–718, June 2021. The 667–718 range includes the discussion and rejoinder. **OK.** (Could add "(with Discussion)" to the title.)

**What threshold it recommends: 1.01.** From Section 2, "Recommendations for practice":

> "In Section 4, we propose modifications to R̂ based on rank-normalizing and folding the posterior draws, only using the sample if R̂ < 1.01. This threshold is much tighter than the one recommended by Gelman and Rubin (1992), reflecting lessons learnt over more than 25 years of use, as well as the simulation results in Appendix A."

The same section adds two more conditions:

> "In addition, we recommend running at least four chains by default."

> "To ensure reliable estimates of variances and autocorrelations needed for R̂ and ESS, we recommend requiring that the rank-normalized ESS is greater than 400 ..."

**Does the post's use fit?** The numbers do: 1.007 and 1.004 are both below 1.01. This assumes the values are the rank-normalized split-R̂ from this paper. ArviZ's `az.rhat` / `az.summary` default, which PyMC uses, is that version, but the author should confirm. The placement does not fit as well. Divergent transitions are not the paper's subject. The paper mentions them only in its eight-schools example, as an HMC-specific diagnostic:

> "Still, we observe a lot of divergent transitions, which in itself is already a sufficient indicator of convergence problems."

As written, the citation sits after "no divergent transitions", which suggests that the paper sets a standard for divergences. It does not. The paper also asks for ESS > 400 and four or more chains, which the sentence does not report.

**Support: partly.**

**Evidence level:** full text (arXiv 1903.08008v5, 22 Jun 2021, the final version).

**Proposed rewording:**

> "The two forecast fits had maximum R-hat 1.007 and 1.004, below the 1.01 threshold recommended by Vehtari et al (2021), and no divergent transitions."

If the run logs show four or more chains and bulk and tail ESS above 400, the author could add: "with at least four chains and effective sample sizes above 400, as that paper also recommends." Add this only if the logs confirm it.

---

## B7. Barber et al 2021 (jackknife+ / CV+)

**Post:** "The non-Bayesian models get forecast ranges from CV+ (Barber et al 2021)"

**Metadata.** Crossref gives Barber RF, Candès EJ, Ramdas A, Tibshirani RJ, "Predictive inference with the jackknife+", *Annals of Statistics* 49(1):486–507, Feb 2021. **OK.**

**Support: yes.** CV+ is defined in Section 3 ("CV+ for K-fold cross-validation"):

> "Using these residuals, we can define the CV+ prediction interval as ..."

> "Further, we extend the jackknife+ to K-fold cross validation and similarly establish rigorous coverage properties." (abstract)

**Caveat (not a citation error).** The guarantee assumes exchangeable data ("Assuming exchangeable training samples, we prove ..."). It is also 1 − 2α − √(2/n), not 1 − α: "Theorem 4 ensures 1 − 2α − √2/n coverage for K-fold CV+ at any choice of K." If the post anywhere claims nominal coverage, such as "90% ranges", for a forecast of a held-out spring, it should not credit that claim to this paper's guarantee.

**Evidence level:** full text (arXiv 1905.02928v3).

---

## B8. Gneiting & Raftery 2007 (CRPS)

**Post:** "every model is scored by the continuous ranked probability score (CRPS; Gneiting & Raftery 2007), which for a single-number forecast equals the absolute error"

**Metadata.** Crossref gives "Strictly Proper Scoring Rules, Prediction, and Estimation", Gneiting T, Raftery AE, *JASA* 102(477):359–378, March 2007. **OK.**

**Support: yes, explicitly.** Section 4.2, p. 367:

> "In negative orientation, the CRPS can be reported in the same unit as the observations, and it generalizes the absolute error to which it reduces if F is a deterministic forecast—that is, a point measure. Thus the CRPS provides a direct way to compare deterministic and probabilistic forecasts."

The paper's main convention is positively oriented, where higher is better. The reduction to absolute error is stated for the negative orientation (CRPS*, where lower is better), which is the usual way the score is reported and matches the post's use as an error.

**Evidence level:** full text (PDF hosted at sites.stat.washington.edu/raftery, in the published JASA layout with journal page headers).

---

## B9. Hoerl & Kennard 1970; Zou & Hastie 2005; Park & Mazer 2018

**Post:** "Ridge and elastic net: All eight predictors, penalty chosen by an inner hidden-spring test (Hoerl & Kennard 1970; Zou & Hastie 2005; Park & Mazer 2018)"

**Metadata.**
- Hoerl & Kennard: Crossref gives "Ridge Regression: Biased Estimation for Nonorthogonal Problems", *Technometrics* 12(1):55–67, Feb 1970. **OK.**
- Zou & Hastie: Crossref gives "Regularization and Variable Selection Via the Elastic Net", *JRSS B* 67(2):301–320, 2005. **OK.**
- Park & Mazer: Crossref and PubMed give "Overlooked climate parameters best predict flowering onset: Assessing phenological models using the elastic net", *Global Change Biology* 24(12):5972–5984, 2018. **OK.**

**Support: yes for all three, as citations for the methods.** The citations name the methods. The "inner hidden-spring test" for choosing the penalty is the author's own design. Neither method paper uses it: Hoerl & Kennard use the ridge trace, and Zou & Hastie use tenfold CV. The placement does not suggest otherwise.

- Hoerl & Kennard (abstract): "Proposed is an estimation procedure based on adding small positive quantities to the diagonal of X′X. Introduced is the ridge trace, a method for showing in two dimensions the effects of nonorthogonality."
- Zou & Hastie: "We propose the elastic net, a new regularization and variable selection method." and "We call the function (1−α)|β|_1 + α|β|^2 the elastic net penalty, which is a convex combination of the lasso and ridge penalty." (I rewrote the formula from the garbled extracted text; the words are verbatim.)
- Park & Mazer (abstract): "we compare the predictive capacity of phenological models constructed from the collection dates of herbarium specimens vs. repeated in situ observations of individual plants using a regression approach-elastic net regularization-that has not previously been used in phenological modeling, but exhibits several advantages over ordinary least squares and stepwise regression." This supports citing it as a precedent for the elastic net in flowering phenology, and it uses herbarium records.

**Evidence level:** Hoerl & Kennard, abstract only (OpenAlex; the T&F page returned 403). Zou & Hastie, full text (PDF on Hastie's Stanford site). Park & Mazer, abstract only (PubMed).

---

## B10. Ke et al 2017 (LightGBM)

**Post:** "LightGBM: All eight predictors, settings from a 24-cell search (Ke et al 2017)"

**Metadata.** The listed URL papers.nips.cc/paper/6907-... redirects to the official proceedings page (papers.nips.cc/paper_files/paper/2017/hash/6449f44a102fde848669bdd9eb6b76fa-Abstract.html). That page shows "LightGBM: A Highly Efficient Gradient Boosting Decision Tree", Ke, Meng, Finley, Wang, Chen, Ma, Ye, Liu, "Advances in Neural Information Processing Systems 30 (NIPS 2017)". Its current official BibTeX has `pages = {}`. The archived official BibTeX for the old URL (Wayback, 9 Jan 2020) has `pages = {3146--3154}`. **OK.** The page numbers are correct as published on the old proceedings site, but the current site no longer lists them.

**Support: yes.** From the proceedings abstract: "We call our new GBDT implementation with GOSS and EFB LightGBM." The 24-cell search is the author's own procedure and is not credited to the paper.

**Evidence level:** full text (official NeurIPS PDF, 9 pages) and the proceedings abstract page.
