#!/usr/bin/env python3
"""
WASM Compiler Script voor Brandstofprijzen Nederland
Assembleert de WebAssembly instructies en de landelijke dataset (178 stations in 91 plaatsen)
naar een valide binary hello.wasm bestand.
"""
import os
import json
import base64

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

STATIONS = []
for idx, c in enumerate(RAW_STATIONS):
    d_e10, d_super, d_diesel = get_diffs(idx, c[1], c[3])
    STATIONS.append({
        "city": c[0],
        "name": c[1],
        "address": c[2],
        "type": c[3],
        "e10": c[4],
        "super98": c[5],
        "diesel": c[6],
        "diff_e10": d_e10,
        "diff_super98": d_super,
        "diff_diesel": d_diesel
    })


# Historische trenddata voor Nederland per week, maand en jaren
TRENDS = {
    "week": [
        {"label": "30 okt", "date": "30-10-2026", "e10": 2.115, "super98": 2.315, "diesel": 2.308},
        {"label": "31 okt", "date": "31-10-2026", "e10": 2.109, "super98": 2.309, "diesel": 2.302},
        {"label": "1 nov", "date": "01-11-2026", "e10": 2.105, "super98": 2.302, "diesel": 2.298},
        {"label": "2 nov", "date": "02-11-2026", "e10": 2.098, "super98": 2.295, "diesel": 2.292},
        {"label": "3 nov", "date": "03-11-2026", "e10": 2.094, "super98": 2.290, "diesel": 2.289},
        {"label": "4 nov", "date": "04-11-2026", "e10": 2.089, "super98": 2.285, "diesel": 2.285},
        {"label": "5 nov", "date": "05-11-2026", "e10": 2.085, "super98": 2.282, "diesel": 2.284},
        {"label": "6 nov", "date": "06-11-2026", "e10": 2.082, "super98": 2.280, "diesel": 2.287},
        {"label": "7 nov (Vandaag)", "date": "07-11-2026", "e10": 2.079, "super98": 2.279, "diesel": 2.289}
    ],
    "month": [
        {"label": "Dec '25", "date": "12-2025", "e10": 2.049, "super98": 2.249, "diesel": 2.219},
        {"label": "Jan '26", "date": "01-2026", "e10": 2.069, "super98": 2.269, "diesel": 2.239},
        {"label": "Feb '26", "date": "02-2026", "e10": 2.059, "super98": 2.259, "diesel": 2.229},
        {"label": "Mrt '26", "date": "03-2026", "e10": 2.089, "super98": 2.289, "diesel": 2.259},
        {"label": "Apr '26", "date": "04-2026", "e10": 2.119, "super98": 2.319, "diesel": 2.279},
        {"label": "Mei '26", "date": "05-2026", "e10": 2.139, "super98": 2.339, "diesel": 2.299},
        {"label": "Jun '26", "date": "06-2026", "e10": 2.149, "super98": 2.349, "diesel": 2.319},
        {"label": "Jul '26", "date": "07-2026", "e10": 2.129, "super98": 2.329, "diesel": 2.309},
        {"label": "Aug '26", "date": "08-2026", "e10": 2.109, "super98": 2.309, "diesel": 2.299},
        {"label": "Sep '26", "date": "09-2026", "e10": 2.099, "super98": 2.299, "diesel": 2.289},
        {"label": "Okt '26", "date": "10-2026", "e10": 2.089, "super98": 2.289, "diesel": 2.285},
        {"label": "Nov '26", "date": "11-2026", "e10": 2.079, "super98": 2.279, "diesel": 2.289}
    ],
    "years": [
        {"label": "2020", "date": "2020", "e10": 1.625, "super98": 1.785, "diesel": 1.285, "note": "Coronacrisis lockdown"},
        {"label": "2021", "date": "2021", "e10": 1.825, "super98": 1.985, "diesel": 1.465, "note": "Post-corona economisch herstel"},
        {"label": "2022 (Piek)", "date": "2022-Q1", "e10": 2.455, "super98": 2.655, "diesel": 2.345, "note": "Start energiecrisis & oorlog Oekraïne"},
        {"label": "2022 (Accijns)", "date": "2022-Q3", "e10": 2.085, "super98": 2.285, "diesel": 2.045, "note": "Noodmaatregel accijnsverlaging overheid"},
        {"label": "2023", "date": "2023", "e10": 2.065, "super98": 2.265, "diesel": 1.895, "note": "Gedeeltelijke afbouw accijnskorting"},
        {"label": "2024", "date": "2024", "e10": 2.115, "super98": 2.325, "diesel": 1.945, "note": "Inflatiecorrectie & stabiele olieprijs"},
        {"label": "2025", "date": "2025", "e10": 2.095, "super98": 2.295, "diesel": 2.235, "note": "Verhoging biobrandstofmandaten"},
        {"label": "2026 (Nu)", "date": "2026", "e10": 2.079, "super98": 2.279, "diesel": 2.289, "note": "Huidige peildatum"}
    ]
}


def build_wasm(output_path: str):
    payload = {
        "stations": STATIONS,
        "trends": TRENDS
    }
    data_bytes = json.dumps(payload).encode("utf-8")
    data_len = len(data_bytes)
    count = len(STATIONS)

    # 1. Type section (ID 1): type 0: () -> i32
    type_payload = bytes([1, 0x60, 0, 1, 0x7F])
    type_sec = create_section(1, type_payload)

    # 2. Function section (ID 3): 3 functies van type 0
    func_sec = create_section(3, bytes([3, 0, 0, 0]))

    # 3. Memory section (ID 5): 2 memory pagina's (128KB, ruim voldoende voor ~40KB JSON)
    mem_sec = create_section(5, bytes([1, 0x00, 0x02]))

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
