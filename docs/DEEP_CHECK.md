# 🔬 Deep check — does a feed actually WORK, not just answer HTTP?

**the ENTIRE registry** — all **1501 feeds**, each pushed through the full pipeline on **2026-07-24** (feeds over 25 MB marked `skipped` — download cap keeps the run bandwidth-sane):

| Stage | Feeds | % of sample |
|---|---:|---:|
| 📡 Reachable (HTTP 200) | 1436/1501 | 95 % |
| 📦 Valid GTFS, ingested end-to-end | 1387/1501 | 92 % |
| 🗺️ Routable (CSA planned a real trip today) | 751/1501 | 50 % |

> `ingested` proves download → zip validation → parse → schedule DB → atomic swap. `routable` additionally proves the feed has service today and the journey planner finds a ride along the feed's own trips. Non-routable ingests are usually expired calendars — the feed's own data problem, not a pipeline failure.

<details><summary>Every sampled feed</summary>

| Feed | City | Reach | Ingest | Route | Note |
|---|---|:---:|:---:|:---:|---|
| `bydgoszcz` | Bydgoszcz | ✅ | ✅ | ✅ |  |
| `germany-fern` | Germany (long-distance rail) | ✅ | ✅ | ✅ |  |
| `germany-regional` | Germany (regional rail) | ✅ | ✅ | ✅ |  |
| `kielce` | Kielce | ✅ | ✅ | ✅ |  |
| `lublin` | Lublin | ✅ | ✅ | ✅ |  |
| `mbta-boston` | Boston | ✅ | ✅ | ✅ |  |
| `mdb-1009` | Bydgoszcz | ✅ | ✅ | ✅ |  |
| `mdb-101` | Pasadena | ✅ | ✅ | ✅ |  |
| `mdb-1011` | Mazowieckie | ✅ | ✅ | ✅ |  |
| `mdb-1013` | Lublin | ✅ | ✅ | ✅ |  |
| `mdb-1025` | Nantes | ✅ | ✅ | ✅ |  |
| `mdb-1027` | Beograd | ✅ | ✅ | ✅ |  |
| `mdb-1029` | Auckland Transport | ✅ | ✅ | ✅ |  |
| `mdb-104` | Corona | ✅ | ✅ | ✅ |  |
| `mdb-1040` | Druskininkai | ✅ | ✅ | ✅ |  |
| `mdb-1041` | Kaunas | ✅ | ✅ | ✅ |  |
| `mdb-1042` | Klaipėda | ✅ | ✅ | ✅ |  |
| `mdb-1043` | Panevėžys | ✅ | ✅ | ✅ |  |
| `mdb-1044` | Vilnius | ✅ | ✅ | ✅ |  |
| `mdb-1053` | Virginia | ✅ | ✅ | ✅ |  |
| `mdb-1059` | Varese | ✅ | ✅ | ✅ |  |
| `mdb-106` | Beaumont | ✅ | ✅ | ✅ |  |
| `mdb-1060` | Shreveport | ✅ | ✅ | ✅ |  |
| `mdb-1062` | Venice | ✅ | ✅ | ✅ |  |
| `mdb-1068` | Toremar Toscana Regionale Mari | ✅ | ✅ | ✅ |  |
| `mdb-1071` | Bay of Plenty | ✅ | ✅ | ✅ |  |
| `mdb-1082` | Hofmann Omnibusverkehr GmbH | ✅ | ✅ | ✅ |  |
| `mdb-1094` | Aachen | ✅ | ✅ | ✅ |  |
| `mdb-1096` | Pays de la Loire | ✅ | ✅ | ✅ |  |
| `mdb-1098` | Hämeenlinna | ✅ | ✅ | ✅ |  |
| `mdb-11` | Amtrak | ✅ | ✅ | ✅ |  |
| `mdb-1102` | Porvoon Museorautatie, Pieksäm | ✅ | ✅ | ✅ |  |
| `mdb-1103` | Greater Manchester | ✅ | ✅ | ✅ |  |
| `mdb-111` | St. George | ✅ | ✅ | ✅ |  |
| `mdb-1110` | Wilmington | ✅ | ✅ | ✅ |  |
| `mdb-1115` | Freiburg | ✅ | ✅ | ✅ |  |
| `mdb-1120` | Niš | ✅ | ✅ | ✅ |  |
| `mdb-1121` | Knoxville | ✅ | ✅ | ✅ |  |
| `mdb-1126` | Florida | ✅ | ✅ | ✅ |  |
| `mdb-1127` | Kotka | ✅ | ✅ | ✅ |  |
| `mdb-1128` | Kouvola | ✅ | ✅ | ✅ |  |
| `mdb-1129` | Lahti | ✅ | ✅ | ✅ |  |
| `mdb-1130` | Mikkeli | ✅ | ✅ | ✅ |  |
| `mdb-1131` | Vaasa | ✅ | ✅ | ✅ |  |
| `mdb-1156` | Virginia | ✅ | ✅ | ✅ |  |
| `mdb-1158` | Médenine | ✅ | ✅ | ✅ |  |
| `mdb-117` | Yreka | ✅ | ✅ | ✅ |  |
| `mdb-118` | Susanville | ✅ | ✅ | ✅ |  |
| `mdb-1189` | Blacksburg | ✅ | ✅ | ✅ |  |
| `mdb-1198` | Long Beach | ✅ | ✅ | ✅ |  |
| `mdb-120` | Nevada | ✅ | ✅ | ✅ |  |
| `mdb-121` | Grants Pass | ✅ | ✅ | ✅ |  |
| `mdb-1210` | Los Angeles | ✅ | ✅ | ✅ |  |
| `mdb-1212` | Société Régionale Wallonne du  | ✅ | ✅ | ✅ |  |
| `mdb-1224` | Aachen | ✅ | ✅ | ✅ |  |
| `mdb-1227` | Joensuu | ✅ | ✅ | ✅ |  |
| `mdb-1232` | Pueblo | ✅ | ✅ | ✅ |  |
| `mdb-1235` | Delaware | ✅ | ✅ | ✅ |  |
| `mdb-1240` | Los Alamos | ✅ | ✅ | ✅ |  |
| `mdb-125` | Klamath Falls | ✅ | ✅ | ✅ |  |
| `mdb-1254` | Astoria | ✅ | ✅ | ✅ |  |
| `mdb-1256` | Nancy | ✅ | ✅ | ✅ |  |
| `mdb-126` | Corvallis | ✅ | ✅ | ✅ |  |
| `mdb-1270` | Kraków | ✅ | ✅ | ✅ |  |
| `mdb-1272` | Cascais | ✅ | ✅ | ✅ |  |
| `mdb-1286` | Mazamet | ✅ | ✅ | ✅ |  |
| `mdb-1288` | Napa | ✅ | ✅ | ✅ |  |
| `mdb-1290` | Trójmieście | ✅ | ✅ | ✅ |  |
| `mdb-1292` | Rejseplanen | ✅ | ✅ | ✅ |  |
| `mdb-13` | San Diego | ✅ | ✅ | ✅ |  |
| `mdb-130` | Oakridge | ✅ | ✅ | ✅ |  |
| `mdb-1316` | Bilbao | ✅ | ✅ | ✅ |  |
| `mdb-1319` | Marche | ✅ | ✅ | ✅ |  |
| `mdb-132` | Albany | ✅ | ✅ | ✅ |  |
| `mdb-1326` | Kraków | ✅ | ✅ | ✅ |  |
| `mdb-1327` | Klamath Falls | ✅ | ✅ | ✅ |  |
| `mdb-133` | Eugene | ✅ | ✅ | ✅ |  |
| `mdb-1330` | Seattle | ✅ | ✅ | ✅ |  |
| `mdb-135` | Albany | ✅ | ✅ | ✅ |  |
| `mdb-137` | Sweet Home | ✅ | ✅ | ✅ |  |
| `mdb-139` | Bend | ✅ | ✅ | ✅ |  |
| `mdb-141` | Ontario | ✅ | ✅ | ✅ |  |
| `mdb-147` | Phoenix | ✅ | ✅ | ✅ |  |
| `mdb-15` | Orange County | ✅ | ✅ | ✅ |  |
| `mdb-150` | Austin | ✅ | ✅ | ✅ |  |
| `mdb-153` | Dallas | ✅ | ✅ | ✅ |  |
| `mdb-158` | Cottonwood | ✅ | ✅ | ✅ |  |
| `mdb-163` | Colorado | ✅ | ✅ | ✅ |  |
| `mdb-164` | Snowmass Village | ✅ | ✅ | ✅ |  |
| `mdb-166` | Albuquerque | ✅ | ✅ | ✅ |  |
| `mdb-17` | Yuma | ✅ | ✅ | ✅ |  |
| `mdb-171` | Pocatello | ✅ | ✅ | ✅ |  |
| `mdb-172` | Denver | ✅ | ✅ | ✅ |  |
| `mdb-174` | Vail | ✅ | ✅ | ✅ |  |
| `mdb-175` | Winter Park | ✅ | ✅ | ✅ |  |
| `mdb-176` | Colorado | ✅ | ✅ | ✅ |  |
| `mdb-177` | Estes Park | ✅ | ✅ | ✅ |  |
| `mdb-178` | Denver | ✅ | ✅ | ✅ |  |
| `mdb-1784` | Towson | ✅ | ✅ | ✅ |  |
| `mdb-1791` | Rio de Janeiro | ✅ | ✅ | ✅ |  |
| `mdb-1806` | Miramichi | ✅ | ✅ | ✅ |  |
| `mdb-181` | Boulder | ✅ | ✅ | ✅ |  |
| `mdb-182` | Norman | ✅ | ✅ | ✅ |  |
| `mdb-1826` | Bettendorf | ✅ | ✅ | ✅ |  |
| `mdb-1832` | Železničná spoločnosť Slovensk | ✅ | ✅ | ✅ |  |
| `mdb-1833` | Alytaus apskritis | ✅ | ✅ | ✅ |  |
| `mdb-1839` | Communauté de Communes de l'Ou | ✅ | ✅ | ✅ |  |
| `mdb-1854` | Auvergne-Rhône-Alpes | ✅ | ✅ | ✅ |  |
| `mdb-1856` | Catalunya | ✅ | ✅ | ✅ |  |
| `mdb-1858` | Belleville | ✅ | ✅ | ✅ |  |
| `mdb-1859` | Bruxelles | ✅ | ✅ | ✅ |  |
| `mdb-1864` | Temuco | ✅ | ✅ | ✅ |  |
| `mdb-1868` | wallonne, Région | ✅ | ✅ | ✅ |  |
| `mdb-1877` | Fougères | ✅ | ✅ | ✅ |  |
| `mdb-1884` | Mayenne | ✅ | ✅ | ✅ |  |
| `mdb-1888` | Saintes | ✅ | ✅ | ✅ |  |
| `mdb-1890` | Rosny-sous-Bois | ✅ | ✅ | ✅ |  |
| `mdb-1901` | Olomouc | ✅ | ✅ | ✅ |  |
| `mdb-1903` | Veszprém | ✅ | ✅ | ✅ |  |
| `mdb-1905` | Arizona | ✅ | ✅ | ✅ |  |
| `mdb-1907` | Białystok | ✅ | ✅ | ✅ |  |
| `mdb-1908` | Małopolskie | ✅ | ✅ | ✅ |  |
| `mdb-1909` | Jakarta Raya | ✅ | ✅ | ✅ |  |
| `mdb-1915` | OSYPA | ✅ | ✅ | ✅ |  |
| `mdb-1916` | OSEA | ✅ | ✅ | ✅ |  |
| `mdb-1917` | Intercity buses | ✅ | ✅ | ✅ |  |
| `mdb-1918` | NPT | ✅ | ✅ | ✅ |  |
| `mdb-1919` | LPT | ✅ | ✅ | ✅ |  |
| `mdb-1924` | Hong Kong Government Transport | ✅ | ✅ | ✅ |  |
| `mdb-1929` | Borders Buses | ✅ | ✅ | ✅ |  |
| `mdb-193` | Des Moines | ✅ | ✅ | ✅ |  |
| `mdb-1930` | Blackpool Transport | ✅ | ✅ | ✅ |  |
| `mdb-1931` | Cardiff | ✅ | ✅ | ✅ |  |
| `mdb-1932` | Buckinghamshire | ✅ | ✅ | ✅ |  |
| `mdb-1933` | East Riding of Yorkshire | ✅ | ✅ | ✅ |  |
| `mdb-1934` | Cornwall | ✅ | ✅ | ✅ |  |
| `mdb-1935` | Go North East | ✅ | ✅ | ✅ |  |
| `mdb-1937` | West Berkshire | ✅ | ✅ | ✅ |  |
| `mdb-1938` | Essex | ✅ | ✅ | ✅ |  |
| `mdb-1939` | Hertfordshire | ✅ | ✅ | ✅ |  |
| `mdb-194` | Marshalltown | ✅ | ✅ | ✅ |  |
| `mdb-1940` | Norfolk | ✅ | ✅ | ✅ |  |
| `mdb-1941` | Inverclyde | ✅ | ✅ | ✅ |  |
| `mdb-1942` | Metrobus | ✅ | ✅ | ✅ |  |
| `mdb-1945` | Newport | ✅ | ✅ | ✅ |  |
| `mdb-1947` | Oxfordshire | ✅ | ✅ | ✅ |  |
| `mdb-1948` | Plymouth | ✅ | ✅ | ✅ |  |
| `mdb-195` | Ottumwa | ✅ | ✅ | ✅ |  |
| `mdb-1950` | Salisbury Reds | ✅ | ✅ | ✅ |  |
| `mdb-1957` | Argyll and Bute | ✅ | ✅ | ✅ |  |
| `mdb-197` | Iowa City | ✅ | ✅ | ✅ |  |
| `mdb-1971` | Burlington | ✅ | ✅ | ✅ |  |
| `mdb-1979` | Flagstaff | ✅ | ✅ | ✅ |  |
| `mdb-198` | Cedar Rapids | ✅ | ✅ | ✅ |  |
| `mdb-1984` | Vrancea | ✅ | ✅ | ✅ |  |
| `mdb-199` | Burlington | ✅ | ✅ | ✅ |  |
| `mdb-1993` | Toronto | ✅ | ✅ | ✅ |  |
| `mdb-1995` | Toronto | ✅ | ✅ | ✅ |  |
| `mdb-1997` | Lethbridge | ✅ | ✅ | ✅ |  |
| `mdb-1999` | Redondo Beach | ✅ | ✅ | ✅ |  |
| `mdb-200` | Muscatine | ✅ | ✅ | ✅ |  |
| `mdb-2000` | Lancaster | ✅ | ✅ | ✅ |  |
| `mdb-2001` | Canton | ✅ | ✅ | ✅ |  |
| `mdb-2008` | Regione Autonoma della Sardegn | ✅ | ✅ | ✅ |  |
| `mdb-2016` | Liepāja | ✅ | ✅ | ✅ |  |
| `mdb-2017` | Rēzekne | ✅ | ✅ | ✅ |  |
| `mdb-202` | Clinton | ✅ | ✅ | ✅ |  |
| `mdb-2020` | Ostuni | ✅ | ✅ | ✅ |  |
| `mdb-2021` | Brindisi | ✅ | ✅ | ✅ |  |
| `mdb-2022` | Brindisi | ✅ | ✅ | ✅ |  |
| `mdb-2023` | Francavilla | ✅ | ✅ | ✅ |  |
| `mdb-203` | Fort Dodge | ✅ | ✅ | ✅ |  |
| `mdb-2035` | St. Louis | ✅ | ✅ | ✅ |  |
| `mdb-2037` | Minnesota | ✅ | ✅ | ✅ |  |
| `mdb-2039` | Denver | ✅ | ✅ | ✅ |  |
| `mdb-204` | Mason City | ✅ | ✅ | ✅ |  |
| `mdb-2041` | Denver | ✅ | ✅ | ✅ |  |
| `mdb-2047` | Denver | ✅ | ✅ | ✅ |  |
| `mdb-2050` | San Miguel County | ✅ | ✅ | ✅ |  |
| `mdb-2051` | Denver | ✅ | ✅ | ✅ |  |
| `mdb-2057` | CP - Comboios de Portugal | ✅ | ✅ | ✅ |  |
| `mdb-206` | Minneapolis | ✅ | ✅ | ✅ |  |
| `mdb-2060` | Houston | ✅ | ✅ | ✅ |  |
| `mdb-2062` | Oklahoma City | ✅ | ✅ | ✅ |  |
| `mdb-2063` | Lawrence | ✅ | ✅ | ✅ |  |
| `mdb-2064` | Berks Area | ✅ | ✅ | ✅ |  |
| `mdb-2065` | Baton Rouge | ✅ | ✅ | ✅ |  |
| `mdb-2066` | Bloomington | ✅ | ✅ | ✅ |  |
| `mdb-2067` | Lexington | ✅ | ✅ | ✅ |  |
| `mdb-2068` | Fort Wright | ✅ | ✅ | ✅ |  |
| `mdb-2069` | Appleton | ✅ | ✅ | ✅ |  |
| `mdb-2071` | Akron | ✅ | ✅ | ✅ |  |
| `mdb-2072` | Ann Arbor | ✅ | ✅ | ✅ |  |
| `mdb-2075` | Las Cruces | ✅ | ✅ | ✅ |  |
| `mdb-2076` | Greeley | ✅ | ✅ | ✅ |  |
| `mdb-2081` | Huntsville | ✅ | ✅ | ✅ |  |
| `mdb-2083` | Dubuque | ✅ | ✅ | ✅ |  |
| `mdb-2086` | Ełk | ✅ | ✅ | ✅ |  |
| `mdb-2087` | Polregio | ✅ | ✅ | ✅ |  |
| `mdb-2089` | Toruń | ✅ | ✅ | ✅ |  |
| `mdb-2090` | Radom | ✅ | ✅ | ✅ |  |
| `mdb-2094` | Gdynia | ✅ | ✅ | ✅ |  |
| `mdb-2098` | București | ✅ | ✅ | ✅ |  |
| `mdb-21` | Coos Bay | ✅ | ✅ | ✅ |  |
| `mdb-210` | Lima | ✅ | ✅ | ✅ |  |
| `mdb-2114` | Sinaia | ✅ | ✅ | ✅ |  |
| `mdb-2115` | Craiova | ✅ | ✅ | ✅ |  |
| `mdb-2116` | Iași | ✅ | ✅ | ✅ |  |
| `mdb-2119` | Pleven | ✅ | ✅ | ✅ |  |
| `mdb-212` | Montrose | ✅ | ✅ | ✅ |  |
| `mdb-2122` | Richland | ✅ | ✅ | ✅ |  |
| `mdb-2126` | Montréal | ✅ | ✅ | ✅ |  |
| `mdb-2127` | Milwaukee | ✅ | ✅ | ✅ |  |
| `mdb-2131` | Saint John | ✅ | ✅ | ✅ |  |
| `mdb-2132` | Charlottetown | ✅ | ✅ | ✅ |  |
| `mdb-2141` | PM | ✅ | ✅ | ✅ |  |
| `mdb-2142` | Québec | ✅ | ✅ | ✅ |  |
| `mdb-2143` | Brașov | ✅ | ✅ | ✅ |  |
| `mdb-2149` | Burbank | ✅ | ✅ | ✅ |  |
| `mdb-2154` | Ottawa | ✅ | ✅ | ✅ |  |
| `mdb-2190` | Palo Verde Valley | ✅ | ✅ | ✅ |  |
| `mdb-2194` | Vermont | ✅ | ✅ | ✅ |  |
| `mdb-2195` | San Miguel County | ✅ | ✅ | ✅ |  |
| `mdb-2196` | Makah | ✅ | ✅ | ✅ |  |
| `mdb-2197` | Squaxin island | ✅ | ✅ | ✅ |  |
| `mdb-2198` | Pulaski | ✅ | ✅ | ✅ |  |
| `mdb-2199` | Grand Forks | ✅ | ✅ | ✅ |  |
| `mdb-22` | Brookings | ✅ | ✅ | ✅ |  |
| `mdb-220` | Banning | ✅ | ✅ | ✅ |  |
| `mdb-2202` | Monterey Park | ✅ | ✅ | ✅ |  |
| `mdb-2204` | Kings County | ✅ | ✅ | ✅ |  |
| `mdb-2205` | Corvallis | ✅ | ✅ | ✅ |  |
| `mdb-2208` | Peoria | ✅ | ✅ | ✅ |  |
| `mdb-2209` | Columbia | ✅ | ✅ | ✅ |  |
| `mdb-2212` | Málaga | ✅ | ✅ | ✅ |  |
| `mdb-2216` | Toledo | ✅ | ✅ | ✅ |  |
| `mdb-2224` | Emeryville | ✅ | ✅ | ✅ |  |
| `mdb-2231` | Karlsruhe | ✅ | ✅ | ✅ |  |
| `mdb-2232` | Pueblo | ✅ | ✅ | ✅ |  |
| `mdb-2241` | Gwinnett County | ✅ | ✅ | ✅ |  |
| `mdb-2242` | Norwalk | ✅ | ✅ | ✅ |  |
| `mdb-2243` | Arcadia | ✅ | ✅ | ✅ |  |
| `mdb-2244` | Concord | ✅ | ✅ | ✅ |  |
| `mdb-2245` | Raleigh | ✅ | ✅ | ✅ |  |
| `mdb-2246` | Racine | ✅ | ✅ | ✅ |  |
| `mdb-2247` | Baldwin Park | ✅ | ✅ | ✅ |  |
| `mdb-225` | Anchorage | ✅ | ✅ | ✅ |  |
| `mdb-2254` | Traverse City | ✅ | ✅ | ✅ |  |
| `mdb-2255` | Lake County | ✅ | ✅ | ✅ |  |
| `mdb-2256` | Portage County | ✅ | ✅ | ✅ |  |
| `mdb-2261` | Omaha | ✅ | ✅ | ✅ |  |
| `mdb-2262` | Beaver County | ✅ | ✅ | ✅ |  |
| `mdb-2265` | Charlotte | ✅ | ✅ | ✅ |  |
| `mdb-2266` | Fort Wayne | ✅ | ✅ | ✅ |  |
| `mdb-2267` | Bloomington | ✅ | ✅ | ✅ |  |
| `mdb-2268` | Saint Maryʼs County | ✅ | ✅ | ✅ |  |
| `mdb-2269` | Lincoln | ✅ | ✅ | ✅ |  |
| `mdb-2272` | Santa Maria | ✅ | ✅ | ✅ |  |
| `mdb-2273` | Modesto | ✅ | ✅ | ✅ |  |
| `mdb-2274` | Roanoke | ✅ | ✅ | ✅ |  |
| `mdb-2275` | Auburn | ✅ | ✅ | ✅ |  |
| `mdb-2276` | Rimouski | ✅ | ✅ | ✅ |  |
| `mdb-2277` | Cary | ✅ | ✅ | ✅ |  |
| `mdb-2278` | Roaring Folk Valley | ✅ | ✅ | ✅ |  |
| `mdb-2281` | Detroit | ✅ | ✅ | ✅ |  |
| `mdb-2282` | Ketchum | ✅ | ✅ | ✅ |  |
| `mdb-2283` | Corvallis | ✅ | ✅ | ✅ |  |
| `mdb-2285` | Annapolis | ✅ | ✅ | ✅ |  |
| `mdb-2286` | Washington County | ✅ | ✅ | ✅ |  |
| `mdb-2287` | Flint | ✅ | ✅ | ✅ |  |
| `mdb-2296` | Brown County | ✅ | ✅ | ✅ |  |
| `mdb-2297` | Amtrak Vermonter | ✅ | ✅ | ✅ |  |
| `mdb-2298` | Asotin County | ✅ | ✅ | ✅ |  |
| `mdb-23` | Newport | ✅ | ✅ | ✅ |  |
| `mdb-2303` | Johnson County | ✅ | ✅ | ✅ |  |
| `mdb-2307` | Port Angeles | ✅ | ✅ | ✅ |  |
| `mdb-2308` | Virginia | ✅ | ✅ | ✅ |  |
| `mdb-2309` | Grant County | ✅ | ✅ | ✅ |  |
| `mdb-2312` | Rockland County | ✅ | ✅ | ✅ |  |
| `mdb-2313` | Jackson | ✅ | ✅ | ✅ |  |
| `mdb-2318` | Chelan | ✅ | ✅ | ✅ |  |
| `mdb-2325` | Washington | ✅ | ✅ | ✅ |  |
| `mdb-2326` | Auburn | ✅ | ✅ | ✅ |  |
| `mdb-2328` | Nevada | ✅ | ✅ | ✅ |  |
| `mdb-2329` | Nelson | ✅ | ✅ | ✅ |  |
| `mdb-233` | Utica | ✅ | ✅ | ✅ |  |
| `mdb-2331` | Washington | ✅ | ✅ | ✅ |  |
| `mdb-2333` | Munich | ✅ | ✅ | ✅ |  |
| `mdb-2337` | Latvia by Gustavs Svalbe gsval | ✅ | ✅ | ✅ |  |
| `mdb-234` | Colorado | ✅ | ✅ | ✅ |  |
| `mdb-2341` | Chișinău | ✅ | ✅ | ✅ |  |
| `mdb-2345` | Tirana | ✅ | ✅ | ✅ |  |
| `mdb-2347` | Illinois | ✅ | ✅ | ✅ |  |
| `mdb-235` | Blackstone | ✅ | ✅ | ✅ |  |
| `mdb-2350` | Hawaii | ✅ | ✅ | ✅ |  |
| `mdb-2351` | Nevada | ✅ | ✅ | ✅ |  |
| `mdb-2361` | Dana Point | ✅ | ✅ | ✅ |  |
| `mdb-2374` | Lviv | ✅ | ✅ | ✅ |  |
| `mdb-2377` | Željeznički prevoz Crne Gore | ✅ | ✅ | ✅ |  |
| `mdb-2379` | Sorel-Tracy | ✅ | ✅ | ✅ |  |
| `mdb-238` | Bristol | ✅ | ✅ | ✅ |  |
| `mdb-2395` | Colorado | ✅ | ✅ | ✅ |  |
| `mdb-24` | Florence | ✅ | ✅ | ✅ |  |
| `mdb-2413` | City of Golden | ✅ | ✅ | ✅ |  |
| `mdb-2415` | Radford | ✅ | ✅ | ✅ |  |
| `mdb-2417` | Maritime Bus | ✅ | ✅ | ✅ |  |
| `mdb-2418` | Morrow County | ✅ | ✅ | ✅ |  |
| `mdb-2432` | Frederick | ✅ | ✅ | ✅ |  |
| `mdb-2433` | Avon | ✅ | ✅ | ✅ |  |
| `mdb-244` | Ketchikan | ✅ | ✅ | ✅ |  |
| `mdb-2440` | Danville | ✅ | ✅ | ✅ |  |
| `mdb-2441` | Petersburg | ✅ | ✅ | ✅ |  |
| `mdb-2442` | Pulaski | ✅ | ✅ | ✅ |  |
| `mdb-2443` | Virginia | ✅ | ✅ | ✅ |  |
| `mdb-2444` | Virginia | ✅ | ✅ | ✅ |  |
| `mdb-2445` | Virginia | ✅ | ✅ | ✅ |  |
| `mdb-2447` | Virginia | ✅ | ✅ | ✅ |  |
| `mdb-2448` | Virginia | ✅ | ✅ | ✅ |  |
| `mdb-245` | Wenatchee | ✅ | ✅ | ✅ |  |
| `mdb-2456` | Ellensburg | ✅ | ✅ | ✅ |  |
| `mdb-2457` | Hyderabad | ✅ | ✅ | ✅ |  |
| `mdb-2458` | Car Jaune | ✅ | ✅ | ✅ |  |
| `mdb-246` | Tillamook | ✅ | ✅ | ✅ |  |
| `mdb-2463` | Quesnel | ✅ | ✅ | ✅ |  |
| `mdb-2464` | Revelstoke | ✅ | ✅ | ✅ |  |
| `mdb-2466` | Salt Spring Island | ✅ | ✅ | ✅ |  |
| `mdb-2467` | Mount Waddington | ✅ | ✅ | ✅ |  |
| `mdb-2468` | Thompson-Nicola Regional Distr | ✅ | ✅ | ✅ |  |
| `mdb-2469` | 100 Mile House | ✅ | ✅ | ✅ |  |
| `mdb-247` | Portland | ✅ | ✅ | ✅ |  |
| `mdb-2470` | Pemberton Valley | ✅ | ✅ | ✅ |  |
| `mdb-2471` | Merritt | ✅ | ✅ | ✅ |  |
| `mdb-2472` | Smithers | ✅ | ✅ | ✅ |  |
| `mdb-2473` | Nanaimo | ✅ | ✅ | ✅ |  |
| `mdb-25` | Bishop | ✅ | ✅ | ✅ |  |
| `mdb-250` | Yamhill | ✅ | ✅ | ✅ |  |
| `mdb-2508` | Shuswap | ✅ | ✅ | ✅ |  |
| `mdb-251` | Woodburn | ✅ | ✅ | ✅ |  |
| `mdb-2510` | Bulkley-Nechako | ✅ | ✅ | ✅ |  |
| `mdb-2514` | Campbell River | ✅ | ✅ | ✅ |  |
| `mdb-2520` | Columbia Valley | ✅ | ✅ | ✅ |  |
| `mdb-2528` | British Columbia | ✅ | ✅ | ✅ |  |
| `mdb-2529` | Powell River | ✅ | ✅ | ✅ |  |
| `mdb-2532` | South Okanagan-Similkameen | ✅ | ✅ | ✅ |  |
| `mdb-2536` | Creston Valley | ✅ | ✅ | ✅ |  |
| `mdb-2543` | Port Edward | ✅ | ✅ | ✅ |  |
| `mdb-2547` | Fort St. John | ✅ | ✅ | ✅ |  |
| `mdb-255` | Portland | ✅ | ✅ | ✅ |  |
| `mdb-2551` | Kamloops | ✅ | ✅ | ✅ |  |
| `mdb-2563` | Squamish | ✅ | ✅ | ✅ |  |
| `mdb-2567` | British Columbia | ✅ | ✅ | ✅ |  |
| `mdb-2575` | West Coast | ✅ | ✅ | ✅ |  |
| `mdb-2579` | Nelson | ✅ | ✅ | ✅ |  |
| `mdb-258` | Vancouver | ✅ | ✅ | ✅ |  |
| `mdb-2583` | Whistler | ✅ | ✅ | ✅ |  |
| `mdb-2587` | Williams Lake | ✅ | ✅ | ✅ |  |
| `mdb-259` | Longview | ✅ | ✅ | ✅ |  |
| `mdb-2591` | Medicine Hat | ✅ | ✅ | ✅ |  |
| `mdb-2597` | Elbląg | ✅ | ✅ | ✅ |  |
| `mdb-2598` | Kraków | ✅ | ✅ | ✅ |  |
| `mdb-260` | Hood River | ✅ | ✅ | ✅ |  |
| `mdb-2603` | Rouyn-Noranda | ✅ | ✅ | ✅ |  |
| `mdb-261` | Sandy | ✅ | ✅ | ✅ |  |
| `mdb-2611` | Canton | ✅ | ✅ | ✅ |  |
| `mdb-262` | Washington | ✅ | ✅ | ✅ |  |
| `mdb-2621` | Oregon | ✅ | ✅ | ✅ |  |
| `mdb-263` | Aberdeen | ✅ | ✅ | ✅ |  |
| `mdb-2634` | Midland | ✅ | ✅ | ✅ |  |
| `mdb-2635` | Dublin | ✅ | ✅ | ✅ |  |
| `mdb-2636` | Bus Éireann | ✅ | ✅ | ✅ |  |
| `mdb-2637` | Irish Rail | ✅ | ✅ | ✅ |  |
| `mdb-2638` | Dublin | ✅ | ✅ | ✅ |  |
| `mdb-2639` | Dublin | ✅ | ✅ | ✅ |  |
| `mdb-264` | Washington | ✅ | ✅ | ✅ |  |
| `mdb-2640` | Dublin | ✅ | ✅ | ✅ |  |
| `mdb-2652` | Jackson | ✅ | ✅ | ✅ |  |
| `mdb-266` | Olympia | ✅ | ✅ | ✅ |  |
| `mdb-2662` | Louisville | ✅ | ✅ | ✅ |  |
| `mdb-2668` | Calabria | ✅ | ✅ | ✅ |  |
| `mdb-267` | King County | ✅ | ✅ | ✅ |  |
| `mdb-268` | Seattle | ✅ | ✅ | ✅ |  |
| `mdb-2686` | Nouvelle-Aquitaine | ✅ | ✅ | ✅ |  |
| `mdb-2687` | Turin | ✅ | ✅ | ✅ |  |
| `mdb-2688` | Essex County | ✅ | ✅ | ✅ |  |
| `mdb-2691` | Arroyo de la Encomienda | ✅ | ✅ | ✅ |  |
| `mdb-2706` | Wilsonville | ✅ | ✅ | ✅ |  |
| `mdb-2709` | Trinity County | ✅ | ✅ | ✅ |  |
| `mdb-2739` | Sandy | ✅ | ✅ | ✅ |  |
| `mdb-2740` | Oregon | ✅ | ✅ | ✅ |  |
| `mdb-2741` | Oregon | ✅ | ✅ | ✅ |  |
| `mdb-276` | Yakima | ✅ | ✅ | ✅ |  |
| `mdb-277` | Yakima | ✅ | ✅ | ✅ |  |
| `mdb-279` | Washington | ✅ | ✅ | ✅ |  |
| `mdb-28` | Los Angeles | ✅ | ✅ | ✅ |  |
| `mdb-280` | Washington | ✅ | ✅ | ✅ |  |
| `mdb-2802` | Madrid | ✅ | ✅ | ✅ |  |
| `mdb-2820` | Madrid | ✅ | ✅ | ✅ |  |
| `mdb-2831` | Rutland | ✅ | ✅ | ✅ |  |
| `mdb-2838` | Guimarães | ✅ | ✅ | ✅ |  |
| `mdb-2839` | Pori | ✅ | ✅ | ✅ |  |
| `mdb-284` | Bellingham | ✅ | ✅ | ✅ |  |
| `mdb-2840` | Connecticut | ✅ | ✅ | ✅ |  |
| `mdb-2848` | Sofia City | ✅ | ✅ | ✅ |  |
| `mdb-2857` | Bisbee | ✅ | ✅ | ✅ |  |
| `mdb-2858` | Sedona | ✅ | ✅ | ✅ |  |
| `mdb-2859` | Hiawathaland Transit | ✅ | ✅ | ✅ |  |
| `mdb-2861` | City of Galveston | ✅ | ✅ | ✅ |  |
| `mdb-2867` | Indian Railways | ✅ | ✅ | ✅ |  |
| `mdb-2868` | Timișoara | ✅ | ✅ | ✅ |  |
| `mdb-287` | Washington | ✅ | ✅ | ✅ |  |
| `mdb-2871` | Hokkaidô | ✅ | ✅ | ✅ |  |
| `mdb-2877` | Philadelphia | ✅ | ✅ | ✅ |  |
| `mdb-2880` | Mountain View | ✅ | ✅ | ✅ |  |
| `mdb-2881` | Watertown | ✅ | ✅ | ✅ |  |
| `mdb-2884` | Springfield | ✅ | ✅ | ✅ |  |
| `mdb-2885` | Fairfax | ✅ | ✅ | ✅ |  |
| `mdb-289` | Wallowa | ✅ | ✅ | ✅ |  |
| `mdb-2890` | Dallas Fort Worth | ✅ | ✅ | ✅ |  |
| `mdb-2894` | Clovis | ✅ | ✅ | ✅ |  |
| `mdb-290` | Spokane | ✅ | ✅ | ✅ |  |
| `mdb-2900` | Flixbus GB | ✅ | ✅ | ✅ |  |
| `mdb-2901` | PAME EXPRESS | ✅ | ✅ | ✅ |  |
| `mdb-2906` | Xplore Dundee | ✅ | ✅ | ✅ |  |
| `mdb-2909` | Coach Services | ✅ | ✅ | ✅ |  |
| `mdb-2911` | Midland Bluebird | ✅ | ✅ | ✅ |  |
| `mdb-2912` | Sanders Coaches | ✅ | ✅ | ✅ |  |
| `mdb-2913` | Thames Valley Buses | ✅ | ✅ | ✅ |  |
| `mdb-2919` | Bratislavský kraj | ✅ | ✅ | ✅ |  |
| `mdb-292` | Missoula | ✅ | ✅ | ✅ |  |
| `mdb-2921` | Lisbon | ✅ | ✅ | ✅ |  |
| `mdb-2925` | Beograd | ✅ | ✅ | ✅ |  |
| `mdb-2927` | Srbijavoz | ✅ | ✅ | ✅ |  |
| `mdb-2931` | Ужгородська міська рада | ✅ | ✅ | ✅ |  |
| `mdb-2932` | Стрийська міська рада | ✅ | ✅ | ✅ |  |
| `mdb-2937` | San Francisco | ✅ | ✅ | ✅ |  |
| `mdb-2938` | Mandai Wildlife Reserve | ✅ | ✅ | ✅ |  |
| `mdb-294` | Juneau | ✅ | ✅ | ✅ |  |
| `mdb-295` | Bozeman | ✅ | ✅ | ✅ |  |
| `mdb-2991` | LTG Link | ✅ | ✅ | ✅ |  |
| `mdb-2993` | Regione Autonoma della Sardegn | ✅ | ✅ | ✅ |  |
| `mdb-3` | Barrie | ✅ | ✅ | ✅ |  |
| `mdb-301` | Duluth | ✅ | ✅ | ✅ |  |
| `mdb-302` | Elmira | ✅ | ✅ | ✅ |  |
| `mdb-3031` | Redding | ✅ | ✅ | ✅ |  |
| `mdb-3032` | Humboldt County | ✅ | ✅ | ✅ |  |
| `mdb-3033` | Boston | ✅ | ✅ | ✅ |  |
| `mdb-3035` | New Jersey | ✅ | ✅ | ✅ |  |
| `mdb-3037` | Columbia County Rider | ✅ | ✅ | ✅ |  |
| `mdb-3038` | Everett | ✅ | ✅ | ✅ |  |
| `mdb-304` | Jamestown | ✅ | ✅ | ✅ |  |
| `mdb-3041` | Bologna | ✅ | ✅ | ✅ |  |
| `mdb-3043` | HŽ Passenger Transport | ✅ | ✅ | ✅ |  |
| `mdb-3046` | Ungheni | ✅ | ✅ | ✅ |  |
| `mdb-3047` | Tallinna linn | ✅ | ✅ | ✅ |  |
| `mdb-307` | Cincinnati | ✅ | ✅ | ✅ |  |
| `mdb-308` | DeKalb | ✅ | ✅ | ✅ |  |
| `mdb-309` | Colorado Springs | ✅ | ✅ | ✅ |  |
| `mdb-3093` | San Diego | ✅ | ✅ | ✅ |  |
| `mdb-3094` | Chico | ✅ | ✅ | ✅ |  |
| `mdb-3095` | Bellflower | ✅ | ✅ | ✅ |  |
| `mdb-3096` | Santa Barbara | ✅ | ✅ | ✅ |  |
| `mdb-3097` | California | ✅ | ✅ | ✅ |  |
| `mdb-3098` | Rosemead | ✅ | ✅ | ✅ |  |
| `mdb-3099` | Tracy | ✅ | ✅ | ✅ |  |
| `mdb-3104` | Funchal | ✅ | ✅ | ✅ |  |
| `mdb-3106` | Kommuneqarfik Sermersooq | ✅ | ✅ | ✅ |  |
| `mdb-3108` | Georgian Railway | ✅ | ✅ | ✅ |  |
| `mdb-3109` | Corvallis | ✅ | ✅ | ✅ |  |
| `mdb-3112` | Aberdeen | ✅ | ✅ | ✅ |  |
| `mdb-3114` | Rochester-Genesee | ✅ | ✅ | ✅ |  |
| `mdb-3115` | New York | ✅ | ✅ | ✅ |  |
| `mdb-3116` | Columbia County | ✅ | ✅ | ✅ |  |
| `mdb-3117` | Merced | ✅ | ✅ | ✅ |  |
| `mdb-312` | Oregon | ✅ | ✅ | ✅ |  |
| `mdb-3121` | Žaliasis regionas | ✅ | ✅ | ✅ |  |
| `mdb-3122` | Śląskie | ✅ | ✅ | ✅ |  |
| `mdb-3125` | Kutno | ✅ | ✅ | ✅ |  |
| `mdb-313` | Georgetown | ✅ | ✅ | ✅ |  |
| `mdb-3130` | Transportation Management Asso | ✅ | ✅ | ✅ |  |
| `mdb-3131` | Ahmedabad Janmarg Ltd, Ahmedab | ✅ | ✅ | ✅ |  |
| `mdb-3137` | PMPML | ✅ | ✅ | ✅ |  |
| `mdb-3138` | Mumbai Bus (BEST, KDMT) | ✅ | ✅ | ✅ |  |
| `mdb-3141` | Hubli Dharwad Bus Rapid Transi | ✅ | ✅ | ✅ |  |
| `mdb-3142` | Rajkot Rampath Limited | ✅ | ✅ | ✅ |  |
| `mdb-3143` | San Francisco | ✅ | ✅ | ✅ |  |
| `mdb-3146` | SkyBus Melbourne | ✅ | ✅ | ✅ |  |
| `mdb-3154` | DZK | ✅ | ✅ | ✅ |  |
| `mdb-3155` | Aytos-Avtrotransport Ltd. | ✅ | ✅ | ✅ |  |
| `mdb-3157` | BAS.MY Kangar | ✅ | ✅ | ✅ |  |
| `mdb-3158` | BAS.MY Alor Setar | ✅ | ✅ | ✅ |  |
| `mdb-3159` | BAS.MY Kota Bharu | ✅ | ✅ | ✅ |  |
| `mdb-316` | Iowa City | ✅ | ✅ | ✅ |  |
| `mdb-3160` | BAS.MY Kuala Terengganu | ✅ | ✅ | ✅ |  |
| `mdb-3164` | BAS.MY Melaka | ✅ | ✅ | ✅ |  |
| `mdb-3165` | BAS.MY Johor Bahru | ✅ | ✅ | ✅ |  |
| `mdb-3166` | BAS.MY Kuching | ✅ | ✅ | ✅ |  |
| `mdb-3175` | Tokyo | ✅ | ✅ | ✅ |  |
| `mdb-3176` | Tokyo | ✅ | ✅ | ✅ |  |
| `mdb-3178` | Cecil Transit | ✅ | ✅ | ✅ |  |
| `mdb-3182` | Urban Trans Vlora | ✅ | ✅ | ✅ |  |
| `mdb-3183` | GoTriangle | ✅ | ✅ | ✅ |  |
| `mdb-3186` | Barreiro | ✅ | ✅ | ✅ |  |
| `mdb-3187` | Springfield Mass Transit Distr | ✅ | ✅ | ✅ |  |
| `mdb-3189` | Komunikacja miejska w Jarosław | ✅ | ✅ | ✅ |  |
| `mdb-3192` | New York | ✅ | ✅ | ✅ |  |
| `mdb-3193` | Georgia | ✅ | ✅ | ✅ |  |
| `mdb-32` | Oxnard | ✅ | ✅ | ✅ |  |
| `mdb-320` | Delano | ✅ | ✅ | ✅ |  |
| `mdb-324` | Fort Myers | ✅ | ✅ | ✅ |  |
| `mdb-325` | Tampa | ✅ | ✅ | ✅ |  |
| `mdb-329` | Tampa | ✅ | ✅ | ✅ |  |
| `mdb-330` | Fort Lauderdale | ✅ | ✅ | ✅ |  |
| `mdb-332` | Palm Beach | ✅ | ✅ | ✅ |  |
| `mdb-334` | Virginia | ✅ | ✅ | ✅ |  |
| `mdb-338` | Montgomery | ✅ | ✅ | ✅ |  |
| `mdb-347` | Orlando | ✅ | ✅ | ✅ |  |
| `mdb-348` | Sarasota | ✅ | ✅ | ✅ |  |
| `mdb-35` | California | ✅ | ✅ | ✅ |  |
| `mdb-352` | Charleston | ✅ | ✅ | ✅ |  |
| `mdb-36` | Lawndale | ✅ | ✅ | ✅ |  |
| `mdb-361` | Nashville | ✅ | ✅ | ✅ |  |
| `mdb-362` | Kentucky | ✅ | ✅ | ✅ |  |
| `mdb-368` | Atlanta | ✅ | ✅ | ✅ |  |
| `mdb-37` | Santa Monica | ✅ | ✅ | ✅ |  |
| `mdb-373` | Greensboro | ✅ | ✅ | ✅ |  |
| `mdb-381` | Lynchburg | ✅ | ✅ | ✅ |  |
| `mdb-388` | Urbana | ✅ | ✅ | ✅ |  |
| `mdb-389` | Chicago | ✅ | ✅ | ✅ |  |
| `mdb-394` | Madison | ✅ | ✅ | ✅ |  |
| `mdb-397` | Oshkosh | ✅ | ✅ | ✅ |  |
| `mdb-399` | Sheboygan | ✅ | ✅ | ✅ |  |
| `mdb-40` | Simi Valley | ✅ | ✅ | ✅ |  |
| `mdb-400` | Grand Rapids | ✅ | ✅ | ✅ |  |
| `mdb-402` | Lansing | ✅ | ✅ | ✅ |  |
| `mdb-403` | Dayton | ✅ | ✅ | ✅ |  |
| `mdb-404` | Columbus | ✅ | ✅ | ✅ |  |
| `mdb-406` | Cleveland | ✅ | ✅ | ✅ |  |
| `mdb-407` | Morgantown | ✅ | ✅ | ✅ |  |
| `mdb-41` | Pasadena | ✅ | ✅ | ✅ |  |
| `mdb-410` | Cleveland | ✅ | ✅ | ✅ |  |
| `mdb-415` | Ann Arbor | ✅ | ✅ | ✅ |  |
| `mdb-422` | Brockton | ✅ | ✅ | ✅ |  |
| `mdb-426` | Nantucket | ✅ | ✅ | ✅ |  |
| `mdb-429` | Franklin | ✅ | ✅ | ✅ |  |
| `mdb-43` | San Luis Obispo | ✅ | ✅ | ✅ |  |
| `mdb-430` | Rutland | ✅ | ✅ | ✅ |  |
| `mdb-432` | Worcester | ✅ | ✅ | ✅ |  |
| `mdb-433` | Massachusetts | ✅ | ✅ | ✅ |  |
| `mdb-437` | Boston | ✅ | ✅ | ✅ |  |
| `mdb-439` | Massachusetts | ✅ | ✅ | ✅ |  |
| `mdb-44` | San Luis Obispo | ✅ | ✅ | ✅ |  |
| `mdb-441` | Boston | ✅ | ✅ | ✅ |  |
| `mdb-442` | Billerica | ✅ | ✅ | ✅ |  |
| `mdb-443` | Massachusetts | ✅ | ✅ | ✅ |  |
| `mdb-444` | Lowell | ✅ | ✅ | ✅ |  |
| `mdb-447` | Massachusetts | ✅ | ✅ | ✅ |  |
| `mdb-450` | Vermont | ✅ | ✅ | ✅ |  |
| `mdb-452` | Maine | ✅ | ✅ | ✅ |  |
| `mdb-456` | Colorado | ✅ | ✅ | ✅ |  |
| `mdb-457` | Poughkeepsie | ✅ | ✅ | ✅ |  |
| `mdb-459` | Colorado | ✅ | ✅ | ✅ |  |
| `mdb-46` | Bakersfield | ✅ | ✅ | ✅ |  |
| `mdb-461` | Virginia | ✅ | ✅ | ✅ |  |
| `mdb-463` | Greensville County | ✅ | ✅ | ✅ |  |
| `mdb-467` | Maryland | ✅ | ✅ | ✅ |  |
| `mdb-468` | Maryland | ✅ | ✅ | ✅ |  |
| `mdb-469` | Maryland | ✅ | ✅ | ✅ |  |
| `mdb-470` | Maryland | ✅ | ✅ | ✅ |  |
| `mdb-472` | Rocky Mount | ✅ | ✅ | ✅ |  |
| `mdb-477` | Maryland | ✅ | ✅ | ✅ |  |
| `mdb-482` | Alexandria | ✅ | ✅ | ✅ |  |
| `mdb-483` | Fairfax | ✅ | ✅ | ✅ |  |
| `mdb-485` | Arlington | ✅ | ✅ | ✅ |  |
| `mdb-488` | Montgomery County | ✅ | ✅ | ✅ |  |
| `mdb-507` | Long Island | ✅ | ✅ | ✅ |  |
| `mdb-508` | New Jersey | ✅ | ✅ | ✅ |  |
| `mdb-509` | New Jersey | ✅ | ✅ | ✅ |  |
| `mdb-511` | New York City | ✅ | ✅ | ✅ |  |
| `mdb-515` | New York City | ✅ | ✅ | ✅ |  |
| `mdb-516` | New York City | ✅ | ✅ | ✅ |  |
| `mdb-519` | New York City | ✅ | ✅ | ✅ |  |
| `mdb-521` | Nassau | ✅ | ✅ | ✅ |  |
| `mdb-524` | New York City | ✅ | ✅ | ✅ |  |
| `mdb-526` | Poughkeepsie | ✅ | ✅ | ✅ |  |
| `mdb-53` | San Francisco | ✅ | ✅ | ✅ |  |
| `mdb-531` | New York | ✅ | ✅ | ✅ |  |
| `mdb-536` | Norwich | ✅ | ✅ | ✅ |  |
| `mdb-537` | Berkshire | ✅ | ✅ | ✅ |  |
| `mdb-538` | Albany | ✅ | ✅ | ✅ |  |
| `mdb-54` | San Francisco | ✅ | ✅ | ✅ |  |
| `mdb-544` | Plattsburgh | ✅ | ✅ | ✅ |  |
| `mdb-545` | North Malone | ✅ | ✅ | ✅ |  |
| `mdb-546` | Plattsburgh | ✅ | ✅ | ✅ |  |
| `mdb-551` | Middletown | ✅ | ✅ | ✅ |  |
| `mdb-553` | Connecticut | ✅ | ✅ | ✅ |  |
| `mdb-556` | Massachusetts | ✅ | ✅ | ✅ |  |
| `mdb-559` | Iowa City | ✅ | ✅ | ✅ |  |
| `mdb-566` | Lowville | ✅ | ✅ | ✅ |  |
| `mdb-569` | Lubbock | ✅ | ✅ | ✅ |  |
| `mdb-571` | Indianapolis | ✅ | ✅ | ✅ |  |
| `mdb-573` | New York | ✅ | ✅ | ✅ |  |
| `mdb-578` | Moorpark | ✅ | ✅ | ✅ |  |
| `mdb-585` | South Bend | ✅ | ✅ | ✅ |  |
| `mdb-586` | Olean | ✅ | ✅ | ✅ |  |
| `mdb-589` | Cooperstown | ✅ | ✅ | ✅ |  |
| `mdb-59` | Stanford | ✅ | ✅ | ✅ |  |
| `mdb-590` | Pendleton | ✅ | ✅ | ✅ |  |
| `mdb-591` | Petersburg | ✅ | ✅ | ✅ |  |
| `mdb-608` | Winchester | ✅ | ✅ | ✅ |  |
| `mdb-61` | San Mateo | ✅ | ✅ | ✅ |  |
| `mdb-611` | Bluefield | ✅ | ✅ | ✅ |  |
| `mdb-613` | New York | ✅ | ✅ | ✅ |  |
| `mdb-621` | Virginia | ✅ | ✅ | ✅ |  |
| `mdb-626` | Florida | ✅ | ✅ | ✅ |  |
| `mdb-631` | Hartford | ✅ | ✅ | ✅ |  |
| `mdb-646` | Tulare | ✅ | ✅ | ✅ |  |
| `mdb-648` | Wien | ✅ | ✅ | ✅ |  |
| `mdb-650` | Magnetic Island | ✅ | ✅ | ✅ |  |
| `mdb-651` | Maryborough | ✅ | ✅ | ✅ |  |
| `mdb-652` | Brisbane | ✅ | ✅ | ✅ |  |
| `mdb-653` | Toowoomba | ✅ | ✅ | ✅ |  |
| `mdb-654` | Warwick | ✅ | ✅ | ✅ |  |
| `mdb-659` | Bourgogne-Franche-Comté | ✅ | ✅ | ✅ |  |
| `mdb-660` | Adelaide | ✅ | ✅ | ✅ |  |
| `mdb-665` | Hobart | ✅ | ✅ | ✅ |  |
| `mdb-667` | Gladstone | ✅ | ✅ | ✅ |  |
| `mdb-669` | Caboolture | ✅ | ✅ | ✅ |  |
| `mdb-670` | Queensland | ✅ | ✅ | ✅ |  |
| `mdb-671` | Gympie | ✅ | ✅ | ✅ |  |
| `mdb-672` | Bundaberg | ✅ | ✅ | ✅ |  |
| `mdb-673` | Queensland | ✅ | ✅ | ✅ |  |
| `mdb-674` | Cairns | ✅ | ✅ | ✅ |  |
| `mdb-675` | Queensland | ✅ | ✅ | ✅ |  |
| `mdb-676` | Proserpine | ✅ | ✅ | ✅ |  |
| `mdb-677` | Townsville | ✅ | ✅ | ✅ |  |
| `mdb-678` | Mackay | ✅ | ✅ | ✅ |  |
| `mdb-68` | California | ✅ | ✅ | ✅ |  |
| `mdb-681` | Burnie | ✅ | ✅ | ✅ |  |
| `mdb-682` | Launceston | ✅ | ✅ | ✅ |  |
| `mdb-686` | Société nationale des chemins  | ✅ | ✅ | ✅ |  |
| `mdb-689` | Whitehorse | ✅ | ✅ | ✅ |  |
| `mdb-69` | Ukiah | ✅ | ✅ | ✅ |  |
| `mdb-690` | Vancouver | ✅ | ✅ | ✅ |  |
| `mdb-696` | Vancouver | ✅ | ✅ | ✅ |  |
| `mdb-70` | Santa Rosa | ✅ | ✅ | ✅ |  |
| `mdb-710` | Dawson Creek | ✅ | ✅ | ✅ |  |
| `mdb-715` | Regina | ✅ | ✅ | ✅ |  |
| `mdb-718` | Cornwall | ✅ | ✅ | ✅ |  |
| `mdb-720` | Windsor | ✅ | ✅ | ✅ |  |
| `mdb-724` | Burlington | ✅ | ✅ | ✅ |  |
| `mdb-730` | Mississauga | ✅ | ✅ | ✅ |  |
| `mdb-733` | Kingston | ✅ | ✅ | ✅ |  |
| `mdb-734` | Halifax | ✅ | ✅ | ✅ |  |
| `mdb-736` | Thunder Bay | ✅ | ✅ | ✅ |  |
| `mdb-737` | Sudbury | ✅ | ✅ | ✅ |  |
| `mdb-740` | Gatineau | ✅ | ✅ | ✅ |  |
| `mdb-741` | Varennes | ✅ | ✅ | ✅ |  |
| `mdb-742` | Québec | ✅ | ✅ | ✅ |  |
| `mdb-743` | Québec | ✅ | ✅ | ✅ |  |
| `mdb-744` | Québec | ✅ | ✅ | ✅ |  |
| `mdb-748` | Québec | ✅ | ✅ | ✅ |  |
| `mdb-750` | Québec | ✅ | ✅ | ✅ |  |
| `mdb-753` | Sainte-Julie | ✅ | ✅ | ✅ |  |
| `mdb-754` | Québec | ✅ | ✅ | ✅ |  |
| `mdb-755` | L'Assomption | ✅ | ✅ | ✅ |  |
| `mdb-757` | Québec | ✅ | ✅ | ✅ |  |
| `mdb-761` | Port Alberni | ✅ | ✅ | ✅ |  |
| `mdb-763` | Lévis | ✅ | ✅ | ✅ |  |
| `mdb-767` | Praha, hlavní mešto | ✅ | ✅ | ✅ |  |
| `mdb-769` | Ravensburg | ✅ | ✅ | ✅ |  |
| `mdb-770` | Bayern | ✅ | ✅ | ✅ |  |
| `mdb-771` | Hechingen | ✅ | ✅ | ✅ |  |
| `mdb-772` | Baden-Württemberg | ✅ | ✅ | ✅ |  |
| `mdb-774` | Schweizer Reisen | ✅ | ✅ | ✅ |  |
| `mdb-776` | Ulm | ✅ | ✅ | ✅ |  |
| `mdb-778` | Bayern | ✅ | ✅ | ✅ |  |
| `mdb-779` | Munich | ✅ | ✅ | ✅ |  |
| `mdb-78` | Pinole | ✅ | ✅ | ✅ |  |
| `mdb-782` | Berlin | ✅ | ✅ | ✅ |  |
| `mdb-783` | Heilbronn | ✅ | ✅ | ✅ |  |
| `mdb-787` | Tenerife | ✅ | ✅ | ✅ |  |
| `mdb-79` | Yuba City | ✅ | ✅ | ✅ |  |
| `mdb-791` | Madrid | ✅ | ✅ | ✅ |  |
| `mdb-793` | Madrid | ✅ | ✅ | ✅ |  |
| `mdb-8` | São Paulo | ✅ | ✅ | ✅ |  |
| `mdb-80` | Fairfield | ✅ | ✅ | ✅ |  |
| `mdb-800` | Oregon | ✅ | ✅ | ✅ |  |
| `mdb-801` | Colorado | ✅ | ✅ | ✅ |  |
| `mdb-804` | Albany | ✅ | ✅ | ✅ |  |
| `mdb-805` | Ignacio | ✅ | ✅ | ✅ |  |
| `mdb-813` | Solvang | ✅ | ✅ | ✅ |  |
| `mdb-816` | Snoqualmie | ✅ | ✅ | ✅ |  |
| `mdb-819` | Hampton | ✅ | ✅ | ✅ |  |
| `mdb-82` | Davis | ✅ | ✅ | ✅ |  |
| `mdb-820` | Colorado | ✅ | ✅ | ✅ |  |
| `mdb-822` | Washington | ✅ | ✅ | ✅ |  |
| `mdb-823` | New York | ✅ | ✅ | ✅ |  |
| `mdb-828` | Virginia | ✅ | ✅ | ✅ |  |
| `mdb-83` | Lodi | ✅ | ✅ | ✅ |  |
| `mdb-830` | Wausau | ✅ | ✅ | ✅ |  |
| `mdb-832` | Virginia | ✅ | ✅ | ✅ |  |
| `mdb-838` | Washington | ✅ | ✅ | ✅ |  |
| `mdb-85` | Fresno | ✅ | ✅ | ✅ |  |
| `mdb-851` | Elmira | ✅ | ✅ | ✅ |  |
| `mdb-854` | Azienda Trasporti Automobilist | ✅ | ✅ | ✅ |  |
| `mdb-855` | Milan | ✅ | ✅ | ✅ |  |
| `mdb-858` | Bayern | ✅ | ✅ | ✅ |  |
| `mdb-861` | Pécs | ✅ | ✅ | ✅ |  |
| `mdb-864` | Turku | ✅ | ✅ | ✅ |  |
| `mdb-867` | Jyväskylä | ✅ | ✅ | ✅ |  |
| `mdb-868` | Kuopio | ✅ | ✅ | ✅ |  |
| `mdb-869` | Oulu | ✅ | ✅ | ✅ |  |
| `mdb-871` | Watertown | ✅ | ✅ | ✅ |  |
| `mdb-882` | Altavista | ✅ | ✅ | ✅ |  |
| `mdb-883` |  Molalla | ✅ | ✅ | ✅ |  |
| `mdb-884` | Rīga | ✅ | ✅ | ✅ |  |
| `mdb-885` | Fort Worth | ✅ | ✅ | ✅ |  |
| `mdb-886` | Stockton | ✅ | ✅ | ✅ |  |
| `mdb-891` | Venice | ✅ | ✅ | ✅ |  |
| `mdb-892` | Barcelona | ✅ | ✅ | ✅ |  |
| `mdb-893` | Napoli | ✅ | ✅ | ✅ |  |
| `mdb-895` | Cagliari | ✅ | ✅ | ✅ |  |
| `mdb-897` | Nevada | ✅ | ✅ | ✅ |  |
| `mdb-898` | Paimboeuf | ✅ | ✅ | ✅ |  |
| `mdb-90` | Fresno | ✅ | ✅ | ✅ |  |
| `mdb-900` | Baden-Württemberg | ✅ | ✅ | ✅ |  |
| `mdb-905` | Huntington | ✅ | ✅ | ✅ |  |
| `mdb-906` | Baden-Württemberg | ✅ | ✅ | ✅ |  |
| `mdb-91` | Madera | ✅ | ✅ | ✅ |  |
| `mdb-911` | Clarkstown | ✅ | ✅ | ✅ |  |
| `mdb-916` | Long Beach | ✅ | ✅ | ✅ |  |
| `mdb-92` | Jackson | ✅ | ✅ | ✅ |  |
| `mdb-923` | Ames | ✅ | ✅ | ✅ |  |
| `mdb-927` | Poughkeepsie | ✅ | ✅ | ✅ |  |
| `mdb-928` | Poughkeepsie | ✅ | ✅ | ✅ |  |
| `mdb-929` | Lappeenranta | ✅ | ✅ | ✅ |  |
| `mdb-932` | Eugene | ✅ | ✅ | ✅ |  |
| `mdb-935` | Canberra | ✅ | ✅ | ✅ |  |
| `mdb-94` | Tahoe City | ✅ | ✅ | ✅ |  |
| `mdb-97` | San Bernardino | ✅ | ✅ | ✅ |  |
| `mdb-978` | Trentino-Alto Adige | ✅ | ✅ | ✅ |  |
| `mdb-981` | Szczecin | ✅ | ✅ | ✅ |  |
| `mdb-983` | Otago | ✅ | ✅ | ✅ |  |
| `mdb-988` | Provence-Alpes-Côte-d’Azur | ✅ | ✅ | ✅ |  |
| `mdb-991` | Regione Autonoma della Sardegn | ✅ | ✅ | ✅ |  |
| `mdb-994` | Commerce | ✅ | ✅ | ✅ |  |
| `nyc-subway` | New York City Subway | ✅ | ✅ | ✅ |  |
| `radom` | Radom | ✅ | ✅ | ✅ |  |
| `rzeszow` | Rzeszów | ✅ | ✅ | ✅ |  |
| `szczecin-zditm` | Szczecin | ✅ | ✅ | ✅ |  |
| `torun` | Toruń | ✅ | ✅ | ✅ |  |
| `mdb-100` | Anaheim | ✅ | ✅ | — | no multi-stop trips |
| `mdb-1001` | Wielkopolskie | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1003` | Barcelona | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1004` | Barcelona | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1010` | Bystry | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1012` | Łomża | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1017` | Málaga | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1021` | Managua | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1022` | Nicaragua | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1023` | Estelí | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1024` | Toulouse | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-103` | El Monte | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1031` | Trento | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1038` | Lisboa | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1039` | Alicante | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1047` | Regione Autonoma della Sardegn | ✅ | ✅ | — | no multi-stop trips |
| `mdb-1052` | Regione Autonoma della Sardegn | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1054` | Valenciana, Comunitat | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1055` | Grenoble | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1056` | Marseille | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1063` | Venice | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1066` | Lecce | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1067` | Sacramento | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-107` | Big Bear | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1076` | SMRT, SBS Transit (SBST), Land | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1080` | Washington | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1084` | Freiburg | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1085` | Baden-Württemberg | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1087` | Colorado | ✅ | ✅ | — | no multi-stop trips |
| `mdb-1088` | Bruxelles | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1089` | Regional Rail Transport German | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-109` | Bullhead City | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1091` | DPN, AVL, CFL, CFLBus, RGTR, T | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1093` | Baden-Württemberg | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1108` | Régime Général des Transports  | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1111` | Moncton | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1112` | Nancy | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1114` | Finferries, Alandstrafiken, Ro | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1116` | Besançon | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-112` | Oregon | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-113` | Modoc County | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1132` | Wellington | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1135` | Bilbao | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1141` | Colorado | ✅ | ✅ | — | no multi-stop trips |
| `mdb-1159` | Paris | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-116` | Red Bluff | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1162` | Bilbao | ✅ | ✅ | — | no multi-stop trips |
| `mdb-1172` | Thüringen | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1176` | Śląskie | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1178` | San Francisco | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1180` | Québec | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1195` | Broomfield | ✅ | ✅ | — | no multi-stop trips |
| `mdb-12` | Long Beach | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1229` | Bogor | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-123` | Roseburg | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1246` | Santa Barbara | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1255` | Seinäjoki | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1257` | Nantes | ✅ | ✅ | — | no multi-stop trips |
| `mdb-1258` | Pays de la Loire | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-127` | Oregon | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-128` | Salem | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1284` | Oregon | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1287` | Virginia | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-129` | Eugene | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1294` | Rome | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1295` | Woodland | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1298` | Metz | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1308` | Alabama | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-131` | Eugene | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1314` | Paris | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1328` | Virginia | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1329` | Abu Dhabi Emirate | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1331` | Washington | ✅ | ✅ | — | no multi-stop trips |
| `mdb-1332` | Modesto | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-142` | Boise | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-148` | El Paso | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-151` | Denton | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-152` | Dallas | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-156` | Arizona | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-16` | Laguna Beach | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-160` | Farmington | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-161` | Colorado | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-165` | New Mexico | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-167` | New Mexico | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-168` | Colorado Springs | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-170` | Salt Lake City | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1789` | Choletais | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-179` | Fort Collins | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1820` | Toulon | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1823` | Izmir | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1827` | Ljubljana | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1828` | Izmir | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1829` | Izmir | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1830` | Mexico City | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1831` | Bangkok | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1834` | Šiaulių apskritis | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1835` | Greater Kochi | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1837` | Bretagne | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1838` | Seine-Eure | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1840` | Communauté d'agglomération Le  | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1842` | Santa Cruz | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1860` | Antwerp | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-187` | Kansas City | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1870` | Valenciana, Comunidad | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1871` | British Columbia | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1872` | Santa Barbara County | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1876` | Boulogne-sur-Mer | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1878` | Avignon | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1879` | Rochefort | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1880` | Bonneville | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1882` | Bar-le-Duc, Verdun, Commercy | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1889` | Alès | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1892` | Ucel | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1894` | Île de Ré | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1899` | Albertville | ✅ | ✅ | — | no multi-stop trips |
| `mdb-190` | St. Louis | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1902` | Liberec | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-191` | Sioux City | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1914` | Santiago de los Caballeros | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-192` | Sioux Falls | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1928` | Brighton and Hove | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1943` | Bournemouth, Christchurch and  | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1944` | West Berkshire | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1946` | Nottingham | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1949` | Reading | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1951` | Isle of Wight | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1952` | Swindon | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1953` | Transdev Blazefield | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1954` | Bournemouth and Poole | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1955` | Hampshire | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1956` | Warrington | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1958` | Hanover | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-196` | Coralville | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1970` | Shuttler | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1973` | Athens | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1985` | Aeroexpreso | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1987` | Centre-Val de Loire | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1988` | Amiens Métropole | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1989` | Longuenesse | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1990` | Dunkirk | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1991` | Central Fraser Valley | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1992` | Red Deer | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1994` | Brampton | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1996` | Sherbrooke | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-1998` | Saint-Quentin | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2` | London | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-20` | Crescent City | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2002` | Angoulême | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2003` | Cannes | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2004` | Grasse | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2005` | La Roche-sur-Yon | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2006` | Rhône | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2007` | Angers | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2009` | Regione Autonoma della Sardegn | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-201` | Rock Island | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2015` | Pasažieru Vilciens | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2018` | Jūrmala | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2019` | Rockford | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2026` | Wilmington | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2030` | San Diego | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2031` | Vancouver | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2032` | Winona | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2033` | Oaxaca | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2034` | Puerto Vallarta | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2036` | Prague | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2038` | Minnesota | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2042` | Denver | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2043` | Denver | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2044` | Denver | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2045` | Denver | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2046` | Denver | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2048` | Denver | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2049` | Denver | ✅ | ✅ | — | no multi-stop trips |
| `mdb-205` | Minneapolis | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2052` | Denver | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2053` | Systemaufgaben Kundeninformati | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2054` | Denver | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2055` | Daytrip Shuttle | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2056` | Daytrip Shuttle | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2059` | Morro Bay | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2061` | Eagle County | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2074` | Raleigh | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2077` | Communauté urbaine de Douala | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2078` | Abidjan | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2079` | Binghamton | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-208` | Eau Claire | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2080` | Savannah | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2082` | Chattanooga | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2084` | Wejherowo | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2085` | Świnoujście | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-209` | New York City | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2091` | Warsaw | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2092` | Warsaw | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2093` | Gdańsk | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2099` | Sibiu | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2100` | Constanța | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2101` | Oradea | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2102` | Zalău | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2121` | Cluj-Napoca | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2133` | Pays dʼAix | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2134` | Cancun | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2136` | Sacramento | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2137` | Sacramento | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2138` | OBB Personenverkehr AG Kundens | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2139` | MAT mobilités | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2146` | Albany | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2148` | Porto | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2150` | Navarra | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2151` | San Jose | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2152` | Lille | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2153` | Dijon | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2155` | South Moravian | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2156` | Adams County | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2157` | Bent County | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2161` | Loveland | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2164` | Concord | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2165` | Aurora | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2169` | Kiowa County | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2170` | La Junta | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2171` | Lakewood | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2172` | Manteca | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2173` | Granby | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2174` | Stanislaus County | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2175` | Littleton | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2178` | Steamboat Springs | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2179` | Roaring Fork Valley | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2180` | San Joaquin County | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2181` | Colorado | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2182` | Colorado Springs | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2184` | Durango | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2185` | Pueblo | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2186` | Modesto | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2187` | California | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2188` | Colorado | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2189` | Milton-Freewater | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2191` | Boulder | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2192` | Massachusetts | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2193` | Longview | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2200` | Trujillo | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2201` | Montebello | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2206` | Tucson | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2210` | El Segundo | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2211` | Anniston | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2223` | Washington | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2233` | Arvin | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-224` | Virginia | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2240` | Preston | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2248` | Cudahy | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2249` | Bell | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2250` | La Puente | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2251` | Sierra Madre | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2253` | Toronto | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2257` | Citrus County | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2258` | Manatee County | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2259` | Collier County | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2263` | Birmingham | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2264` | Pulaski County | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2270` | Gardena | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2279` | Ridgecrest | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-228` | Bell Gardens | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2280` | Denver | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2284` | Carlsbad | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2288` | Grand Junction | ✅ | ✅ | — | no multi-stop trips |
| `mdb-229` | Benson | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2290` | Durango | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2291` | Lake County | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2292` | Colorado Springs | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2293` | Fort Collins | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2294` | Pagosa Springs | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2295` | California | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2299` | Mansfield | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-230` | Las Animas | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2301` | Litchfield | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2302` | Washington | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2304` | Davenport | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2306` | Colorado | ✅ | ✅ | — | no multi-stop trips |
| `mdb-231` | Bethesda | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2310` | Skagit County | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2311` | Lynnwood | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2314` | Washington | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2315` | Thousand Oaks | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2316` | Kimball | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2317` | Kiryas Joel | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2319` | Lummi Island | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2320` | Washington | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2321` | Megabus | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2322` | Miami Beach  | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2323` | Miami Gardens | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2324` | Middletown | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2327` | Washington | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2330` | Colorado | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2332` | Chicago | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2336` | Mumbai | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2346` | New Mexico | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2353` | New York | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2354` | Arizona | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2356` | Colorado Springs | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2357` | Porto | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-236` | Ripon | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2362` | San Clemente | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2366` | Guadajalara Metropolitan Area | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2367` | Fortaleza | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-237` | Breckenridge | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2373` | Palermo | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2381` | Isparta | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2385` | B-Bus | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2386` | Nouvelle Aquitaine | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2387` | Rzeszów | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2389` | British Columbia | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2394` | Yosemite | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2399` | Katowice | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2400` | Fuenlabrada | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2404` | Riom Limagne et Volcans | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2407` | Sincelejo | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2408` | Almada | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2411` | Virginia | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2414` | Black Hawk County | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2419` | Gadsen | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2420` | Tennessee | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2421` | Tennessee | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2425` | Santa Cruz | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-243` | Klawock | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2434` | Arlington | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2435` | Roanoke | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2436` | Virginia | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2437` | Virginia | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2438` | Williamsburg | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2439` | Warsaw | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2446` | Cape Cod | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2460` | Fredericton | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2461` | Kalisz | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2462` | Hazelton | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2515` | Clearwater | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2519` | Ministry of Transport and Road | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-252` | Canby | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2524` | Comox Valley | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-253` | Portland | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-254` | Portland | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2555` | Kelowna | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-257` | Oregon | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2571` | Victoria | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2595` | Bengaluru | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2604` | Occitanie | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2610` | Genoa | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2615` | Sark Shipping | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2616` | Vail | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2618` | Hamilton | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2622` | Bordeaux | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2626` | Sens | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2627` |  Troyes Champagne Métropole | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2628` |  Troyes Champagne Métropole | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2632` | Angra dos Reis | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2641` | Portland | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2642` | Portland | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2648` | Huntington Park | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2649` | Hampton | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-265` | Washington | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2650` | Schenectady | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2651` | Nordrhein-Westfalen | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2666` | Milan | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2667` | Santa Cruz | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2679` | New York | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2685` | Ville de Honfleur | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2689` | Kórnik | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2690` | Extremadura | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-270` | Seattle | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-271` | Washington | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2720` | Madrid | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2738` | Nueves-Maisons | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-278` | Selah | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-283` | Seattle | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2836` | Famalicão,Santo Tirso,Trofa | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2837` | Barcelos | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2841` | Trento | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2855` | Kingman | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2856` | Coolidge | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-286` | Washington | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2860` | Town of Miami | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2863` | Show Low | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2864` | Douglas | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2882` | Vermont | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-29` | Los Angeles | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2902` | Wächtersbach | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2905` | Uusimaa | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2907` | Bluestar Bus | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2908` | Go Devon Bus | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2910` | Gradski parking d.o.o. | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2922` | Türkiye | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2923` | Santa Eulalia del Río | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2926` | Catalonia | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2928` | Niš | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-293` | Missoula | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2933` | Just Use Wheels | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2934` | Fortaleza | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2935` | Fortaleza | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-2936` | City of Alexandria | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2994` | Regione Autonoma della Sardegn | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2995` | Regione Autonoma della Sardegn | ✅ | ✅ | — | no multi-stop trips |
| `mdb-2996` | Regione Autonoma della Sardegn | ✅ | ✅ | — | no multi-stop trips |
| `mdb-30` | Los Angeles | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-3039` | Hope College | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-3040` | Bologna | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-3042` | Ferrara | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-3049` | ONCF (Office National des Chem | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-305` | Elmira | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-3050` | APSRTC | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-3052` | Metro Bilbao | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-3081` | Reus | ✅ | ✅ | — | no multi-stop trips |
| `mdb-310` | Helena | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-3100` | Thousand Oaks | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-3105` | New Jersey | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-3107` | European Sleeper | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-3123` | Optima Express | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-3132` | Administration des transports  | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-3134` | VD-Express | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-3139` | Delhi Transport Corporation | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-314` | Compton | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-3140` | Guelph Transit | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-3144` | Lagos State | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-3149` | Salisbury | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-315` | Corpus Christi | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-3153` | ELRON | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-3156` | Rzeszowski Transport Miejski | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-3161` | BAS.MY Ipoh | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-3162` | BAS.MY Seremban A | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-3163` | BAS.MY Seremban B | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-317` | Cripple Creek | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-3179` | Consiliul Județean Buzău - Tra | ✅ | ✅ | — | no multi-stop trips |
| `mdb-3180` | PKS w Rzeszowie S.A. | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-3184` | Kecskeméti Kisvasút | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-3185` | Kumejima Ocean Jet Co., Ltd. | ✅ | ✅ | — | no multi-stop trips |
| `mdb-3188` | Transporte Público Urbano de I | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-319` | Groome Transportation | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-3190` | Laval | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-3191` | Polish Trains | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-322` | Key West | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-326` | Pinellas County | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-333` | Pompano Beach | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-335` | Pensacola | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-337` | Panama City | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-34` | Torrance | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-340` | Spring Hill | ✅ | ✅ | — | no multi-stop trips |
| `mdb-343` | Ocala | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-344` | Tallahassee | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-349` | Daytona Beach | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-350` | Saint Augustine | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-360` | Nashville | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-378` | Durham | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-38` | Culver City | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-383` | California | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-384` | Michigan | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-387` | Terre Haute | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-393` | Janesville | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-396` | Waukesha | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-409` | Pittsburgh | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-412` | Erie | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-413` | Detroit | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-414` | Michigan | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-418` | Attleboro | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-419` | North Kingstown | ✅ | ✅ | — | no multi-stop trips |
| `mdb-420` | New Bedford | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-421` | Massachusetts | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-423` | Massachusetts | ✅ | ✅ | — | no multi-stop trips |
| `mdb-424` | Massachusetts | ✅ | ✅ | — | no multi-stop trips |
| `mdb-425` | Massachusetts | ✅ | ✅ | — | no multi-stop trips |
| `mdb-427` | New Bedford | ✅ | ✅ | — | no multi-stop trips |
| `mdb-435` | Boston | ✅ | ✅ | — | no multi-stop trips |
| `mdb-436` | Boston | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-445` | Massachusetts | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-448` | Vermont | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-451` | New Hampshire | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-455` | Colorado Springs | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-460` | Express Arrow | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-464` | Detroit | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-466` | Maryland | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-47` | Bakersfield | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-473` | Hampton | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-474` | Williamsburg | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-475` | Kent | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-48` | Tulare | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-489` | Maryland | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-490` | Baltimore | ✅ | ✅ | — | no multi-stop trips |
| `mdb-493` | Maryland | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-495` | Ocean City | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-496` | Massachusetts | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-499` | York | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-500` | Maryland | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-501` | Aberdeen | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-502` | Philadelphia | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-503` | Philadelphia | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-51` | San Francisco | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-510` | New York City | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-512` | New York City | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-513` | New York City | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-514` | New York City | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-517` | Jersey City | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-52` | San Francisco | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-520` | New York City | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-523` | Pennsylvania | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-528` | New York City | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-530` | Bridgeport | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-532` | New York | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-533` | Rochester | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-534` | Syracuse | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-535` | Ithaca | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-539` | Bennington | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-547` | Burlington | ✅ | ✅ | — | no multi-stop trips |
| `mdb-55` | Modesto | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-550` | Connecticut | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-554` | Newport | ✅ | ✅ | — | no multi-stop trips |
| `mdb-555` | Massachusetts | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-56` | Monterey | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-560` | Klamath Falls | ✅ | ✅ | — | no multi-stop trips |
| `mdb-565` | Las Vegas | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-567` | Washington | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-568` | Longview | ✅ | ✅ | — | no multi-stop trips |
| `mdb-57` | San Jose | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-570` | Los Angeles | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-572` | Madera | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-579` | Palm Springs | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-58` | Hollister | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-580` | Washington | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-581` | Crested Butte | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-583` | Needles | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-594` | Town of Mountain Village | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-599` | Vacaville | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-600` | Aix les Bains | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-605` | Portland | ✅ | ✅ | — | no multi-stop trips |
| `mdb-606` | Los Angeles | ✅ | ✅ | — | no multi-stop trips |
| `mdb-607` | Boulder | ✅ | ✅ | — | no multi-stop trips |
| `mdb-614` | Colorado | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-615` | Greensboro | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-617` | California | ✅ | ✅ | — | no multi-stop trips |
| `mdb-618` | Baltimore | ✅ | ✅ | — | no multi-stop trips |
| `mdb-619` | Turlock | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-620` | Gary | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-624` | Rhode Island | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-625` | Texas | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-628` | California | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-629` | Burlington | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-639` | Eugene | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-64` | Livermore | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-641` | Grenoble | ✅ | ✅ | — | no multi-stop trips |
| `mdb-642` | Communauté de l'Auxerrois | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-643` | Genoa | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-645` | Cape Cod | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-65` | Escalon | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-655` | Rockhampton | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-656` | Vannes | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-658` | Chalon-sur-Saône | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-66` | San Mateo | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-67` | San Francisco | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-679` | Magnetic Island | ✅ | ✅ | — | no multi-stop trips |
| `mdb-680` | Darwin | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-685` | Antwerpen | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-687` | Belo Horizonte | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-7` | Porto Alegre | ✅ | ✅ | — | no multi-stop trips |
| `mdb-711` | Banff | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-712` | Calgary | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-714` | Edmonton | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-716` | Saskatoon | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-717` | Winnipeg | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-725` | Oakville | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-726` | Durham | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-728` | York | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-732` | Toronto | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-735` | VIA Rail Canada | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-739` | La Pêche | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-74` | Oakland | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-745` | Québec | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-747` | Québec | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-75` | Colorado | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-751` | Longueuil | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-752` | La Vallée-du-Richelieu | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-758` | St. John's | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-759` | Milton | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-76` | Fairfield | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-768` | Long-distance rail transport i | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-77` | Sacramento | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-773` | Ulm | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-777` | Mannheim | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-780` | Bayern | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-788` | Santa Cruz de Tenerife | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-789` | Hauts-de-France | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-794` | Madrid | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-795` | València | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-797` | Vitoria-Gasteiz | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-802` | Detroit | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-81` | Rio Vista | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-811` | Colorado | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-814` | Elmira | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-824` | New York | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-827` | Colorado | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-833` | Salem | ✅ | ✅ | — | no multi-stop trips |
| `mdb-834` | Albany | ✅ | ✅ | — | no multi-stop trips |
| `mdb-839` | Santa Fe | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-84` | Nevada County | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-841` | Provence-Alpes-Côte-d’Azur | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-842` | Provence-Alpes-Côte-d’Azur | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-843` | Provence-Alpes-Côte-d’Azur | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-844` | Occitanie | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-845` | Provence-Alpes-Côte d'Azur | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-852` | Burlington | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-856` | Grand Est | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-857` | Augsburg | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-862` | Budapest | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-866` | Tampereen joukkoliikenne (JOLI | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-875` | Yates | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-879` | Colorado Springs | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-887` | Szeged | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-888` | Provence-Alpes-Côte-d’Azur | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-889` | Provence-Alpes-Côte-d’Azur | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-890` | Provence-Alpes-Côte-d'Azur | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-896` | Messina | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-899` | Ithaca | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-9` | Belo Horizonte | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-902` | Richmond | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-903` | Asheville | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-907` | Rockhampton | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-910` | New York | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-915` | Stamford | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-918` | Baden-Württemberg | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-920` | Tuttlingen | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-93` | San Andreas | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-931` | Burns | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-933` | Bend | ✅ | ✅ | — | no multi-stop trips |
| `mdb-936` | Canberra | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-96` | California | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-98` | Riverside | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-980` | Wroclaw | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-982` | Poznań | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-99` | Hesperia | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-990` | Budapest | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-993` | Madrid | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-996` | Grasse | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `mdb-999` | Brest | ✅ | ✅ | — | no service today (expired/inactive calendar?) |
| `berlin-vbb` | Berlin / Brandenburg | ✅ | — | — | skipped: 75 MB > 25 MB sample cap |
| `cta-chicago` | Chicago | ✅ | — | — | skipped: 67 MB > 25 MB sample cap |
| `gzm-katowice` | GZM / Katowice / Silesia | ✅ | — | — | skipped: 44 MB > 25 MB sample cap |
| `mdb-1026` | Paris | ✅ | — | — | ValueError: stop_times.txt exceeds 8000000 rows limit |
| `mdb-1077` | OVapi | ✅ | — | — | ingest exceeded 240s |
| `mdb-1078` | Entur | ✅ | — | — | ValueError: zip exceeds 250 MB limit |
| `mdb-1081` | Ulmer Eisenbahnfreunde, Sächsi | ✅ | — | — | ValueError: zip exceeds 250 MB limit |
| `mdb-1086` | Perth | ✅ | — | — | KeyError: 'shape_pt_sequence' |
| `mdb-1090` | Public Transport Germany | ✅ | — | — | ingest exceeded 240s |
| `mdb-1104` | CFR Călători, Astra Trans Carp | ✅ | — | — | ValueError: not a GTFS feed: missing routes.txt |
| `mdb-1220` | Buenos Aires | ✅ | — | — | ValueError: stop_times.txt exceeds 8000000 rows limit |
| `mdb-1276` | Miaoli | ✅ | — | — | _csv.Error: line contains NUL |
| `mdb-1788` | Wasco | ✅ | — | — | ValueError: not a GTFS feed: missing routes.txt |
| `mdb-1808` | Addis Ababa | ✅ | — | — | AttributeError: 'NoneType' object has no attribute 'strip' |
| `mdb-1814` | Kumasi | ✅ | — | — | ValueError: not a GTFS feed: missing routes.txt |
| `mdb-1817` | Monrovia | ✅ | — | — | ValueError: not a GTFS feed: missing routes.txt |
| `mdb-1818` | Dixon | ✅ | — | — | ValueError: not a GTFS feed: missing routes.txt |
| `mdb-1819` | Anaheim | ✅ | — | — | ValueError: not a GTFS feed: missing routes.txt |
| `mdb-1824` | Izmir | ✅ | — | — | ValueError: not a GTFS feed: missing routes.txt |
| `mdb-1867` | Salina | — | — | — | HTTP error |
| `mdb-1927` | Braga | ✅ | — | — | KeyError: 'shape_pt_sequence' |
| `mdb-1936` | Manchester | ✅ | — | — | ValueError: not a GTFS feed: missing trips.txt |
| `mdb-2014` | BODS UK aggregate feed | ✅ | — | — | ValueError: zip exceeds 250 MB limit |
| `mdb-2027` | Lisboa | ✅ | — | — | ValueError: stop_times.txt exceeds 8000000 rows limit |
| `mdb-2106` | Buzău | — | — | — | HTTP error |
| `mdb-2107` | Târgoviște | — | — | — | HTTP error |
| `mdb-2108` | Ploiești | — | — | — | HTTP error |
| `mdb-2203` | Sacramento | — | — | — | HTTP error |
| `mdb-2234` | Camarillo | ✅ | — | — | ValueError: not a GTFS feed: missing routes.txt |
| `mdb-2235` | San Juan Capistrano | ✅ | — | — | ValueError: not a GTFS feed: missing routes.txt |
| `mdb-2236` | Taft | ✅ | — | — | ValueError: not a GTFS feed: missing routes.txt |
| `mdb-2238` | Berkeley | ✅ | — | — | ValueError: not a GTFS feed: missing routes.txt |
| `mdb-2360` | Halle | — | — | — | HTTP error |
| `mdb-2363` | Danville | — | — | — | HTTP error |
| `mdb-2364` | Transport for Ireland (TFI) | ✅ | — | — | ValueError: stop_times.txt exceeds 8000000 rows limit |
| `mdb-2393` | Baden-Wuttemberg | — | — | — | HTTP error |
| `mdb-2412` | Gainesville | — | — | — | HTTP error |
| `mdb-2416` | Massachusetts | — | — | — | HTTP error |
| `mdb-2426` | Georgia | ✅ | — | — | TypeError: int() argument must be a string, a bytes-like object or a n |
| `mdb-2430` | Virginia | — | — | — | HTTP error |
| `mdb-2431` | Eurostar, Thalys, SNCF, DB ICE | — | — | — | HTTP error |
| `mdb-2449` | New South Wales | ✅ | — | — | ValueError: zip exceeds 250 MB limit |
| `mdb-2602` | Moose Jaw | — | — | — | HTTP error |
| `mdb-2608` | Hawai'i Island | — | — | — | HTTP error |
| `mdb-2620` | Renfe | ✅ | — | — | KeyError: 'end_date' |
| `mdb-2653` | Renfe commuter trains (Cercani | ✅ | — | — | KeyError: 'end_date' |
| `mdb-2710` | Kocaeli | — | — | — | HTTP error |
| `mdb-2842` | Royan | — | — | — | HTTP error |
| `mdb-2853` | Redding | — | — | — | HTTP error |
| `mdb-2854` | Chicago | ✅ | — | — | KeyError: 'trip_id' |
| `mdb-2865` | Toluca | — | — | — | HTTP error |
| `mdb-2866` | Jilotepec | — | — | — | HTTP error |
| `mdb-2875` | County Cork | — | — | — | HTTP error |
| `mdb-2876` | Lake Tahoe | — | — | — | HTTP error |
| `mdb-2883` | Mountain View | — | — | — | HTTP error |
| `mdb-2886` | San Francisco | — | — | — | HTTP error |
| `mdb-2898` | Systemaufgaben Kundeninformati | ✅ | — | — | ValueError: stop_times.txt exceeds 8000000 rows limit |
| `mdb-2904` | Czech national bus feed JDF | — | — | — | HTTP error |
| `mdb-2914` | Dartford | — | — | — | HTTP error |
| `mdb-2929` | Lisbon | — | — | — | HTTP error |
| `mdb-299` | Long Beach | ✅ | — | — | ValueError: not a GTFS feed: missing routes.txt |
| `mdb-2992` | Coimbra | — | — | — | HTTP error |
| `mdb-3036` | King of Prussia | — | — | — | HTTP error |
| `mdb-3048` | Queensland | — | — | — | HTTP error |
| `mdb-3051` | Land Transport Authority (Sing | — | — | — | HTTP error |
| `mdb-3128` | Istanbul | — | — | — | HTTP error |
| `mdb-3129` | Vancouver | — | — | — | HTTP error |
| `mdb-3133` | Algoa Bus | — | — | — | HTTP error |
| `mdb-3135` | GTFS Honduras Open (National T | — | — | — | HTTP error |
| `mdb-3145` | Autobuses urbanos de Burgos | — | — | — | HTTP error |
| `mdb-3147` | Hobart | ✅ | — | — | ValueError: not a GTFS feed: missing routes.txt |
| `mdb-3150` | Waterloo | — | — | — | HTTP error |
| `mdb-3151` | GRT ION Light Rail | — | — | — | HTTP error |
| `mdb-3177` | Glendale | — | — | — | HTTP error |
| `mdb-3181` | Centro Comercial RÍO Shopping  | ✅ | — | — | ValueError: not a GTFS feed: missing routes.txt |
| `mdb-3201` | Marsala | — | — | — | HTTP error |
| `mdb-3202` | El Paso | — | — | — | HTTP error |
| `mdb-3205` | North Carolina | — | — | — | HTTP error |
| `mdb-3206` | California | — | — | — | HTTP error |
| `mdb-3207` | Florida | — | — | — | HTTP error |
| `mdb-3208` | San Francisco | — | — | — | HTTP error |
| `mdb-3209` | Pensacola | — | — | — | HTTP error |
| `mdb-3210` | Gulfport | — | — | — | HTTP error |
| `mdb-3211` | Colorado | — | — | — | HTTP error |
| `mdb-3215` | DELFI Germany-wide scheduled t | — | — | — | HTTP error |
| `mdb-3218` | Dallas | — | — | — | HTTP error |
| `mdb-3219` | Medford | — | — | — | HTTP error |
| `mdb-3220` | Athens Urban Transport Organiz | — | — | — | HTTP error |
| `mdb-3221` | Athens Urban Transport Organiz | — | — | — | HTTP error |
| `mdb-3225` | Curitiba | — | — | — | HTTP error |
| `mdb-3230` | Kyiv | — | — | — | HTTP error |
| `mdb-3233` | Berlin | — | — | — | HTTP error |
| `mdb-3234` | Berlin | — | — | — | HTTP error |
| `mdb-3235` | ABuss OÜ, Aktsiaselts Hansa Bu | — | — | — | HTTP error |
| `mdb-3236` | Romanian Railway Operators | — | — | — | HTTP error |
| `mdb-331` | Miami | ✅ | — | — | ValueError: not a GTFS feed: missing routes.txt |
| `mdb-3340` | Melbourne | — | — | — | HTTP error |
| `mdb-3354` | Al Qahirah | — | — | — | HTTP error |
| `mdb-3355` | Cairo | — | — | — | HTTP error |
| `mdb-3357` | Región Metropolitana de Santia | — | — | — | HTTP error |
| `mdb-3358` | Distrito Capital de Bogotá | — | — | — | HTTP error |
| `mdb-3361` | Hyderabad | — | — | — | HTTP error |
| `mdb-3362` | Hamburg | — | — | — | HTTP error |
| `mdb-518` | New York City | ✅ | — | — | ValueError: not a GTFS feed: missing routes.txt |
| `mdb-683` | Alice Springs | ✅ | — | — | KeyError: 'route_id' |
| `mdb-684` | Vlaams Gewest | ✅ | — | — | ValueError: unpacked size exceeds 2500 MB limit |
| `mdb-784` | Rursee-Schifffahrt KG | ✅ | — | — | ValueError: zip exceeds 250 MB limit |
| `mdb-812` | Santa Clarita | ✅ | — | — | ValueError: not a GTFS feed: missing routes.txt |
| `mdb-865` | Helsinki | ✅ | — | — | ValueError: stop_times.txt exceeds 8000000 rows limit |
| `mdb-912` | Puglia | ✅ | — | — | ValueError: not a GTFS feed: missing routes.txt |
| `mdb-992` | Rīga | ✅ | — | — | KeyError: 'shape_pt_sequence' |
| `pkp-trains` | Poland (national rail / PKP) | ✅ | — | — | skipped: 28 MB > 25 MB sample cap |
| `trimet-portland` | Portland, OR | ✅ | — | — | skipped: 38 MB > 25 MB sample cap |
| `warszawa-ztm` | Warszawa | ✅ | — | — | skipped: 97 MB > 25 MB sample cap |

</details>


<sub>Reproduce: `python3 scripts/deep_check.py all` · numeric samples use a fixed seed, so they are stable between runs.</sub>