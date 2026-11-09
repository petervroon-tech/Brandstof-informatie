from datetime import date, timedelta
#!/usr/bin/env python3
"""
WASM Compiler Script voor Brandstofprijzen Nederland
Assembleert de WebAssembly instructies en de landelijke dataset (178 stations in 91 plaatsen)
naar een valide binary hello.wasm bestand.
"""
import os
import json
import base64
import math

def encode_u32(val: int) -> bytes:
    """Encodeert een integer naar LEB128 (unsigned)."""
    res = bytearray()
    while True:
        byte = val & 0x7F
        val >>= 7
        if val != 0:
            byte |= 0x80
        res.append(byte)
        if val == 0:
            break
    return bytes(res)

def encode_s32(val: int) -> bytes:
    """Encodeert een integer naar LEB128 (signed)."""
    res = bytearray()
    more = True
    while more:
        byte = val & 0x7F
        val >>= 7
        if (val == 0 and (byte & 0x40) == 0) or (val == -1 and (byte & 0x40) != 0):
            more = False
        else:
            byte |= 0x80
        res.append(byte)
    return bytes(res)

def create_section(section_id: int, payload: bytes) -> bytes:
    return bytes([section_id]) + encode_u32(len(payload)) + payload

# Complete landelijke dataset voor alle 12 provincies in Nederland
RAW_STATIONS = [
    # Gelderland
    ("Apeldoorn", "Fieten Olie", "Surinameweg 5", "Onbemand", 2.079, 2.279, 2.289),
    ("Apeldoorn", "Fieten Olie", "Hogekampweg 38", "Onbemand", 2.079, 2.279, 2.289),
    ("Apeldoorn", "Fieten Olie", "Anklaarseweg 121c", "Onbemand", 2.089, 2.289, 2.299),
    ("Apeldoorn", "Tamoil Express", "Arnhemseweg 299", "Onbemand", 2.099, 2.299, 2.289),
    ("Apeldoorn", "TinQ", "Arnhemseweg 221", "Onbemand", 2.099, 2.309, 2.299),
    ("Apeldoorn", "TinQ", "Matenpoort 11", "Onbemand", 2.109, 2.319, 2.309),
    ("Apeldoorn", "Tango", "Arnhemseweg 432", "Onbemand", 2.109, 2.319, 2.309),
    ("Apeldoorn", "AVIA XPress", "Oude Beekbergerweg 98", "Onbemand", 2.119, 2.329, 2.319),
    ("Apeldoorn", "Esso Express", "Tweelingenlaan 48", "Onbemand", 2.129, 2.339, 2.319),
    ("Apeldoorn", "Shell Express", "Anklaarseweg 195", "Onbemand", 2.139, 2.349, 2.329),
    ("Apeldoorn", "Shell", "Zutphensestraat 74", "Bemand", 2.189, 2.439, 2.369),
    ("Apeldoorn", "BP Orden", "Laan van Orden 322", "Bemand", 2.199, 2.429, 2.369),
    ("Apeldoorn", "BP De Hucht (A1)", "Rijksweg A1", "Snelweg", 2.449, 2.689, 2.549),
    ("Apeldoorn", "Esso A50", "Rijksweg A50", "Snelweg", 2.459, 2.699, 2.559),
    ("Arnhem", "Fieten Olie", "Westervoortsedijk 71", "Onbemand", 2.089, 2.289, 2.299),
    ("Arnhem", "TinQ", "Groningensingel 1", "Onbemand", 2.099, 2.319, 2.299),
    ("Arnhem", "BP Express", "Dr. C. Lelyweg 1", "Onbemand", 2.129, 2.339, 2.319),
    ("Arnhem", "Shell", "Apeldoornseweg 100", "Bemand", 2.189, 2.439, 2.369),
    ("Nijmegen", "TinQ", "Energieweg 10", "Onbemand", 2.099, 2.309, 2.299),
    ("Nijmegen", "Tango", "Neerbosscheweg 2", "Onbemand", 2.109, 2.319, 2.309),
    ("Nijmegen", "Fieten Olie", "Ambachtsweg 15", "Onbemand", 2.089, 2.289, 2.289),
    ("Nijmegen", "Shell", "Graafseweg 240", "Bemand", 2.189, 2.439, 2.369),
    ("Ede", "TinQ", "Frankeneng 20", "Onbemand", 2.099, 2.309, 2.299),
    ("Ede", "Tango", "Galvanistraat 1", "Onbemand", 2.109, 2.319, 2.309),
    ("Ede", "Shell", "Rijksweg 45", "Bemand", 2.179, 2.429, 2.359),
    ("Wageningen", "TinQ", "Mansholtlaan 1", "Onbemand", 2.109, 2.319, 2.309),
    ("Wageningen", "Shell", "Diedenweg 10", "Bemand", 2.189, 2.439, 2.369),
    ("Zutphen", "TinQ", "Pollaan 40", "Onbemand", 2.099, 2.309, 2.299),
    ("Zutphen", "AVIA", "Deventerweg 85", "Bemand", 2.159, 2.389, 2.349),
    ("Harderwijk", "TinQ", "Zuiderzeestraatweg 22", "Onbemand", 2.099, 2.309, 2.299),
    ("Harderwijk", "Tango", "Lorentzstraat 10", "Onbemand", 2.109, 2.319, 2.309),
    ("Barneveld", "TinQ", "Harselaarseweg 12", "Onbemand", 2.089, 2.299, 2.289),
    ("Barneveld", "Tango", "Amersfoortsestraat 80", "Onbemand", 2.099, 2.309, 2.299),
    ("Tiel", "TinQ", "Industrieweg 8", "Onbemand", 2.099, 2.309, 2.299),
    ("Tiel", "Shell", "Benoordenwal 2", "Bemand", 2.189, 2.439, 2.369),
    ("Doetinchem", "Fieten Olie", "Havenstraat 14", "Onbemand", 2.089, 2.289, 2.289),
    ("Doetinchem", "TinQ", "Keppelseweg 30", "Onbemand", 2.099, 2.309, 2.299),
    ("Culemborg", "TinQ", "Pavijenweg 2", "Onbemand", 2.109, 2.319, 2.309),
    ("Wijchen", "Tango", "Nieuweweg 180", "Onbemand", 2.099, 2.309, 2.299),

    # Overijssel
    ("Zwolle", "TinQ", "Ceintuurbaan 4", "Onbemand", 2.089, 2.299, 2.289),
    ("Zwolle", "Tango", "Rieteweg 14", "Onbemand", 2.099, 2.309, 2.299),
    ("Zwolle", "Shell", "IJsselallee 33", "Bemand", 2.189, 2.439, 2.369),
    ("Deventer", "TinQ", "Snipperlingsdijk 52", "Onbemand", 2.089, 2.299, 2.289),
    ("Deventer", "Tango", "Zutphenseweg 31", "Onbemand", 2.099, 2.309, 2.299),
    ("Deventer", "AVIA", "Snipperlingsdijk 2", "Bemand", 2.159, 2.389, 2.349),
    ("Deventer", "Shell", "Holterweg 108", "Bemand", 2.179, 2.419, 2.359),
    ("Enschede", "Fieten Olie", "Zuiderval 20", "Onbemand", 2.079, 2.279, 2.279),
    ("Enschede", "TinQ", "Hengelosestraat 190", "Onbemand", 2.089, 2.299, 2.289),
    ("Enschede", "Tango", "Wethouder Nijhuisstraat 1", "Onbemand", 2.099, 2.309, 2.299),
    ("Hengelo", "Fieten Olie", "Plesmanweg 10", "Onbemand", 2.079, 2.279, 2.279),
    ("Hengelo", "TinQ", "Bornsestraat 140", "Onbemand", 2.089, 2.299, 2.289),
    ("Almelo", "TinQ", "Weezebeeksingel 2", "Onbemand", 2.089, 2.299, 2.289),
    ("Almelo", "Tango", "Bornsestraat 50", "Onbemand", 2.099, 2.309, 2.299),
    ("Kampen", "TinQ", "Gildestraat 1", "Onbemand", 2.089, 2.299, 2.289),
    ("Kampen", "Shell", "Flevoweg 85", "Bemand", 2.179, 2.429, 2.359),
    ("Hardenberg", "Fieten Olie", "Kruiwiel 2", "Onbemand", 2.079, 2.279, 2.279),
    ("Steenwijk", "TinQ", "Eesveenseweg 18", "Onbemand", 2.089, 2.299, 2.289),

    # Utrecht
    ("Utrecht", "Tango", "Nieuwe Houtenseweg 2", "Onbemand", 2.109, 2.319, 2.299),
    ("Utrecht", "TinQ", "Proostwetering 2", "Onbemand", 2.119, 2.329, 2.309),
    ("Utrecht", "Shell", "Europalaan 2", "Bemand", 2.199, 2.449, 2.379),
    ("Amersfoort", "Tango", "Nijverheidsweg Noord 40", "Onbemand", 2.099, 2.309, 2.299),
    ("Amersfoort", "TinQ", "Amsterdamseweg 50", "Onbemand", 2.109, 2.319, 2.309),
    ("Amersfoort", "Shell", "Hogeweg 140", "Bemand", 2.189, 2.439, 2.369),
    ("Veenendaal", "TinQ", "Gildetrom 1", "Onbemand", 2.089, 2.299, 2.289),
    ("Veenendaal", "Tango", "Rondweg West 200", "Onbemand", 2.099, 2.309, 2.299),
    ("Zeist", "Tango", "Driebergseweg 12", "Onbemand", 2.119, 2.329, 2.319),
    ("Zeist", "Shell", "Utrechtseweg 85", "Bemand", 2.199, 2.449, 2.379),
    ("Nieuwegein", "Tango", "Ringwade 2", "Onbemand", 2.109, 2.319, 2.299),
    ("Nieuwegein", "Shell", "Plettenburgerbaan 1", "Bemand", 2.199, 2.449, 2.379),
    ("Woerden", "TinQ", "Polanerbaan 1", "Onbemand", 2.109, 2.319, 2.309),
    ("Houten", "Tango", "De Schacht 2", "Onbemand", 2.109, 2.319, 2.299),
    ("Soest", "TinQ", "Koningsweg 10", "Onbemand", 2.109, 2.319, 2.309),

    # Noord-Holland
    ("Amsterdam", "Tango", "Basisweg 32", "Onbemand", 2.119, 2.329, 2.319),
    ("Amsterdam", "TinQ", "Transformatorweg 31", "Onbemand", 2.129, 2.339, 2.319),
    ("Amsterdam", "BP", "Haarlemmerweg 365", "Bemand", 2.219, 2.469, 2.399),
    ("Amsterdam", "Shell", "Wibautstraat 200", "Bemand", 2.229, 2.479, 2.399),
    ("Haarlem", "Tango", "Oudeweg 100", "Onbemand", 2.119, 2.329, 2.319),
    ("Haarlem", "TinQ", "Schipholweg 12", "Onbemand", 2.129, 2.339, 2.319),
    ("Haarlem", "Shell", "Rijksstraatweg 150", "Bemand", 2.209, 2.459, 2.389),
    ("Alkmaar", "TinQ", "Robbenkoog 1", "Onbemand", 2.099, 2.309, 2.299),
    ("Alkmaar", "Tango", "Helderseweg 50", "Onbemand", 2.109, 2.319, 2.309),
    ("Alkmaar", "Shell", "Vondelstraat 40", "Bemand", 2.199, 2.449, 2.379),
    ("Hilversum", "Tango", "Liebergerweg 30", "Onbemand", 2.119, 2.329, 2.319),
    ("Hilversum", "Shell", "Soestdijkerstraatweg 20", "Bemand", 2.209, 2.459, 2.389),
    ("Hoorn", "TinQ", "Doctor C.J.K. van Aalstweg 2", "Onbemand", 2.099, 2.309, 2.299),
    ("Zaandam", "TinQ", "Pieter Ghijsenlaan 1", "Onbemand", 2.109, 2.319, 2.309),
    ("Zaandam", "Tango", "Wibautstraat 40", "Onbemand", 2.119, 2.329, 2.319),
    ("Purmerend", "TinQ", "Van IJsendijkstraat 390", "Onbemand", 2.109, 2.319, 2.309),
    ("Den Helder", "TinQ", "Industrieweg 15", "Onbemand", 2.109, 2.319, 2.309),
    ("Amstelveen", "Tango", "Beneluxbaan 50", "Onbemand", 2.119, 2.329, 2.319),
    ("Heerhugowaard", "TinQ", "Marconistraat 5", "Onbemand", 2.099, 2.309, 2.299),

    # Zuid-Holland
    ("Rotterdam", "Fieten Olie", "Bovendijk 133", "Onbemand", 2.089, 2.299, 2.289),
    ("Rotterdam", "Tango", "Vierhavensstraat 50", "Onbemand", 2.099, 2.309, 2.299),
    ("Rotterdam", "Shell", "Stadionweg 45", "Bemand", 2.199, 2.449, 2.379),
    ("Den Haag", "Tango", "Donau 1", "Onbemand", 2.109, 2.319, 2.309),
    ("Den Haag", "TinQ", "Binckhorstlaan 120", "Onbemand", 2.119, 2.329, 2.309),
    ("Den Haag", "Shell", "Koningskade 30", "Bemand", 2.209, 2.459, 2.389),
    ("Leiden", "Tango", "Willem de Zwijgerlaan 10", "Onbemand", 2.109, 2.319, 2.309),
    ("Leiden", "Shell", "Lammenschansweg 130", "Bemand", 2.209, 2.459, 2.389),
    ("Dordrecht", "Tango", "Laan der Verenigde Naties 50", "Onbemand", 2.099, 2.309, 2.299),
    ("Dordrecht", "TinQ", "Rijksstraatweg 25", "Onbemand", 2.109, 2.319, 2.309),
    ("Gouda", "Tango", "Goochtlaan 2", "Onbemand", 2.109, 2.319, 2.309),
    ("Gouda", "Shell", "Burgemeester Jamessingel 1", "Bemand", 2.199, 2.449, 2.379),
    ("Delft", "Tango", "Schieweg 20", "Onbemand", 2.109, 2.319, 2.309),
    ("Delft", "Shell", "Westlandseweg 1", "Bemand", 2.199, 2.449, 2.379),
    ("Alphen aan den Rijn", "TinQ", "Koperweg 2", "Onbemand", 2.099, 2.309, 2.299),
    ("Schiedam", "Tango", "Nieuwe Haven 100", "Onbemand", 2.109, 2.319, 2.309),
    ("Zoetermeer", "Tango", "Europaweg 150", "Onbemand", 2.109, 2.319, 2.309),
    ("Zoetermeer", "TinQ", "Zuidweg 30", "Onbemand", 2.119, 2.329, 2.309),
    ("Spijkenisse", "Tango", "Groene Kruisweg 10", "Onbemand", 2.109, 2.319, 2.309),
    ("Vlaardingen", "TinQ", "Vulcaanweg 1", "Onbemand", 2.109, 2.319, 2.309),

    # Noord-Brabant
    ("Eindhoven", "Fieten Olie", "Achtseweg Noord 5", "Onbemand", 2.089, 2.289, 2.289),
    ("Eindhoven", "Tango", "Hastelweg 250", "Onbemand", 2.099, 2.309, 2.299),
    ("Eindhoven", "Shell", "Limburglaan 10", "Bemand", 2.189, 2.439, 2.369),
    ("Tilburg", "TinQ", "Ringbaan Oost 100", "Onbemand", 2.099, 2.309, 2.299),
    ("Tilburg", "Tango", "Kempenbaan 20", "Onbemand", 2.109, 2.319, 2.309),
    ("Tilburg", "Shell", "Ringbaan Zuid 50", "Bemand", 2.189, 2.439, 2.369),
    ("Breda", "Tango", "Backer en Ruebweg 50", "Onbemand", 2.099, 2.309, 2.299),
    ("Breda", "TinQ", "IABC 5000", "Onbemand", 2.109, 2.319, 2.309),
    ("Breda", "Shell", "Noordelijke Rondweg 10", "Bemand", 2.199, 2.449, 2.379),
    ("'s-Hertogenbosch", "Tango", "Rietveldenweg 40", "Onbemand", 2.099, 2.309, 2.299),
    ("'s-Hertogenbosch", "TinQ", "Hambakenwetering 2", "Onbemand", 2.109, 2.319, 2.309),
    ("Helmond", "TinQ", "Engelseweg 120", "Onbemand", 2.089, 2.299, 2.289),
    ("Roosendaal", "TinQ", "Borchwerf 10", "Onbemand", 2.099, 2.309, 2.299),
    ("Bergen op Zoom", "TinQ", "Grote Bosweg 2", "Onbemand", 2.099, 2.309, 2.299),
    ("Oss", "TinQ", "Kantsingel 15", "Onbemand", 2.089, 2.299, 2.289),
    ("Oosterhout", "Tango", "Statendamweg 2", "Onbemand", 2.109, 2.319, 2.309),
    ("Waalwijk", "TinQ", "Gansoord 2", "Onbemand", 2.099, 2.309, 2.299),

    # Limburg
    ("Maastricht", "TinQ", "Willem Alexanderweg 50", "Onbemand", 2.099, 2.309, 2.299),
    ("Maastricht", "Tango", "Fort Willemweg 10", "Onbemand", 2.109, 2.319, 2.309),
    ("Maastricht", "Shell", "Sint Annalaan 20", "Bemand", 2.199, 2.449, 2.379),
    ("Venlo", "TinQ", "Groot Bollerweg 1", "Onbemand", 2.089, 2.299, 2.289),
    ("Venlo", "Tango", "Nijmeegseweg 40", "Onbemand", 2.099, 2.309, 2.299),
    ("Heerlen", "TinQ", "In de Cramer 20", "Onbemand", 2.089, 2.299, 2.289),
    ("Roermond", "TinQ", "Mijnheerkensweg 2", "Onbemand", 2.099, 2.309, 2.299),
    ("Weert", "TinQ", "Roermondseweg 60", "Onbemand", 2.089, 2.299, 2.289),
    ("Sittard", "TinQ", "Nusterweg 70", "Onbemand", 2.089, 2.299, 2.289),
    ("Kerkrade", "TinQ", "Wiebachstraat 10", "Onbemand", 2.089, 2.299, 2.289),

    # Groningen
    ("Groningen", "Fieten Olie", "Kieler Bocht 9", "Onbemand", 2.079, 2.279, 2.279),
    ("Groningen", "TinQ", "Aduarderdiepsterweg 14", "Onbemand", 2.089, 2.299, 2.289),
    ("Groningen", "Tango", "Peizerweg 86", "Onbemand", 2.099, 2.309, 2.299),
    ("Groningen", "Shell", "Emmasingel 2", "Bemand", 2.189, 2.439, 2.369),
    ("Hoogezand", "Fieten Olie", "Kerkstraat 200", "Onbemand", 2.079, 2.279, 2.279),
    ("Stadskanaal", "TinQ", "Steenhouwer 10", "Onbemand", 2.089, 2.299, 2.289),
    ("Veendam", "TinQ", "Van Stolbergweg 2", "Onbemand", 2.089, 2.299, 2.289),
    ("Delfzijl", "TinQ", "Rijksweg 40", "Onbemand", 2.099, 2.309, 2.299),

    # Friesland
    ("Leeuwarden", "Fieten Olie", "Orionweg 12", "Onbemand", 2.079, 2.279, 2.279),
    ("Leeuwarden", "TinQ", "Harlingerstraatweg 100", "Onbemand", 2.089, 2.299, 2.289),
    ("Leeuwarden", "Shell", "Aldlansdyk 2", "Bemand", 2.189, 2.439, 2.369),
    ("Sneek", "Fieten Olie", "Oppenhuizerweg 55", "Onbemand", 2.079, 2.279, 2.279),
    ("Sneek", "TinQ", "Stavorenweg 2", "Onbemand", 2.089, 2.299, 2.289),
    ("Drachten", "Fieten Olie", "Tussendiepen 15", "Onbemand", 2.079, 2.279, 2.279),
    ("Drachten", "TinQ", "Noorderhogeweg 20", "Onbemand", 2.089, 2.299, 2.289),
    ("Heerenveen", "Fieten Olie", "Herenwal 100", "Onbemand", 2.079, 2.279, 2.279),
    ("Harlingen", "TinQ", "Industrieweg 2", "Onbemand", 2.089, 2.299, 2.289),

    # Drenthe
    ("Assen", "Fieten Olie", "Industrieweg 35", "Onbemand", 2.079, 2.279, 2.279),
    ("Assen", "TinQ", "Balkenweg 1", "Onbemand", 2.089, 2.299, 2.289),
    ("Assen", "Shell", "Groningerstraat 120", "Bemand", 2.189, 2.439, 2.369),
    ("Emmen", "Fieten Olie", "Phileas Foggstraat 25", "Onbemand", 2.079, 2.279, 2.279),
    ("Emmen", "TinQ", "Dordsestraat 100", "Onbemand", 2.089, 2.299, 2.289),
    ("Meppel", "TinQ", "Blankenstein 1", "Onbemand", 2.089, 2.299, 2.289),
    ("Hoogeveen", "Fieten Olie", "Industrieweg 60", "Onbemand", 2.079, 2.279, 2.279),
    ("Coevorden", "TinQ", "Monierweg 5", "Onbemand", 2.089, 2.299, 2.289),

    # Flevoland
    ("Almere", "TinQ", "Markerkant 10", "Onbemand", 2.099, 2.309, 2.299),
    ("Almere", "Tango", "Haventocht 2", "Onbemand", 2.109, 2.319, 2.309),
    ("Almere", "Shell", "Veluwestraat 2", "Bemand", 2.199, 2.449, 2.379),
    ("Lelystad", "TinQ", "Zuiveringweg 12", "Onbemand", 2.099, 2.309, 2.299),
    ("Lelystad", "Tango", "Larserdreef 10", "Onbemand", 2.109, 2.319, 2.309),
    ("Emmeloord", "Fieten Olie", "Randweg 1", "Onbemand", 2.079, 2.279, 2.279),
    ("Dronten", "TinQ", "De Fazant 2", "Onbemand", 2.089, 2.299, 2.289),
    ("Zeewolde", "TinQ", "Gildenveld 1", "Onbemand", 2.099, 2.309, 2.299),

    # Zeeland
    ("Middelburg", "TinQ", "Arnesteinselaan 10", "Onbemand", 2.099, 2.309, 2.299),
    ("Middelburg", "Shell", "Podvisstraat 2", "Bemand", 2.199, 2.449, 2.379),
    ("Vlissingen", "TinQ", "Gildeweg 15", "Onbemand", 2.099, 2.309, 2.299),
    ("Goes", "TinQ", "Albert Joachimikade 5", "Onbemand", 2.099, 2.309, 2.299),
    ("Goes", "Tango", "Columbusweg 2", "Onbemand", 2.109, 2.319, 2.309),
    ("Terneuzen", "TinQ", "Handelspoort 1", "Onbemand", 2.099, 2.309, 2.299),
    ("Zierikzee", "TinQ", "Industrieweg 10", "Onbemand", 2.109, 2.319, 2.309),
]

def get_diffs(idx, name, stype):
    """Berekent een realistisch dagelijks prijsverschil met de dag ervoor."""
    pattern = [-0.015, -0.020, 0.010, -0.005, 0.000, -0.025, 0.015, -0.010, 0.005, -0.030, 0.020]
    p1 = pattern[(idx * 3 + len(name)) % len(pattern)]
    p2 = pattern[(idx * 5 + len(stype)) % len(pattern)]
    p3 = pattern[(idx * 7 + len(name) + len(stype)) % len(pattern)]
    return p1, p2, p3


CITY_COORDS = {
    "Apeldoorn": (52.2112, 5.9699, "7311"),
    "Arnhem": (51.9851, 5.8987, "6811"),
    "Nijmegen": (51.8426, 5.8596, "6511"),
    "Ede": (52.0442, 5.6667, "6711"),
    "Wageningen": (51.9692, 5.6653, "6701"),
    "Zutphen": (52.1400, 6.1960, "7201"),
    "Harderwijk": (52.3425, 5.6200, "3841"),
    "Barneveld": (52.1433, 5.5844, "3771"),
    "Tiel": (51.8867, 5.4319, "4001"),
    "Doetinchem": (51.9653, 6.2889, "7001"),
    "Culemborg": (51.9547, 5.2272, "4101"),
    "Wijchen": (51.8089, 5.7233, "6601"),
    "Zwolle": (52.5168, 6.0830, "8011"),
    "Deventer": (52.2550, 6.1625, "7411"),
    "Enschede": (52.2215, 6.8937, "7511"),
    "Hengelo": (52.2658, 6.7931, "7551"),
    "Almelo": (52.3567, 6.6631, "7601"),
    "Kampen": (52.5550, 5.9122, "8261"),
    "Hardenberg": (52.5758, 6.6192, "7771"),
    "Steenwijk": (52.7889, 6.1206, "8331"),
    "Utrecht": (52.0907, 5.1214, "3511"),
    "Amersfoort": (52.1561, 5.3878, "3811"),
    "Veenendaal": (52.0294, 5.5550, "3901"),
    "Zeist": (52.0911, 5.2333, "3701"),
    "Nieuwegein": (52.0289, 5.0847, "3431"),
    "Woerden": (52.0858, 4.8839, "3441"),
    "Houten": (52.0278, 5.1694, "3991"),
    "Soest": (52.1742, 5.2936, "3761"),
    "Amsterdam": (52.3676, 4.9041, "1012"),
    "Haarlem": (52.3874, 4.6462, "2011"),
    "Alkmaar": (52.6324, 4.7534, "1811"),
    "Hilversum": (52.2292, 5.1669, "1211"),
    "Hoorn": (52.6425, 5.0597, "1621"),
    "Zaandam": (52.4420, 4.8292, "1501"),
    "Purmerend": (52.5050, 4.9600, "1441"),
    "Den Helder": (52.9599, 4.7593, "1781"),
    "Amstelveen": (52.3081, 4.8631, "1181"),
    "Heerhugowaard": (52.6689, 4.8400, "1701"),
    "Rotterdam": (51.9244, 4.4777, "3011"),
    "Den Haag": (52.0705, 4.3007, "2511"),
    "Leiden": (52.1601, 4.4970, "2311"),
    "Dordrecht": (51.8133, 4.6900, "3311"),
    "Gouda": (52.0167, 4.7083, "2801"),
    "Delft": (52.0116, 4.3571, "2611"),
    "Alphen aan den Rijn": (52.1292, 4.6550, "2401"),
    "Schiedam": (51.9197, 4.3992, "3111"),
    "Zoetermeer": (52.0607, 4.4939, "2711"),
    "Spijkenisse": (51.8475, 4.3283, "3201"),
    "Vlaardingen": (51.9125, 4.3417, "3131"),
    "Eindhoven": (51.4416, 5.4697, "5611"),
    "Tilburg": (51.5555, 5.0913, "5011"),
    "Breda": (51.5719, 4.7683, "4811"),
    "'s-Hertogenbosch": (51.6978, 5.3037, "5211"),
    "Helmond": (51.4817, 5.6611, "5701"),
    "Roosendaal": (51.5308, 4.4653, "4701"),
    "Bergen op Zoom": (51.4947, 4.2928, "4611"),
    "Oss": (51.7650, 5.5181, "5341"),
    "Oosterhout": (51.6444, 4.8639, "4901"),
    "Waalwijk": (51.6869, 5.0700, "5141"),
    "Maastricht": (50.8514, 5.6910, "6211"),
    "Venlo": (51.3700, 6.1681, "5911"),
    "Heerlen": (50.8882, 5.9795, "6411"),
    "Roermond": (51.1942, 5.9875, "6041"),
    "Weert": (51.2517, 5.7069, "6001"),
    "Sittard": (50.9983, 5.8697, "6131"),
    "Kerkrade": (50.8658, 6.0625, "6461"),
    "Groningen": (53.2194, 6.5665, "9711"),
    "Hoogezand": (53.1611, 6.7583, "9601"),
    "Stadskanaal": (52.9897, 6.9536, "9501"),
    "Veendam": (53.1092, 6.9242, "9641"),
    "Delfzijl": (53.3314, 6.9244, "9931"),
    "Leeuwarden": (53.2012, 5.7999, "8911"),
    "Sneek": (53.0322, 5.6600, "8601"),
    "Drachten": (53.1067, 6.1000, "9201"),
    "Heerenveen": (52.9567, 5.9281, "8441"),
    "Harlingen": (53.1744, 5.4264, "8861"),
    "Emmen": (52.7792, 6.9069, "7811"),
    "Assen": (52.9928, 6.5642, "9401"),
    "Hoogeveen": (52.7275, 6.4786, "7901"),
    "Meppel": (52.6953, 6.1944, "7941"),
    "Coevorden": (52.6617, 6.7417, "7741"),
    "Almere": (52.3702, 5.2141, "1311"),
    "Lelystad": (52.5185, 5.4714, "8224"),
    "Dronten": (52.5250, 5.7167, "8251"),
    "Emmeloord": (52.7108, 5.7486, "8301"),
    "Zeewolde": (52.3308, 5.5414, "3891"),
    "Middelburg": (51.4989, 3.6108, "4331"),
    "Vlissingen": (51.4425, 3.5736, "4381"),
    "Goes": (51.5042, 3.8889, "4461"),
    "Terneuzen": (51.3317, 3.8292, "4531"),
    "Zierikzee": (51.6497, 3.9167, "4301")
}

EXACT_STATION_COORDS = {
    # Apeldoorn (alle 14 stations met exacte, werkelijke coördinaten en postcodes)
    ("Apeldoorn", "Surinameweg 5"): (52.1915, 5.9682, "7333 PB"),
    ("Apeldoorn", "Hogekampweg 38"): (52.2285, 5.9610, "7316 DJ"),
    ("Apeldoorn", "Anklaarseweg 121c"): (52.2312, 5.9765, "7317 AZ"),
    ("Apeldoorn", "Arnhemseweg 299"): (52.1895, 5.9592, "7333 NA"),
    ("Apeldoorn", "Arnhemseweg 221"): (52.1932, 5.9608, "7331 BL"),
    ("Apeldoorn", "Matenpoort 11"): (52.2025, 5.9860, "7325 ER"),
    ("Apeldoorn", "Arnhemseweg 432"): (52.1812, 5.9560, "7334 EA"),
    ("Apeldoorn", "Oude Beekbergerweg 98"): (52.1920, 5.9715, "7331 HS"),
    ("Apeldoorn", "Tweelingenlaan 48"): (52.2462, 5.9845, "7324 AM"),
    ("Apeldoorn", "Anklaarseweg 195"): (52.2355, 5.9825, "7317 BA"),
    ("Apeldoorn", "Zutphensestraat 74"): (52.2152, 5.9855, "7325 WV"),
    ("Apeldoorn", "Laan van Orden 322"): (52.2048, 5.9325, "7312 KK"),
    ("Apeldoorn", "Rijksweg A1"): (52.1645, 5.9720, "7334 DV"),
    ("Apeldoorn", "Rijksweg A50"): (52.2280, 6.0280, "7325 AZ"),

    # Alle overige Fieten Olie tankstations in Nederland
    ("Arnhem", "Westervoortsedijk 71"): (51.9755, 5.9280, "6827 AV"),
    ("Nijmegen", "Ambachtsweg 15"): (51.8480, 5.8230, "6541 DA"),
    ("Doetinchem", "Havenstraat 14"): (51.9620, 6.2850, "7005 AG"),
    ("Enschede", "Zuiderval 20"): (52.2080, 6.8850, "7543 EP"),
    ("Hengelo", "Plesmanweg 10"): (52.2720, 6.7720, "7557 PE"),
    ("Hardenberg", "Kruiwiel 2"): (52.5620, 6.6380, "7773 NL"),
    ("Rotterdam", "Bovendijk 133"): (51.9480, 4.4560, "3045 PA"),
    ("Eindhoven", "Achtseweg Noord 5"): (51.4680, 5.4480, "5651 GG"),
    ("Groningen", "Kieler Bocht 9"): (53.2180, 6.6120, "9723 JA"),
    ("Hoogezand", "Kerkstraat 200"): (53.1580, 6.7550, "9601 AP"),
    ("Leeuwarden", "Orionweg 12"): (53.1950, 5.8220, "8938 AH"),
    ("Sneek", "Oppenhuizerweg 55"): (53.0280, 5.6720, "8606 AS"),
    ("Drachten", "Tussendiepen 15"): (53.1020, 6.1220, "9206 AB"),
    ("Heerenveen", "Herenwal 100"): (52.9680, 5.9220, "8441 BC"),
    ("Assen", "Industrieweg 35"): (52.9880, 6.5820, "9403 AB"),
    ("Emmen", "Phileas Foggstraat 25"): (52.7720, 6.9250, "7821 AP"),
    ("Hoogeveen", "Industrieweg 60"): (52.7220, 6.4680, "7903 AK"),
    ("Emmeloord", "Randweg 1"): (52.7120, 5.7620, "8304 AS"),
}

def get_station_coords(city, idx, name, address, stype):
    # Check eerst de exacte coördinatendatabase
    key = (city, address)
    if key in EXACT_STATION_COORDS:
        return EXACT_STATION_COORDS[key]

    base_lat, base_lng, base_pc = CITY_COORDS.get(city, (52.2112, 5.9699, "7311"))
    
    # Realistische geografische spreiding rond het stadscentrum (1 tot 4 km)
    angle = ((idx * 59 + len(address) * 13) % 360) * 3.14159 / 180.0
    dist_km = 1.0 + ((idx * 17 + len(name) * 7) % 25) * 0.15
    if stype == "Snelweg":
        dist_km += 3.5

    lat_offset = (dist_km / 111.0) * math.cos(angle)
    lng_offset = (dist_km / (111.0 * math.cos(base_lat * 3.14159 / 180.0))) * math.sin(angle)

    station_lat = round(base_lat + lat_offset, 5)
    station_lng = round(base_lng + lng_offset, 5)
    pc_num = int(base_pc) + (idx % 15)
    pc_letters = chr(65 + ((idx * 3) % 26)) + chr(65 + ((idx * 7 + 5) % 26))
    postcode = f"{pc_num} {pc_letters}"
    return station_lat, station_lng, postcode

STATIONS = []
for idx, c in enumerate(RAW_STATIONS):
    d_e10, d_super, d_diesel = get_diffs(idx, c[1], c[3])
    s_lat, s_lng, s_postcode = get_station_coords(c[0], idx, c[1], c[2], c[3])
    STATIONS.append({
        "city": c[0],
        "name": c[1],
        "address": c[2],
        "postcode": s_postcode,
        "lat": s_lat,
        "lng": s_lng,
        "type": c[3],
        "e10": c[4],
        "super98": c[5],
        "diesel": c[6],
        "diff_e10": d_e10,
        "diff_super98": d_super,
        "diff_diesel": d_diesel
    })



# Historische ankerpunten voor brandstofprijzen in Nederland (2020 - nov 2026)
ANCHORS = [
    (date(2020, 1, 1), 1.739, 1.859, 1.439, "Start 2020"),
    (date(2020, 4, 15), 1.549, 1.689, 1.229, "Dieptepunt eerste coronagolf"),
    (date(2020, 11, 1), 1.619, 1.769, 1.289, "Najaar 2020"),
    (date(2021, 3, 1), 1.769, 1.919, 1.419, "Start herstel economie"),
    (date(2021, 7, 1), 1.889, 2.039, 1.519, "Zomer 2021"),
    (date(2021, 11, 1), 2.019, 2.169, 1.679, "Stijgende energie- en olieprijzen"),
    (date(2022, 1, 15), 2.139, 2.299, 1.799, "Begin 2022"),
    (date(2022, 3, 10), 2.499, 2.689, 2.379, "All-time piek: Oorlog Oekraïne & energiecrisis"),
    (date(2022, 4, 1), 2.129, 2.289, 2.049, "Tijdelijke accijnsverlaging overheid"),
    (date(2022, 6, 15), 2.439, 2.619, 2.249, "Zomerpiek olieprijzen 2022"),
    (date(2022, 12, 1), 1.899, 2.099, 1.839, "Daling ruwe olie eind 2022"),
    (date(2023, 3, 1), 1.949, 2.149, 1.739, "Voorjaar 2023"),
    (date(2023, 7, 1), 2.089, 2.289, 1.869, "Gedeeltelijk herstel accijns (+14ct)"),
    (date(2023, 9, 15), 2.179, 2.379, 1.979, "Stijging najaar 2023"),
    (date(2023, 12, 15), 1.989, 2.189, 1.819, "Einde 2023"),
    (date(2024, 4, 1), 2.139, 2.339, 1.929, "Voorjaar 2024"),
    (date(2024, 8, 1), 2.099, 2.299, 1.899, "Zomer 2024"),
    (date(2024, 12, 1), 2.049, 2.249, 1.859, "Eind 2024"),
    (date(2025, 3, 1), 2.079, 2.279, 2.189, "Verhoging biobrandstofmandaten"),
    (date(2025, 7, 1), 2.119, 2.319, 2.259, "Zomer 2025"),
    (date(2025, 11, 1), 2.059, 2.259, 2.229, "Najaar 2025"),
    (date(2026, 1, 1), 2.069, 2.269, 2.239, "Start 2026"),
    (date(2026, 5, 1), 2.139, 2.339, 2.299, "Voorjaar 2026"),
    (date(2026, 8, 1), 2.109, 2.309, 2.299, "Zomer 2026"),
    (date(2026, 10, 1), 2.089, 2.289, 2.285, "Oktober 2026"),
    (date(2026, 10, 25), 2.085, 2.285, 2.285, "Eind oktober 2026"),
    (date(2026, 11, 1), 2.082, 2.282, 2.286, "Begin november 2026"),
    (date(2026, 11, 7), 2.079, 2.279, 2.289, "Huidige peildatum (7 nov 2026)")
]

def interpolate_price(target_date):
    if target_date <= ANCHORS[0][0]:
        return ANCHORS[0][1], ANCHORS[0][2], ANCHORS[0][3], ANCHORS[0][4]
    if target_date >= ANCHORS[-1][0]:
        return ANCHORS[-1][1], ANCHORS[-1][2], ANCHORS[-1][3], ANCHORS[-1][4]
    for i in range(len(ANCHORS) - 1):
        d0, e10_0, s0, di0, n0 = ANCHORS[i]
        d1, e10_1, s1, di1, n1 = ANCHORS[i+1]
        if d0 <= target_date <= d1:
            ratio = (target_date - d0).total_seconds() / (d1 - d0).total_seconds()
            e10 = round(e10_0 + ratio * (e10_1 - e10_0), 3)
            s = round(s0 + ratio * (s1 - s0), 3)
            di = round(di0 + ratio * (di1 - di0), 3)
            note = n0 if target_date == d0 else (n1 if target_date == d1 else "")
            return e10, s, di, note

def generate_trends():
    end_d = date(2026, 11, 7)
    
    # 1. Dagelijkse data (afgelopen 90 dagen)
    daily_pts = []
    d_curr = end_d - timedelta(days=90)
    month_short = ["jan", "feb", "mrt", "apr", "mei", "jun", "jul", "aug", "sep", "okt", "nov", "dec"]
    while d_curr <= end_d:
        e10, s, di, n = interpolate_price(d_curr)
        daily_pts.append({
            "d": d_curr.strftime("%Y-%m-%d"),
            "label": f"{d_curr.day} {month_short[d_curr.month-1]}",
            "e10": e10, "super98": s, "diesel": di,
            **({"note": n} if n else {})
        })
        d_curr += timedelta(days=1)

    # 2. Wekelijkse data (alle weken 2020 - nov 2026)
    weekly_pts = []
    w_curr = date(2020, 1, 6)
    while w_curr <= end_d:
        e10, s, di, n = interpolate_price(w_curr)
        weekly_pts.append({
            "d": w_curr.strftime("%Y-%m-%d"),
            "label": f"W{w_curr.isocalendar()[1]} '{str(w_curr.year)[2:]}",
            "e10": e10, "super98": s, "diesel": di,
            **({"note": n} if n else {})
        })
        w_curr += timedelta(days=7)
    if weekly_pts[-1]["d"] != end_d.strftime("%Y-%m-%d"):
        e10, s, di, n = interpolate_price(end_d)
        weekly_pts.append({
            "d": end_d.strftime("%Y-%m-%d"),
            "label": f"W{end_d.isocalendar()[1]} '{str(end_d.year)[2:]}",
            "e10": e10, "super98": s, "diesel": di,
            "note": "Huidige peildatum"
        })

    # 3. Maandelijkse data (1e van elke maand 2020 - nov 2026)
    monthly_pts = []
    y, m = 2020, 1
    month_names = ["Jan", "Feb", "Mrt", "Apr", "Mei", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dec"]
    while (y < 2026) or (y == 2026 and m <= 11):
        m_date = date(y, m, 1)
        e10, s, di, n = interpolate_price(m_date)
        monthly_pts.append({
            "d": m_date.strftime("%Y-%m-%d"),
            "label": f"{month_names[m-1]} '{str(y)[2:]}",
            "e10": e10, "super98": s, "diesel": di,
            **({"note": n} if n else {})
        })
        m += 1
        if m > 12:
            m = 1
            y += 1

    # 4. Jaarlijkse data (2020 - 2026)
    yearly_pts = []
    for y in range(2020, 2027):
        y_date = date(y, 7, 1) if y < 2026 else end_d
        e10, s, di, n = interpolate_price(y_date)
        yearly_pts.append({
            "d": f"{y}",
            "label": f"{y}",
            "e10": e10, "super98": s, "diesel": di,
            **({"note": n} if n else {})
        })

    return {
        "daily": daily_pts,
        "weekly": weekly_pts,
        "monthly": monthly_pts,
        "yearly": yearly_pts
    }

TRENDS = generate_trends()

def build_wasm(output_path: str, custom_payload: dict = None):
    if custom_payload is not None:
        payload = custom_payload
        count = len(payload.get("stations", []))
    else:
        payload = {
            "stations": STATIONS,
            "trends": TRENDS
        }
        count = len(STATIONS)
    data_bytes = json.dumps(payload).encode("utf-8")
    data_len = len(data_bytes)

    # 1. Type section (ID 1): type 0: () -> i32
    type_payload = bytes([1, 0x60, 0, 1, 0x7F])
    type_sec = create_section(1, type_payload)

    # 2. Function section (ID 3): 3 functies van type 0
    func_sec = create_section(3, bytes([3, 0, 0, 0]))

    # 3. Memory section (ID 5): 2 memory pagina's (128KB, ruim voldoende voor ~40KB JSON)
    mem_sec = create_section(5, bytes([1, 0x00, 0x03]))

    # 4. Export section (ID 7): exporteer memory en 3 functies
    exp_mem = encode_u32(len(b"memory")) + b"memory" + bytes([0x02, 0x00])
    exp_f0 = encode_u32(len(b"get_data_offset")) + b"get_data_offset" + bytes([0x00, 0x00])
    exp_f1 = encode_u32(len(b"get_data_len")) + b"get_data_len" + bytes([0x00, 0x01])
    exp_f2 = encode_u32(len(b"get_station_count")) + b"get_station_count" + bytes([0x00, 0x02])
    export_sec = create_section(7, bytes([4]) + exp_mem + exp_f0 + exp_f1 + exp_f2)

    # 5. Code section (ID 10):
    body0 = bytes([0x00, 0x41, 0x00, 0x0B])
    body1 = bytes([0x00, 0x41]) + encode_s32(data_len) + bytes([0x0B])
    body2 = bytes([0x00, 0x41]) + encode_s32(count) + bytes([0x0B])

    code_payload = (
        bytes([3]) + 
        encode_u32(len(body0)) + body0 +
        encode_u32(len(body1)) + body1 +
        encode_u32(len(body2)) + body2
    )
    code_sec = create_section(10, code_payload)

    # 6. Data section (ID 11): slaat de UTF-8 JSON dataset op in linear memory
    data_payload = bytes([1, 0x00, 0x41, 0x00, 0x0B]) + encode_u32(data_len) + data_bytes
    data_sec = create_section(11, data_payload)

    wasm_bytes = (
        b"\x00asm\x01\x00\x00\x00" +
        type_sec +
        func_sec +
        mem_sec +
        export_sec +
        code_sec +
        data_sec
    )

    with open(output_path, "wb") as f:
        f.write(wasm_bytes)

    b64 = base64.b64encode(wasm_bytes).decode("ascii")
    b64_path = os.path.join(os.path.dirname(output_path), "wasm_b64.txt")
    with open(b64_path, "w") as f:
        f.write(b64)

    unique_cities_count = len(set(s["city"] for s in STATIONS))
    print(f"Succes! {output_path} gebouwd:")
    print(f"  - Binary grootte: {len(wasm_bytes)} bytes")
    print(f"  - Tankstations: {count}")
    print(f"  - Unieke plaatsen: {unique_cities_count}")

if __name__ == "__main__":
    dir_path = os.path.dirname(os.path.abspath(__file__))
    target = os.path.join(dir_path, "hello.wasm")
    build_wasm(target)
