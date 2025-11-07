"""Postal code name lookup for Danish postal codes.

This module provides a mapping from Danish postal codes to city names.
Data sourced from Danish postal code registry.
"""

# Comprehensive Danish postal code to city name mapping
# Format: postnummer -> by_navn
POSTAL_CODE_NAMES = {
    # Major cities
    1000: "København K", 1050: "København K", 1100: "København K",
    2000: "Frederiksberg", 2100: "København Ø", 2200: "København N",
    2300: "København S", 2400: "København NV", 2450: "København SV",
    2500: "Valby", 2600: "Glostrup", 2700: "Brønshøj", 2720: "Vanløse",
    2800: "Kgs. Lyngby", 2900: "Hellerup", 2920: "Charlottenlund",
    3000: "Helsingør", 3400: "Hillerød", 3500: "Værløse", 3600: "Frederikssund",
    3700: "Rønne", 4000: "Roskilde", 4100: "Ringsted", 4200: "Slagelse",
    4220: "Korsør", 4230: "Skælskør", 4241: "Vemmelev", 4242: "Boeslunde",
    4243: "Rude", 4244: "Agersø", 4245: "Omø", 4250: "Fuglebjerg",
    4261: "Dalmose", 4262: "Sandved", 4270: "Høng", 4281: "Gørlev",
    4291: "Ruds Vedby", 4293: "Dianalund", 4295: "Stenlille",
    4300: "Holbæk", 4320: "Lejre", 4330: "Hvalsø", 4340: "Tølløse",
    4350: "Ugerløse", 4360: "Kirke Eskilstrup", 4370: "Store Merløse",
    4390: "Vipperød", 4400: "Kalundborg", 4420: "Regstrup", 4440: "Mørkøv",
    4450: "Jyderup", 4460: "Snertinge", 4470: "Svebølle", 4480: "Store Fuglede",
    4490: "Jerslev Sjælland", 4500: "Nykøbing Sj", 4520: "Svinninge",
    4532: "Gislinge", 4534: "Hørve", 4540: "Fårevejle", 4550: "Asnæs",
    4560: "Vig", 4571: "Grevinge", 4572: "Nørre Asmindrup",
    4573: "Højby", 4581: "Rørvig", 4591: "Føllenslev", 4592: "Sejerø",
    4593: "Eskebjerg", 4600: "Køge", 4621: "Gadstrup", 4622: "Havdrup",
    4623: "Lille Skensved", 4632: "Bjæverskov", 4640: "Faxe",
    4652: "Hårlev", 4653: "Karise", 4654: "Faxe Ladeplads",
    4660: "Store Heddinge", 4671: "Strøby", 4672: "Klippinge",
    4673: "Rødvig Stevns", 4681: "Herfølge", 4682: "Tureby",
    4683: "Rønnede", 4684: "Holmegaard", 4690: "Haslev",
    4700: "Næstved", 4720: "Præstø", 4733: "Tappernøje",
    4735: "Mern", 4736: "Karrebæksminde", 4750: "Lundby",
    4760: "Vordingborg", 4771: "Kalvehave", 4772: "Langebæk",
    4773: "Stensved", 4780: "Stege", 4791: "Borre",
    4792: "Askeby", 4793: "Bogø By", 4800: "Nykøbing F",
    4840: "Nørre Alslev", 4850: "Stubbekøbing", 4862: "Guldborg",
    4863: "Eskilstrup", 4871: "Horbelev", 4872: "Idestrup",
    4873: "Væggerløse", 4874: "Gedser", 4880: "Nysted",
    4891: "Toreby L", 4892: "Kettinge", 4894: "Øster Ulslev",
    4895: "Errindlev", 4900: "Nakskov", 4912: "Harpelunde",
    4913: "Horslunde", 4920: "Søllested", 4930: "Maribo",
    4941: "Bandholm", 4943: "Torrig L", 4944: "Fejø",
    4945: "Femø", 4951: "Nørreballe", 4952: "Stokkemarke",
    4953: "Vesterborg", 4960: "Holeby", 4970: "Rødby",
    4983: "Dannemare", 4990: "Sakskøbing",

    5000: "Odense C", 5200: "Odense V", 5210: "Odense NV",
    5220: "Odense SØ", 5230: "Odense M", 5240: "Odense NØ",
    5250: "Odense SV", 5260: "Odense S", 5270: "Odense N",
    5290: "Marslev", 5300: "Kerteminde", 5320: "Agedrup",
    5330: "Munkebo", 5350: "Rynkeby", 5370: "Mesinge",
    5380: "Dalby", 5390: "Martofte", 5400: "Bogense",
    5450: "Otterup", 5462: "Morud", 5463: "Harndrup",
    5464: "Brenderup Fyn", 5466: "Asperup", 5471: "Søndersø",
    5474: "Veflinge", 5485: "Skamby", 5491: "Blommenslyst",
    5492: "Vissenbjerg", 5500: "Middelfart", 5540: "Ullerslev",
    5550: "Langeskov", 5560: "Aarup", 5580: "Nørre Aaby",
    5591: "Gelsted", 5592: "Ejby", 5600: "Faaborg",
    5602: "Bøjden", 5610: "Assens", 5620: "Glamsbjerg",
    5631: "Ebberup", 5642: "Millinge", 5672: "Broby",
    5683: "Haarby", 5690: "Tommerup", 5700: "Svendborg",
    5750: "Ringe", 5762: "Vester Skerninge", 5771: "Stenstrup",
    5772: "Kværndrup", 5792: "Årslev", 5800: "Nyborg",
    5853: "Ørbæk", 5854: "Gislev", 5856: "Ryslinge",
    5863: "Ferritslev Fyn", 5871: "Frørup", 5874: "Hesselager",
    5881: "Skårup Fyn", 5882: "Vejstrup", 5883: "Oure",
    5884: "Gudme", 5892: "Gudbjerg Sydfyn", 5900: "Rudkøbing",
    5932: "Humble", 5935: "Bagenkop", 5953: "Tranekær",
    5960: "Marstal", 5970: "Ærøskøbing", 5985: "Søby Ærø",

    6000: "Kolding", 6040: "Egtved", 6051: "Almind",
    6052: "Viuf", 6064: "Jordrup", 6070: "Christiansfeld",
    6091: "Bjert", 6092: "Sønder Stenderup", 6093: "Sjølund",
    6094: "Hejls", 6100: "Haderslev", 6200: "Aabenraa",
    6230: "Rødekro", 6240: "Løgumkloster", 6261: "Bredebro",
    6270: "Tønder", 6280: "Højer", 6300: "Gråsten",
    6310: "Broager", 6320: "Egernsund", 6330: "Padborg",
    6340: "Kruså", 6360: "Tinglev", 6372: "Bylderup-Bov",
    6392: "Bolderslev", 6400: "Sønderborg", 6430: "Nordborg",
    6440: "Augustenborg", 6470: "Sydals", 6500: "Vojens",
    6510: "Gram", 6520: "Toftlund", 6534: "Agerskov",
    6535: "Branderup J", 6541: "Bevtoft", 6560: "Sommersted",
    6580: "Vamdrup", 6600: "Vejen", 6621: "Gesten",
    6622: "Bække", 6623: "Vorbasse", 6630: "Rødding",
    6640: "Lunderskov", 6650: "Brørup", 6660: "Lintrup",
    6670: "Holsted", 6682: "Hovborg", 6683: "Føvling",
    6690: "Gørding", 6700: "Esbjerg", 6701: "Esbjerg",
    6705: "Esbjerg Ø", 6710: "Esbjerg V", 6715: "Esbjerg N",
    6720: "Fanø", 6731: "Tjæreborg", 6740: "Bramming",
    6752: "Glejbjerg", 6753: "Agerbæk", 6760: "Ribe",
    6771: "Gredstedbro", 6780: "Skærbæk", 6792: "Rømø",
    6800: "Varde", 6818: "Årre", 6823: "Ansager",
    6830: "Nørre Nebel", 6840: "Oksbøl", 6851: "Janderup Vestj",
    6852: "Billum", 6853: "Vejers Strand", 6854: "Henne",
    6855: "Outrup", 6857: "Blåvand", 6862: "Tistrup",
    6870: "Ølgod", 6880: "Tarm", 6893: "Hemmet",
    6900: "Skjern", 6920: "Videbæk", 6933: "Kibæk",
    6940: "Lem St", 6950: "Ringkøbing", 6960: "Hvide Sande",
    6971: "Spjald", 6973: "Ørnhøj", 6980: "Tim",
    6990: "Ulfborg",

    7000: "Fredericia", 7080: "Børkop", 7100: "Vejle",
    7120: "Vejle Øst", 7130: "Juelsminde", 7140: "Stouby",
    7150: "Barrit", 7160: "Tørring", 7171: "Uldum",
    7173: "Vonge", 7182: "Bredsten", 7183: "Randbøl",
    7184: "Vandel", 7190: "Billund", 7200: "Grindsted",
    7250: "Hejnsvig", 7260: "Sønder Omme", 7270: "Stakroge",
    7280: "Sønder Felding", 7300: "Jelling", 7321: "Gadbjerg",
    7323: "Give", 7330: "Brande", 7361: "Ejstrupholm",
    7362: "Hampen", 7400: "Herning", 7430: "Ikast",
    7441: "Bording", 7442: "Engesvang", 7451: "Sunds",
    7470: "Karup J", 7480: "Vildbjerg", 7490: "Aulum",
    7500: "Holstebro", 7540: "Haderup", 7550: "Sørvad",
    7560: "Hjerm", 7570: "Vemb", 7600: "Struer",
    7620: "Lemvig", 7650: "Bøvlingbjerg", 7660: "Bækmarksbro",
    7673: "Harboøre", 7680: "Thyborøn", 7700: "Thisted",
    7730: "Hanstholm", 7741: "Frøstrup", 7742: "Vesløs",
    7752: "Snedsted", 7755: "Bedsted Thy", 7760: "Hurup Thy",
    7770: "Vestervig", 7790: "Thyholm", 7800: "Skive",
    7830: "Vinderup", 7840: "Højslev", 7850: "Stoholm Jyll",
    7860: "Spøttrup", 7870: "Roslev", 7884: "Fur",
    7900: "Nykøbing M", 7950: "Erslev", 7960: "Karby",
    7970: "Redsted M", 7980: "Vils", 7990: "Øster Assels",

    8000: "Aarhus C", 8100: "Aarhus C", 8200: "Aarhus N",
    8210: "Aarhus V", 8220: "Brabrand", 8230: "Åbyhøj",
    8240: "Risskov", 8250: "Egå", 8260: "Viby J",
    8270: "Højbjerg", 8300: "Odder", 8305: "Samsø",
    8310: "Tranbjerg J", 8320: "Mårslet", 8330: "Beder",
    8340: "Malling", 8350: "Hundslund", 8355: "Solbjerg",
    8361: "Hasselager", 8362: "Hørning", 8370: "Hadsten",
    8380: "Trige", 8381: "Tilst", 8382: "Hinnerup",
    8400: "Ebeltoft", 8410: "Rønde", 8420: "Knebel",
    8444: "Balle", 8450: "Hammel", 8462: "Harlev J",
    8464: "Galten", 8471: "Sabro", 8472: "Sporup",
    8500: "Grenaa", 8520: "Lystrup", 8530: "Hjortshøj",
    8541: "Skødstrup", 8543: "Hornslet", 8544: "Mørke",
    8550: "Ryomgård", 8560: "Kolind", 8570: "Trustrup",
    8581: "Nimtofte", 8585: "Glesborg", 8586: "Ørum Djurs",
    8592: "Anholt", 8600: "Silkeborg", 8620: "Kjellerup",
    8632: "Lemming", 8641: "Sorring", 8643: "Ans By",
    8653: "Them", 8654: "Bryrup", 8660: "Skanderborg",
    8670: "Låsby", 8680: "Ry", 8700: "Horsens",
    8721: "Daugård", 8722: "Hedensted", 8723: "Løsning",
    8732: "Hovedgård", 8740: "Brædstrup", 8751: "Gedved",
    8752: "Østbirk", 8762: "Flemming", 8765: "Klovborg",
    8766: "Nørre Snede", 8781: "Stenderup", 8783: "Hornsyld",
    8789: "Endelave", 8799: "Tunø", 8800: "Viborg",
    8830: "Tjele", 8840: "Rødkærsbro", 8850: "Bjerringbro",
    8860: "Ulstrup", 8870: "Langå", 8881: "Thorsø",
    8882: "Fårvang", 8883: "Gjern", 8900: "Randers",
    8920: "Randers NV", 8930: "Randers NØ", 8940: "Randers SV",
    8950: "Ørsted", 8960: "Randers SØ", 8961: "Allingåbro",
    8963: "Auning", 8970: "Havndal", 8981: "Spentrup",
    8983: "Gjerlev J", 8990: "Fårup",

    9000: "Aalborg", 9200: "Aalborg SV", 9210: "Aalborg SØ",
    9220: "Aalborg Øst", 9230: "Svenstrup J", 9240: "Nibe",
    9260: "Gistrup", 9270: "Klarup", 9280: "Storvorde",
    9293: "Kongerslev", 9300: "Sæby", 9310: "Vodskov",
    9320: "Hjallerup", 9330: "Dronninglund", 9340: "Asaa",
    9352: "Dybvad", 9362: "Gandrup", 9370: "Hals",
    9380: "Vestbjerg", 9381: "Sulsted", 9382: "Tylstrup",
    9400: "Nørresundby", 9430: "Vadum", 9440: "Aabybro",
    9460: "Brovst", 9480: "Løkken", 9490: "Pandrup",
    9492: "Blokhus", 9493: "Saltum", 9500: "Hobro",
    9510: "Arden", 9520: "Skørping", 9530: "Støvring",
    9541: "Suldrup", 9550: "Mariager", 9560: "Hadsund",
    9574: "Bælum", 9575: "Terndrup", 9600: "Aars",
    9610: "Nørager", 9620: "Aalestrup", 9631: "Gedsted",
    9632: "Møldrup", 9640: "Farsø", 9670: "Løgstør",
    9681: "Ranum", 9690: "Fjerritslev", 9700: "Brønderslev",
    9740: "Jerslev J", 9750: "Østervrå", 9760: "Vrå",
    9800: "Hjørring", 9830: "Tårs", 9850: "Hirtshals",
    9870: "Sindal", 9881: "Bindslev", 9900: "Frederikshavn",
    9940: "Læsø", 9970: "Strandby", 9981: "Jerup",
    9990: "Skagen",
}


def get_postal_code_name(postal_code):
    """Get city name for a postal code.

    Args:
        postal_code: Integer postal code (e.g., 9500)

    Returns:
        str: Formatted postal code with name (e.g., "9500 Hobro")
             or just the postal code if name not found
    """
    try:
        postal_code = int(postal_code)
        if postal_code in POSTAL_CODE_NAMES:
            return f"{postal_code} {POSTAL_CODE_NAMES[postal_code]}"
        else:
            return str(postal_code)
    except (ValueError, TypeError):
        return str(postal_code)


def format_postal_code_with_name(postal_code):
    """Format postal code with city name for display in reports.

    This is an alias for get_postal_code_name() for clarity.

    Args:
        postal_code: Integer postal code

    Returns:
        str: Formatted string like "2920 Charlottenlund"
    """
    return get_postal_code_name(postal_code)
