# 🔬 Deep check — does a feed actually WORK, not just answer HTTP?

Random sample of **120 world-catalog feeds**, each pushed through the full pipeline on **2026-07-24** (feeds over 25 MB skipped to keep the sample bandwidth-friendly):

| Stage | Feeds | % of sample |
|---|---:|---:|
| 📡 Reachable (HTTP 200) | 114/120 | 95 % |
| 📦 Valid GTFS, ingested end-to-end | 114/120 | 95 % |
| 🗺️ Routable (CSA planned a real trip today) | 60/120 | 50 % |

> `ingested` proves download → zip validation → parse → schedule DB → atomic swap. `routable` additionally proves the feed has service today and the journey planner finds a ride along the feed's own trips. Non-routable ingests are usually expired calendars — the feed's own data problem, not a pipeline failure.

<details><summary>Every sampled feed</summary>

| Feed | City | Reach | Ingest | Route | Note |
|---|---|:---:|:---:|:---:|---|
| `mdb-1013` | Lublin | ✅ | ✅ | ✅ |  |
| `mdb-1041` | Kaunas | ✅ | ✅ | ✅ |  |
| `mdb-1059` | Varese | ✅ | ✅ | ✅ |  |
| `mdb-1068` | Toremar Toscana Regionale Mari | ✅ | ✅ | ✅ |  |
| `mdb-1098` | Hämeenlinna | ✅ | ✅ | ✅ |  |
| `mdb-1121` | Knoxville | ✅ | ✅ | ✅ |  |
| `mdb-1131` | Vaasa | ✅ | ✅ | ✅ |  |
| `mdb-1210` | Los Angeles | ✅ | ✅ | ✅ |  |
| `mdb-1240` | Los Alamos | ✅ | ✅ | ✅ |  |
| `mdb-1319` | Marche | ✅ | ✅ | ✅ |  |
| `mdb-15` | Orange County | ✅ | ✅ | ✅ |  |
| `mdb-171` | Pocatello | ✅ | ✅ | ✅ |  |
| `mdb-1791` | Rio de Janeiro | ✅ | ✅ | ✅ |  |
| `mdb-1826` | Bettendorf | ✅ | ✅ | ✅ |  |
| `mdb-1858` | Belleville | ✅ | ✅ | ✅ |  |
| `mdb-2016` | Liepāja | ✅ | ✅ | ✅ |  |
| `mdb-2021` | Brindisi | ✅ | ✅ | ✅ |  |
| `mdb-2072` | Ann Arbor | ✅ | ✅ | ✅ |  |
| `mdb-2081` | Huntsville | ✅ | ✅ | ✅ |  |
| `mdb-2143` | Brașov | ✅ | ✅ | ✅ |  |
| `mdb-2277` | Cary | ✅ | ✅ | ✅ |  |
| `mdb-2308` | Virginia | ✅ | ✅ | ✅ |  |
| `mdb-2328` | Nevada | ✅ | ✅ | ✅ |  |
| `mdb-233` | Utica | ✅ | ✅ | ✅ |  |
| `mdb-2345` | Tirana | ✅ | ✅ | ✅ |  |
| `mdb-2377` | Željeznički prevoz Crne Gore | ✅ | ✅ | ✅ |  |
| `mdb-2379` | Sorel-Tracy | ✅ | ✅ | ✅ |  |
| `mdb-2441` | Petersburg | ✅ | ✅ | ✅ |  |
| `mdb-246` | Tillamook | ✅ | ✅ | ✅ |  |
| `mdb-2639` | Dublin | ✅ | ✅ | ✅ |  |
| `mdb-2668` | Calabria | ✅ | ✅ | ✅ |  |
| `mdb-28` | Los Angeles | ✅ | ✅ | ✅ |  |
| `mdb-2839` | Pori | ✅ | ✅ | ✅ |  |
| `mdb-284` | Bellingham | ✅ | ✅ | ✅ |  |
| `mdb-2859` | Hiawathaland Transit | ✅ | ✅ | ✅ |  |
| `mdb-2880` | Mountain View | ✅ | ✅ | ✅ |  |
| `mdb-290` | Spokane | ✅ | ✅ | ✅ |  |
| `mdb-2991` | LTG Link | ✅ | ✅ | ✅ |  |
| `mdb-3032` | Humboldt County | ✅ | ✅ | ✅ |  |
| `mdb-3095` | Bellflower | ✅ | ✅ | ✅ |  |
| `mdb-3097` | California | ✅ | ✅ | ✅ |  |
| `mdb-3125` | Kutno | ✅ | ✅ | ✅ |  |
| `mdb-3176` | Tokyo | ✅ | ✅ | ✅ |  |
| `mdb-3183` | GoTriangle | ✅ | ✅ | ✅ |  |
| `mdb-3192` | New York | ✅ | ✅ | ✅ |  |
| `mdb-389` | Chicago | ✅ | ✅ | ✅ |  |
| `mdb-397` | Oshkosh | ✅ | ✅ | ✅ |  |
| `mdb-399` | Sheboygan | ✅ | ✅ | ✅ |  |
| `mdb-515` | New York City | ✅ | ✅ | ✅ |  |
| `mdb-521` | Nassau | ✅ | ✅ | ✅ |  |
| `mdb-526` | Poughkeepsie | ✅ | ✅ | ✅ |  |
| `mdb-608` | Winchester | ✅ | ✅ | ✅ |  |
| `mdb-674` | Cairns | ✅ | ✅ | ✅ |  |
| `mdb-70` | Santa Rosa | ✅ | ✅ | ✅ |  |
| `mdb-718` | Cornwall | ✅ | ✅ | ✅ |  |
| `mdb-724` | Burlington | ✅ | ✅ | ✅ |  |
| `mdb-770` | Bayern | ✅ | ✅ | ✅ |  |
| `mdb-804` | Albany | ✅ | ✅ | ✅ |  |
| `mdb-854` | Azienda Trasporti Automobilist | ✅ | ✅ | ✅ |  |
| `mdb-882` | Altavista | ✅ | ✅ | ✅ |  |
| `mdb-1010` | Bystry | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1012` | Łomża | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1024` | Toulouse | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1047` | Regione Autonoma della Sardegn | ✅ | ✅ | — | no multi-stop trips |
| `mdb-1111` | Moncton | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1141` | Colorado | ✅ | ✅ | — | no multi-stop trips |
| `mdb-127` | Oregon | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-151` | Denton | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-156` | Arizona | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1834` | Šiaulių apskritis | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1928` | Brighton and Hove | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1943` | Bournemouth, Christchurch and  | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1952` | Swindon | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2015` | Pasažieru Vilciens | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2032` | Winona | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2036` | Prague | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2044` | Denver | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2099` | Sibiu | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2102` | Zalău | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2156` | Adams County | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2170` | La Junta | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2240` | Preston | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2249` | Bell | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-228` | Bell Gardens | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2280` | Denver | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2321` | Megabus | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2381` | Isparta | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2461` | Kalisz | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2555` | Kelowna | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2616` | Vail | ✅ | ✅ | — | no multi-stop trips |
| `mdb-265` | Washington | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2689` | Kórnik | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-315` | Corpus Christi | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-3163` | BAS.MY Seremban B | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-317` | Cripple Creek | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-322` | Key West | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-350` | Saint Augustine | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-384` | Michigan | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-421` | Massachusetts | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-475` | Kent | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-490` | Baltimore | ✅ | ✅ | — | no multi-stop trips |
| `mdb-52` | San Francisco | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-532` | New York | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-579` | Palm Springs | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-580` | Washington | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-639` | Eugene | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-66` | San Mateo | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-714` | Edmonton | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-717` | Winnipeg | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-726` | Durham | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-890` | Provence-Alpes-Côte-d'Azur | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-918` | Baden-Württemberg | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-931` | Burns | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-98` | Riverside | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2363` | Danville | — | — | — | HTTP error |
| `mdb-2430` | Virginia | — | — | — | HTTP error |
| `mdb-2853` | Redding | — | — | — | HTTP error |
| `mdb-2875` | County Cork | — | — | — | HTTP error |
| `mdb-2929` | Lisbon | — | — | — | HTTP error |
| `mdb-3206` | California | — | — | — | HTTP error |

</details>


<sub>Reproduce: `python3 scripts/deep_check.py 120` · fixed seed, so the sample is stable between runs.</sub>