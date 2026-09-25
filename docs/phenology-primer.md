# Phenology and data primer: bluebonnets, iNaturalist, and NOAA

## 1. The plant

The Texas bluebonnet (*Lupinus texensis*) is a **winter annual**: seeds germinate in autumn, the seedling overwinters as a flat rosette of leaves, and the plant flowers from March into April, sets seed, and dies by early summer. The seed coat is hard and impermeable to water (**physical dormancy**); only a fraction of seeds in any lot absorbs water and germinates in a given autumn. Acid scarification opens small pores in the seed coat and raises germination from 16–71% to 85–95% ([Davis et al 1991]), and seed that has been scarified loses viability within months in warm, humid storage while unscarified seed keeps it ([Mackay 2005]). Unscarified seed can therefore remain in the soil for more than one year, which is the reason the persistence baseline (B1) is on the ladder.

The folk explanation for a good bloom year, repeated each spring by the Lady Bird Johnson Wildflower Center, Texas A&M AgriLife, and Texas Parks and Wildlife staff, is rain in the autumn when seeds germinate, followed by a mild winter. No peer-reviewed field study was found that measures this for *L. texensis*. The closest evidence comes from desert winter annuals, whose germination requires a rain event above a threshold (about 25 mm) within a seasonal window ([Went 1949]; [Beatley 1974]), and whose germinating rains have moved later in the Sonoran Desert, changing which species establish ([Kimball et al 2010]). No study was found that shows *L. texensis* requires winter chilling to flower. Winter temperature is expected to act mainly on **timing**: warmer winters accumulate growing degree days sooner.

**Growing degree days** (GDD) measure accumulated warmth: for each day, `max(0, (Tmax + Tmin) / 2 − base)`, summed over a period. With a base of 5 °C, a day averaging 15 °C contributes 10. This project sums 1 January to 28/29 February ([McMaster & Wilhelm 1997] discusses the choices of base and averaging method).

## 2. iNaturalist as a measuring instrument

iNaturalist is a platform where anyone uploads a photograph of an organism with a date and location, and other users identify it. An observation becomes **research grade** when at least two identifiers agree at species level and more than two-thirds of the identifications agree; **needs ID** observations are still waiting; together they are **verifiable**.

iNaturalist was not designed to measure abundance, and three properties of the data shape every choice in this project:

1. **Effort grows.** Texas plant observations in March–April rose about 40-fold between 2016 and 2026. Raw bluebonnet counts measure the number of users more than the number of bluebonnets. The project divides bluebonnet records by all plant records from the same county and days. This is the **target-group** idea from species-distribution modeling ([Phillips et al 2009]): observers who photograph other plants are the background against which bluebonnet records are counted. It assumes the share of their attention that bluebonnets receive, in an average spring, does not drift over the years.
2. **Effort is uneven in time.** Observations cluster on weekends and during organized events ([Di Cecco et al 2021]). The largest is the **City Nature Challenge**, a four-day bioblitz at the end of April in which Austin, Dallas–Fort Worth, Houston, and San Antonio compete; in 2025 and 2026 it produced a weekly bluebonnet count about twice the real peak. Its days are removed from both counts. Dividing each day's bluebonnet count by that day's plant count before estimating the median date removes the weekend pattern.
3. **Attention is uneven across species.** Showy species are over-recorded relative to their abundance ([Callaghan et al 2021]). The index is therefore not a density; it is a relative measure, compared within a county across springs.

**Upload lag.** Observations are uploaded days to months after they are made, and identification continues for years. The 2027 target will be computed from data retrieved on 15 May 2027. To make earlier springs comparable, each spring's data are restricted to observations uploaded by 15 May of that spring (the API's `created_d2` filter), and to verifiable rather than research-grade observations.

**Timing from presence-only records.** Nobody records the absence of flowers, so the dates of observations are a sample of the flowering period weighted by where and when people looked. Estimators of onset and peak from such records ([Pearse et al 2017]; [Belitz et al 2020]) are biased when effort is uneven, and [Iler et al 2021] argue that they should not be read as the true first or peak flowering date. This project reports the **effort-weighted median date**: each day's bluebonnet count is divided by that day's plant count, smoothed with a 7-day moving sum, and the date at which half of the season's total is reached is the target. The median is a stable summary of when bluebonnets were most observed per unit of effort; it is not the date of maximum bloom in any field.

**Roadside seeding.** The Texas Department of Transportation and the public have sown bluebonnet seed along highways for decades, and wild populations are genetically homogenized as a result ([Turner et al 2018]). Much of what is photographed is seeded roadside stands, and the county normal absorbs the difference between counties in how much was sown, but not changes in sowing from year to year.

## 3. NOAA weather

- **nClimDiv** (NOAA NCEI) publishes monthly precipitation, temperature, and the Palmer Drought Severity Index (PDSI) for every U.S. county from 1895, computed from a gridded analysis of station data. It is revised as late reports arrive and is released early each month for the previous month. In its files Texas has the NCDC state code 41, not the FIPS code 48.
- **GHCN-Daily** (Global Historical Climatology Network) holds daily maximum and minimum temperatures from individual stations. Freeze days and growing degree days need daily values, so each county uses the nearest station with at least 90% of days present in the season.
- **ENSO.** The El Niño–Southern Oscillation is the alternation of warm (El Niño) and cold (La Niña) sea-surface temperatures in the central Pacific. El Niño winters are wetter than average in Texas ([Ropelewski & Halpert 1986]). The **Oceanic Niño Index** (ONI) is the three-month mean temperature anomaly in the Niño-3.4 region; an October–December ONI of +0.5 °C or more defines the analog springs used to fill months not yet observed in the 2027 forecast.
- **PDSI** is an index of soil moisture balance; values below −2 indicate moderate drought, above +2 moist conditions.

References are listed in `docs/post/README.md`.
