# Offline WVS sensitivity audit

Offline quality-only baseline, NOT production Basic. Quality = 0.6 popularity + 0.4 rating/5. Production group ranking weights untouched.



Within each country and source domain: center eligible Relative-vs-Global pp by domain mean; divide by maximum absolute centered value; affinity=0.5+0.5*normalized_signal*coverage/100. Zero spread -> neutral. Normalize before category alias averaging and item semantic mapping. Eligibility gates unchanged.



Amplifies within-country contrasts and discards absolute distance from global. Negative global deltas may become above-neutral relative preferences. Country-domain max scaling is outlier-sensitive; especially fragile with only three environments. Exploratory, not calibrated confidence.



## raw_affinity

{'first_shortlist_change_vs_basic': {'India': None, 'Canada': None}, 'first_country_shortlist_difference': None}



### WVS 0%

Country overlap: {"country_city_overlap": {"intersection": 4, "union": 4, "jaccard": 1.0, "only_first": [], "only_second": []}, "country_activity_overlap": {"intersection": 25, "union": 25, "jaccard": 1.0, "only_first": [], "only_second": []}}



**India**

Top 10: Unaizah > Farasan > Buraydah > Tabuk > Jazan > Abha > Al Makhwah > Najran > Al Baha > Baljurashi

Top 4: Unaizah, Farasan, Buraydah, Tabuk

Overlaps vs Basic: {"city": {"intersection": 4, "union": 4, "jaccard": 1.0, "only_first": [], "only_second": []}, "activity": {"intersection": 25, "union": 25, "jaccard": 1.0, "only_first": [], "only_second": []}}

Rank changes: {"Unaizah": {"basic": 1, "current": 1, "positions_gained": 0}, "Farasan": {"basic": 2, "current": 2, "positions_gained": 0}, "Buraydah": {"basic": 3, "current": 3, "positions_gained": 0}, "Tabuk": {"basic": 4, "current": 4, "positions_gained": 0}, "Jazan": {"basic": 5, "current": 5, "positions_gained": 0}, "Abha": {"basic": 6, "current": 6, "positions_gained": 0}, "Al Makhwah": {"basic": 7, "current": 7, "positions_gained": 0}, "Najran": {"basic": 8, "current": 8, "positions_gained": 0}, "Al Baha": {"basic": 9, "current": 9, "positions_gained": 0}, "Baljurashi": {"basic": 10, "current": 10, "positions_gained": 0}, "Al Kharj": {"basic": 11, "current": 11, "positions_gained": 0}, "Riyadh": {"basic": 12, "current": 12, "positions_gained": 0}}

Margins: {"3-4": 1.75, "4-5": 0.8375000000000057, "5-6": 0.7625000000000028, "3-6": 3.3500000000000085}

Unaizah: Al-Musawkaf Market [place_0043] (95.4); Al-Bassam Heritage House [place_0046] (93.4); Al-Hajeb Parks [place_0048] (93.2); Uneyzah Mall [place_0055] (92.6); Al-Aoshaziyah Lake [place_0053] (82.8)

Farasan: Farasan Islands Trip [place_0033] (94.2); Farasan Snorkeling & Diving [place_0317] (93.8); Farasan Boat Tour [place_0034] (89.6); Farasan Island Archaeological Site [place_0313] (85.2)

Buraydah: Al-Nakheel Mall Buraydah [place_0054] (96.6); Al-Uqailat Museum [place_0042] (92.8); Garden of Al-Montazah [place_0060] (91.4); Buraydah Water Tower [place_0050] (89.4); Al-Bassr Garden Park [place_0056] (89.4); King Khalid Wildlife Park [place_0047] (89.2); Al-Jarad Heritage Market [place_0051] (86.6); Al-Faiha Garden [place_0061] (84.2)

Tabuk: Tabuk Park Mall [place_0068] (94.0); Jabal Al-Lawz [place_0070] (92.8); Tabuk Regional Museum [place_0080] (92.2); Hegjaz Railway Station [place_0077] (91.0); Tabuk Castle [place_0072] (90.8); Boulevard Tabuk [place_0069] (90.6); Prince Fahd bin Sultan Park [place_0076] (90.6); King Abdulaziz Heritage Garden [place_0084] (89.4)



**Canada**

Top 10: Unaizah > Farasan > Buraydah > Tabuk > Jazan > Abha > Al Makhwah > Najran > Al Baha > Baljurashi

Top 4: Unaizah, Farasan, Buraydah, Tabuk

Overlaps vs Basic: {"city": {"intersection": 4, "union": 4, "jaccard": 1.0, "only_first": [], "only_second": []}, "activity": {"intersection": 25, "union": 25, "jaccard": 1.0, "only_first": [], "only_second": []}}

Rank changes: {"Unaizah": {"basic": 1, "current": 1, "positions_gained": 0}, "Farasan": {"basic": 2, "current": 2, "positions_gained": 0}, "Buraydah": {"basic": 3, "current": 3, "positions_gained": 0}, "Tabuk": {"basic": 4, "current": 4, "positions_gained": 0}, "Jazan": {"basic": 5, "current": 5, "positions_gained": 0}, "Abha": {"basic": 6, "current": 6, "positions_gained": 0}, "Al Makhwah": {"basic": 7, "current": 7, "positions_gained": 0}, "Najran": {"basic": 8, "current": 8, "positions_gained": 0}, "Al Baha": {"basic": 9, "current": 9, "positions_gained": 0}, "Baljurashi": {"basic": 10, "current": 10, "positions_gained": 0}, "Al Kharj": {"basic": 11, "current": 11, "positions_gained": 0}, "Riyadh": {"basic": 12, "current": 12, "positions_gained": 0}}

Margins: {"3-4": 1.75, "4-5": 0.8375000000000057, "5-6": 0.7625000000000028, "3-6": 3.3500000000000085}

Unaizah: Al-Musawkaf Market [place_0043] (95.4); Al-Bassam Heritage House [place_0046] (93.4); Al-Hajeb Parks [place_0048] (93.2); Uneyzah Mall [place_0055] (92.6); Al-Aoshaziyah Lake [place_0053] (82.8)

Farasan: Farasan Islands Trip [place_0033] (94.2); Farasan Snorkeling & Diving [place_0317] (93.8); Farasan Boat Tour [place_0034] (89.6); Farasan Island Archaeological Site [place_0313] (85.2)

Buraydah: Al-Nakheel Mall Buraydah [place_0054] (96.6); Al-Uqailat Museum [place_0042] (92.8); Garden of Al-Montazah [place_0060] (91.4); Buraydah Water Tower [place_0050] (89.4); Al-Bassr Garden Park [place_0056] (89.4); King Khalid Wildlife Park [place_0047] (89.2); Al-Jarad Heritage Market [place_0051] (86.6); Al-Faiha Garden [place_0061] (84.2)

Tabuk: Tabuk Park Mall [place_0068] (94.0); Jabal Al-Lawz [place_0070] (92.8); Tabuk Regional Museum [place_0080] (92.2); Hegjaz Railway Station [place_0077] (91.0); Tabuk Castle [place_0072] (90.8); Boulevard Tabuk [place_0069] (90.6); Prince Fahd bin Sultan Park [place_0076] (90.6); King Abdulaziz Heritage Garden [place_0084] (89.4)



### WVS 10%

Country overlap: {"country_city_overlap": {"intersection": 4, "union": 4, "jaccard": 1.0, "only_first": [], "only_second": []}, "country_activity_overlap": {"intersection": 25, "union": 25, "jaccard": 1.0, "only_first": [], "only_second": []}}



**India**

Top 10: Unaizah > Farasan > Buraydah > Tabuk > Jazan > Abha > Al Makhwah > Najran > Al Baha > Baljurashi

Top 4: Unaizah, Farasan, Buraydah, Tabuk

Overlaps vs Basic: {"city": {"intersection": 4, "union": 4, "jaccard": 1.0, "only_first": [], "only_second": []}, "activity": {"intersection": 25, "union": 25, "jaccard": 1.0, "only_first": [], "only_second": []}}

Rank changes: {"Unaizah": {"basic": 1, "current": 1, "positions_gained": 0}, "Farasan": {"basic": 2, "current": 2, "positions_gained": 0}, "Buraydah": {"basic": 3, "current": 3, "positions_gained": 0}, "Tabuk": {"basic": 4, "current": 4, "positions_gained": 0}, "Jazan": {"basic": 5, "current": 5, "positions_gained": 0}, "Abha": {"basic": 6, "current": 6, "positions_gained": 0}, "Al Makhwah": {"basic": 7, "current": 7, "positions_gained": 0}, "Najran": {"basic": 8, "current": 8, "positions_gained": 0}, "Al Baha": {"basic": 9, "current": 9, "positions_gained": 0}, "Baljurashi": {"basic": 10, "current": 10, "positions_gained": 0}, "Al Kharj": {"basic": 11, "current": 11, "positions_gained": 0}, "Riyadh": {"basic": 12, "current": 12, "positions_gained": 0}}

Margins: {"3-4": 1.6329865451168075, "4-5": 0.6727295176545312, "5-6": 0.6982417428520478, "3-6": 3.0039578056233864}

Unaizah: Al-Musawkaf Market [place_0043] (90.947); Al-Hajeb Parks [place_0048] (89.3098); Al-Bassam Heritage House [place_0046] (89.0681); Uneyzah Mall [place_0055] (88.7112); Al-Aoshaziyah Lake [place_0053] (79.9498)

Farasan: Farasan Islands Trip [place_0033] (90.2783); Farasan Snorkeling & Diving [place_0317] (89.9183); Farasan Boat Tour [place_0034] (86.1383); Farasan Island Archaeological Site [place_0313] (81.767)

Buraydah: Al-Nakheel Mall Buraydah [place_0054] (92.3112); Al-Uqailat Museum [place_0042] (88.5445); Garden of Al-Montazah [place_0060] (87.6898); Al-Bassr Garden Park [place_0056] (85.8898); King Khalid Wildlife Park [place_0047] (85.7098); Buraydah Water Tower [place_0050] (85.5552); Al-Jarad Heritage Market [place_0051] (83.027); Al-Faiha Garden [place_0061] (81.2098)

Tabuk: Tabuk Park Mall [place_0068] (89.9712); Jabal Al-Lawz [place_0070] (88.9498); Tabuk Regional Museum [place_0080] (88.0045); Prince Fahd bin Sultan Park [place_0076] (86.9698); Hegjaz Railway Station [place_0077] (86.9245); Boulevard Tabuk [place_0069] (86.7655); Tabuk Castle [place_0072] (86.7445); King Abdulaziz Heritage Garden [place_0084] (85.8898)



**Canada**

Top 10: Unaizah > Farasan > Buraydah > Tabuk > Jazan > Abha > Al Makhwah > Najran > Al Baha > Baljurashi

Top 4: Unaizah, Farasan, Buraydah, Tabuk

Overlaps vs Basic: {"city": {"intersection": 4, "union": 4, "jaccard": 1.0, "only_first": [], "only_second": []}, "activity": {"intersection": 25, "union": 25, "jaccard": 1.0, "only_first": [], "only_second": []}}

Rank changes: {"Unaizah": {"basic": 1, "current": 1, "positions_gained": 0}, "Farasan": {"basic": 2, "current": 2, "positions_gained": 0}, "Buraydah": {"basic": 3, "current": 3, "positions_gained": 0}, "Tabuk": {"basic": 4, "current": 4, "positions_gained": 0}, "Jazan": {"basic": 5, "current": 5, "positions_gained": 0}, "Abha": {"basic": 6, "current": 6, "positions_gained": 0}, "Al Makhwah": {"basic": 7, "current": 7, "positions_gained": 0}, "Najran": {"basic": 8, "current": 8, "positions_gained": 0}, "Al Baha": {"basic": 9, "current": 9, "positions_gained": 0}, "Baljurashi": {"basic": 10, "current": 10, "positions_gained": 0}, "Al Kharj": {"basic": 11, "current": 11, "positions_gained": 0}, "Riyadh": {"basic": 12, "current": 12, "positions_gained": 0}}

Margins: {"3-4": 1.628763957191282, "4-5": 0.7850069927723808, "5-6": 0.5935392530031152, "3-6": 3.007310202966778}

Unaizah: Al-Musawkaf Market [place_0043] (90.4678); Al-Hajeb Parks [place_0048] (88.7046); Al-Bassam Heritage House [place_0046] (88.6327); Uneyzah Mall [place_0055] (87.9692); Al-Aoshaziyah Lake [place_0053] (79.3446)

Farasan: Farasan Islands Trip [place_0033] (89.4254); Farasan Snorkeling & Diving [place_0317] (89.0654); Farasan Boat Tour [place_0034] (85.2854); Farasan Island Archaeological Site [place_0313] (81.2878)

Buraydah: Al-Nakheel Mall Buraydah [place_0054] (91.5692); Al-Uqailat Museum [place_0042] (88.1279); Garden of Al-Montazah [place_0060] (87.0846); Al-Bassr Garden Park [place_0056] (85.2846); King Khalid Wildlife Park [place_0047] (85.1046); Buraydah Water Tower [place_0050] (85.0855); Al-Jarad Heritage Market [place_0051] (82.5478); Al-Faiha Garden [place_0061] (80.6046)

Tabuk: Tabuk Park Mall [place_0068] (89.2292); Jabal Al-Lawz [place_0070] (88.3446); Tabuk Regional Museum [place_0080] (87.5879); Hegjaz Railway Station [place_0077] (86.5079); Prince Fahd bin Sultan Park [place_0076] (86.3646); Tabuk Castle [place_0072] (86.3279); Boulevard Tabuk [place_0069] (86.1769); King Abdulaziz Heritage Garden [place_0084] (85.2846)



### WVS 20%

Country overlap: {"country_city_overlap": {"intersection": 4, "union": 4, "jaccard": 1.0, "only_first": [], "only_second": []}, "country_activity_overlap": {"intersection": 25, "union": 25, "jaccard": 1.0, "only_first": [], "only_second": []}}



**India**

Top 10: Unaizah > Farasan > Buraydah > Tabuk > Jazan > Abha > Al Makhwah > Najran > Al Baha > Baljurashi

Top 4: Unaizah, Farasan, Buraydah, Tabuk

Overlaps vs Basic: {"city": {"intersection": 4, "union": 4, "jaccard": 1.0, "only_first": [], "only_second": []}, "activity": {"intersection": 25, "union": 25, "jaccard": 1.0, "only_first": [], "only_second": []}}

Rank changes: {"Unaizah": {"basic": 1, "current": 1, "positions_gained": 0}, "Farasan": {"basic": 2, "current": 2, "positions_gained": 0}, "Buraydah": {"basic": 3, "current": 3, "positions_gained": 0}, "Tabuk": {"basic": 4, "current": 4, "positions_gained": 0}, "Jazan": {"basic": 5, "current": 5, "positions_gained": 0}, "Abha": {"basic": 6, "current": 6, "positions_gained": 0}, "Al Makhwah": {"basic": 7, "current": 7, "positions_gained": 0}, "Najran": {"basic": 8, "current": 8, "positions_gained": 0}, "Al Baha": {"basic": 9, "current": 9, "positions_gained": 0}, "Baljurashi": {"basic": 10, "current": 10, "positions_gained": 0}, "Al Kharj": {"basic": 11, "current": 11, "positions_gained": 0}, "Riyadh": {"basic": 12, "current": 12, "positions_gained": 0}}

Margins: {"3-4": 1.5159730902335866, "4-5": 0.507959035309085, "5-6": 0.6339834857040785, "3-6": 2.65791561124675}

Unaizah: Al-Musawkaf Market [place_0043] (86.4939); Al-Hajeb Parks [place_0048] (85.4195); Uneyzah Mall [place_0055] (84.8224); Al-Bassam Heritage House [place_0046] (84.7362); Al-Aoshaziyah Lake [place_0053] (77.0995)

Farasan: Farasan Islands Trip [place_0033] (86.3565); Farasan Snorkeling & Diving [place_0317] (86.0365); Farasan Boat Tour [place_0034] (82.6765); Farasan Island Archaeological Site [place_0313] (78.3339)

Buraydah: Al-Nakheel Mall Buraydah [place_0054] (88.0224); Al-Uqailat Museum [place_0042] (84.289); Garden of Al-Montazah [place_0060] (83.9795); Al-Bassr Garden Park [place_0056] (82.3795); King Khalid Wildlife Park [place_0047] (82.2195); Buraydah Water Tower [place_0050] (81.7103); Al-Jarad Heritage Market [place_0051] (79.4539); Al-Faiha Garden [place_0061] (78.2195)

Tabuk: Tabuk Park Mall [place_0068] (85.9424); Jabal Al-Lawz [place_0070] (85.0995); Tabuk Regional Museum [place_0080] (83.809); Prince Fahd bin Sultan Park [place_0076] (83.3395); Boulevard Tabuk [place_0069] (82.931); Hegjaz Railway Station [place_0077] (82.849); Tabuk Castle [place_0072] (82.689); King Abdulaziz Heritage Garden [place_0084] (82.3795)



**Canada**

Top 10: Unaizah > Farasan > Buraydah > Tabuk > Jazan > Abha > Al Makhwah > Najran > Al Baha > Baljurashi

Top 4: Unaizah, Farasan, Buraydah, Tabuk

Overlaps vs Basic: {"city": {"intersection": 4, "union": 4, "jaccard": 1.0, "only_first": [], "only_second": []}, "activity": {"intersection": 25, "union": 25, "jaccard": 1.0, "only_first": [], "only_second": []}}

Rank changes: {"Unaizah": {"basic": 1, "current": 1, "positions_gained": 0}, "Farasan": {"basic": 2, "current": 2, "positions_gained": 0}, "Buraydah": {"basic": 3, "current": 3, "positions_gained": 0}, "Tabuk": {"basic": 4, "current": 4, "positions_gained": 0}, "Jazan": {"basic": 5, "current": 5, "positions_gained": 0}, "Abha": {"basic": 6, "current": 6, "positions_gained": 0}, "Al Makhwah": {"basic": 7, "current": 7, "positions_gained": 0}, "Najran": {"basic": 8, "current": 8, "positions_gained": 0}, "Al Baha": {"basic": 9, "current": 9, "positions_gained": 0}, "Baljurashi": {"basic": 10, "current": 10, "positions_gained": 0}, "Al Kharj": {"basic": 11, "current": 11, "positions_gained": 0}, "Riyadh": {"basic": 12, "current": 12, "positions_gained": 0}}

Margins: {"3-4": 1.507527914382564, "4-5": 0.732513985544756, "5-6": 0.42457850600619906, "3-6": 2.664620405933519}

Unaizah: Al-Musawkaf Market [place_0043] (85.5357); Al-Hajeb Parks [place_0048] (84.2092); Al-Bassam Heritage House [place_0046] (83.8653); Uneyzah Mall [place_0055] (83.3385); Al-Aoshaziyah Lake [place_0053] (75.8892)

Farasan: Farasan Islands Trip [place_0033] (84.6508); Farasan Snorkeling & Diving [place_0317] (84.3308); Farasan Boat Tour [place_0034] (80.9708); Farasan Island Archaeological Site [place_0313] (77.3757)

Buraydah: Al-Nakheel Mall Buraydah [place_0054] (86.5385); Al-Uqailat Museum [place_0042] (83.4559); Garden of Al-Montazah [place_0060] (82.7692); Al-Bassr Garden Park [place_0056] (81.1692); King Khalid Wildlife Park [place_0047] (81.0092); Buraydah Water Tower [place_0050] (80.771); Al-Jarad Heritage Market [place_0051] (78.4957); Al-Faiha Garden [place_0061] (77.0092)

Tabuk: Tabuk Park Mall [place_0068] (84.4585); Jabal Al-Lawz [place_0070] (83.8892); Tabuk Regional Museum [place_0080] (82.9759); Prince Fahd bin Sultan Park [place_0076] (82.1292); Hegjaz Railway Station [place_0077] (82.0159); Tabuk Castle [place_0072] (81.8559); Boulevard Tabuk [place_0069] (81.7537); King Abdulaziz Heritage Garden [place_0084] (81.1692)



### WVS 30%

Country overlap: {"country_city_overlap": {"intersection": 4, "union": 4, "jaccard": 1.0, "only_first": [], "only_second": []}, "country_activity_overlap": {"intersection": 25, "union": 25, "jaccard": 1.0, "only_first": [], "only_second": []}}



**India**

Top 10: Unaizah > Farasan > Buraydah > Tabuk > Jazan > Abha > Al Makhwah > Najran > Al Baha > Baljurashi

Top 4: Unaizah, Farasan, Buraydah, Tabuk

Overlaps vs Basic: {"city": {"intersection": 4, "union": 4, "jaccard": 1.0, "only_first": [], "only_second": []}, "activity": {"intersection": 25, "union": 25, "jaccard": 1.0, "only_first": [], "only_second": []}}

Rank changes: {"Unaizah": {"basic": 1, "current": 1, "positions_gained": 0}, "Farasan": {"basic": 2, "current": 2, "positions_gained": 0}, "Buraydah": {"basic": 3, "current": 3, "positions_gained": 0}, "Tabuk": {"basic": 4, "current": 4, "positions_gained": 0}, "Jazan": {"basic": 5, "current": 5, "positions_gained": 0}, "Abha": {"basic": 6, "current": 6, "positions_gained": 0}, "Al Makhwah": {"basic": 7, "current": 7, "positions_gained": 0}, "Najran": {"basic": 8, "current": 8, "positions_gained": 0}, "Al Baha": {"basic": 9, "current": 9, "positions_gained": 0}, "Baljurashi": {"basic": 10, "current": 10, "positions_gained": 0}, "Al Kharj": {"basic": 11, "current": 11, "positions_gained": 0}, "Riyadh": {"basic": 12, "current": 12, "positions_gained": 0}}

Margins: {"3-4": 1.3989596353503941, "4-5": 0.3431885529635963, "5-6": 0.5697252285561518, "3-6": 2.3118734168701423}

Unaizah: Al-Musawkaf Market [place_0043] (82.0409); Al-Hajeb Parks [place_0048] (81.5293); Uneyzah Mall [place_0055] (80.9337); Al-Bassam Heritage House [place_0046] (80.4043); Al-Aoshaziyah Lake [place_0053] (74.2493)

Farasan: Farasan Islands Trip [place_0033] (82.4348); Farasan Snorkeling & Diving [place_0317] (82.1548); Farasan Boat Tour [place_0034] (79.2148); Farasan Island Archaeological Site [place_0313] (74.9009)

Buraydah: Al-Nakheel Mall Buraydah [place_0054] (83.7337); Garden of Al-Montazah [place_0060] (80.2693); Al-Uqailat Museum [place_0042] (80.0335); Al-Bassr Garden Park [place_0056] (78.8693); King Khalid Wildlife Park [place_0047] (78.7293); Buraydah Water Tower [place_0050] (77.8655); Al-Jarad Heritage Market [place_0051] (75.8809); Al-Faiha Garden [place_0061] (75.2293)

Tabuk: Tabuk Park Mall [place_0068] (81.9137); Jabal Al-Lawz [place_0070] (81.2493); Prince Fahd bin Sultan Park [place_0076] (79.7093); Tabuk Regional Museum [place_0080] (79.6135); Boulevard Tabuk [place_0069] (79.0965); King Abdulaziz Heritage Garden [place_0084] (78.8693); Hegjaz Railway Station [place_0077] (78.7735); Tabuk Castle [place_0072] (78.6335)



**Canada**

Top 10: Unaizah > Farasan > Buraydah > Tabuk > Jazan > Abha > Al Makhwah > Najran > Al Baha > Baljurashi

Top 4: Unaizah, Farasan, Buraydah, Tabuk

Overlaps vs Basic: {"city": {"intersection": 4, "union": 4, "jaccard": 1.0, "only_first": [], "only_second": []}, "activity": {"intersection": 25, "union": 25, "jaccard": 1.0, "only_first": [], "only_second": []}}

Rank changes: {"Unaizah": {"basic": 1, "current": 1, "positions_gained": 0}, "Farasan": {"basic": 2, "current": 2, "positions_gained": 0}, "Buraydah": {"basic": 3, "current": 3, "positions_gained": 0}, "Tabuk": {"basic": 4, "current": 4, "positions_gained": 0}, "Jazan": {"basic": 5, "current": 5, "positions_gained": 0}, "Abha": {"basic": 6, "current": 6, "positions_gained": 0}, "Al Makhwah": {"basic": 7, "current": 7, "positions_gained": 0}, "Najran": {"basic": 8, "current": 8, "positions_gained": 0}, "Al Baha": {"basic": 9, "current": 9, "positions_gained": 0}, "Baljurashi": {"basic": 10, "current": 10, "positions_gained": 0}, "Al Kharj": {"basic": 11, "current": 11, "positions_gained": 0}, "Riyadh": {"basic": 12, "current": 12, "positions_gained": 0}}

Margins: {"3-4": 1.3862918715738175, "4-5": 0.6800209783171454, "5-6": 0.2556177590093256, "3-6": 2.3219306089002885}

Unaizah: Al-Musawkaf Market [place_0043] (80.6035); Al-Hajeb Parks [place_0048] (79.7138); Al-Bassam Heritage House [place_0046] (79.098); Uneyzah Mall [place_0055] (78.7077); Al-Aoshaziyah Lake [place_0053] (72.4338)

Farasan: Farasan Islands Trip [place_0033] (79.8763); Farasan Snorkeling & Diving [place_0317] (79.5963); Farasan Boat Tour [place_0034] (76.6563); Farasan Island Archaeological Site [place_0313] (73.4635)

Buraydah: Al-Nakheel Mall Buraydah [place_0054] (81.5077); Al-Uqailat Museum [place_0042] (78.7838); Garden of Al-Montazah [place_0060] (78.4538); Al-Bassr Garden Park [place_0056] (77.0538); King Khalid Wildlife Park [place_0047] (76.9138); Buraydah Water Tower [place_0050] (76.4564); Al-Jarad Heritage Market [place_0051] (74.4435); Al-Faiha Garden [place_0061] (73.4138)

Tabuk: Tabuk Park Mall [place_0068] (79.6877); Jabal Al-Lawz [place_0070] (79.4338); Tabuk Regional Museum [place_0080] (78.3638); Prince Fahd bin Sultan Park [place_0076] (77.8938); Hegjaz Railway Station [place_0077] (77.5238); Tabuk Castle [place_0072] (77.3838); Boulevard Tabuk [place_0069] (77.3306); King Abdulaziz Heritage Garden [place_0084] (77.0538)



### WVS 40%

Country overlap: {"country_city_overlap": {"intersection": 4, "union": 4, "jaccard": 1.0, "only_first": [], "only_second": []}, "country_activity_overlap": {"intersection": 25, "union": 25, "jaccard": 1.0, "only_first": [], "only_second": []}}



**India**

Top 10: Farasan > Unaizah > Buraydah > Tabuk > Jazan > Abha > Al Baha > Al Makhwah > Najran > Baljurashi

Top 4: Farasan, Unaizah, Buraydah, Tabuk

Overlaps vs Basic: {"city": {"intersection": 4, "union": 4, "jaccard": 1.0, "only_first": [], "only_second": []}, "activity": {"intersection": 25, "union": 25, "jaccard": 1.0, "only_first": [], "only_second": []}}

Rank changes: {"Farasan": {"basic": 2, "current": 1, "positions_gained": 1}, "Unaizah": {"basic": 1, "current": 2, "positions_gained": -1}, "Buraydah": {"basic": 3, "current": 3, "positions_gained": 0}, "Tabuk": {"basic": 4, "current": 4, "positions_gained": 0}, "Jazan": {"basic": 5, "current": 5, "positions_gained": 0}, "Abha": {"basic": 6, "current": 6, "positions_gained": 0}, "Al Baha": {"basic": 9, "current": 7, "positions_gained": 2}, "Al Makhwah": {"basic": 7, "current": 8, "positions_gained": -1}, "Najran": {"basic": 8, "current": 9, "positions_gained": -1}, "Baljurashi": {"basic": 10, "current": 10, "positions_gained": 0}, "Al Kharj": {"basic": 11, "current": 11, "positions_gained": 0}, "Riyadh": {"basic": 12, "current": 12, "positions_gained": 0}}

Margins: {"3-4": 1.2819461804671874, "4-5": 0.17841807061815018, "5-6": 0.5054669714081825, "3-6": 1.9658312224935202}

Farasan: Farasan Islands Trip [place_0033] (78.513); Farasan Snorkeling & Diving [place_0317] (78.273); Farasan Boat Tour [place_0034] (75.753); Farasan Island Archaeological Site [place_0313] (71.4679)

Unaizah: Al-Hajeb Parks [place_0048] (77.6391); Al-Musawkaf Market [place_0043] (77.5879); Uneyzah Mall [place_0055] (77.0449); Al-Bassam Heritage House [place_0046] (76.0724); Al-Aoshaziyah Lake [place_0053] (71.3991)

Buraydah: Al-Nakheel Mall Buraydah [place_0054] (79.4449); Garden of Al-Montazah [place_0060] (76.5591); Al-Uqailat Museum [place_0042] (75.778); Al-Bassr Garden Park [place_0056] (75.3591); King Khalid Wildlife Park [place_0047] (75.2391); Buraydah Water Tower [place_0050] (74.0207); Al-Jarad Heritage Market [place_0051] (72.3079); Al-Faiha Garden [place_0061] (72.2391)

Tabuk: Tabuk Park Mall [place_0068] (77.8849); Jabal Al-Lawz [place_0070] (77.3991); Prince Fahd bin Sultan Park [place_0076] (76.0791); Tabuk Regional Museum [place_0080] (75.418); King Abdulaziz Heritage Garden [place_0084] (75.3591); Boulevard Tabuk [place_0069] (75.262); Hegjaz Railway Station [place_0077] (74.698); Tabuk Castle [place_0072] (74.578)



**Canada**

Top 10: Unaizah > Farasan > Buraydah > Tabuk > Jazan > Abha > Al Makhwah > Najran > Al Baha > Baljurashi

Top 4: Unaizah, Farasan, Buraydah, Tabuk

Overlaps vs Basic: {"city": {"intersection": 4, "union": 4, "jaccard": 1.0, "only_first": [], "only_second": []}, "activity": {"intersection": 25, "union": 25, "jaccard": 1.0, "only_first": [], "only_second": []}}

Rank changes: {"Unaizah": {"basic": 1, "current": 1, "positions_gained": 0}, "Farasan": {"basic": 2, "current": 2, "positions_gained": 0}, "Buraydah": {"basic": 3, "current": 3, "positions_gained": 0}, "Tabuk": {"basic": 4, "current": 4, "positions_gained": 0}, "Jazan": {"basic": 5, "current": 5, "positions_gained": 0}, "Abha": {"basic": 6, "current": 6, "positions_gained": 0}, "Al Makhwah": {"basic": 7, "current": 7, "positions_gained": 0}, "Najran": {"basic": 8, "current": 8, "positions_gained": 0}, "Al Baha": {"basic": 9, "current": 9, "positions_gained": 0}, "Baljurashi": {"basic": 10, "current": 10, "positions_gained": 0}, "Al Kharj": {"basic": 11, "current": 11, "positions_gained": 0}, "Riyadh": {"basic": 12, "current": 12, "positions_gained": 0}}

Margins: {"3-4": 1.2650558287651137, "4-5": 0.6275279710895205, "5-6": 0.0866570120124237, "3-6": 1.979240811867058}

Unaizah: Al-Musawkaf Market [place_0043] (75.6713); Al-Hajeb Parks [place_0048] (75.2184); Al-Bassam Heritage House [place_0046] (74.3306); Uneyzah Mall [place_0055] (74.077); Al-Aoshaziyah Lake [place_0053] (68.9784)

Farasan: Farasan Islands Trip [place_0033] (75.1017); Farasan Snorkeling & Diving [place_0317] (74.8617); Farasan Boat Tour [place_0034] (72.3417); Farasan Island Archaeological Site [place_0313] (69.5513)

Buraydah: Al-Nakheel Mall Buraydah [place_0054] (76.477); Garden of Al-Montazah [place_0060] (74.1384); Al-Uqailat Museum [place_0042] (74.1118); Al-Bassr Garden Park [place_0056] (72.9384); King Khalid Wildlife Park [place_0047] (72.8184); Buraydah Water Tower [place_0050] (72.1419); Al-Jarad Heritage Market [place_0051] (70.3913); Al-Faiha Garden [place_0061] (69.8184)

Tabuk: Jabal Al-Lawz [place_0070] (74.9784); Tabuk Park Mall [place_0068] (74.917); Tabuk Regional Museum [place_0080] (73.7518); Prince Fahd bin Sultan Park [place_0076] (73.6584); Hegjaz Railway Station [place_0077] (73.0318); King Abdulaziz Heritage Garden [place_0084] (72.9384); Tabuk Castle [place_0072] (72.9118); Boulevard Tabuk [place_0069] (72.9074)



### WVS 50%

Country overlap: {"country_city_overlap": {"intersection": 4, "union": 4, "jaccard": 1.0, "only_first": [], "only_second": []}, "country_activity_overlap": {"intersection": 25, "union": 25, "jaccard": 1.0, "only_first": [], "only_second": []}}



**India**

Top 10: Farasan > Unaizah > Buraydah > Tabuk > Jazan > Abha > Al Baha > Al Makhwah > Najran > Baljurashi

Top 4: Farasan, Unaizah, Buraydah, Tabuk

Overlaps vs Basic: {"city": {"intersection": 4, "union": 4, "jaccard": 1.0, "only_first": [], "only_second": []}, "activity": {"intersection": 25, "union": 25, "jaccard": 1.0, "only_first": [], "only_second": []}}

Rank changes: {"Farasan": {"basic": 2, "current": 1, "positions_gained": 1}, "Unaizah": {"basic": 1, "current": 2, "positions_gained": -1}, "Buraydah": {"basic": 3, "current": 3, "positions_gained": 0}, "Tabuk": {"basic": 4, "current": 4, "positions_gained": 0}, "Jazan": {"basic": 5, "current": 5, "positions_gained": 0}, "Abha": {"basic": 6, "current": 6, "positions_gained": 0}, "Al Baha": {"basic": 9, "current": 7, "positions_gained": 2}, "Al Makhwah": {"basic": 7, "current": 8, "positions_gained": -1}, "Najran": {"basic": 8, "current": 9, "positions_gained": -1}, "Baljurashi": {"basic": 10, "current": 10, "positions_gained": 0}, "Al Kharj": {"basic": 11, "current": 11, "positions_gained": 0}, "Riyadh": {"basic": 12, "current": 12, "positions_gained": 0}}

Margins: {"3-4": 1.164932725583995, "4-5": 0.01364758827270407, "5-6": 0.44120871426021324, "3-6": 1.6197890281169123}

Farasan: Farasan Islands Trip [place_0033] (74.5913); Farasan Snorkeling & Diving [place_0317] (74.3913); Farasan Boat Tour [place_0034] (72.2913); Farasan Island Archaeological Site [place_0313] (68.0348)

Unaizah: Al-Hajeb Parks [place_0048] (73.7488); Uneyzah Mall [place_0055] (73.1561); Al-Musawkaf Market [place_0043] (73.1348); Al-Bassam Heritage House [place_0046] (71.7405); Al-Aoshaziyah Lake [place_0053] (68.5488)

Buraydah: Al-Nakheel Mall Buraydah [place_0054] (75.1561); Garden of Al-Montazah [place_0060] (72.8488); Al-Bassr Garden Park [place_0056] (71.8488); King Khalid Wildlife Park [place_0047] (71.7488); Al-Uqailat Museum [place_0042] (71.5225); Buraydah Water Tower [place_0050] (70.1758); Al-Faiha Garden [place_0061] (69.2488); Al-Jarad Heritage Market [place_0051] (68.7348)

Tabuk: Tabuk Park Mall [place_0068] (73.8561); Jabal Al-Lawz [place_0070] (73.5488); Prince Fahd bin Sultan Park [place_0076] (72.4488); King Abdulaziz Heritage Garden [place_0084] (71.8488); Boulevard Tabuk [place_0069] (71.4275); Tabuk Regional Museum [place_0080] (71.2225); Hegjaz Railway Station [place_0077] (70.6225); Tabuk Castle [place_0072] (70.5225)



**Canada**

Top 10: Unaizah > Buraydah > Farasan > Tabuk > Abha > Jazan > Al Makhwah > Al Baha > Najran > Baljurashi

Top 4: Unaizah, Buraydah, Farasan, Tabuk

Overlaps vs Basic: {"city": {"intersection": 4, "union": 4, "jaccard": 1.0, "only_first": [], "only_second": []}, "activity": {"intersection": 25, "union": 25, "jaccard": 1.0, "only_first": [], "only_second": []}}

Rank changes: {"Unaizah": {"basic": 1, "current": 1, "positions_gained": 0}, "Buraydah": {"basic": 3, "current": 2, "positions_gained": 1}, "Farasan": {"basic": 2, "current": 3, "positions_gained": -1}, "Tabuk": {"basic": 4, "current": 4, "positions_gained": 0}, "Abha": {"basic": 6, "current": 5, "positions_gained": 1}, "Jazan": {"basic": 5, "current": 6, "positions_gained": -1}, "Al Makhwah": {"basic": 7, "current": 7, "positions_gained": 0}, "Al Baha": {"basic": 9, "current": 8, "positions_gained": 1}, "Najran": {"basic": 8, "current": 9, "positions_gained": -1}, "Baljurashi": {"basic": 10, "current": 10, "positions_gained": 0}, "Al Kharj": {"basic": 11, "current": 11, "positions_gained": 0}, "Riyadh": {"basic": 12, "current": 12, "positions_gained": 0}}

Margins: {"3-4": 1.0933753824561165, "4-5": 0.4927312288774175, "5-6": 0.08230373498447818, "3-6": 1.6684103463180122}

Unaizah: Al-Musawkaf Market [place_0043] (70.7392); Al-Hajeb Parks [place_0048] (70.723); Al-Bassam Heritage House [place_0046] (69.5633); Uneyzah Mall [place_0055] (69.4462); Al-Aoshaziyah Lake [place_0053] (65.523)

Buraydah: Al-Nakheel Mall Buraydah [place_0054] (71.4462); Garden of Al-Montazah [place_0060] (69.823); Al-Uqailat Museum [place_0042] (69.4397); Al-Bassr Garden Park [place_0056] (68.823); King Khalid Wildlife Park [place_0047] (68.723); Buraydah Water Tower [place_0050] (67.8274); Al-Jarad Heritage Market [place_0051] (66.3392); Al-Faiha Garden [place_0061] (66.223)

Farasan: Farasan Islands Trip [place_0033] (70.3271); Farasan Snorkeling & Diving [place_0317] (70.1271); Farasan Boat Tour [place_0034] (68.0271); Farasan Island Archaeological Site [place_0313] (65.6392)

Tabuk: Jabal Al-Lawz [place_0070] (70.523); Tabuk Park Mall [place_0068] (70.1462); Prince Fahd bin Sultan Park [place_0076] (69.423); Tabuk Regional Museum [place_0080] (69.1397); King Abdulaziz Heritage Garden [place_0084] (68.823); Hegjaz Railway Station [place_0077] (68.5397); Boulevard Tabuk [place_0069] (68.4843); Tabuk Castle [place_0072] (68.4397)



## centered_relative_distinctiveness

{'first_shortlist_change_vs_basic': {'India': 10, 'Canada': 20}, 'first_country_shortlist_difference': 10}



### WVS 0%

Country overlap: {"country_city_overlap": {"intersection": 4, "union": 4, "jaccard": 1.0, "only_first": [], "only_second": []}, "country_activity_overlap": {"intersection": 25, "union": 25, "jaccard": 1.0, "only_first": [], "only_second": []}}



**India**

Top 10: Unaizah > Farasan > Buraydah > Tabuk > Jazan > Abha > Al Makhwah > Najran > Al Baha > Baljurashi

Top 4: Unaizah, Farasan, Buraydah, Tabuk

Overlaps vs Basic: {"city": {"intersection": 4, "union": 4, "jaccard": 1.0, "only_first": [], "only_second": []}, "activity": {"intersection": 25, "union": 25, "jaccard": 1.0, "only_first": [], "only_second": []}}

Rank changes: {"Unaizah": {"basic": 1, "current": 1, "positions_gained": 0}, "Farasan": {"basic": 2, "current": 2, "positions_gained": 0}, "Buraydah": {"basic": 3, "current": 3, "positions_gained": 0}, "Tabuk": {"basic": 4, "current": 4, "positions_gained": 0}, "Jazan": {"basic": 5, "current": 5, "positions_gained": 0}, "Abha": {"basic": 6, "current": 6, "positions_gained": 0}, "Al Makhwah": {"basic": 7, "current": 7, "positions_gained": 0}, "Najran": {"basic": 8, "current": 8, "positions_gained": 0}, "Al Baha": {"basic": 9, "current": 9, "positions_gained": 0}, "Baljurashi": {"basic": 10, "current": 10, "positions_gained": 0}, "Al Kharj": {"basic": 11, "current": 11, "positions_gained": 0}, "Riyadh": {"basic": 12, "current": 12, "positions_gained": 0}}

Margins: {"3-4": 1.75, "4-5": 0.8375000000000057, "5-6": 0.7625000000000028, "3-6": 3.3500000000000085}

Unaizah: Al-Musawkaf Market [place_0043] (95.4); Al-Bassam Heritage House [place_0046] (93.4); Al-Hajeb Parks [place_0048] (93.2); Uneyzah Mall [place_0055] (92.6); Al-Aoshaziyah Lake [place_0053] (82.8)

Farasan: Farasan Islands Trip [place_0033] (94.2); Farasan Snorkeling & Diving [place_0317] (93.8); Farasan Boat Tour [place_0034] (89.6); Farasan Island Archaeological Site [place_0313] (85.2)

Buraydah: Al-Nakheel Mall Buraydah [place_0054] (96.6); Al-Uqailat Museum [place_0042] (92.8); Garden of Al-Montazah [place_0060] (91.4); Buraydah Water Tower [place_0050] (89.4); Al-Bassr Garden Park [place_0056] (89.4); King Khalid Wildlife Park [place_0047] (89.2); Al-Jarad Heritage Market [place_0051] (86.6); Al-Faiha Garden [place_0061] (84.2)

Tabuk: Tabuk Park Mall [place_0068] (94.0); Jabal Al-Lawz [place_0070] (92.8); Tabuk Regional Museum [place_0080] (92.2); Hegjaz Railway Station [place_0077] (91.0); Tabuk Castle [place_0072] (90.8); Boulevard Tabuk [place_0069] (90.6); Prince Fahd bin Sultan Park [place_0076] (90.6); King Abdulaziz Heritage Garden [place_0084] (89.4)



**Canada**

Top 10: Unaizah > Farasan > Buraydah > Tabuk > Jazan > Abha > Al Makhwah > Najran > Al Baha > Baljurashi

Top 4: Unaizah, Farasan, Buraydah, Tabuk

Overlaps vs Basic: {"city": {"intersection": 4, "union": 4, "jaccard": 1.0, "only_first": [], "only_second": []}, "activity": {"intersection": 25, "union": 25, "jaccard": 1.0, "only_first": [], "only_second": []}}

Rank changes: {"Unaizah": {"basic": 1, "current": 1, "positions_gained": 0}, "Farasan": {"basic": 2, "current": 2, "positions_gained": 0}, "Buraydah": {"basic": 3, "current": 3, "positions_gained": 0}, "Tabuk": {"basic": 4, "current": 4, "positions_gained": 0}, "Jazan": {"basic": 5, "current": 5, "positions_gained": 0}, "Abha": {"basic": 6, "current": 6, "positions_gained": 0}, "Al Makhwah": {"basic": 7, "current": 7, "positions_gained": 0}, "Najran": {"basic": 8, "current": 8, "positions_gained": 0}, "Al Baha": {"basic": 9, "current": 9, "positions_gained": 0}, "Baljurashi": {"basic": 10, "current": 10, "positions_gained": 0}, "Al Kharj": {"basic": 11, "current": 11, "positions_gained": 0}, "Riyadh": {"basic": 12, "current": 12, "positions_gained": 0}}

Margins: {"3-4": 1.75, "4-5": 0.8375000000000057, "5-6": 0.7625000000000028, "3-6": 3.3500000000000085}

Unaizah: Al-Musawkaf Market [place_0043] (95.4); Al-Bassam Heritage House [place_0046] (93.4); Al-Hajeb Parks [place_0048] (93.2); Uneyzah Mall [place_0055] (92.6); Al-Aoshaziyah Lake [place_0053] (82.8)

Farasan: Farasan Islands Trip [place_0033] (94.2); Farasan Snorkeling & Diving [place_0317] (93.8); Farasan Boat Tour [place_0034] (89.6); Farasan Island Archaeological Site [place_0313] (85.2)

Buraydah: Al-Nakheel Mall Buraydah [place_0054] (96.6); Al-Uqailat Museum [place_0042] (92.8); Garden of Al-Montazah [place_0060] (91.4); Buraydah Water Tower [place_0050] (89.4); Al-Bassr Garden Park [place_0056] (89.4); King Khalid Wildlife Park [place_0047] (89.2); Al-Jarad Heritage Market [place_0051] (86.6); Al-Faiha Garden [place_0061] (84.2)

Tabuk: Tabuk Park Mall [place_0068] (94.0); Jabal Al-Lawz [place_0070] (92.8); Tabuk Regional Museum [place_0080] (92.2); Hegjaz Railway Station [place_0077] (91.0); Tabuk Castle [place_0072] (90.8); Boulevard Tabuk [place_0069] (90.6); Prince Fahd bin Sultan Park [place_0076] (90.6); King Abdulaziz Heritage Garden [place_0084] (89.4)



### WVS 10%

Country overlap: {"country_city_overlap": {"intersection": 3, "union": 5, "jaccard": 0.6, "only_first": ["Jazan"], "only_second": ["Tabuk"]}, "country_activity_overlap": {"intersection": 17, "union": 33, "jaccard": 0.5151515151515151, "only_first": ["place_0032", "place_0301", "place_0302", "place_0304", "place_0307", "place_0312", "place_0314", "place_0318"], "only_second": ["place_0068", "place_0069", "place_0070", "place_0072", "place_0076", "place_0077", "place_0080", "place_0084"]}}



**India**

Top 10: Farasan > Unaizah > Buraydah > Jazan > Tabuk > Abha > Al Baha > Al Makhwah > Najran > Baljurashi

Top 4: Farasan, Unaizah, Buraydah, Jazan

Overlaps vs Basic: {"city": {"intersection": 3, "union": 5, "jaccard": 0.6, "only_first": ["Tabuk"], "only_second": ["Jazan"]}, "activity": {"intersection": 17, "union": 33, "jaccard": 0.5151515151515151, "only_first": ["place_0068", "place_0069", "place_0070", "place_0072", "place_0076", "place_0077", "place_0080", "place_0084"], "only_second": ["place_0032", "place_0301", "place_0302", "place_0304", "place_0307", "place_0312", "place_0314", "place_0318"]}}

Rank changes: {"Farasan": {"basic": 2, "current": 1, "positions_gained": 1}, "Unaizah": {"basic": 1, "current": 2, "positions_gained": -1}, "Buraydah": {"basic": 3, "current": 3, "positions_gained": 0}, "Jazan": {"basic": 5, "current": 4, "positions_gained": 1}, "Tabuk": {"basic": 4, "current": 5, "positions_gained": -1}, "Abha": {"basic": 6, "current": 6, "positions_gained": 0}, "Al Baha": {"basic": 9, "current": 7, "positions_gained": 2}, "Al Makhwah": {"basic": 7, "current": 8, "positions_gained": -1}, "Najran": {"basic": 8, "current": 9, "positions_gained": -1}, "Baljurashi": {"basic": 10, "current": 10, "positions_gained": 0}, "Al Kharj": {"basic": 11, "current": 11, "positions_gained": 0}, "Riyadh": {"basic": 12, "current": 12, "positions_gained": 0}}

Margins: {"3-4": 2.0750775253724356, "4-5": 0.28584021315892016, "5-6": 0.544877638275338, "3-6": 2.9057953768066938}

Farasan: Farasan Islands Trip [place_0033] (93.4173); Farasan Snorkeling & Diving [place_0317] (93.0573); Farasan Boat Tour [place_0034] (89.2773); Farasan Island Archaeological Site [place_0313] (80.0896)

Unaizah: Al-Hajeb Parks [place_0048] (91.8057); Uneyzah Mall [place_0055] (90.3205); Al-Musawkaf Market [place_0043] (89.2696); Al-Bassam Heritage House [place_0046] (86.1349); Al-Aoshaziyah Lake [place_0053] (82.4457)

Buraydah: Al-Nakheel Mall Buraydah [place_0054] (93.9205); Garden of Al-Montazah [place_0060] (90.1857); Al-Bassr Garden Park [place_0056] (88.3857); King Khalid Wildlife Park [place_0047] (88.2057); Al-Uqailat Museum [place_0042] (85.8561); Buraydah Water Tower [place_0050] (84.0002); Al-Faiha Garden [place_0061] (83.7057); Al-Jarad Heritage Market [place_0051] (81.3496)

Jazan: Farasan Islands Marine Reserve [place_0301] (95.7573); Wadi Lajab Canyon [place_0304] (92.7057); Jazan Corniche & Beach [place_0302] (88.5573); Habalah Hanging Village Viewpoint [place_0307] (87.6657); Jazan Mall [place_0318] (86.5405); Jazan Season Entertainment Zone [place_0314] (85.6841); Jazan Corniche Walk [place_0032] (85.3173); Jazan Coffee Farm Experience [place_0312] (84.9002)



**Canada**

Top 10: Unaizah > Buraydah > Farasan > Tabuk > Abha > Jazan > Al Baha > Al Makhwah > Najran > Baljurashi

Top 4: Unaizah, Buraydah, Farasan, Tabuk

Overlaps vs Basic: {"city": {"intersection": 4, "union": 4, "jaccard": 1.0, "only_first": [], "only_second": []}, "activity": {"intersection": 25, "union": 25, "jaccard": 1.0, "only_first": [], "only_second": []}}

Rank changes: {"Unaizah": {"basic": 1, "current": 1, "positions_gained": 0}, "Buraydah": {"basic": 3, "current": 2, "positions_gained": 1}, "Farasan": {"basic": 2, "current": 3, "positions_gained": -1}, "Tabuk": {"basic": 4, "current": 4, "positions_gained": 0}, "Abha": {"basic": 6, "current": 5, "positions_gained": 1}, "Jazan": {"basic": 5, "current": 6, "positions_gained": -1}, "Al Baha": {"basic": 9, "current": 7, "positions_gained": 2}, "Al Makhwah": {"basic": 7, "current": 8, "positions_gained": -1}, "Najran": {"basic": 8, "current": 9, "positions_gained": -1}, "Baljurashi": {"basic": 10, "current": 10, "positions_gained": 0}, "Al Kharj": {"basic": 11, "current": 11, "positions_gained": 0}, "Riyadh": {"basic": 12, "current": 12, "positions_gained": 0}}

Margins: {"3-4": 2.2887195361819295, "4-5": 0.45079328363243576, "5-6": 0.813612993577749, "3-6": 3.553125813392114}

Unaizah: Al-Hajeb Parks [place_0048] (92.6761); Al-Musawkaf Market [place_0043] (91.1957); Al-Bassam Heritage House [place_0046] (88.2852); Uneyzah Mall [place_0055] (88.1815); Al-Aoshaziyah Lake [place_0053] (83.3161)

Buraydah: Al-Nakheel Mall Buraydah [place_0054] (91.7815); Garden of Al-Montazah [place_0060] (91.0561); Al-Bassr Garden Park [place_0056] (89.2561); King Khalid Wildlife Park [place_0047] (89.0761); Al-Uqailat Museum [place_0042] (88.3328); Buraydah Water Tower [place_0050] (86.0895); Al-Faiha Garden [place_0061] (84.5761); Al-Jarad Heritage Market [place_0051] (83.2757)

Farasan: Farasan Islands Trip [place_0033] (91.0918); Farasan Snorkeling & Diving [place_0317] (90.7318); Farasan Boat Tour [place_0034] (86.9518); Farasan Island Archaeological Site [place_0313] (82.0157)

Tabuk: Jabal Al-Lawz [place_0070] (92.3161); Prince Fahd bin Sultan Park [place_0076] (90.3361); Tabuk Park Mall [place_0068] (89.4415); King Abdulaziz Heritage Garden [place_0084] (89.2561); Tabuk Regional Museum [place_0080] (87.7928); Boulevard Tabuk [place_0069] (87.1633); Hegjaz Railway Station [place_0077] (86.7128); Tabuk Castle [place_0072] (86.5328)



### WVS 20%

Country overlap: {"country_city_overlap": {"intersection": 3, "union": 5, "jaccard": 0.6, "only_first": ["Jazan"], "only_second": ["Abha"]}, "country_activity_overlap": {"intersection": 17, "union": 30, "jaccard": 0.5666666666666667, "only_first": ["place_0032", "place_0301", "place_0302", "place_0304", "place_0305", "place_0307", "place_0318", "place_0319"], "only_second": ["act_0001", "place_0025", "place_0027", "place_0028", "place_0029"]}}



**India**

Top 10: Farasan > Unaizah > Buraydah > Jazan > Abha > Tabuk > Al Baha > Al Makhwah > Baljurashi > Najran

Top 4: Farasan, Unaizah, Buraydah, Jazan

Overlaps vs Basic: {"city": {"intersection": 3, "union": 5, "jaccard": 0.6, "only_first": ["Tabuk"], "only_second": ["Jazan"]}, "activity": {"intersection": 17, "union": 33, "jaccard": 0.5151515151515151, "only_first": ["place_0068", "place_0069", "place_0070", "place_0072", "place_0076", "place_0077", "place_0080", "place_0084"], "only_second": ["place_0032", "place_0301", "place_0302", "place_0304", "place_0305", "place_0307", "place_0318", "place_0319"]}}

Rank changes: {"Farasan": {"basic": 2, "current": 1, "positions_gained": 1}, "Unaizah": {"basic": 1, "current": 2, "positions_gained": -1}, "Buraydah": {"basic": 3, "current": 3, "positions_gained": 0}, "Jazan": {"basic": 5, "current": 4, "positions_gained": 1}, "Abha": {"basic": 6, "current": 5, "positions_gained": 1}, "Tabuk": {"basic": 4, "current": 6, "positions_gained": -2}, "Al Baha": {"basic": 9, "current": 7, "positions_gained": 2}, "Al Makhwah": {"basic": 7, "current": 8, "positions_gained": -1}, "Baljurashi": {"basic": 10, "current": 9, "positions_gained": 1}, "Najran": {"basic": 8, "current": 10, "positions_gained": -2}, "Al Kharj": {"basic": 11, "current": 11, "positions_gained": 0}, "Riyadh": {"basic": 12, "current": 12, "positions_gained": 0}}

Margins: {"3-4": 1.5626550507448513, "4-5": 0.8989357028684992, "5-6": 0.5102447234493326, "3-6": 2.971835477062683}

Farasan: Farasan Islands Trip [place_0033] (92.6347); Farasan Snorkeling & Diving [place_0317] (92.3147); Farasan Boat Tour [place_0034] (88.9547); Farasan Island Archaeological Site [place_0313] (74.9793)

Unaizah: Al-Hajeb Parks [place_0048] (90.4114); Uneyzah Mall [place_0055] (88.0411); Al-Musawkaf Market [place_0043] (83.1393); Al-Aoshaziyah Lake [place_0053] (82.0914); Al-Bassam Heritage House [place_0046] (78.8698)

Buraydah: Al-Nakheel Mall Buraydah [place_0054] (91.2411); Garden of Al-Montazah [place_0060] (88.9714); Al-Bassr Garden Park [place_0056] (87.3714); King Khalid Wildlife Park [place_0047] (87.2114); Al-Faiha Garden [place_0061] (83.2114); Al-Uqailat Museum [place_0042] (78.9122); Buraydah Water Tower [place_0050] (78.6005); Al-Jarad Heritage Market [place_0051] (76.0993)

Jazan: Farasan Islands Marine Reserve [place_0301] (94.7147); Wadi Lajab Canyon [place_0304] (91.2114); Jazan Corniche & Beach [place_0302] (88.3147); Habalah Hanging Village Viewpoint [place_0307] (86.7314); Jazan Corniche Walk [place_0032] (85.4347); Jazan Mall [place_0318] (84.6811); Red Sea Mall Jazan [place_0319] (82.6011); Jazan Mangrove Park [place_0305] (82.4114)



**Canada**

Top 10: Unaizah > Buraydah > Farasan > Abha > Tabuk > Jazan > Al Baha > Al Makhwah > Najran > Baljurashi

Top 4: Unaizah, Buraydah, Farasan, Abha

Overlaps vs Basic: {"city": {"intersection": 3, "union": 5, "jaccard": 0.6, "only_first": ["Tabuk"], "only_second": ["Abha"]}, "activity": {"intersection": 17, "union": 30, "jaccard": 0.5666666666666667, "only_first": ["place_0068", "place_0069", "place_0070", "place_0072", "place_0076", "place_0077", "place_0080", "place_0084"], "only_second": ["act_0001", "place_0025", "place_0027", "place_0028", "place_0029"]}}

Rank changes: {"Unaizah": {"basic": 1, "current": 1, "positions_gained": 0}, "Buraydah": {"basic": 3, "current": 2, "positions_gained": 1}, "Farasan": {"basic": 2, "current": 3, "positions_gained": -1}, "Abha": {"basic": 6, "current": 4, "positions_gained": 2}, "Tabuk": {"basic": 4, "current": 5, "positions_gained": -1}, "Jazan": {"basic": 5, "current": 6, "positions_gained": -1}, "Al Baha": {"basic": 9, "current": 7, "positions_gained": 2}, "Al Makhwah": {"basic": 7, "current": 8, "positions_gained": -1}, "Najran": {"basic": 8, "current": 9, "positions_gained": -1}, "Baljurashi": {"basic": 10, "current": 10, "positions_gained": 0}, "Al Kharj": {"basic": 11, "current": 11, "positions_gained": 0}, "Riyadh": {"basic": 12, "current": 12, "positions_gained": 0}}

Margins: {"3-4": 1.3790256396287361, "4-5": 0.6984134327351228, "5-6": 1.6913125544203922, "3-6": 3.768751626784251}

Unaizah: Al-Hajeb Parks [place_0048] (92.1522); Al-Musawkaf Market [place_0043] (86.9915); Al-Aoshaziyah Lake [place_0053] (83.8322); Uneyzah Mall [place_0055] (83.7629); Al-Bassam Heritage House [place_0046] (83.1704)

Buraydah: Garden of Al-Montazah [place_0060] (90.7122); Al-Bassr Garden Park [place_0056] (89.1122); King Khalid Wildlife Park [place_0047] (88.9522); Al-Nakheel Mall Buraydah [place_0054] (86.9629); Al-Faiha Garden [place_0061] (84.9522); Al-Uqailat Museum [place_0042] (83.8656); Buraydah Water Tower [place_0050] (82.7791); Al-Jarad Heritage Market [place_0051] (79.9515)

Farasan: Farasan Islands Trip [place_0033] (87.9836); Farasan Snorkeling & Diving [place_0317] (87.6636); Farasan Boat Tour [place_0034] (84.3036); Farasan Island Archaeological Site [place_0313] (78.8315)

Abha: Al Soudah Park [place_0025] (91.9922); Abha Cable Car Experience [place_0028] (86.0722); Abu Kheyal Park [place_0027] (84.7922); High City Walk [act_0001] (82.6067); Al Habala Village [place_0029] (71.1194)



### WVS 30%

Country overlap: {"country_city_overlap": {"intersection": 3, "union": 5, "jaccard": 0.6, "only_first": ["Jazan"], "only_second": ["Abha"]}, "country_activity_overlap": {"intersection": 17, "union": 30, "jaccard": 0.5666666666666667, "only_first": ["place_0032", "place_0301", "place_0302", "place_0304", "place_0305", "place_0307", "place_0318", "place_0319"], "only_second": ["act_0001", "place_0025", "place_0027", "place_0028", "place_0029"]}}



**India**

Top 10: Farasan > Unaizah > Buraydah > Jazan > Abha > Tabuk > Baljurashi > Al Baha > Al Makhwah > Najran

Top 4: Farasan, Unaizah, Buraydah, Jazan

Overlaps vs Basic: {"city": {"intersection": 3, "union": 5, "jaccard": 0.6, "only_first": ["Tabuk"], "only_second": ["Jazan"]}, "activity": {"intersection": 17, "union": 33, "jaccard": 0.5151515151515151, "only_first": ["place_0068", "place_0069", "place_0070", "place_0072", "place_0076", "place_0077", "place_0080", "place_0084"], "only_second": ["place_0032", "place_0301", "place_0302", "place_0304", "place_0305", "place_0307", "place_0318", "place_0319"]}}

Rank changes: {"Farasan": {"basic": 2, "current": 1, "positions_gained": 1}, "Unaizah": {"basic": 1, "current": 2, "positions_gained": -1}, "Buraydah": {"basic": 3, "current": 3, "positions_gained": 0}, "Jazan": {"basic": 5, "current": 4, "positions_gained": 1}, "Abha": {"basic": 6, "current": 5, "positions_gained": 1}, "Tabuk": {"basic": 4, "current": 6, "positions_gained": -2}, "Baljurashi": {"basic": 10, "current": 7, "positions_gained": 3}, "Al Baha": {"basic": 9, "current": 8, "positions_gained": 1}, "Al Makhwah": {"basic": 7, "current": 9, "positions_gained": -2}, "Najran": {"basic": 8, "current": 10, "positions_gained": -2}, "Al Kharj": {"basic": 11, "current": 11, "positions_gained": 0}, "Riyadh": {"basic": 12, "current": 12, "positions_gained": 0}}

Margins: {"3-4": 1.0502325761172813, "4-5": 0.9671535543027687, "5-6": 1.565367085173989, "3-6": 3.582753215594039}

Farasan: Farasan Islands Trip [place_0033] (91.852); Farasan Snorkeling & Diving [place_0317] (91.572); Farasan Boat Tour [place_0034] (88.632); Farasan Island Archaeological Site [place_0313] (69.8689)

Unaizah: Al-Hajeb Parks [place_0048] (89.0171); Uneyzah Mall [place_0055] (85.7616); Al-Aoshaziyah Lake [place_0053] (81.7371); Al-Musawkaf Market [place_0043] (77.0089); Al-Bassam Heritage House [place_0046] (71.6047)

Buraydah: Al-Nakheel Mall Buraydah [place_0054] (88.5616); Garden of Al-Montazah [place_0060] (87.7571); Al-Bassr Garden Park [place_0056] (86.3571); King Khalid Wildlife Park [place_0047] (86.2171); Al-Faiha Garden [place_0061] (82.7171); Buraydah Water Tower [place_0050] (73.2007); Al-Uqailat Museum [place_0042] (71.9683); Al-Jarad Heritage Market [place_0051] (70.8489)

Jazan: Farasan Islands Marine Reserve [place_0301] (93.672); Wadi Lajab Canyon [place_0304] (89.7171); Jazan Corniche & Beach [place_0302] (88.072); Habalah Hanging Village Viewpoint [place_0307] (85.7971); Jazan Corniche Walk [place_0032] (85.552); Jazan Mall [place_0318] (82.8216); Jazan Mangrove Park [place_0305] (82.0171); Red Sea Mall Jazan [place_0319] (81.0016)



**Canada**

Top 10: Buraydah > Unaizah > Farasan > Abha > Tabuk > Baljurashi > Al Baha > Jazan > Al Makhwah > Najran

Top 4: Buraydah, Unaizah, Farasan, Abha

Overlaps vs Basic: {"city": {"intersection": 3, "union": 5, "jaccard": 0.6, "only_first": ["Tabuk"], "only_second": ["Abha"]}, "activity": {"intersection": 17, "union": 30, "jaccard": 0.5666666666666667, "only_first": ["place_0068", "place_0069", "place_0070", "place_0072", "place_0076", "place_0077", "place_0080", "place_0084"], "only_second": ["act_0001", "place_0025", "place_0027", "place_0028", "place_0029"]}}

Rank changes: {"Buraydah": {"basic": 3, "current": 1, "positions_gained": 2}, "Unaizah": {"basic": 1, "current": 2, "positions_gained": -1}, "Farasan": {"basic": 2, "current": 3, "positions_gained": -1}, "Abha": {"basic": 6, "current": 4, "positions_gained": 2}, "Tabuk": {"basic": 4, "current": 5, "positions_gained": -1}, "Baljurashi": {"basic": 10, "current": 6, "positions_gained": 4}, "Al Baha": {"basic": 9, "current": 7, "positions_gained": 2}, "Jazan": {"basic": 5, "current": 8, "positions_gained": -3}, "Al Makhwah": {"basic": 7, "current": 9, "positions_gained": -2}, "Najran": {"basic": 8, "current": 10, "positions_gained": -2}, "Al Kharj": {"basic": 11, "current": 11, "positions_gained": 0}, "Riyadh": {"basic": 12, "current": 12, "positions_gained": 0}}

Margins: {"3-4": 0.018538459443107058, "4-5": 1.8476201491026814, "5-6": 1.3238472232796, "3-6": 3.1900058318253883}

Buraydah: Garden of Al-Montazah [place_0060] (90.3684); Al-Bassr Garden Park [place_0056] (88.9684); King Khalid Wildlife Park [place_0047] (88.8284); Al-Faiha Garden [place_0061] (85.3284); Al-Nakheel Mall Buraydah [place_0054] (82.1444); Buraydah Water Tower [place_0050] (79.4686); Al-Uqailat Museum [place_0042] (79.3985); Al-Jarad Heritage Market [place_0051] (76.6272)

Unaizah: Al-Hajeb Parks [place_0048] (91.6284); Al-Aoshaziyah Lake [place_0053] (84.3484); Al-Musawkaf Market [place_0043] (82.7872); Uneyzah Mall [place_0055] (79.3444); Al-Bassam Heritage House [place_0046] (78.0556)

Farasan: Farasan Islands Trip [place_0033] (84.8754); Farasan Snorkeling & Diving [place_0317] (84.5954); Farasan Boat Tour [place_0034] (81.6554); Farasan Island Archaeological Site [place_0313] (75.6472)

Abha: Al Soudah Park [place_0025] (91.4884); Abha Cable Car Experience [place_0028] (86.3084); Abu Kheyal Park [place_0027] (85.1884); High City Walk [act_0001] (79.31); Al Habala Village [place_0029] (66.0791)



### WVS 40%

Country overlap: {"country_city_overlap": {"intersection": 2, "union": 6, "jaccard": 0.3333333333333333, "only_first": ["Farasan", "Jazan"], "only_second": ["Abha", "Baljurashi"]}, "country_activity_overlap": {"intersection": 13, "union": 34, "jaccard": 0.38235294117647056, "only_first": ["place_0032", "place_0033", "place_0034", "place_0301", "place_0302", "place_0304", "place_0305", "place_0307", "place_0313", "place_0317", "place_0318", "place_0319"], "only_second": ["act_0001", "act_0012", "act_0019", "place_0025", "place_0027", "place_0028", "place_0029", "place_0295", "place_0296"]}}



**India**

Top 10: Farasan > Buraydah > Unaizah > Jazan > Abha > Baljurashi > Tabuk > Al Baha > Al Makhwah > Najran

Top 4: Farasan, Buraydah, Unaizah, Jazan

Overlaps vs Basic: {"city": {"intersection": 3, "union": 5, "jaccard": 0.6, "only_first": ["Tabuk"], "only_second": ["Jazan"]}, "activity": {"intersection": 17, "union": 33, "jaccard": 0.5151515151515151, "only_first": ["place_0068", "place_0069", "place_0070", "place_0072", "place_0076", "place_0077", "place_0080", "place_0084"], "only_second": ["place_0032", "place_0301", "place_0302", "place_0304", "place_0305", "place_0307", "place_0318", "place_0319"]}}

Rank changes: {"Farasan": {"basic": 2, "current": 1, "positions_gained": 1}, "Buraydah": {"basic": 3, "current": 2, "positions_gained": 1}, "Unaizah": {"basic": 1, "current": 3, "positions_gained": -2}, "Jazan": {"basic": 5, "current": 4, "positions_gained": 1}, "Abha": {"basic": 6, "current": 5, "positions_gained": 1}, "Baljurashi": {"basic": 10, "current": 6, "positions_gained": 4}, "Tabuk": {"basic": 4, "current": 7, "positions_gained": -3}, "Al Baha": {"basic": 9, "current": 8, "positions_gained": 1}, "Al Makhwah": {"basic": 7, "current": 9, "positions_gained": -2}, "Najran": {"basic": 8, "current": 10, "positions_gained": -2}, "Al Kharj": {"basic": 11, "current": 11, "positions_gained": 0}, "Riyadh": {"basic": 12, "current": 12, "positions_gained": 0}}

Margins: {"3-4": 0.12434902033170658, "4-5": 1.0353714057370382, "5-6": 0.008668258675726292, "3-6": 1.168388684744471}

Farasan: Farasan Islands Trip [place_0033] (91.0694); Farasan Snorkeling & Diving [place_0317] (90.8294); Farasan Boat Tour [place_0034] (88.3094); Farasan Island Archaeological Site [place_0313] (64.7586)

Buraydah: Garden of Al-Montazah [place_0060] (86.5428); Al-Nakheel Mall Buraydah [place_0054] (85.8822); Al-Bassr Garden Park [place_0056] (85.3428); King Khalid Wildlife Park [place_0047] (85.2228); Al-Faiha Garden [place_0061] (82.2228); Buraydah Water Tower [place_0050] (67.8009); Al-Jarad Heritage Market [place_0051] (65.5986); Al-Uqailat Museum [place_0042] (65.0244)

Unaizah: Al-Hajeb Parks [place_0048] (87.6228); Uneyzah Mall [place_0055] (83.4822); Al-Aoshaziyah Lake [place_0053] (81.3828); Al-Musawkaf Market [place_0043] (70.8786); Al-Bassam Heritage House [place_0046] (64.3397)

Jazan: Farasan Islands Marine Reserve [place_0301] (92.6294); Wadi Lajab Canyon [place_0304] (88.2228); Jazan Corniche & Beach [place_0302] (87.8294); Jazan Corniche Walk [place_0032] (85.6694); Habalah Hanging Village Viewpoint [place_0307] (84.8628); Jazan Mangrove Park [place_0305] (81.6228); Jazan Mall [place_0318] (80.9622); Red Sea Mall Jazan [place_0319] (79.4022)



**Canada**

Top 10: Buraydah > Unaizah > Abha > Baljurashi > Farasan > Tabuk > Al Baha > Al Makhwah > Jazan > Najran

Top 4: Buraydah, Unaizah, Abha, Baljurashi

Overlaps vs Basic: {"city": {"intersection": 2, "union": 6, "jaccard": 0.3333333333333333, "only_first": ["Farasan", "Tabuk"], "only_second": ["Abha", "Baljurashi"]}, "activity": {"intersection": 13, "union": 34, "jaccard": 0.38235294117647056, "only_first": ["place_0033", "place_0034", "place_0068", "place_0069", "place_0070", "place_0072", "place_0076", "place_0077", "place_0080", "place_0084", "place_0313", "place_0317"], "only_second": ["act_0001", "act_0012", "act_0019", "place_0025", "place_0027", "place_0028", "place_0029", "place_0295", "place_0296"]}}

Rank changes: {"Buraydah": {"basic": 3, "current": 1, "positions_gained": 2}, "Unaizah": {"basic": 1, "current": 2, "positions_gained": -1}, "Abha": {"basic": 6, "current": 3, "positions_gained": 3}, "Baljurashi": {"basic": 10, "current": 4, "positions_gained": 6}, "Farasan": {"basic": 2, "current": 5, "positions_gained": -3}, "Tabuk": {"basic": 4, "current": 6, "positions_gained": -2}, "Al Baha": {"basic": 9, "current": 7, "positions_gained": 2}, "Al Makhwah": {"basic": 7, "current": 8, "positions_gained": -1}, "Jazan": {"basic": 5, "current": 9, "positions_gained": -4}, "Najran": {"basic": 8, "current": 10, "positions_gained": -2}, "Al Kharj": {"basic": 11, "current": 11, "positions_gained": 0}, "Riyadh": {"basic": 12, "current": 12, "positions_gained": 0}}

Margins: {"3-4": 0.17862316317635418, "4-5": 1.1633255575661536, "5-6": 1.6548781447277179, "3-6": 2.9968268654702257}

Buraydah: Garden of Al-Montazah [place_0060] (90.0245); Al-Bassr Garden Park [place_0056] (88.8245); King Khalid Wildlife Park [place_0047] (88.7045); Al-Faiha Garden [place_0061] (85.7045); Al-Nakheel Mall Buraydah [place_0054] (77.3259); Buraydah Water Tower [place_0050] (76.1582); Al-Uqailat Museum [place_0042] (74.9313); Al-Jarad Heritage Market [place_0051] (73.303)

Unaizah: Al-Hajeb Parks [place_0048] (91.1045); Al-Aoshaziyah Lake [place_0053] (84.8645); Al-Musawkaf Market [place_0043] (78.583); Uneyzah Mall [place_0055] (74.9259); Al-Bassam Heritage House [place_0046] (72.9409)

Abha: Al Soudah Park [place_0025] (90.9845); Abha Cable Car Experience [place_0028] (86.5445); Abu Kheyal Park [place_0027] (85.5845); High City Walk [act_0001] (76.0133); Al Habala Village [place_0029] (61.0388)

Baljurashi: Sunset Mountain View Tour [act_0019] (81.3845); Baljurashi Mountain Drive [act_0012] (81.0245); Baljurashi Viewpoint [place_0296] (79.1045); Al Kharrarah Waterfall [place_0295] (77.9045)



### WVS 50%

Country overlap: {"country_city_overlap": {"intersection": 2, "union": 6, "jaccard": 0.3333333333333333, "only_first": ["Farasan", "Jazan"], "only_second": ["Abha", "Unaizah"]}, "country_activity_overlap": {"intersection": 12, "union": 34, "jaccard": 0.35294117647058826, "only_first": ["place_0032", "place_0033", "place_0034", "place_0301", "place_0302", "place_0304", "place_0305", "place_0307", "place_0313", "place_0317", "place_0318", "place_0319"], "only_second": ["act_0001", "place_0025", "place_0027", "place_0028", "place_0029", "place_0043", "place_0046", "place_0048", "place_0053", "place_0055"]}}



**India**

Top 10: Farasan > Baljurashi > Buraydah > Jazan > Unaizah > Abha > Al Baha > Tabuk > Al Makhwah > Najran

Top 4: Farasan, Baljurashi, Buraydah, Jazan

Overlaps vs Basic: {"city": {"intersection": 2, "union": 6, "jaccard": 0.3333333333333333, "only_first": ["Tabuk", "Unaizah"], "only_second": ["Baljurashi", "Jazan"]}, "activity": {"intersection": 12, "union": 37, "jaccard": 0.32432432432432434, "only_first": ["place_0043", "place_0046", "place_0048", "place_0053", "place_0055", "place_0068", "place_0069", "place_0070", "place_0072", "place_0076", "place_0077", "place_0080", "place_0084"], "only_second": ["act_0012", "act_0019", "place_0032", "place_0295", "place_0296", "place_0301", "place_0302", "place_0304", "place_0305", "place_0307", "place_0318", "place_0319"]}}

Rank changes: {"Farasan": {"basic": 2, "current": 1, "positions_gained": 1}, "Baljurashi": {"basic": 10, "current": 2, "positions_gained": 8}, "Buraydah": {"basic": 3, "current": 3, "positions_gained": 0}, "Jazan": {"basic": 5, "current": 4, "positions_gained": 1}, "Unaizah": {"basic": 1, "current": 5, "positions_gained": -4}, "Abha": {"basic": 6, "current": 6, "positions_gained": 0}, "Al Baha": {"basic": 9, "current": 7, "positions_gained": 2}, "Tabuk": {"basic": 4, "current": 8, "positions_gained": -4}, "Al Makhwah": {"basic": 7, "current": 9, "positions_gained": -2}, "Najran": {"basic": 8, "current": 10, "positions_gained": -2}, "Al Kharj": {"basic": 11, "current": 11, "positions_gained": 0}, "Riyadh": {"basic": 12, "current": 12, "positions_gained": 0}}

Margins: {"3-4": 0.025387626862141133, "4-5": 0.8739387245853436, "5-6": 0.2296505325859215, "3-6": 1.1289768840334062}

Farasan: Farasan Islands Trip [place_0033] (90.2867); Farasan Snorkeling & Diving [place_0317] (90.0867); Farasan Boat Tour [place_0034] (87.9867); Farasan Island Archaeological Site [place_0313] (59.6482)

Baljurashi: Sunset Mountain View Tour [act_0019] (78.1285); Baljurashi Mountain Drive [act_0012] (77.8285); Baljurashi Viewpoint [place_0296] (76.2285); Al Kharrarah Waterfall [place_0295] (75.2285)

Buraydah: Garden of Al-Montazah [place_0060] (85.3285); Al-Bassr Garden Park [place_0056] (84.3285); King Khalid Wildlife Park [place_0047] (84.2285); Al-Nakheel Mall Buraydah [place_0054] (83.2027); Al-Faiha Garden [place_0061] (81.7285); Buraydah Water Tower [place_0050] (62.4012); Al-Jarad Heritage Market [place_0051] (60.3482); Al-Uqailat Museum [place_0042] (58.0805)

Jazan: Farasan Islands Marine Reserve [place_0301] (91.5867); Jazan Corniche & Beach [place_0302] (87.5867); Wadi Lajab Canyon [place_0304] (86.7285); Jazan Corniche Walk [place_0032] (85.7867); Habalah Hanging Village Viewpoint [place_0307] (83.9285); Jazan Mangrove Park [place_0305] (81.2285); Jazan Mall [place_0318] (79.1027); Red Sea Mall Jazan [place_0319] (77.8027)



**Canada**

Top 10: Baljurashi > Buraydah > Abha > Unaizah > Farasan > Al Baha > Tabuk > Al Makhwah > Najran > Jazan

Top 4: Baljurashi, Buraydah, Abha, Unaizah

Overlaps vs Basic: {"city": {"intersection": 2, "union": 6, "jaccard": 0.3333333333333333, "only_first": ["Farasan", "Tabuk"], "only_second": ["Abha", "Baljurashi"]}, "activity": {"intersection": 13, "union": 34, "jaccard": 0.38235294117647056, "only_first": ["place_0033", "place_0034", "place_0068", "place_0069", "place_0070", "place_0072", "place_0076", "place_0077", "place_0080", "place_0084", "place_0313", "place_0317"], "only_second": ["act_0001", "act_0012", "act_0019", "place_0025", "place_0027", "place_0028", "place_0029", "place_0295", "place_0296"]}}

Rank changes: {"Baljurashi": {"basic": 10, "current": 1, "positions_gained": 9}, "Buraydah": {"basic": 3, "current": 2, "positions_gained": 1}, "Abha": {"basic": 6, "current": 3, "positions_gained": 3}, "Unaizah": {"basic": 1, "current": 4, "positions_gained": -3}, "Farasan": {"basic": 2, "current": 5, "positions_gained": -3}, "Al Baha": {"basic": 9, "current": 6, "positions_gained": 3}, "Tabuk": {"basic": 4, "current": 7, "positions_gained": -3}, "Al Makhwah": {"basic": 7, "current": 8, "positions_gained": -1}, "Najran": {"basic": 8, "current": 9, "positions_gained": -1}, "Jazan": {"basic": 5, "current": 10, "positions_gained": -5}, "Al Kharj": {"basic": 11, "current": 11, "positions_gained": 0}, "Riyadh": {"basic": 12, "current": 12, "positions_gained": 0}}

Margins: {"3-4": 0.6567300106081859, "4-5": 2.045705890319951, "5-6": 0.07859226216606885, "3-6": 2.7810281630942058}

Baljurashi: Sunset Mountain View Tour [act_0019] (82.4806); Baljurashi Mountain Drive [act_0012] (82.1806); Baljurashi Viewpoint [place_0296] (80.5806); Al Kharrarah Waterfall [place_0295] (79.5806)

Buraydah: Garden of Al-Montazah [place_0060] (89.6806); Al-Bassr Garden Park [place_0056] (88.6806); King Khalid Wildlife Park [place_0047] (88.5806); Al-Faiha Garden [place_0061] (86.0806); Buraydah Water Tower [place_0050] (72.8477); Al-Nakheel Mall Buraydah [place_0054] (72.5073); Al-Uqailat Museum [place_0042] (70.4641); Al-Jarad Heritage Market [place_0051] (69.9787)

Abha: Al Soudah Park [place_0025] (90.4806); Abha Cable Car Experience [place_0028] (86.7806); Abu Kheyal Park [place_0027] (85.9806); High City Walk [act_0001] (72.7166); Al Habala Village [place_0029] (55.9985)

Unaizah: Al-Hajeb Parks [place_0048] (90.5806); Al-Aoshaziyah Lake [place_0053] (85.3806); Al-Musawkaf Market [place_0043] (74.3787); Uneyzah Mall [place_0055] (70.5073); Al-Bassam Heritage House [place_0046] (67.8261)