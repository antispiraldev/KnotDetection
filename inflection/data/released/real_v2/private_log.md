# Private data-preparation log: `real_v2` (SEALED, identities and test outcomes)

Dataset Maddison Project Database 2020 (Groningen Growth and Development Centre), version 2020, sha256 `d20853c2e0930d6855fb6d8138da11f24fcf313d234e2db9773ea1f551adfec3`, downloaded 2026-09-22T19:12:32+00:00 from https://www.rug.nl/ggdc/historicaldevelopment/maddison/data/mpd2020.xlsx.
Sheet used: `Full data`.

Fallback used: False.

## TEST class balance
- windows 981, events 130, controls 851, base rate 0.133
- severe events (horizon minimum below 0.6 x the record maximum): 47
- by era: {'post1950': 462, 'pre1950': 519}; events by era: {'pre1950': 77, 'post1950': 53}
- countries: 74; windows per country: min 1, max 123

## DEV class balance
- windows 1030, events 189, controls 841, base rate 0.183
- severe events (horizon minimum below 0.6 x the record maximum): 47
- by era: {'post1950': 381, 'pre1950': 649}; events by era: {'pre1950': 144, 'post1950': 45}
- countries: 73; windows per country: min 1, max 138

## Test windows
| id | group | countrycode | country | t0 | event_year | severe | era |
|---|---|---|---|---|---|---|---|
| real_v2-0000 | g0000 | GTM | Guatemala | 1985 | None | False | post1950 |
| real_v2-0001 | g0001 | BEL | Belgium | 1975 | None | False | post1950 |
| real_v2-0002 | g0002 | FIN | Finland | 2000 | None | False | post1950 |
| real_v2-0003 | g0003 | NOR | Norway | 1885 | None | False | pre1950 |
| real_v2-0004 | g0004 | FRA | France | 1350 | None | False | pre1950 |
| real_v2-0005 | g0005 | CHE | Switzerland | 1920 | 1921 | False | pre1950 |
| real_v2-0006 | g0003 | NOR | Norway | 1880 | None | False | pre1950 |
| real_v2-0007 | g0004 | FRA | France | 1965 | None | False | post1950 |
| real_v2-0008 | g0003 | NOR | Norway | 1960 | None | False | post1950 |
| real_v2-0009 | g0004 | FRA | France | 1700 | None | False | pre1950 |
| real_v2-0010 | g0006 | POL | Poland | 1540 | None | False | pre1950 |
| real_v2-0011 | g0007 | CAN | Canada | 1950 | None | False | pre1950 |
| real_v2-0012 | g0003 | NOR | Norway | 1890 | None | False | pre1950 |
| real_v2-0013 | g0008 | NZL | New Zealand | 1910 | None | False | pre1950 |
| real_v2-0014 | g0006 | POL | Poland | 1475 | None | False | pre1950 |
| real_v2-0015 | g0009 | PER | Peru | 1855 | None | False | pre1950 |
| real_v2-0016 | g0009 | PER | Peru | 1795 | 1801 | False | pre1950 |
| real_v2-0017 | g0004 | FRA | France | 1365 | None | False | pre1950 |
| real_v2-0018 | g0010 | BOL | Bolivia (Plurinational State of) | 1940 | None | False | pre1950 |
| real_v2-0019 | g0011 | GNQ | Equatorial Guinea | 1980 | 1981 | False | post1950 |
| real_v2-0020 | g0012 | TGO | Togo | 1980 | 1983 | True | post1950 |
| real_v2-0021 | g0008 | NZL | New Zealand | 1945 | None | False | pre1950 |
| real_v2-0022 | g0003 | NOR | Norway | 1970 | None | False | post1950 |
| real_v2-0023 | g0006 | POL | Poland | 1725 | None | False | pre1950 |
| real_v2-0024 | g0006 | POL | Poland | 1735 | None | False | pre1950 |
| real_v2-0025 | g0013 | SYR | Syrian Arab Republic | 1980 | None | False | post1950 |
| real_v2-0026 | g0014 | LKA | Sri Lanka | 1980 | None | False | post1950 |
| real_v2-0027 | g0006 | POL | Poland | 1525 | None | False | pre1950 |
| real_v2-0028 | g0004 | FRA | France | 1480 | None | False | pre1950 |
| real_v2-0029 | g0015 | COL | Colombia | 1995 | None | False | post1950 |
| real_v2-0030 | g0016 | DNK | Denmark | 1880 | None | False | pre1950 |
| real_v2-0031 | g0009 | PER | Peru | 1790 | 1801 | False | pre1950 |
| real_v2-0032 | g0017 | ECU | Ecuador | 1955 | None | False | post1950 |
| real_v2-0033 | g0009 | PER | Peru | 1740 | None | False | pre1950 |
| real_v2-0034 | g0009 | PER | Peru | 1720 | None | False | pre1950 |
| real_v2-0035 | g0018 | CSK | Czechoslovakia | 1980 | None | False | post1950 |
| real_v2-0036 | g0019 | CHN | China | 1980 | None | False | post1950 |
| real_v2-0037 | g0011 | GNQ | Equatorial Guinea | 2010 | 2016 | True | post1950 |
| real_v2-0038 | g0017 | ECU | Ecuador | 2000 | None | False | post1950 |
| real_v2-0039 | g0004 | FRA | France | 1530 | None | False | pre1950 |
| real_v2-0040 | g0020 | ESP | Spain | 1960 | None | False | post1950 |
| real_v2-0041 | g0006 | POL | Poland | 1645 | None | False | pre1950 |
| real_v2-0042 | g0021 | AUT | Austria | 1925 | None | False | pre1950 |
| real_v2-0043 | g0004 | FRA | France | 1445 | None | False | pre1950 |
| real_v2-0044 | g0016 | DNK | Denmark | 1855 | None | False | pre1950 |
| real_v2-0045 | g0001 | BEL | Belgium | 1935 | None | False | pre1950 |
| real_v2-0046 | g0022 | VEN | Venezuela (Bolivarian Republic of) | 1915 | 1916 | False | pre1950 |
| real_v2-0047 | g0004 | FRA | France | 1435 | None | False | pre1950 |
| real_v2-0048 | g0016 | DNK | Denmark | 1850 | None | False | pre1950 |
| real_v2-0049 | g0000 | GTM | Guatemala | 1970 | None | False | post1950 |
| real_v2-0050 | g0019 | CHN | China | 2000 | None | False | post1950 |
| real_v2-0051 | g0021 | AUT | Austria | 1935 | 1945 | True | pre1950 |
| real_v2-0052 | g0023 | MLI | Mali | 1995 | None | False | post1950 |
| real_v2-0053 | g0024 | BRB | Barbados | 1990 | None | False | post1950 |
| real_v2-0054 | g0006 | POL | Poland | 1505 | None | False | pre1950 |
| real_v2-0055 | g0020 | ESP | Spain | 1955 | None | False | post1950 |
| real_v2-0056 | g0020 | ESP | Spain | 1915 | None | False | pre1950 |
| real_v2-0057 | g0006 | POL | Poland | 1600 | 1615 | False | pre1950 |
| real_v2-0058 | g0021 | AUT | Austria | 1940 | 1945 | True | pre1950 |
| real_v2-0059 | g0002 | FIN | Finland | 1900 | None | False | pre1950 |
| real_v2-0060 | g0004 | FRA | France | 1865 | None | False | pre1950 |
| real_v2-0061 | g0006 | POL | Poland | 1625 | None | False | pre1950 |
| real_v2-0062 | g0020 | ESP | Spain | 1900 | None | False | pre1950 |
| real_v2-0063 | g0016 | DNK | Denmark | 1995 | None | False | post1950 |
| real_v2-0064 | g0025 | PSE | State of Palestine | 2000 | 2001 | False | post1950 |
| real_v2-0065 | g0026 | CHL | Chile | 1840 | None | False | pre1950 |
| real_v2-0066 | g0024 | BRB | Barbados | 1985 | None | False | post1950 |
| real_v2-0067 | g0027 | ETH | Ethiopia | 1985 | 1992 | False | post1950 |
| real_v2-0068 | g0014 | LKA | Sri Lanka | 1945 | None | False | pre1950 |
| real_v2-0069 | g0028 | DZA | Algeria | 1990 | None | False | post1950 |
| real_v2-0070 | g0029 | MUS | Mauritius | 1985 | None | False | post1950 |
| real_v2-0071 | g0030 | IDN | Indonesia | 1910 | None | False | pre1950 |
| real_v2-0072 | g0005 | CHE | Switzerland | 1940 | None | False | pre1950 |
| real_v2-0073 | g0031 | DEU | Germany | 1990 | None | False | post1950 |
| real_v2-0074 | g0016 | DNK | Denmark | 1940 | None | False | pre1950 |
| real_v2-0075 | g0010 | BOL | Bolivia (Plurinational State of) | 1985 | None | False | post1950 |
| real_v2-0076 | g0009 | PER | Peru | 1635 | None | False | pre1950 |
| real_v2-0077 | g0009 | PER | Peru | 1765 | None | False | pre1950 |
| real_v2-0078 | g0032 | ISR | Israel | 1990 | None | False | post1950 |
| real_v2-0079 | g0020 | ESP | Spain | 1925 | 1938 | False | pre1950 |
| real_v2-0080 | g0009 | PER | Peru | 1625 | None | False | pre1950 |
| real_v2-0081 | g0033 | ZWE | Zimbabwe | 1990 | 2003 | False | post1950 |
| real_v2-0082 | g0034 | YEM | Yemen | 2015 | 2016 | True | post1950 |
| real_v2-0083 | g0035 | PHL | Philippines | 1940 | 1946 | True | pre1950 |
| real_v2-0084 | g0005 | CHE | Switzerland | 1895 | None | False | pre1950 |
| real_v2-0085 | g0031 | DEU | Germany | 1975 | None | False | post1950 |
| real_v2-0086 | g0006 | POL | Poland | 1855 | None | False | pre1950 |
| real_v2-0087 | g0036 | LSO | Lesotho | 1980 | None | False | post1950 |
| real_v2-0088 | g0014 | LKA | Sri Lanka | 1950 | None | False | pre1950 |
| real_v2-0089 | g0020 | ESP | Spain | 1910 | None | False | pre1950 |
| real_v2-0090 | g0005 | CHE | Switzerland | 1905 | None | False | pre1950 |
| real_v2-0091 | g0037 | TUR | Turkey | 1995 | None | False | post1950 |
| real_v2-0092 | g0001 | BEL | Belgium | 1970 | None | False | post1950 |
| real_v2-0093 | g0014 | LKA | Sri Lanka | 2000 | None | False | post1950 |
| real_v2-0094 | g0019 | CHN | China | 1990 | None | False | post1950 |
| real_v2-0095 | g0001 | BEL | Belgium | 1980 | None | False | post1950 |
| real_v2-0096 | g0038 | GRC | Greece | 1895 | 1901 | False | pre1950 |
| real_v2-0097 | g0016 | DNK | Denmark | 1885 | None | False | pre1950 |
| real_v2-0098 | g0039 | BRA | Brazil | 1960 | None | False | post1950 |
| real_v2-0099 | g0004 | FRA | France | 1520 | None | False | pre1950 |
| real_v2-0100 | g0004 | FRA | France | 1335 | None | False | pre1950 |
| real_v2-0101 | g0040 | TWN | Taiwan, Province of China | 1940 | 1950 | False | pre1950 |
| real_v2-0102 | g0006 | POL | Poland | 1775 | None | False | pre1950 |
| real_v2-0103 | g0039 | BRA | Brazil | 1880 | 1893 | False | pre1950 |
| real_v2-0104 | g0004 | FRA | France | 1730 | None | False | pre1950 |
| real_v2-0105 | g0026 | CHL | Chile | 1985 | None | False | post1950 |
| real_v2-0106 | g0009 | PER | Peru | 1955 | None | False | post1950 |
| real_v2-0107 | g0007 | CAN | Canada | 1905 | None | False | pre1950 |
| real_v2-0108 | g0031 | DEU | Germany | 1980 | None | False | post1950 |
| real_v2-0109 | g0026 | CHL | Chile | 1905 | None | False | pre1950 |
| real_v2-0110 | g0021 | AUT | Austria | 1915 | 1916 | False | pre1950 |
| real_v2-0111 | g0007 | CAN | Canada | 1995 | None | False | post1950 |
| real_v2-0112 | g0014 | LKA | Sri Lanka | 1920 | None | False | pre1950 |
| real_v2-0113 | g0028 | DZA | Algeria | 1995 | None | False | post1950 |
| real_v2-0114 | g0021 | AUT | Austria | 1910 | 1919 | False | pre1950 |
| real_v2-0115 | g0003 | NOR | Norway | 2000 | None | False | post1950 |
| real_v2-0116 | g0005 | CHE | Switzerland | 1965 | None | False | post1950 |
| real_v2-0117 | g0041 | NAM | Namibia | 1995 | None | False | post1950 |
| real_v2-0118 | g0042 | JAM | Jamaica | 1995 | None | False | post1950 |
| real_v2-0119 | g0014 | LKA | Sri Lanka | 1925 | None | False | pre1950 |
| real_v2-0120 | g0000 | GTM | Guatemala | 1960 | None | False | post1950 |
| real_v2-0121 | g0038 | GRC | Greece | 1875 | None | False | pre1950 |
| real_v2-0122 | g0003 | NOR | Norway | 1910 | None | False | pre1950 |
| real_v2-0123 | g0043 | HND | Honduras | 1970 | None | False | post1950 |
| real_v2-0124 | g0044 | CYP | Cyprus | 1985 | None | False | post1950 |
| real_v2-0125 | g0045 | NIC | Nicaragua | 1950 | None | False | pre1950 |
| real_v2-0126 | g0004 | FRA | France | 1850 | None | False | pre1950 |
| real_v2-0127 | g0020 | ESP | Spain | 1935 | 1936 | False | pre1950 |
| real_v2-0128 | g0004 | FRA | France | 1680 | None | False | pre1950 |
| real_v2-0129 | g0005 | CHE | Switzerland | 1900 | None | False | pre1950 |
| real_v2-0130 | g0046 | LAO | Lao People's DR | 2000 | None | False | post1950 |
| real_v2-0131 | g0006 | POL | Poland | 1550 | None | False | pre1950 |
| real_v2-0132 | g0006 | POL | Poland | 1615 | 1616 | False | pre1950 |
| real_v2-0133 | g0017 | ECU | Ecuador | 1980 | None | False | post1950 |
| real_v2-0134 | g0047 | JPN | Japan | 1975 | None | False | post1950 |
| real_v2-0135 | g0016 | DNK | Denmark | 1895 | None | False | pre1950 |
| real_v2-0136 | g0048 | SEN | Senegal | 2000 | None | False | post1950 |
| real_v2-0137 | g0004 | FRA | France | 1725 | None | False | pre1950 |
| real_v2-0138 | g0030 | IDN | Indonesia | 1865 | None | False | pre1950 |
| real_v2-0139 | g0021 | AUT | Austria | 1970 | None | False | post1950 |
| real_v2-0140 | g0008 | NZL | New Zealand | 1920 | None | False | pre1950 |
| real_v2-0141 | g0003 | NOR | Norway | 1900 | None | False | pre1950 |
| real_v2-0142 | g0049 | GNB | Guinea-Bissau | 1990 | None | False | post1950 |
| real_v2-0143 | g0031 | DEU | Germany | 1915 | 1919 | False | pre1950 |
| real_v2-0144 | g0016 | DNK | Denmark | 1990 | None | False | post1950 |
| real_v2-0145 | g0050 | EGY | Egypt | 1995 | None | False | post1950 |
| real_v2-0146 | g0002 | FIN | Finland | 1910 | 1918 | False | pre1950 |
| real_v2-0147 | g0001 | BEL | Belgium | 1990 | None | False | post1950 |
| real_v2-0148 | g0018 | CSK | Czechoslovakia | 1985 | None | False | post1950 |
| real_v2-0149 | g0019 | CHN | China | 1985 | None | False | post1950 |
| real_v2-0150 | g0006 | POL | Poland | 1740 | None | False | pre1950 |
| real_v2-0151 | g0004 | FRA | France | 1985 | None | False | post1950 |
| real_v2-0152 | g0051 | SWZ | Swaziland | 1995 | None | False | post1950 |
| real_v2-0153 | g0015 | COL | Colombia | 1990 | None | False | post1950 |
| real_v2-0154 | g0005 | CHE | Switzerland | 1890 | None | False | pre1950 |
| real_v2-0155 | g0023 | MLI | Mali | 2000 | None | False | post1950 |
| real_v2-0156 | g0038 | GRC | Greece | 1955 | None | False | post1950 |
| real_v2-0157 | g0006 | POL | Poland | 1455 | None | False | pre1950 |
| real_v2-0158 | g0041 | NAM | Namibia | 1985 | 1990 | False | post1950 |
| real_v2-0159 | g0020 | ESP | Spain | 1950 | None | False | pre1950 |
| real_v2-0160 | g0004 | FRA | France | 1580 | None | False | pre1950 |
| real_v2-0161 | g0004 | FRA | France | 1640 | None | False | pre1950 |
| real_v2-0162 | g0052 | MYS | Malaysia | 1995 | None | False | post1950 |
| real_v2-0163 | g0002 | FIN | Finland | 1935 | None | False | pre1950 |
| real_v2-0164 | g0017 | ECU | Ecuador | 1940 | None | False | pre1950 |
| real_v2-0165 | g0038 | GRC | Greece | 1930 | 1942 | True | pre1950 |
| real_v2-0166 | g0045 | NIC | Nicaragua | 1975 | 1979 | True | post1950 |
| real_v2-0167 | g0039 | BRA | Brazil | 1915 | None | False | pre1950 |
| real_v2-0168 | g0001 | BEL | Belgium | 1900 | None | False | pre1950 |
| real_v2-0169 | g0005 | CHE | Switzerland | 1935 | None | False | pre1950 |
| real_v2-0170 | g0044 | CYP | Cyprus | 2000 | None | False | post1950 |
| real_v2-0171 | g0049 | GNB | Guinea-Bissau | 1980 | None | False | post1950 |
| real_v2-0172 | g0042 | JAM | Jamaica | 1985 | 1986 | False | post1950 |
| real_v2-0173 | g0003 | NOR | Norway | 1975 | None | False | post1950 |
| real_v2-0174 | g0032 | ISR | Israel | 1985 | None | False | post1950 |
| real_v2-0175 | g0006 | POL | Poland | 1650 | None | False | pre1950 |
| real_v2-0176 | g0035 | PHL | Philippines | 1985 | None | False | post1950 |
| real_v2-0177 | g0004 | FRA | France | 1635 | None | False | pre1950 |
| real_v2-0178 | g0043 | HND | Honduras | 2000 | None | False | post1950 |
| real_v2-0179 | g0001 | BEL | Belgium | 1955 | None | False | post1950 |
| real_v2-0180 | g0005 | CHE | Switzerland | 1995 | None | False | post1950 |
| real_v2-0181 | g0004 | FRA | France | 1695 | None | False | pre1950 |
| real_v2-0182 | g0004 | FRA | France | 1375 | None | False | pre1950 |
| real_v2-0183 | g0037 | TUR | Turkey | 1970 | None | False | post1950 |
| real_v2-0184 | g0009 | PER | Peru | 1745 | None | False | pre1950 |
| real_v2-0185 | g0003 | NOR | Norway | 1985 | None | False | post1950 |
| real_v2-0186 | g0053 | BHR | Bahrain | 1995 | None | False | post1950 |
| real_v2-0187 | g0006 | POL | Poland | 1605 | 1615 | False | pre1950 |
| real_v2-0188 | g0031 | DEU | Germany | 1885 | None | False | pre1950 |
| real_v2-0189 | g0021 | AUT | Austria | 1965 | None | False | post1950 |
| real_v2-0190 | g0004 | FRA | France | 1895 | None | False | pre1950 |
| real_v2-0191 | g0009 | PER | Peru | 1695 | None | False | pre1950 |
| real_v2-0192 | g0054 | BGD | Bangladesh | 1985 | None | False | post1950 |
| real_v2-0193 | g0009 | PER | Peru | 1750 | None | False | pre1950 |
| real_v2-0194 | g0039 | BRA | Brazil | 1990 | None | False | post1950 |
| real_v2-0195 | g0020 | ESP | Spain | 1995 | None | False | post1950 |
| real_v2-0196 | g0054 | BGD | Bangladesh | 1995 | None | False | post1950 |
| real_v2-0197 | g0020 | ESP | Spain | 1920 | None | False | pre1950 |
| real_v2-0198 | g0007 | CAN | Canada | 1920 | 1921 | False | pre1950 |
| real_v2-0199 | g0009 | PER | Peru | 1785 | None | False | pre1950 |
| real_v2-0200 | g0046 | LAO | Lao People's DR | 1980 | None | False | post1950 |
| real_v2-0201 | g0038 | GRC | Greece | 1865 | None | False | pre1950 |
| real_v2-0202 | g0025 | PSE | State of Palestine | 1985 | None | False | post1950 |
| real_v2-0203 | g0016 | DNK | Denmark | 1955 | None | False | post1950 |
| real_v2-0204 | g0052 | MYS | Malaysia | 1990 | None | False | post1950 |
| real_v2-0205 | g0055 | BFA | Burkina Faso | 2000 | None | False | post1950 |
| real_v2-0206 | g0020 | ESP | Spain | 1895 | None | False | pre1950 |
| real_v2-0207 | g0003 | NOR | Norway | 1965 | None | False | post1950 |
| real_v2-0208 | g0046 | LAO | Lao People's DR | 1985 | None | False | post1950 |
| real_v2-0209 | g0048 | SEN | Senegal | 1990 | None | False | post1950 |
| real_v2-0210 | g0056 | GIN | Guinea | 1985 | None | False | post1950 |
| real_v2-0211 | g0008 | NZL | New Zealand | 1900 | None | False | pre1950 |
| real_v2-0212 | g0043 | HND | Honduras | 1965 | None | False | post1950 |
| real_v2-0213 | g0030 | IDN | Indonesia | 1915 | None | False | pre1950 |
| real_v2-0214 | g0020 | ESP | Spain | 1980 | None | False | post1950 |
| real_v2-0215 | g0008 | NZL | New Zealand | 1995 | None | False | post1950 |
| real_v2-0216 | g0041 | NAM | Namibia | 2000 | None | False | post1950 |
| real_v2-0217 | g0020 | ESP | Spain | 1990 | None | False | post1950 |
| real_v2-0218 | g0004 | FRA | France | 1420 | None | False | pre1950 |
| real_v2-0219 | g0006 | POL | Poland | 1560 | None | False | pre1950 |
| real_v2-0220 | g0047 | JPN | Japan | 2000 | None | False | post1950 |
| real_v2-0221 | g0026 | CHL | Chile | 1945 | None | False | pre1950 |
| real_v2-0222 | g0009 | PER | Peru | 1700 | None | False | pre1950 |
| real_v2-0223 | g0044 | CYP | Cyprus | 1990 | None | False | post1950 |
| real_v2-0224 | g0016 | DNK | Denmark | 1860 | None | False | pre1950 |
| real_v2-0225 | g0049 | GNB | Guinea-Bissau | 1985 | None | False | post1950 |
| real_v2-0226 | g0002 | FIN | Finland | 1890 | None | False | pre1950 |
| real_v2-0227 | g0008 | NZL | New Zealand | 2000 | None | False | post1950 |
| real_v2-0228 | g0004 | FRA | France | 1600 | None | False | pre1950 |
| real_v2-0229 | g0004 | FRA | France | 1625 | None | False | pre1950 |
| real_v2-0230 | g0057 | HRV | Croatia | 2000 | None | False | post1950 |
| real_v2-0231 | g0001 | BEL | Belgium | 1925 | None | False | pre1950 |
| real_v2-0232 | g0058 | DOM | Dominican Republic | 1985 | None | False | post1950 |
| real_v2-0233 | g0006 | POL | Poland | 1465 | None | False | pre1950 |
| real_v2-0234 | g0006 | POL | Poland | 1545 | None | False | pre1950 |
| real_v2-0235 | g0022 | VEN | Venezuela (Bolivarian Republic of) | 1995 | 2002 | False | post1950 |
| real_v2-0236 | g0006 | POL | Poland | 1480 | None | False | pre1950 |
| real_v2-0237 | g0005 | CHE | Switzerland | 1910 | None | False | pre1950 |
| real_v2-0238 | g0006 | POL | Poland | 1520 | None | False | pre1950 |
| real_v2-0239 | g0006 | POL | Poland | 1495 | None | False | pre1950 |
| real_v2-0240 | g0009 | PER | Peru | 1865 | 1880 | True | pre1950 |
| real_v2-0241 | g0001 | BEL | Belgium | 1965 | None | False | post1950 |
| real_v2-0242 | g0015 | COL | Colombia | 1910 | None | False | pre1950 |
| real_v2-0243 | g0034 | YEM | Yemen | 1990 | None | False | post1950 |
| real_v2-0244 | g0053 | BHR | Bahrain | 1990 | None | False | post1950 |
| real_v2-0245 | g0006 | POL | Poland | 1585 | None | False | pre1950 |
| real_v2-0246 | g0039 | BRA | Brazil | 1940 | None | False | pre1950 |
| real_v2-0247 | g0055 | BFA | Burkina Faso | 1990 | None | False | post1950 |
| real_v2-0248 | g0016 | DNK | Denmark | 1930 | None | False | pre1950 |
| real_v2-0249 | g0030 | IDN | Indonesia | 1940 | 1949 | False | pre1950 |
| real_v2-0250 | g0059 | RUS | Russian Federation | 1990 | 1994 | False | post1950 |
| real_v2-0251 | g0030 | IDN | Indonesia | 1890 | None | False | pre1950 |
| real_v2-0252 | g0021 | AUT | Austria | 1930 | 1945 | True | pre1950 |
| real_v2-0253 | g0014 | LKA | Sri Lanka | 1970 | None | False | post1950 |
| real_v2-0254 | g0022 | VEN | Venezuela (Bolivarian Republic of) | 1975 | None | False | post1950 |
| real_v2-0255 | g0057 | HRV | Croatia | 1985 | 1991 | False | post1950 |
| real_v2-0256 | g0043 | HND | Honduras | 1995 | None | False | post1950 |
| real_v2-0257 | g0004 | FRA | France | 1545 | None | False | pre1950 |
| real_v2-0258 | g0021 | AUT | Austria | 1980 | None | False | post1950 |
| real_v2-0259 | g0004 | FRA | France | 1705 | None | False | pre1950 |
| real_v2-0260 | g0035 | PHL | Philippines | 2000 | None | False | post1950 |
| real_v2-0261 | g0004 | FRA | France | 1330 | None | False | pre1950 |
| real_v2-0262 | g0060 | LBY | Libya | 2010 | 2011 | True | post1950 |
| real_v2-0263 | g0061 | CPV | Cabo Verde | 1985 | None | False | post1950 |
| real_v2-0264 | g0009 | PER | Peru | 1915 | None | False | pre1950 |
| real_v2-0265 | g0006 | POL | Poland | 1785 | None | False | pre1950 |
| real_v2-0266 | g0004 | FRA | France | 1660 | None | False | pre1950 |
| real_v2-0267 | g0010 | BOL | Bolivia (Plurinational State of) | 1925 | None | False | pre1950 |
| real_v2-0268 | g0004 | FRA | France | 1605 | None | False | pre1950 |
| real_v2-0269 | g0007 | CAN | Canada | 1990 | None | False | post1950 |
| real_v2-0270 | g0033 | ZWE | Zimbabwe | 1995 | 2003 | True | post1950 |
| real_v2-0271 | g0001 | BEL | Belgium | 2000 | None | False | post1950 |
| real_v2-0272 | g0023 | MLI | Mali | 1980 | None | False | post1950 |
| real_v2-0273 | g0035 | PHL | Philippines | 1990 | None | False | post1950 |
| real_v2-0274 | g0026 | CHL | Chile | 1860 | None | False | pre1950 |
| real_v2-0275 | g0038 | GRC | Greece | 1965 | None | False | post1950 |
| real_v2-0276 | g0009 | PER | Peru | 1770 | None | False | pre1950 |
| real_v2-0277 | g0005 | CHE | Switzerland | 1990 | None | False | post1950 |
| real_v2-0278 | g0054 | BGD | Bangladesh | 2000 | None | False | post1950 |
| real_v2-0279 | g0030 | IDN | Indonesia | 1900 | None | False | pre1950 |
| real_v2-0280 | g0002 | FIN | Finland | 1955 | None | False | post1950 |
| real_v2-0281 | g0004 | FRA | France | 1540 | None | False | pre1950 |
| real_v2-0282 | g0020 | ESP | Spain | 1970 | None | False | post1950 |
| real_v2-0283 | g0038 | GRC | Greece | 1990 | None | False | post1950 |
| real_v2-0284 | g0042 | JAM | Jamaica | 1990 | None | False | post1950 |
| real_v2-0285 | g0038 | GRC | Greece | 1940 | 1941 | True | pre1950 |
| real_v2-0286 | g0007 | CAN | Canada | 1955 | None | False | post1950 |
| real_v2-0287 | g0002 | FIN | Finland | 1960 | None | False | post1950 |
| real_v2-0288 | g0014 | LKA | Sri Lanka | 1935 | None | False | pre1950 |
| real_v2-0289 | g0004 | FRA | France | 1875 | None | False | pre1950 |
| real_v2-0290 | g0020 | ESP | Spain | 1890 | None | False | pre1950 |
| real_v2-0291 | g0004 | FRA | France | 1505 | None | False | pre1950 |
| real_v2-0292 | g0004 | FRA | France | 1960 | None | False | post1950 |
| real_v2-0293 | g0022 | VEN | Venezuela (Bolivarian Republic of) | 1880 | None | False | pre1950 |
| real_v2-0294 | g0006 | POL | Poland | 1745 | None | False | pre1950 |
| real_v2-0295 | g0015 | COL | Colombia | 1935 | None | False | pre1950 |
| real_v2-0296 | g0047 | JPN | Japan | 1925 | None | False | pre1950 |
| real_v2-0297 | g0030 | IDN | Indonesia | 2000 | None | False | post1950 |
| real_v2-0298 | g0061 | CPV | Cabo Verde | 1980 | None | False | post1950 |
| real_v2-0299 | g0017 | ECU | Ecuador | 1950 | None | False | pre1950 |
| real_v2-0300 | g0006 | POL | Poland | 1660 | None | False | pre1950 |
| real_v2-0301 | g0009 | PER | Peru | 1910 | None | False | pre1950 |
| real_v2-0302 | g0038 | GRC | Greece | 1885 | None | False | pre1950 |
| real_v2-0303 | g0002 | FIN | Finland | 1915 | 1917 | False | pre1950 |
| real_v2-0304 | g0054 | BGD | Bangladesh | 1980 | None | False | post1950 |
| real_v2-0305 | g0009 | PER | Peru | 1810 | 1811 | True | pre1950 |
| real_v2-0306 | g0004 | FRA | France | 1880 | None | False | pre1950 |
| real_v2-0307 | g0006 | POL | Poland | 1885 | None | False | pre1950 |
| real_v2-0308 | g0004 | FRA | France | 1310 | None | False | pre1950 |
| real_v2-0309 | g0006 | POL | Poland | 1555 | None | False | pre1950 |
| real_v2-0310 | g0003 | NOR | Norway | 1955 | None | False | post1950 |
| real_v2-0311 | g0002 | FIN | Finland | 1940 | None | False | pre1950 |
| real_v2-0312 | g0004 | FRA | France | 1670 | None | False | pre1950 |
| real_v2-0313 | g0005 | CHE | Switzerland | 1985 | None | False | post1950 |
| real_v2-0314 | g0051 | SWZ | Swaziland | 2000 | None | False | post1950 |
| real_v2-0315 | g0043 | HND | Honduras | 1980 | None | False | post1950 |
| real_v2-0316 | g0009 | PER | Peru | 1800 | 1801 | False | pre1950 |
| real_v2-0317 | g0033 | ZWE | Zimbabwe | 2000 | 2003 | True | post1950 |
| real_v2-0318 | g0006 | POL | Poland | 1580 | None | False | pre1950 |
| real_v2-0319 | g0015 | COL | Colombia | 2000 | None | False | post1950 |
| real_v2-0320 | g0009 | PER | Peru | 1650 | 1660 | False | pre1950 |
| real_v2-0321 | g0036 | LSO | Lesotho | 1995 | None | False | post1950 |
| real_v2-0322 | g0004 | FRA | France | 1755 | None | False | pre1950 |
| real_v2-0323 | g0006 | POL | Poland | 1440 | None | False | pre1950 |
| real_v2-0324 | g0004 | FRA | France | 1360 | None | False | pre1950 |
| real_v2-0325 | g0001 | BEL | Belgium | 1920 | None | False | pre1950 |
| real_v2-0326 | g0034 | YEM | Yemen | 2005 | 2015 | True | post1950 |
| real_v2-0327 | g0004 | FRA | France | 1550 | None | False | pre1950 |
| real_v2-0328 | g0037 | TUR | Turkey | 1990 | None | False | post1950 |
| real_v2-0329 | g0004 | FRA | France | 1645 | None | False | pre1950 |
| real_v2-0330 | g0026 | CHL | Chile | 1895 | None | False | pre1950 |
| real_v2-0331 | g0062 | COG | Congo | 2000 | None | False | post1950 |
| real_v2-0332 | g0004 | FRA | France | 1475 | None | False | pre1950 |
| real_v2-0333 | g0006 | POL | Poland | 1500 | None | False | pre1950 |
| real_v2-0334 | g0001 | BEL | Belgium | 1910 | 1918 | False | pre1950 |
| real_v2-0335 | g0004 | FRA | France | 1710 | None | False | pre1950 |
| real_v2-0336 | g0022 | VEN | Venezuela (Bolivarian Republic of) | 1940 | None | False | pre1950 |
| real_v2-0337 | g0052 | MYS | Malaysia | 1935 | 1940 | True | pre1950 |
| real_v2-0338 | g0063 | BEN | Benin | 2000 | None | False | post1950 |
| real_v2-0339 | g0006 | POL | Poland | 1570 | None | False | pre1950 |
| real_v2-0340 | g0008 | NZL | New Zealand | 1935 | None | False | pre1950 |
| real_v2-0341 | g0015 | COL | Colombia | 1900 | None | False | pre1950 |
| real_v2-0342 | g0037 | TUR | Turkey | 1980 | None | False | post1950 |
| real_v2-0343 | g0021 | AUT | Austria | 1950 | None | False | pre1950 |
| real_v2-0344 | g0004 | FRA | France | 1385 | None | False | pre1950 |
| real_v2-0345 | g0006 | POL | Poland | 1850 | None | False | pre1950 |
| real_v2-0346 | g0031 | DEU | Germany | 1940 | 1946 | True | pre1950 |
| real_v2-0347 | g0003 | NOR | Norway | 1875 | None | False | pre1950 |
| real_v2-0348 | g0015 | COL | Colombia | 1940 | None | False | pre1950 |
| real_v2-0349 | g0063 | BEN | Benin | 1995 | None | False | post1950 |
| real_v2-0350 | g0055 | BFA | Burkina Faso | 1980 | None | False | post1950 |
| real_v2-0351 | g0004 | FRA | France | 1690 | None | False | pre1950 |
| real_v2-0352 | g0047 | JPN | Japan | 1985 | None | False | post1950 |
| real_v2-0353 | g0031 | DEU | Germany | 1995 | None | False | post1950 |
| real_v2-0354 | g0064 | BGR | Bulgaria | 1990 | None | False | post1950 |
| real_v2-0355 | g0000 | GTM | Guatemala | 1980 | None | False | post1950 |
| real_v2-0356 | g0038 | GRC | Greece | 1995 | None | False | post1950 |
| real_v2-0357 | g0010 | BOL | Bolivia (Plurinational State of) | 1920 | None | False | pre1950 |
| real_v2-0358 | g0040 | TWN | Taiwan, Province of China | 1935 | 1950 | False | pre1950 |
| real_v2-0359 | g0030 | IDN | Indonesia | 1870 | None | False | pre1950 |
| real_v2-0360 | g0065 | KHM | Cambodia | 2000 | None | False | post1950 |
| real_v2-0361 | g0022 | VEN | Venezuela (Bolivarian Republic of) | 2015 | 2016 | True | post1950 |
| real_v2-0362 | g0047 | JPN | Japan | 1915 | None | False | pre1950 |
| real_v2-0363 | g0003 | NOR | Norway | 1945 | None | False | pre1950 |
| real_v2-0364 | g0004 | FRA | France | 1465 | None | False | pre1950 |
| real_v2-0365 | g0031 | DEU | Germany | 1935 | 1946 | True | pre1950 |
| real_v2-0366 | g0006 | POL | Poland | 1715 | None | False | pre1950 |
| real_v2-0367 | g0004 | FRA | France | 2000 | None | False | post1950 |
| real_v2-0368 | g0034 | YEM | Yemen | 1980 | None | False | post1950 |
| real_v2-0369 | g0009 | PER | Peru | 1780 | None | False | pre1950 |
| real_v2-0370 | g0005 | CHE | Switzerland | 1950 | None | False | pre1950 |
| real_v2-0371 | g0009 | PER | Peru | 1840 | None | False | pre1950 |
| real_v2-0372 | g0022 | VEN | Venezuela (Bolivarian Republic of) | 1930 | None | False | pre1950 |
| real_v2-0373 | g0048 | SEN | Senegal | 1985 | None | False | post1950 |
| real_v2-0374 | g0010 | BOL | Bolivia (Plurinational State of) | 1935 | None | False | pre1950 |
| real_v2-0375 | g0006 | POL | Poland | 1800 | 1811 | False | pre1950 |
| real_v2-0376 | g0066 | DMA | Dominica | 1990 | None | False | post1950 |
| real_v2-0377 | g0001 | BEL | Belgium | 1995 | None | False | post1950 |
| real_v2-0378 | g0004 | FRA | France | 1675 | None | False | pre1950 |
| real_v2-0379 | g0039 | BRA | Brazil | 1920 | None | False | pre1950 |
| real_v2-0380 | g0016 | DNK | Denmark | 1910 | None | False | pre1950 |
| real_v2-0381 | g0040 | TWN | Taiwan, Province of China | 2000 | None | False | post1950 |
| real_v2-0382 | g0015 | COL | Colombia | 1925 | None | False | pre1950 |
| real_v2-0383 | g0006 | POL | Poland | 1655 | None | False | pre1950 |
| real_v2-0384 | g0056 | GIN | Guinea | 1990 | None | False | post1950 |
| real_v2-0385 | g0028 | DZA | Algeria | 1980 | None | False | post1950 |
| real_v2-0386 | g0022 | VEN | Venezuela (Bolivarian Republic of) | 1985 | 1989 | False | post1950 |
| real_v2-0387 | g0004 | FRA | France | 1315 | None | False | pre1950 |
| real_v2-0388 | g0016 | DNK | Denmark | 1865 | None | False | pre1950 |
| real_v2-0389 | g0023 | MLI | Mali | 1985 | None | False | post1950 |
| real_v2-0390 | g0056 | GIN | Guinea | 1980 | None | False | post1950 |
| real_v2-0391 | g0006 | POL | Poland | 1845 | None | False | pre1950 |
| real_v2-0392 | g0035 | PHL | Philippines | 1935 | 1946 | True | pre1950 |
| real_v2-0393 | g0020 | ESP | Spain | 1905 | None | False | pre1950 |
| real_v2-0394 | g0006 | POL | Poland | 1720 | None | False | pre1950 |
| real_v2-0395 | g0019 | CHN | China | 1995 | None | False | post1950 |
| real_v2-0396 | g0009 | PER | Peru | 1945 | None | False | pre1950 |
| real_v2-0397 | g0006 | POL | Poland | 1535 | None | False | pre1950 |
| real_v2-0398 | g0067 | HTI | Haiti | 1975 | None | False | post1950 |
| real_v2-0399 | g0016 | DNK | Denmark | 1875 | None | False | pre1950 |
| real_v2-0400 | g0030 | IDN | Indonesia | 1855 | None | False | pre1950 |
| real_v2-0401 | g0007 | CAN | Canada | 1985 | None | False | post1950 |
| real_v2-0402 | g0014 | LKA | Sri Lanka | 1975 | None | False | post1950 |
| real_v2-0403 | g0034 | YEM | Yemen | 2010 | 2015 | True | post1950 |
| real_v2-0404 | g0014 | LKA | Sri Lanka | 1965 | None | False | post1950 |
| real_v2-0405 | g0004 | FRA | France | 1620 | None | False | pre1950 |
| real_v2-0406 | g0027 | ETH | Ethiopia | 1980 | 1992 | False | post1950 |
| real_v2-0407 | g0017 | ECU | Ecuador | 1985 | None | False | post1950 |
| real_v2-0408 | g0009 | PER | Peru | 1755 | None | False | pre1950 |
| real_v2-0409 | g0004 | FRA | France | 1560 | None | False | pre1950 |
| real_v2-0410 | g0060 | LBY | Libya | 2000 | None | False | post1950 |
| real_v2-0411 | g0042 | JAM | Jamaica | 1980 | 1985 | False | post1950 |
| real_v2-0412 | g0006 | POL | Poland | 1510 | None | False | pre1950 |
| real_v2-0413 | g0021 | AUT | Austria | 1955 | None | False | post1950 |
| real_v2-0414 | g0005 | CHE | Switzerland | 1980 | None | False | post1950 |
| real_v2-0415 | g0022 | VEN | Venezuela (Bolivarian Republic of) | 1860 | 1867 | False | pre1950 |
| real_v2-0416 | g0026 | CHL | Chile | 1855 | None | False | pre1950 |
| real_v2-0417 | g0002 | FIN | Finland | 1920 | None | False | pre1950 |
| real_v2-0418 | g0004 | FRA | France | 1665 | None | False | pre1950 |
| real_v2-0419 | g0009 | PER | Peru | 1860 | None | False | pre1950 |
| real_v2-0420 | g0004 | FRA | France | 1595 | None | False | pre1950 |
| real_v2-0421 | g0037 | TUR | Turkey | 2000 | None | False | post1950 |
| real_v2-0422 | g0006 | POL | Poland | 1865 | None | False | pre1950 |
| real_v2-0423 | g0038 | GRC | Greece | 1910 | 1913 | True | pre1950 |
| real_v2-0424 | g0004 | FRA | France | 1610 | None | False | pre1950 |
| real_v2-0425 | g0007 | CAN | Canada | 1930 | 1932 | False | pre1950 |
| real_v2-0426 | g0005 | CHE | Switzerland | 1930 | None | False | pre1950 |
| real_v2-0427 | g0008 | NZL | New Zealand | 1970 | None | False | post1950 |
| real_v2-0428 | g0038 | GRC | Greece | 1935 | 1942 | True | pre1950 |
| real_v2-0429 | g0001 | BEL | Belgium | 1930 | None | False | pre1950 |
| real_v2-0430 | g0026 | CHL | Chile | 1965 | None | False | post1950 |
| real_v2-0431 | g0067 | HTI | Haiti | 1990 | 1992 | False | post1950 |
| real_v2-0432 | g0031 | DEU | Germany | 1900 | None | False | pre1950 |
| real_v2-0433 | g0010 | BOL | Bolivia (Plurinational State of) | 1930 | None | False | pre1950 |
| real_v2-0434 | g0004 | FRA | France | 1750 | None | False | pre1950 |
| real_v2-0435 | g0026 | CHL | Chile | 1980 | None | False | post1950 |
| real_v2-0436 | g0003 | NOR | Norway | 1920 | None | False | pre1950 |
| real_v2-0437 | g0014 | LKA | Sri Lanka | 1995 | None | False | post1950 |
| real_v2-0438 | g0014 | LKA | Sri Lanka | 1990 | None | False | post1950 |
| real_v2-0439 | g0031 | DEU | Germany | 1910 | None | False | pre1950 |
| real_v2-0440 | g0030 | IDN | Indonesia | 1925 | None | False | pre1950 |
| real_v2-0441 | g0009 | PER | Peru | 1940 | None | False | pre1950 |
| real_v2-0442 | g0004 | FRA | France | 1735 | None | False | pre1950 |
| real_v2-0443 | g0016 | DNK | Denmark | 1950 | None | False | pre1950 |
| real_v2-0444 | g0008 | NZL | New Zealand | 1940 | None | False | pre1950 |
| real_v2-0445 | g0006 | POL | Poland | 1530 | None | False | pre1950 |
| real_v2-0446 | g0006 | POL | Poland | 1460 | None | False | pre1950 |
| real_v2-0447 | g0029 | MUS | Mauritius | 1995 | None | False | post1950 |
| real_v2-0448 | g0009 | PER | Peru | 1680 | 1687 | False | pre1950 |
| real_v2-0449 | g0002 | FIN | Finland | 1945 | None | False | pre1950 |
| real_v2-0450 | g0010 | BOL | Bolivia (Plurinational State of) | 1980 | None | False | post1950 |
| real_v2-0451 | g0000 | GTM | Guatemala | 1965 | None | False | post1950 |
| real_v2-0452 | g0004 | FRA | France | 1440 | None | False | pre1950 |
| real_v2-0453 | g0035 | PHL | Philippines | 1995 | None | False | post1950 |
| real_v2-0454 | g0050 | EGY | Egypt | 2000 | None | False | post1950 |
| real_v2-0455 | g0006 | POL | Poland | 1690 | None | False | pre1950 |
| real_v2-0456 | g0004 | FRA | France | 1990 | None | False | post1950 |
| real_v2-0457 | g0030 | IDN | Indonesia | 1880 | None | False | pre1950 |
| real_v2-0458 | g0004 | FRA | France | 1955 | None | False | post1950 |
| real_v2-0459 | g0021 | AUT | Austria | 1945 | 1946 | True | pre1950 |
| real_v2-0460 | g0031 | DEU | Germany | 1955 | None | False | post1950 |
| real_v2-0461 | g0017 | ECU | Ecuador | 1990 | None | False | post1950 |
| real_v2-0462 | g0004 | FRA | France | 1615 | None | False | pre1950 |
| real_v2-0463 | g0039 | BRA | Brazil | 1935 | None | False | pre1950 |
| real_v2-0464 | g0016 | DNK | Denmark | 1985 | None | False | post1950 |
| real_v2-0465 | g0009 | PER | Peru | 1775 | None | False | pre1950 |
| real_v2-0466 | g0009 | PER | Peru | 1730 | None | False | pre1950 |
| real_v2-0467 | g0063 | BEN | Benin | 1985 | None | False | post1950 |
| real_v2-0468 | g0064 | BGR | Bulgaria | 1995 | None | False | post1950 |
| real_v2-0469 | g0039 | BRA | Brazil | 2000 | None | False | post1950 |
| real_v2-0470 | g0065 | KHM | Cambodia | 1980 | None | False | post1950 |
| real_v2-0471 | g0016 | DNK | Denmark | 1970 | None | False | post1950 |
| real_v2-0472 | g0036 | LSO | Lesotho | 2000 | None | False | post1950 |
| real_v2-0473 | g0060 | LBY | Libya | 2005 | 2014 | True | post1950 |
| real_v2-0474 | g0043 | HND | Honduras | 1955 | None | False | post1950 |
| real_v2-0475 | g0058 | DOM | Dominican Republic | 1980 | None | False | post1950 |
| real_v2-0476 | g0009 | PER | Peru | 1995 | None | False | post1950 |
| real_v2-0477 | g0030 | IDN | Indonesia | 1935 | 1949 | False | pre1950 |
| real_v2-0478 | g0009 | PER | Peru | 1950 | None | False | pre1950 |
| real_v2-0479 | g0030 | IDN | Indonesia | 1845 | None | False | pre1950 |
| real_v2-0480 | g0004 | FRA | France | 1860 | None | False | pre1950 |
| real_v2-0481 | g0047 | JPN | Japan | 1990 | None | False | post1950 |
| real_v2-0482 | g0008 | NZL | New Zealand | 1915 | None | False | pre1950 |
| real_v2-0483 | g0039 | BRA | Brazil | 1985 | None | False | post1950 |
| real_v2-0484 | g0005 | CHE | Switzerland | 1960 | None | False | post1950 |
| real_v2-0485 | g0002 | FIN | Finland | 1995 | None | False | post1950 |
| real_v2-0486 | g0004 | FRA | France | 1455 | None | False | pre1950 |
| real_v2-0487 | g0008 | NZL | New Zealand | 1905 | None | False | pre1950 |
| real_v2-0488 | g0042 | JAM | Jamaica | 2000 | None | False | post1950 |
| real_v2-0489 | g0043 | HND | Honduras | 1975 | None | False | post1950 |
| real_v2-0490 | g0004 | FRA | France | 1765 | None | False | pre1950 |
| real_v2-0491 | g0015 | COL | Colombia | 1950 | None | False | pre1950 |
| real_v2-0492 | g0002 | FIN | Finland | 1965 | None | False | post1950 |
| real_v2-0493 | g0022 | VEN | Venezuela (Bolivarian Republic of) | 1870 | None | False | pre1950 |
| real_v2-0494 | g0006 | POL | Poland | 1770 | None | False | pre1950 |
| real_v2-0495 | g0034 | YEM | Yemen | 1985 | None | False | post1950 |
| real_v2-0496 | g0017 | ECU | Ecuador | 1970 | None | False | post1950 |
| real_v2-0497 | g0063 | BEN | Benin | 1980 | None | False | post1950 |
| real_v2-0498 | g0001 | BEL | Belgium | 1905 | 1918 | False | pre1950 |
| real_v2-0499 | g0040 | TWN | Taiwan, Province of China | 1995 | None | False | post1950 |
| real_v2-0500 | g0014 | LKA | Sri Lanka | 1985 | None | False | post1950 |
| real_v2-0501 | g0008 | NZL | New Zealand | 1980 | None | False | post1950 |
| real_v2-0502 | g0004 | FRA | France | 1490 | None | False | pre1950 |
| real_v2-0503 | g0021 | AUT | Austria | 1960 | None | False | post1950 |
| real_v2-0504 | g0000 | GTM | Guatemala | 2000 | None | False | post1950 |
| real_v2-0505 | g0030 | IDN | Indonesia | 1985 | None | False | post1950 |
| real_v2-0506 | g0020 | ESP | Spain | 1975 | None | False | post1950 |
| real_v2-0507 | g0009 | PER | Peru | 1735 | None | False | pre1950 |
| real_v2-0508 | g0018 | CSK | Czechoslovakia | 1990 | None | False | post1950 |
| real_v2-0509 | g0030 | IDN | Indonesia | 1860 | None | False | pre1950 |
| real_v2-0510 | g0017 | ECU | Ecuador | 1995 | None | False | post1950 |
| real_v2-0511 | g0039 | BRA | Brazil | 1885 | 1893 | False | pre1950 |
| real_v2-0512 | g0015 | COL | Colombia | 1930 | None | False | pre1950 |
| real_v2-0513 | g0032 | ISR | Israel | 1995 | None | False | post1950 |
| real_v2-0514 | g0047 | JPN | Japan | 1935 | 1946 | False | pre1950 |
| real_v2-0515 | g0004 | FRA | France | 1740 | None | False | pre1950 |
| real_v2-0516 | g0061 | CPV | Cabo Verde | 1995 | None | False | post1950 |
| real_v2-0517 | g0026 | CHL | Chile | 1930 | 1931 | True | pre1950 |
| real_v2-0518 | g0008 | NZL | New Zealand | 1975 | None | False | post1950 |
| real_v2-0519 | g0006 | POL | Poland | 1880 | None | False | pre1950 |
| real_v2-0520 | g0013 | SYR | Syrian Arab Republic | 1995 | 1999 | True | post1950 |
| real_v2-0521 | g0009 | PER | Peru | 1760 | None | False | pre1950 |
| real_v2-0522 | g0022 | VEN | Venezuela (Bolivarian Republic of) | 1960 | None | False | post1950 |
| real_v2-0523 | g0052 | MYS | Malaysia | 2000 | None | False | post1950 |
| real_v2-0524 | g0021 | AUT | Austria | 1975 | None | False | post1950 |
| real_v2-0525 | g0007 | CAN | Canada | 1965 | None | False | post1950 |
| real_v2-0526 | g0051 | SWZ | Swaziland | 1985 | None | False | post1950 |
| real_v2-0527 | g0064 | BGR | Bulgaria | 1980 | None | False | post1950 |
| real_v2-0528 | g0025 | PSE | State of Palestine | 1990 | 2002 | False | post1950 |
| real_v2-0529 | g0006 | POL | Poland | 2000 | None | False | post1950 |
| real_v2-0530 | g0062 | COG | Congo | 1995 | None | False | post1950 |
| real_v2-0531 | g0009 | PER | Peru | 1665 | None | False | pre1950 |
| real_v2-0532 | g0062 | COG | Congo | 1985 | None | False | post1950 |
| real_v2-0533 | g0027 | ETH | Ethiopia | 1990 | 1992 | False | post1950 |
| real_v2-0534 | g0003 | NOR | Norway | 1930 | None | False | pre1950 |
| real_v2-0535 | g0005 | CHE | Switzerland | 1925 | None | False | pre1950 |
| real_v2-0536 | g0000 | GTM | Guatemala | 1990 | None | False | post1950 |
| real_v2-0537 | g0010 | BOL | Bolivia (Plurinational State of) | 1960 | None | False | post1950 |
| real_v2-0538 | g0056 | GIN | Guinea | 2000 | None | False | post1950 |
| real_v2-0539 | g0016 | DNK | Denmark | 1975 | None | False | post1950 |
| real_v2-0540 | g0008 | NZL | New Zealand | 1930 | None | False | pre1950 |
| real_v2-0541 | g0022 | VEN | Venezuela (Bolivarian Republic of) | 1935 | None | False | pre1950 |
| real_v2-0542 | g0004 | FRA | France | 1870 | None | False | pre1950 |
| real_v2-0543 | g0031 | DEU | Germany | 1905 | None | False | pre1950 |
| real_v2-0544 | g0004 | FRA | France | 1855 | None | False | pre1950 |
| real_v2-0545 | g0007 | CAN | Canada | 1910 | None | False | pre1950 |
| real_v2-0546 | g0001 | BEL | Belgium | 1945 | None | False | pre1950 |
| real_v2-0547 | g0068 | BIH | Bosnia and Herzegovina | 1985 | 1991 | True | post1950 |
| real_v2-0548 | g0009 | PER | Peru | 1920 | None | False | pre1950 |
| real_v2-0549 | g0026 | CHL | Chile | 1975 | None | False | post1950 |
| real_v2-0550 | g0030 | IDN | Indonesia | 1875 | None | False | pre1950 |
| real_v2-0551 | g0022 | VEN | Venezuela (Bolivarian Republic of) | 2000 | 2002 | False | post1950 |
| real_v2-0552 | g0057 | HRV | Croatia | 1990 | 1991 | False | post1950 |
| real_v2-0553 | g0004 | FRA | France | 1935 | 1941 | True | pre1950 |
| real_v2-0554 | g0054 | BGD | Bangladesh | 1990 | None | False | post1950 |
| real_v2-0555 | g0031 | DEU | Germany | 1930 | None | False | pre1950 |
| real_v2-0556 | g0006 | POL | Poland | 1635 | None | False | pre1950 |
| real_v2-0557 | g0010 | BOL | Bolivia (Plurinational State of) | 1955 | None | False | post1950 |
| real_v2-0558 | g0066 | DMA | Dominica | 1980 | None | False | post1950 |
| real_v2-0559 | g0031 | DEU | Germany | 1945 | 1946 | True | pre1950 |
| real_v2-0560 | g0024 | BRB | Barbados | 1980 | None | False | post1950 |
| real_v2-0561 | g0004 | FRA | France | 1590 | None | False | pre1950 |
| real_v2-0562 | g0002 | FIN | Finland | 1985 | None | False | post1950 |
| real_v2-0563 | g0006 | POL | Poland | 1695 | None | False | pre1950 |
| real_v2-0564 | g0026 | CHL | Chile | 2000 | None | False | post1950 |
| real_v2-0565 | g0006 | POL | Poland | 1670 | None | False | pre1950 |
| real_v2-0566 | g0030 | IDN | Indonesia | 1995 | None | False | post1950 |
| real_v2-0567 | g0056 | GIN | Guinea | 1995 | None | False | post1950 |
| real_v2-0568 | g0002 | FIN | Finland | 1990 | None | False | post1950 |
| real_v2-0569 | g0026 | CHL | Chile | 1960 | None | False | post1950 |
| real_v2-0570 | g0004 | FRA | France | 1425 | None | False | pre1950 |
| real_v2-0571 | g0006 | POL | Poland | 1450 | None | False | pre1950 |
| real_v2-0572 | g0018 | CSK | Czechoslovakia | 2000 | None | False | post1950 |
| real_v2-0573 | g0006 | POL | Poland | 1780 | None | False | pre1950 |
| real_v2-0574 | g0039 | BRA | Brazil | 1900 | None | False | pre1950 |
| real_v2-0575 | g0009 | PER | Peru | 1875 | 1879 | True | pre1950 |
| real_v2-0576 | g0053 | BHR | Bahrain | 1985 | None | False | post1950 |
| real_v2-0577 | g0050 | EGY | Egypt | 1980 | None | False | post1950 |
| real_v2-0578 | g0029 | MUS | Mauritius | 1980 | None | False | post1950 |
| real_v2-0579 | g0009 | PER | Peru | 1685 | 1687 | False | pre1950 |
| real_v2-0580 | g0006 | POL | Poland | 1710 | None | False | pre1950 |
| real_v2-0581 | g0009 | PER | Peru | 2000 | None | False | post1950 |
| real_v2-0582 | g0006 | POL | Poland | 1685 | None | False | pre1950 |
| real_v2-0583 | g0015 | COL | Colombia | 1920 | None | False | pre1950 |
| real_v2-0584 | g0022 | VEN | Venezuela (Bolivarian Republic of) | 1865 | 1867 | False | pre1950 |
| real_v2-0585 | g0045 | NIC | Nicaragua | 1955 | None | False | post1950 |
| real_v2-0586 | g0022 | VEN | Venezuela (Bolivarian Republic of) | 1950 | None | False | pre1950 |
| real_v2-0587 | g0038 | GRC | Greece | 1905 | 1913 | True | pre1950 |
| real_v2-0588 | g0009 | PER | Peru | 1980 | 1989 | False | post1950 |
| real_v2-0589 | g0005 | CHE | Switzerland | 1970 | None | False | post1950 |
| real_v2-0590 | g0039 | BRA | Brazil | 1970 | None | False | post1950 |
| real_v2-0591 | g0007 | CAN | Canada | 1960 | None | False | post1950 |
| real_v2-0592 | g0001 | BEL | Belgium | 1960 | None | False | post1950 |
| real_v2-0593 | g0048 | SEN | Senegal | 1995 | None | False | post1950 |
| real_v2-0594 | g0006 | POL | Poland | 1990 | None | False | post1950 |
| real_v2-0595 | g0013 | SYR | Syrian Arab Republic | 1990 | 1999 | False | post1950 |
| real_v2-0596 | g0008 | NZL | New Zealand | 1950 | None | False | pre1950 |
| real_v2-0597 | g0006 | POL | Poland | 1590 | None | False | pre1950 |
| real_v2-0598 | g0004 | FRA | France | 1970 | None | False | post1950 |
| real_v2-0599 | g0004 | FRA | France | 1685 | None | False | pre1950 |
| real_v2-0600 | g0031 | DEU | Germany | 1895 | None | False | pre1950 |
| real_v2-0601 | g0040 | TWN | Taiwan, Province of China | 1980 | None | False | post1950 |
| real_v2-0602 | g0039 | BRA | Brazil | 1980 | None | False | post1950 |
| real_v2-0603 | g0033 | ZWE | Zimbabwe | 1985 | None | False | post1950 |
| real_v2-0604 | g0009 | PER | Peru | 1660 | None | False | pre1950 |
| real_v2-0605 | g0004 | FRA | France | 1535 | None | False | pre1950 |
| real_v2-0606 | g0039 | BRA | Brazil | 1910 | None | False | pre1950 |
| real_v2-0607 | g0050 | EGY | Egypt | 1985 | None | False | post1950 |
| real_v2-0608 | g0046 | LAO | Lao People's DR | 1990 | None | False | post1950 |
| real_v2-0609 | g0032 | ISR | Israel | 1980 | None | False | post1950 |
| real_v2-0610 | g0009 | PER | Peru | 1965 | None | False | post1950 |
| real_v2-0611 | g0016 | DNK | Denmark | 2000 | None | False | post1950 |
| real_v2-0612 | g0008 | NZL | New Zealand | 1965 | None | False | post1950 |
| real_v2-0613 | g0009 | PER | Peru | 1975 | 1990 | False | post1950 |
| real_v2-0614 | g0004 | FRA | France | 1570 | None | False | pre1950 |
| real_v2-0615 | g0055 | BFA | Burkina Faso | 1985 | None | False | post1950 |
| real_v2-0616 | g0069 | MNG | Mongolia | 1985 | None | False | post1950 |
| real_v2-0617 | g0062 | COG | Congo | 1990 | None | False | post1950 |
| real_v2-0618 | g0008 | NZL | New Zealand | 1985 | None | False | post1950 |
| real_v2-0619 | g0004 | FRA | France | 1370 | None | False | pre1950 |
| real_v2-0620 | g0065 | KHM | Cambodia | 1995 | None | False | post1950 |
| real_v2-0621 | g0031 | DEU | Germany | 2000 | None | False | post1950 |
| real_v2-0622 | g0002 | FIN | Finland | 1905 | None | False | pre1950 |
| real_v2-0623 | g0034 | YEM | Yemen | 2000 | 2015 | False | post1950 |
| real_v2-0624 | g0044 | CYP | Cyprus | 1980 | None | False | post1950 |
| real_v2-0625 | g0007 | CAN | Canada | 1900 | None | False | pre1950 |
| real_v2-0626 | g0004 | FRA | France | 1585 | None | False | pre1950 |
| real_v2-0627 | g0004 | FRA | France | 1430 | None | False | pre1950 |
| real_v2-0628 | g0052 | MYS | Malaysia | 1930 | 1940 | False | pre1950 |
| real_v2-0629 | g0002 | FIN | Finland | 1950 | None | False | pre1950 |
| real_v2-0630 | g0022 | VEN | Venezuela (Bolivarian Republic of) | 2010 | 2017 | True | post1950 |
| real_v2-0631 | g0016 | DNK | Denmark | 1900 | None | False | pre1950 |
| real_v2-0632 | g0006 | POL | Poland | 1595 | None | False | pre1950 |
| real_v2-0633 | g0069 | MNG | Mongolia | 1990 | None | False | post1950 |
| real_v2-0634 | g0022 | VEN | Venezuela (Bolivarian Republic of) | 1965 | None | False | post1950 |
| real_v2-0635 | g0037 | TUR | Turkey | 1960 | None | False | post1950 |
| real_v2-0636 | g0026 | CHL | Chile | 1925 | 1932 | False | pre1950 |
| real_v2-0637 | g0006 | POL | Poland | 1485 | None | False | pre1950 |
| real_v2-0638 | g0031 | DEU | Germany | 1985 | None | False | post1950 |
| real_v2-0639 | g0004 | FRA | France | 1500 | None | False | pre1950 |
| real_v2-0640 | g0016 | DNK | Denmark | 1935 | None | False | pre1950 |
| real_v2-0641 | g0015 | COL | Colombia | 1915 | None | False | pre1950 |
| real_v2-0642 | g0009 | PER | Peru | 1675 | 1687 | False | pre1950 |
| real_v2-0643 | g0047 | JPN | Japan | 1960 | None | False | post1950 |
| real_v2-0644 | g0020 | ESP | Spain | 1945 | None | False | pre1950 |
| real_v2-0645 | g0004 | FRA | France | 1410 | None | False | pre1950 |
| real_v2-0646 | g0016 | DNK | Denmark | 1925 | None | False | pre1950 |
| real_v2-0647 | g0001 | BEL | Belgium | 1940 | None | False | pre1950 |
| real_v2-0648 | g0015 | COL | Colombia | 1985 | None | False | post1950 |
| real_v2-0649 | g0030 | IDN | Indonesia | 1990 | None | False | post1950 |
| real_v2-0650 | g0009 | PER | Peru | 1655 | 1660 | False | pre1950 |
| real_v2-0651 | g0031 | DEU | Germany | 1925 | None | False | pre1950 |
| real_v2-0652 | g0010 | BOL | Bolivia (Plurinational State of) | 1970 | None | False | post1950 |
| real_v2-0653 | g0043 | HND | Honduras | 1990 | None | False | post1950 |
| real_v2-0654 | g0004 | FRA | France | 1460 | None | False | pre1950 |
| real_v2-0655 | g0006 | POL | Poland | 1665 | None | False | pre1950 |
| real_v2-0656 | g0015 | COL | Colombia | 1980 | None | False | post1950 |
| real_v2-0657 | g0022 | VEN | Venezuela (Bolivarian Republic of) | 1970 | None | False | post1950 |
| real_v2-0658 | g0051 | SWZ | Swaziland | 1980 | None | False | post1950 |
| real_v2-0659 | g0000 | GTM | Guatemala | 1995 | None | False | post1950 |
| real_v2-0660 | g0003 | NOR | Norway | 1995 | None | False | post1950 |
| real_v2-0661 | g0016 | DNK | Denmark | 1945 | None | False | pre1950 |
| real_v2-0662 | g0044 | CYP | Cyprus | 1995 | None | False | post1950 |
| real_v2-0663 | g0043 | HND | Honduras | 1950 | None | False | pre1950 |
| real_v2-0664 | g0036 | LSO | Lesotho | 1985 | None | False | post1950 |
| real_v2-0665 | g0046 | LAO | Lao People's DR | 1995 | None | False | post1950 |
| real_v2-0666 | g0004 | FRA | France | 1770 | None | False | pre1950 |
| real_v2-0667 | g0067 | HTI | Haiti | 1985 | 1992 | False | post1950 |
| real_v2-0668 | g0053 | BHR | Bahrain | 2000 | None | False | post1950 |
| real_v2-0669 | g0031 | DEU | Germany | 1960 | None | False | post1950 |
| real_v2-0670 | g0004 | FRA | France | 1515 | None | False | pre1950 |
| real_v2-0671 | g0028 | DZA | Algeria | 2000 | None | False | post1950 |
| real_v2-0672 | g0037 | TUR | Turkey | 1985 | None | False | post1950 |
| real_v2-0673 | g0009 | PER | Peru | 1985 | 1989 | False | post1950 |
| real_v2-0674 | g0004 | FRA | France | 1950 | None | False | pre1950 |
| real_v2-0675 | g0006 | POL | Poland | 1470 | None | False | pre1950 |
| real_v2-0676 | g0010 | BOL | Bolivia (Plurinational State of) | 1945 | None | False | pre1950 |
| real_v2-0677 | g0017 | ECU | Ecuador | 1945 | None | False | pre1950 |
| real_v2-0678 | g0001 | BEL | Belgium | 1950 | None | False | pre1950 |
| real_v2-0679 | g0016 | DNK | Denmark | 1870 | None | False | pre1950 |
| real_v2-0680 | g0004 | FRA | France | 1745 | None | False | pre1950 |
| real_v2-0681 | g0006 | POL | Poland | 1640 | None | False | pre1950 |
| real_v2-0682 | g0004 | FRA | France | 1630 | None | False | pre1950 |
| real_v2-0683 | g0026 | CHL | Chile | 1845 | None | False | pre1950 |
| real_v2-0684 | g0070 | CIV | Côte d'Ivoire | 1985 | 1989 | True | post1950 |
| real_v2-0685 | g0010 | BOL | Bolivia (Plurinational State of) | 1950 | None | False | pre1950 |
| real_v2-0686 | g0014 | LKA | Sri Lanka | 1910 | None | False | pre1950 |
| real_v2-0687 | g0047 | JPN | Japan | 1955 | None | False | post1950 |
| real_v2-0688 | g0001 | BEL | Belgium | 1915 | 1918 | False | pre1950 |
| real_v2-0689 | g0039 | BRA | Brazil | 1950 | None | False | pre1950 |
| real_v2-0690 | g0009 | PER | Peru | 1710 | None | False | pre1950 |
| real_v2-0691 | g0004 | FRA | France | 1900 | None | False | pre1950 |
| real_v2-0692 | g0022 | VEN | Venezuela (Bolivarian Republic of) | 1890 | 1899 | False | pre1950 |
| real_v2-0693 | g0003 | NOR | Norway | 1915 | None | False | pre1950 |
| real_v2-0694 | g0006 | POL | Poland | 1565 | None | False | pre1950 |
| real_v2-0695 | g0066 | DMA | Dominica | 1995 | None | False | post1950 |
| real_v2-0696 | g0035 | PHL | Philippines | 1980 | None | False | post1950 |
| real_v2-0697 | g0065 | KHM | Cambodia | 1985 | None | False | post1950 |
| real_v2-0698 | g0016 | DNK | Denmark | 1905 | None | False | pre1950 |
| real_v2-0699 | g0015 | COL | Colombia | 1975 | None | False | post1950 |
| real_v2-0700 | g0021 | AUT | Austria | 1905 | None | False | pre1950 |
| real_v2-0701 | g0015 | COL | Colombia | 1960 | None | False | post1950 |
| real_v2-0702 | g0006 | POL | Poland | 1750 | None | False | pre1950 |
| real_v2-0703 | g0021 | AUT | Austria | 1985 | None | False | post1950 |
| real_v2-0704 | g0001 | BEL | Belgium | 1885 | None | False | pre1950 |
| real_v2-0705 | g0047 | JPN | Japan | 1965 | None | False | post1950 |
| real_v2-0706 | g0002 | FIN | Finland | 1980 | None | False | post1950 |
| real_v2-0707 | g0006 | POL | Poland | 1610 | 1615 | False | pre1950 |
| real_v2-0708 | g0043 | HND | Honduras | 1960 | None | False | post1950 |
| real_v2-0709 | g0004 | FRA | France | 1345 | None | False | pre1950 |
| real_v2-0710 | g0015 | COL | Colombia | 1955 | None | False | post1950 |
| real_v2-0711 | g0014 | LKA | Sri Lanka | 1960 | None | False | post1950 |
| real_v2-0712 | g0016 | DNK | Denmark | 1960 | None | False | post1950 |
| real_v2-0713 | g0006 | POL | Poland | 1860 | None | False | pre1950 |
| real_v2-0714 | g0007 | CAN | Canada | 1970 | None | False | post1950 |
| real_v2-0715 | g0045 | NIC | Nicaragua | 1970 | 1979 | False | post1950 |
| real_v2-0716 | g0026 | CHL | Chile | 1995 | None | False | post1950 |
| real_v2-0717 | g0070 | CIV | Côte d'Ivoire | 1980 | 1989 | False | post1950 |
| real_v2-0718 | g0038 | GRC | Greece | 1960 | None | False | post1950 |
| real_v2-0719 | g0022 | VEN | Venezuela (Bolivarian Republic of) | 1945 | None | False | pre1950 |
| real_v2-0720 | g0004 | FRA | France | 1485 | None | False | pre1950 |
| real_v2-0721 | g0022 | VEN | Venezuela (Bolivarian Republic of) | 1925 | None | False | pre1950 |
| real_v2-0722 | g0010 | BOL | Bolivia (Plurinational State of) | 1995 | None | False | post1950 |
| real_v2-0723 | g0003 | NOR | Norway | 1865 | None | False | pre1950 |
| real_v2-0724 | g0051 | SWZ | Swaziland | 1990 | None | False | post1950 |
| real_v2-0725 | g0005 | CHE | Switzerland | 1955 | None | False | post1950 |
| real_v2-0726 | g0006 | POL | Poland | 1985 | None | False | post1950 |
| real_v2-0727 | g0022 | VEN | Venezuela (Bolivarian Republic of) | 1885 | None | False | pre1950 |
| real_v2-0728 | g0017 | ECU | Ecuador | 1960 | None | False | post1950 |
| real_v2-0729 | g0004 | FRA | France | 1760 | None | False | pre1950 |
| real_v2-0730 | g0010 | BOL | Bolivia (Plurinational State of) | 2000 | None | False | post1950 |
| real_v2-0731 | g0017 | ECU | Ecuador | 1930 | None | False | pre1950 |
| real_v2-0732 | g0066 | DMA | Dominica | 2000 | None | False | post1950 |
| real_v2-0733 | g0003 | NOR | Norway | 1935 | None | False | pre1950 |
| real_v2-0734 | g0004 | FRA | France | 1915 | 1918 | False | pre1950 |
| real_v2-0735 | g0038 | GRC | Greece | 1890 | 1901 | False | pre1950 |
| real_v2-0736 | g0016 | DNK | Denmark | 1980 | None | False | post1950 |
| real_v2-0737 | g0014 | LKA | Sri Lanka | 1905 | None | False | pre1950 |
| real_v2-0738 | g0041 | NAM | Namibia | 1980 | 1990 | False | post1950 |
| real_v2-0739 | g0004 | FRA | France | 1400 | None | False | pre1950 |
| real_v2-0740 | g0049 | GNB | Guinea-Bissau | 1995 | None | False | post1950 |
| real_v2-0741 | g0021 | AUT | Austria | 1990 | None | False | post1950 |
| real_v2-0742 | g0022 | VEN | Venezuela (Bolivarian Republic of) | 2005 | 2017 | False | post1950 |
| real_v2-0743 | g0026 | CHL | Chile | 1920 | 1932 | False | pre1950 |
| real_v2-0744 | g0003 | NOR | Norway | 1895 | None | False | pre1950 |
| real_v2-0745 | g0049 | GNB | Guinea-Bissau | 2000 | None | False | post1950 |
| real_v2-0746 | g0006 | POL | Poland | 1490 | None | False | pre1950 |
| real_v2-0747 | g0004 | FRA | France | 1390 | None | False | pre1950 |
| real_v2-0748 | g0038 | GRC | Greece | 1900 | 1901 | False | pre1950 |
| real_v2-0749 | g0030 | IDN | Indonesia | 1895 | None | False | pre1950 |
| real_v2-0750 | g0038 | GRC | Greece | 1980 | None | False | post1950 |
| real_v2-0751 | g0048 | SEN | Senegal | 1980 | None | False | post1950 |
| real_v2-0752 | g0026 | CHL | Chile | 1970 | None | False | post1950 |
| real_v2-0753 | g0047 | JPN | Japan | 1995 | None | False | post1950 |
| real_v2-0754 | g0006 | POL | Poland | 1705 | None | False | pre1950 |
| real_v2-0755 | g0004 | FRA | France | 1975 | None | False | post1950 |
| real_v2-0756 | g0026 | CHL | Chile | 1865 | None | False | pre1950 |
| real_v2-0757 | g0058 | DOM | Dominican Republic | 1995 | None | False | post1950 |
| real_v2-0758 | g0058 | DOM | Dominican Republic | 2000 | None | False | post1950 |
| real_v2-0759 | g0026 | CHL | Chile | 1950 | None | False | pre1950 |
| real_v2-0760 | g0011 | GNQ | Equatorial Guinea | 2000 | None | False | post1950 |
| real_v2-0761 | g0006 | POL | Poland | 1870 | None | False | pre1950 |
| real_v2-0762 | g0004 | FRA | France | 1980 | None | False | post1950 |
| real_v2-0763 | g0004 | FRA | France | 1655 | None | False | pre1950 |
| real_v2-0764 | g0009 | PER | Peru | 1870 | 1880 | True | pre1950 |
| real_v2-0765 | g0026 | CHL | Chile | 1875 | None | False | pre1950 |
| real_v2-0766 | g0071 | IRQ | Iraq | 1980 | 1981 | True | post1950 |
| real_v2-0767 | g0047 | JPN | Japan | 1945 | 1946 | True | pre1950 |
| real_v2-0768 | g0009 | PER | Peru | 1705 | None | False | pre1950 |
| real_v2-0769 | g0069 | MNG | Mongolia | 2000 | None | False | post1950 |
| real_v2-0770 | g0004 | FRA | France | 1885 | None | False | pre1950 |
| real_v2-0771 | g0006 | POL | Poland | 1995 | None | False | post1950 |
| real_v2-0772 | g0011 | GNQ | Equatorial Guinea | 1995 | None | False | post1950 |
| real_v2-0773 | g0023 | MLI | Mali | 1990 | None | False | post1950 |
| real_v2-0774 | g0024 | BRB | Barbados | 2000 | None | False | post1950 |
| real_v2-0775 | g0026 | CHL | Chile | 1885 | None | False | pre1950 |
| real_v2-0776 | g0006 | POL | Poland | 1875 | None | False | pre1950 |
| real_v2-0777 | g0009 | PER | Peru | 1725 | None | False | pre1950 |
| real_v2-0778 | g0014 | LKA | Sri Lanka | 1900 | None | False | pre1950 |
| real_v2-0779 | g0045 | NIC | Nicaragua | 1960 | None | False | post1950 |
| real_v2-0780 | g0038 | GRC | Greece | 1925 | None | False | pre1950 |
| real_v2-0781 | g0031 | DEU | Germany | 1970 | None | False | post1950 |
| real_v2-0782 | g0052 | MYS | Malaysia | 1980 | None | False | post1950 |
| real_v2-0783 | g0020 | ESP | Spain | 1885 | None | False | pre1950 |
| real_v2-0784 | g0011 | GNQ | Equatorial Guinea | 2015 | 2016 | True | post1950 |
| real_v2-0785 | g0000 | GTM | Guatemala | 1975 | None | False | post1950 |
| real_v2-0786 | g0038 | GRC | Greece | 2000 | None | False | post1950 |
| real_v2-0787 | g0004 | FRA | France | 1650 | None | False | pre1950 |
| real_v2-0788 | g0015 | COL | Colombia | 1965 | None | False | post1950 |
| real_v2-0789 | g0024 | BRB | Barbados | 1995 | None | False | post1950 |
| real_v2-0790 | g0007 | CAN | Canada | 1975 | None | False | post1950 |
| real_v2-0791 | g0026 | CHL | Chile | 1915 | None | False | pre1950 |
| real_v2-0792 | g0036 | LSO | Lesotho | 1990 | None | False | post1950 |
| real_v2-0793 | g0029 | MUS | Mauritius | 1990 | None | False | post1950 |
| real_v2-0794 | g0004 | FRA | France | 1930 | 1941 | True | pre1950 |
| real_v2-0795 | g0009 | PER | Peru | 1640 | None | False | pre1950 |
| real_v2-0796 | g0047 | JPN | Japan | 1940 | 1946 | True | pre1950 |
| real_v2-0797 | g0015 | COL | Colombia | 1905 | None | False | pre1950 |
| real_v2-0798 | g0006 | POL | Poland | 1755 | None | False | pre1950 |
| real_v2-0799 | g0039 | BRA | Brazil | 1995 | None | False | post1950 |
| real_v2-0800 | g0003 | NOR | Norway | 1925 | None | False | pre1950 |
| real_v2-0801 | g0007 | CAN | Canada | 1940 | None | False | pre1950 |
| real_v2-0802 | g0039 | BRA | Brazil | 1905 | None | False | pre1950 |
| real_v2-0803 | g0047 | JPN | Japan | 1980 | None | False | post1950 |
| real_v2-0804 | g0060 | LBY | Libya | 1980 | 1981 | True | post1950 |
| real_v2-0805 | g0002 | FIN | Finland | 1930 | None | False | pre1950 |
| real_v2-0806 | g0004 | FRA | France | 1920 | None | False | pre1950 |
| real_v2-0807 | g0050 | EGY | Egypt | 1990 | None | False | post1950 |
| real_v2-0808 | g0039 | BRA | Brazil | 1945 | None | False | pre1950 |
| real_v2-0809 | g0037 | TUR | Turkey | 1975 | None | False | post1950 |
| real_v2-0810 | g0007 | CAN | Canada | 1980 | None | False | post1950 |
| real_v2-0811 | g0026 | CHL | Chile | 1880 | None | False | pre1950 |
| real_v2-0812 | g0008 | NZL | New Zealand | 1990 | None | False | post1950 |
| real_v2-0813 | g0006 | POL | Poland | 1730 | None | False | pre1950 |
| real_v2-0814 | g0026 | CHL | Chile | 1890 | None | False | pre1950 |
| real_v2-0815 | g0004 | FRA | France | 1925 | None | False | pre1950 |
| real_v2-0816 | g0004 | FRA | France | 1380 | None | False | pre1950 |
| real_v2-0817 | g0039 | BRA | Brazil | 1965 | None | False | post1950 |
| real_v2-0818 | g0038 | GRC | Greece | 1985 | None | False | post1950 |
| real_v2-0819 | g0009 | PER | Peru | 1960 | None | False | post1950 |
| real_v2-0820 | g0004 | FRA | France | 1995 | None | False | post1950 |
| real_v2-0821 | g0004 | FRA | France | 1495 | None | False | pre1950 |
| real_v2-0822 | g0072 | MNE | Montenegro | 1985 | 1992 | True | post1950 |
| real_v2-0823 | g0004 | FRA | France | 1325 | None | False | pre1950 |
| real_v2-0824 | g0030 | IDN | Indonesia | 1885 | None | False | pre1950 |
| real_v2-0825 | g0004 | FRA | France | 1720 | None | False | pre1950 |
| real_v2-0826 | g0026 | CHL | Chile | 1870 | None | False | pre1950 |
| real_v2-0827 | g0006 | POL | Poland | 1980 | None | False | post1950 |
| real_v2-0828 | g0073 | STP | Sao Tome and Principe | 1980 | 1984 | False | post1950 |
| real_v2-0829 | g0062 | COG | Congo | 1980 | None | False | post1950 |
| real_v2-0830 | g0072 | MNE | Montenegro | 1990 | 1992 | True | post1950 |
| real_v2-0831 | g0026 | CHL | Chile | 1955 | None | False | post1950 |
| real_v2-0832 | g0052 | MYS | Malaysia | 1940 | 1941 | True | pre1950 |
| real_v2-0833 | g0003 | NOR | Norway | 1870 | None | False | pre1950 |
| real_v2-0834 | g0006 | POL | Poland | 1445 | None | False | pre1950 |
| real_v2-0835 | g0066 | DMA | Dominica | 1985 | None | False | post1950 |
| real_v2-0836 | g0020 | ESP | Spain | 1985 | None | False | post1950 |
| real_v2-0837 | g0031 | DEU | Germany | 1890 | None | False | pre1950 |
| real_v2-0838 | g0004 | FRA | France | 1405 | None | False | pre1950 |
| real_v2-0839 | g0039 | BRA | Brazil | 1930 | None | False | pre1950 |
| real_v2-0840 | g0003 | NOR | Norway | 1905 | None | False | pre1950 |
| real_v2-0841 | g0004 | FRA | France | 1395 | None | False | pre1950 |
| real_v2-0842 | g0003 | NOR | Norway | 1860 | None | False | pre1950 |
| real_v2-0843 | g0004 | FRA | France | 1555 | None | False | pre1950 |
| real_v2-0844 | g0031 | DEU | Germany | 1880 | None | False | pre1950 |
| real_v2-0845 | g0058 | DOM | Dominican Republic | 1990 | None | False | post1950 |
| real_v2-0846 | g0061 | CPV | Cabo Verde | 2000 | None | False | post1950 |
| real_v2-0847 | g0004 | FRA | France | 1320 | None | False | pre1950 |
| real_v2-0848 | g0039 | BRA | Brazil | 1955 | None | False | post1950 |
| real_v2-0849 | g0001 | BEL | Belgium | 1880 | None | False | pre1950 |
| real_v2-0850 | g0026 | CHL | Chile | 1910 | None | False | pre1950 |
| real_v2-0851 | g0047 | JPN | Japan | 1930 | None | False | pre1950 |
| real_v2-0852 | g0047 | JPN | Japan | 1920 | None | False | pre1950 |
| real_v2-0853 | g0016 | DNK | Denmark | 1920 | None | False | pre1950 |
| real_v2-0854 | g0005 | CHE | Switzerland | 1945 | None | False | pre1950 |
| real_v2-0855 | g0018 | CSK | Czechoslovakia | 1995 | None | False | post1950 |
| real_v2-0856 | g0006 | POL | Poland | 1515 | None | False | pre1950 |
| real_v2-0857 | g0016 | DNK | Denmark | 1915 | None | False | pre1950 |
| real_v2-0858 | g0008 | NZL | New Zealand | 1955 | None | False | post1950 |
| real_v2-0859 | g0010 | BOL | Bolivia (Plurinational State of) | 1975 | None | False | post1950 |
| real_v2-0860 | g0039 | BRA | Brazil | 1890 | 1893 | False | pre1950 |
| real_v2-0861 | g0002 | FIN | Finland | 1895 | None | False | pre1950 |
| real_v2-0862 | g0055 | BFA | Burkina Faso | 1995 | None | False | post1950 |
| real_v2-0863 | g0063 | BEN | Benin | 1990 | None | False | post1950 |
| real_v2-0864 | g0053 | BHR | Bahrain | 1980 | None | False | post1950 |
| real_v2-0865 | g0016 | DNK | Denmark | 1890 | None | False | pre1950 |
| real_v2-0866 | g0010 | BOL | Bolivia (Plurinational State of) | 1965 | None | False | post1950 |
| real_v2-0867 | g0003 | NOR | Norway | 1940 | None | False | pre1950 |
| real_v2-0868 | g0028 | DZA | Algeria | 1985 | None | False | post1950 |
| real_v2-0869 | g0002 | FIN | Finland | 1975 | None | False | post1950 |
| real_v2-0870 | g0020 | ESP | Spain | 1930 | 1936 | False | pre1950 |
| real_v2-0871 | g0030 | IDN | Indonesia | 1980 | None | False | post1950 |
| real_v2-0872 | g0021 | AUT | Austria | 1995 | None | False | post1950 |
| real_v2-0873 | g0008 | NZL | New Zealand | 1960 | None | False | post1950 |
| real_v2-0874 | g0015 | COL | Colombia | 1945 | None | False | pre1950 |
| real_v2-0875 | g0004 | FRA | France | 1910 | None | False | pre1950 |
| real_v2-0876 | g0007 | CAN | Canada | 2000 | None | False | post1950 |
| real_v2-0877 | g0014 | LKA | Sri Lanka | 1940 | None | False | pre1950 |
| real_v2-0878 | g0006 | POL | Poland | 1675 | None | False | pre1950 |
| real_v2-0879 | g0068 | BIH | Bosnia and Herzegovina | 1990 | 1991 | True | post1950 |
| real_v2-0880 | g0009 | PER | Peru | 1925 | None | False | pre1950 |
| real_v2-0881 | g0004 | FRA | France | 1715 | None | False | pre1950 |
| real_v2-0882 | g0026 | CHL | Chile | 1850 | None | False | pre1950 |
| real_v2-0883 | g0022 | VEN | Venezuela (Bolivarian Republic of) | 1980 | 1989 | False | post1950 |
| real_v2-0884 | g0026 | CHL | Chile | 1935 | None | False | pre1950 |
| real_v2-0885 | g0009 | PER | Peru | 1630 | None | False | pre1950 |
| real_v2-0886 | g0014 | LKA | Sri Lanka | 1930 | None | False | pre1950 |
| real_v2-0887 | g0004 | FRA | France | 1575 | None | False | pre1950 |
| real_v2-0888 | g0002 | FIN | Finland | 1970 | None | False | post1950 |
| real_v2-0889 | g0006 | POL | Poland | 1630 | None | False | pre1950 |
| real_v2-0890 | g0067 | HTI | Haiti | 1980 | 1993 | False | post1950 |
| real_v2-0891 | g0009 | PER | Peru | 1850 | None | False | pre1950 |
| real_v2-0892 | g0025 | PSE | State of Palestine | 1980 | None | False | post1950 |
| real_v2-0893 | g0013 | SYR | Syrian Arab Republic | 1985 | 1999 | False | post1950 |
| real_v2-0894 | g0061 | CPV | Cabo Verde | 1990 | None | False | post1950 |
| real_v2-0895 | g0004 | FRA | France | 1565 | None | False | pre1950 |
| real_v2-0896 | g0008 | NZL | New Zealand | 1925 | None | False | pre1950 |
| real_v2-0897 | g0040 | TWN | Taiwan, Province of China | 1990 | None | False | post1950 |
| real_v2-0898 | g0069 | MNG | Mongolia | 1995 | None | False | post1950 |
| real_v2-0899 | g0039 | BRA | Brazil | 1975 | None | False | post1950 |
| real_v2-0900 | g0009 | PER | Peru | 1715 | None | False | pre1950 |
| real_v2-0901 | g0004 | FRA | France | 1940 | 1941 | True | pre1950 |
| real_v2-0902 | g0004 | FRA | France | 1340 | None | False | pre1950 |
| real_v2-0903 | g0003 | NOR | Norway | 1950 | None | False | pre1950 |
| real_v2-0904 | g0017 | ECU | Ecuador | 1975 | None | False | post1950 |
| real_v2-0905 | g0014 | LKA | Sri Lanka | 1915 | None | False | pre1950 |
| real_v2-0906 | g0006 | POL | Poland | 1680 | None | False | pre1950 |
| real_v2-0907 | g0068 | BIH | Bosnia and Herzegovina | 2000 | None | False | post1950 |
| real_v2-0908 | g0025 | PSE | State of Palestine | 1995 | 2002 | False | post1950 |
| real_v2-0909 | g0001 | BEL | Belgium | 1890 | None | False | pre1950 |
| real_v2-0910 | g0026 | CHL | Chile | 1990 | None | False | post1950 |
| real_v2-0911 | g0004 | FRA | France | 1890 | None | False | pre1950 |
| real_v2-0912 | g0065 | KHM | Cambodia | 1990 | None | False | post1950 |
| real_v2-0913 | g0026 | CHL | Chile | 1940 | None | False | pre1950 |
| real_v2-0914 | g0030 | IDN | Indonesia | 1905 | None | False | pre1950 |
| real_v2-0915 | g0004 | FRA | France | 1470 | None | False | pre1950 |
| real_v2-0916 | g0038 | GRC | Greece | 1880 | None | False | pre1950 |
| real_v2-0917 | g0029 | MUS | Mauritius | 2000 | None | False | post1950 |
| real_v2-0918 | g0016 | DNK | Denmark | 1965 | None | False | post1950 |
| real_v2-0919 | g0030 | IDN | Indonesia | 1850 | None | False | pre1950 |
| real_v2-0920 | g0004 | FRA | France | 1415 | None | False | pre1950 |
| real_v2-0921 | g0004 | FRA | France | 1905 | None | False | pre1950 |
| real_v2-0922 | g0009 | PER | Peru | 1645 | 1660 | False | pre1950 |
| real_v2-0923 | g0064 | BGR | Bulgaria | 1985 | None | False | post1950 |
| real_v2-0924 | g0003 | NOR | Norway | 1990 | None | False | post1950 |
| real_v2-0925 | g0017 | ECU | Ecuador | 1935 | None | False | pre1950 |
| real_v2-0926 | g0037 | TUR | Turkey | 1965 | None | False | post1950 |
| real_v2-0927 | g0038 | GRC | Greece | 1975 | None | False | post1950 |
| real_v2-0928 | g0006 | POL | Poland | 1760 | None | False | pre1950 |
| real_v2-0929 | g0052 | MYS | Malaysia | 1985 | None | False | post1950 |
| real_v2-0930 | g0069 | MNG | Mongolia | 1980 | None | False | post1950 |
| real_v2-0931 | g0005 | CHE | Switzerland | 1915 | 1921 | False | pre1950 |
| real_v2-0932 | g0020 | ESP | Spain | 1880 | None | False | pre1950 |
| real_v2-0933 | g0002 | FIN | Finland | 1925 | None | False | pre1950 |
| real_v2-0934 | g0006 | POL | Poland | 1700 | None | False | pre1950 |
| real_v2-0935 | g0001 | BEL | Belgium | 1985 | None | False | post1950 |
| real_v2-0936 | g0020 | ESP | Spain | 2000 | None | False | post1950 |
| real_v2-0937 | g0005 | CHE | Switzerland | 2000 | None | False | post1950 |
| real_v2-0938 | g0007 | CAN | Canada | 1915 | None | False | pre1950 |
| real_v2-0939 | g0005 | CHE | Switzerland | 1885 | None | False | pre1950 |
| real_v2-0940 | g0034 | YEM | Yemen | 1995 | None | False | post1950 |
| real_v2-0941 | g0015 | COL | Colombia | 1970 | None | False | post1950 |
| real_v2-0942 | g0006 | POL | Poland | 1765 | None | False | pre1950 |
| real_v2-0943 | g0030 | IDN | Indonesia | 1920 | None | False | pre1950 |
| real_v2-0944 | g0022 | VEN | Venezuela (Bolivarian Republic of) | 1875 | None | False | pre1950 |
| real_v2-0945 | g0007 | CAN | Canada | 1945 | None | False | pre1950 |
| real_v2-0946 | g0022 | VEN | Venezuela (Bolivarian Republic of) | 1955 | None | False | post1950 |
| real_v2-0947 | g0009 | PER | Peru | 1970 | None | False | post1950 |
| real_v2-0948 | g0004 | FRA | France | 1525 | None | False | pre1950 |
| real_v2-0949 | g0037 | TUR | Turkey | 1955 | None | False | post1950 |
| real_v2-0950 | g0038 | GRC | Greece | 1870 | None | False | pre1950 |
| real_v2-0951 | g0004 | FRA | France | 1510 | None | False | pre1950 |
| real_v2-0952 | g0041 | NAM | Namibia | 1990 | None | False | post1950 |
| real_v2-0953 | g0026 | CHL | Chile | 1900 | None | False | pre1950 |
| real_v2-0954 | g0039 | BRA | Brazil | 1925 | None | False | pre1950 |
| real_v2-0955 | g0031 | DEU | Germany | 1965 | None | False | post1950 |
| real_v2-0956 | g0043 | HND | Honduras | 1985 | None | False | post1950 |
| real_v2-0957 | g0009 | PER | Peru | 1935 | None | False | pre1950 |
| real_v2-0958 | g0033 | ZWE | Zimbabwe | 1980 | None | False | post1950 |
| real_v2-0959 | g0017 | ECU | Ecuador | 1965 | None | False | post1950 |
| real_v2-0960 | g0007 | CAN | Canada | 1925 | 1933 | False | pre1950 |
| real_v2-0961 | g0064 | BGR | Bulgaria | 2000 | None | False | post1950 |
| real_v2-0962 | g0009 | PER | Peru | 1930 | 1932 | False | pre1950 |
| real_v2-0963 | g0020 | ESP | Spain | 1965 | None | False | post1950 |
| real_v2-0964 | g0003 | NOR | Norway | 1980 | None | False | post1950 |
| real_v2-0965 | g0014 | LKA | Sri Lanka | 1955 | None | False | post1950 |
| real_v2-0966 | g0040 | TWN | Taiwan, Province of China | 1985 | None | False | post1950 |
| real_v2-0967 | g0010 | BOL | Bolivia (Plurinational State of) | 1990 | None | False | post1950 |
| real_v2-0968 | g0032 | ISR | Israel | 2000 | None | False | post1950 |
| real_v2-0969 | g0047 | JPN | Japan | 1970 | None | False | post1950 |
| real_v2-0970 | g0006 | POL | Poland | 1575 | None | False | pre1950 |
| real_v2-0971 | g0005 | CHE | Switzerland | 1975 | None | False | post1950 |
| real_v2-0972 | g0021 | AUT | Austria | 1900 | None | False | pre1950 |
| real_v2-0973 | g0009 | PER | Peru | 1845 | None | False | pre1950 |
| real_v2-0974 | g0004 | FRA | France | 1450 | None | False | pre1950 |
| real_v2-0975 | g0004 | FRA | France | 1355 | None | False | pre1950 |
| real_v2-0976 | g0038 | GRC | Greece | 1970 | None | False | post1950 |
| real_v2-0977 | g0001 | BEL | Belgium | 1895 | None | False | pre1950 |
| real_v2-0978 | g0022 | VEN | Venezuela (Bolivarian Republic of) | 1895 | 1899 | False | pre1950 |
| real_v2-0979 | g0021 | AUT | Austria | 2000 | None | False | post1950 |
| real_v2-0980 | g0045 | NIC | Nicaragua | 1965 | None | False | post1950 |

## Countries by group id (group: code, name, split, windows, events)
- g0000: GTM, Guatemala, test, 9 windows, events 0
- g0001: BEL, Belgium, test, 25 windows, events 3
- g0002: FIN, Finland, test, 23 windows, events 2
- g0003: NOR, Norway, test, 29 windows, events 0
- g0004: FRA, France, test, 123 windows, events 4
- g0005: CHE, Switzerland, test, 24 windows, events 2
- g0006: POL, Poland, test, 84 windows, events 5
- g0007: CAN, Canada, test, 20 windows, events 3
- g0008: NZL, New Zealand, test, 21 windows, events 0
- g0009: PER, Peru, test, 61 windows, events 17
- g0010: BOL, Bolivia (Plurinational State of), test, 17 windows, events 0
- g0011: GNQ, Equatorial Guinea, test, 5 windows, events 3
- g0012: TGO, Togo, test, 1 windows, events 1
- g0013: SYR, Syrian Arab Republic, test, 4 windows, events 3
- g0014: LKA, Sri Lanka, test, 21 windows, events 0
- g0015: COL, Colombia, test, 21 windows, events 0
- g0016: DNK, Denmark, test, 31 windows, events 0
- g0017: ECU, Ecuador, test, 15 windows, events 0
- g0018: CSK, Czechoslovakia, test, 5 windows, events 0
- g0019: CHN, China, test, 5 windows, events 0
- g0020: ESP, Spain, test, 24 windows, events 3
- g0021: AUT, Austria, test, 20 windows, events 6
- g0022: VEN, Venezuela (Bolivarian Republic of), test, 27 windows, events 12
- g0023: MLI, Mali, test, 5 windows, events 0
- g0024: BRB, Barbados, test, 5 windows, events 0
- g0025: PSE, State of Palestine, test, 5 windows, events 3
- g0026: CHL, Chile, test, 33 windows, events 3
- g0027: ETH, Ethiopia, test, 3 windows, events 3
- g0028: DZA, Algeria, test, 5 windows, events 0
- g0029: MUS, Mauritius, test, 5 windows, events 0
- g0030: IDN, Indonesia, test, 24 windows, events 2
- g0031: DEU, Germany, test, 23 windows, events 4
- g0032: ISR, Israel, test, 5 windows, events 0
- g0033: ZWE, Zimbabwe, test, 5 windows, events 3
- g0034: YEM, Yemen, test, 8 windows, events 4
- g0035: PHL, Philippines, test, 7 windows, events 2
- g0036: LSO, Lesotho, test, 5 windows, events 0
- g0037: TUR, Turkey, test, 10 windows, events 0
- g0038: GRC, Greece, test, 24 windows, events 8
- g0039: BRA, Brazil, test, 24 windows, events 3
- g0040: TWN, Taiwan, Province of China, test, 7 windows, events 2
- g0041: NAM, Namibia, test, 5 windows, events 2
- g0042: JAM, Jamaica, test, 5 windows, events 2
- g0043: HND, Honduras, test, 11 windows, events 0
- g0044: CYP, Cyprus, test, 5 windows, events 0
- g0045: NIC, Nicaragua, test, 6 windows, events 2
- g0046: LAO, Lao People's DR, test, 5 windows, events 0
- g0047: JPN, Japan, test, 17 windows, events 3
- g0048: SEN, Senegal, test, 5 windows, events 0
- g0049: GNB, Guinea-Bissau, test, 5 windows, events 0
- g0050: EGY, Egypt, test, 5 windows, events 0
- g0051: SWZ, Swaziland, test, 5 windows, events 0
- g0052: MYS, Malaysia, test, 8 windows, events 3
- g0053: BHR, Bahrain, test, 5 windows, events 0
- g0054: BGD, Bangladesh, test, 5 windows, events 0
- g0055: BFA, Burkina Faso, test, 5 windows, events 0
- g0056: GIN, Guinea, test, 5 windows, events 0
- g0057: HRV, Croatia, test, 3 windows, events 2
- g0058: DOM, Dominican Republic, test, 5 windows, events 0
- g0059: RUS, Russian Federation, test, 1 windows, events 1
- g0060: LBY, Libya, test, 4 windows, events 3
- g0061: CPV, Cabo Verde, test, 5 windows, events 0
- g0062: COG, Congo, test, 5 windows, events 0
- g0063: BEN, Benin, test, 5 windows, events 0
- g0064: BGR, Bulgaria, test, 5 windows, events 0
- g0065: KHM, Cambodia, test, 5 windows, events 0
- g0066: DMA, Dominica, test, 5 windows, events 0
- g0067: HTI, Haiti, test, 4 windows, events 3
- g0068: BIH, Bosnia and Herzegovina, test, 3 windows, events 2
- g0069: MNG, Mongolia, test, 5 windows, events 0
- g0070: CIV, Côte d'Ivoire, test, 2 windows, events 2
- g0071: IRQ, Iraq, test, 1 windows, events 1
- g0072: MNE, Montenegro, test, 2 windows, events 2
- g0073: STP, Sao Tome and Principe, test, 1 windows, events 1
- g0074: IRL, Ireland, dev, 10 windows, events 0
- g0075: ITA, Italy, dev, 129 windows, events 16
- g0076: ZAF, South Africa, dev, 23 windows, events 13
- g0077: GBR, United Kingdom, dev, 138 windows, events 16
- g0078: SWE, Sweden, dev, 109 windows, events 38
- g0079: RWA, Rwanda, dev, 3 windows, events 3
- g0080: USA, United States, dev, 34 windows, events 2
- g0081: NLD, Netherlands, dev, 109 windows, events 25
- g0082: ZMB, Zambia, dev, 2 windows, events 1
- g0083: LCA, Saint Lucia, dev, 5 windows, events 0
- g0084: SDN, Sudan (Former), dev, 3 windows, events 2
- g0085: MWI, Malawi, dev, 5 windows, events 0
- g0086: PRT, Portugal, dev, 69 windows, events 14
- g0087: YUG, Former Yugoslavia, dev, 4 windows, events 3
- g0088: VNM, Viet Nam, dev, 5 windows, events 0
- g0089: THA, Thailand, dev, 5 windows, events 0
- g0090: HKG, China, Hong Kong SAR, dev, 5 windows, events 0
- g0091: MEX, Mexico, dev, 54 windows, events 6
- g0092: KOR, Republic of Korea, dev, 5 windows, events 0
- g0093: COM, Comoros, dev, 5 windows, events 0
- g0094: IND, India, dev, 18 windows, events 0
- g0095: ISL, Iceland, dev, 5 windows, events 0
- g0096: SUN, Former USSR, dev, 4 windows, events 4
- g0097: PAN, Panama, dev, 13 windows, events 1
- g0098: CRI, Costa Rica, dev, 11 windows, events 0
- g0099: BWA, Botswana, dev, 5 windows, events 0
- g0100: ARG, Argentina, dev, 20 windows, events 1
- g0101: SYC, Seychelles, dev, 5 windows, events 0
- g0102: AUS, Australia, dev, 31 windows, events 2
- g0103: URY, Uruguay, dev, 20 windows, events 4
- g0104: MMR, Myanmar, dev, 5 windows, events 0
- g0105: SGP, Singapore, dev, 7 windows, events 2
- g0106: MLT, Malta, dev, 5 windows, events 0
- g0107: TZA, U.R. of Tanzania: Mainland, dev, 5 windows, events 0
- g0108: ALB, Albania, dev, 5 windows, events 2
- g0109: PRI, Puerto Rico, dev, 5 windows, events 0
- g0110: JOR, Jordan, dev, 5 windows, events 1
- g0111: SLV, El Salvador, dev, 11 windows, events 0
- g0112: PAK, Pakistan, dev, 5 windows, events 0
- g0113: CUB, Cuba, dev, 11 windows, events 3
- g0114: AFG, Afghanistan, dev, 2 windows, events 2
- g0115: NER, Niger, dev, 1 windows, events 1
- g0116: OMN, Oman, dev, 5 windows, events 0
- g0117: NGA, Nigeria, dev, 4 windows, events 1
- g0118: KEN, Kenya, dev, 5 windows, events 0
- g0119: HUN, Hungary, dev, 5 windows, events 0
- g0120: MRT, Mauritania, dev, 5 windows, events 0
- g0121: GHA, Ghana, dev, 3 windows, events 1
- g0122: CAF, Central African Republic, dev, 1 windows, events 1
- g0123: SAU, Saudi Arabia, dev, 4 windows, events 2
- g0124: PRY, Paraguay, dev, 7 windows, events 0
- g0125: BDI, Burundi, dev, 4 windows, events 3
- g0126: TUN, Tunisia, dev, 5 windows, events 0
- g0127: NPL, Nepal, dev, 5 windows, events 0
- g0128: SLE, Sierra Leone, dev, 4 windows, events 3
- g0129: SVN, Slovenia, dev, 4 windows, events 2
- g0130: GMB, Gambia, dev, 5 windows, events 0
- g0131: UGA, Uganda, dev, 1 windows, events 0
- g0132: CMR, Cameroon, dev, 3 windows, events 2
- g0133: MAR, Morocco, dev, 5 windows, events 0
- g0134: MKD, TFYR of Macedonia, dev, 2 windows, events 2
- g0135: LUX, Luxembourg, dev, 5 windows, events 0
- g0136: SRB, Serbia, dev, 2 windows, events 2
- g0137: ROU, Romania, dev, 14 windows, events 3
- g0138: MDG, Madagascar, dev, 1 windows, events 1
- g0139: TTO, Trinidad and Tobago, dev, 3 windows, events 2
- g0140: LBR, Liberia, dev, 1 windows, events 1
- g0141: TCD, Chad, dev, 1 windows, events 0
- g0142: GAB, Gabon, dev, 1 windows, events 0
- g0143: CZE, Czech Republic, dev, 1 windows, events 0
- g0144: LBN, Lebanon, dev, 1 windows, events 0
- g0145: IRN, Iran (Islamic Republic of), dev, 1 windows, events 0
- g0146: ARE, United Arab Emirates, dev, 1 windows, events 1

Leak-check hits: []
Leak-check hits inside hex digests (coincidences): []

## Seal event

```json
{
  "H": 15,
  "W": 30,
  "dataset": "Maddison Project Database",
  "dataset_sha256": "d20853c2e0930d6855fb6d8138da11f24fcf313d234e2db9773ea1f551adfec3",
  "dataset_version": "2020",
  "event": "pool_built",
  "external": true,
  "fallback_used": false,
  "generator_revision": "60cffe65880fd64f07269ce5e34e83608ceb327a",
  "n_dev_countries": 73,
  "n_dev_windows": 1030,
  "n_obs": 30,
  "n_requested": 981,
  "n_test_countries": 74,
  "n_test_windows": 981,
  "n_worlds": 981,
  "record_sha256": {
    "real": "0843fcc5d7e63abb8c621b624e4899ceaf34dc9203c8d23213f5e216f46c6ec2"
  },
  "sheet": "Full data",
  "test_set": "real_v2",
  "truth_sha256": "b4fbd654207fbd1829c9bd0117d0300e01a9e0bf4db96fccf35278d56249b223"
}
```

Final leak check on the public log after appending the seal event: [] (inside hex digests: [])
