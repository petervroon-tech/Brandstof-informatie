#!/usr/bin/env python3
"""
WASM Compiler Script voor Brandstofprijzen Nederland
Assembleert de WebAssembly instructies en de dataset naar een valide binary hello.wasm bestand.
"""
import os
import json

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

# Actuele tankstations en dagprijzen in Nederland
STATIONS = [
    # Apeldoorn
    {"name": "Fieten Olie", "city": "Apeldoorn", "address": "Surinameweg 5", "type": "Onbemand", "e10": 2.079, "super98": 2.279, "diesel": 2.289},
    {"name": "Fieten Olie", "city": "Apeldoorn", "address": "Hogekampweg 38", "type": "Onbemand", "e10": 2.079, "super98": 2.279, "diesel": 2.289},
    {"name": "Fieten Olie", "city": "Apeldoorn", "address": "Anklaarseweg 121c", "type": "Onbemand", "e10": 2.089, "super98": 2.289, "diesel": 2.299},
    {"name": "Tamoil Express", "city": "Apeldoorn", "address": "Arnhemseweg 299", "type": "Onbemand", "e10": 2.099, "super98": 2.299, "diesel": 2.289},
    {"name": "TinQ", "city": "Apeldoorn", "address": "Arnhemseweg 221", "type": "Onbemand", "e10": 2.099, "super98": 2.309, "diesel": 2.299},
    {"name": "TinQ", "city": "Apeldoorn", "address": "Matenpoort 11", "type": "Onbemand", "e10": 2.109, "super98": 2.319, "diesel": 2.309},
    {"name": "Tango", "city": "Apeldoorn", "address": "Arnhemseweg 432", "type": "Onbemand", "e10": 2.109, "super98": 2.319, "diesel": 2.309},
    {"name": "AVIA XPress", "city": "Apeldoorn", "address": "Oude Beekbergerweg 98", "type": "Onbemand", "e10": 2.119, "super98": 2.329, "diesel": 2.319},
    {"name": "Esso Express", "city": "Apeldoorn", "address": "Tweelingenlaan 48", "type": "Onbemand", "e10": 2.129, "super98": 2.339, "diesel": 2.319},
    {"name": "Shell Express", "city": "Apeldoorn", "address": "Anklaarseweg 195", "type": "Onbemand", "e10": 2.139, "super98": 2.349, "diesel": 2.329},
    {"name": "Shell", "city": "Apeldoorn", "address": "Zutphensestraat 74", "type": "Bemand", "e10": 2.189, "super98": 2.439, "diesel": 2.369},
    {"name": "BP Orden", "city": "Apeldoorn", "address": "Laan van Orden 322", "type": "Bemand", "e10": 2.199, "super98": 2.429, "diesel": 2.369},
    {"name": "BP De Hucht (A1)", "city": "Apeldoorn", "address": "Rijksweg A1", "type": "Snelweg", "e10": 2.449, "super98": 2.689, "diesel": 2.549},
    {"name": "Esso A50", "city": "Apeldoorn", "address": "Rijksweg A50", "type": "Snelweg", "e10": 2.459, "super98": 2.699, "diesel": 2.559},

    # Deventer
    {"name": "TinQ", "city": "Deventer", "address": "Snipperlingsdijk 52", "type": "Onbemand", "e10": 2.089, "super98": 2.299, "diesel": 2.289},
    {"name": "Tango", "city": "Deventer", "address": "Zutphenseweg 31", "type": "Onbemand", "e10": 2.099, "super98": 2.309, "diesel": 2.299},
    {"name": "AVIA", "city": "Deventer", "address": "Snipperlingsdijk 2", "type": "Bemand", "e10": 2.159, "super98": 2.389, "diesel": 2.349},
    {"name": "Shell", "city": "Deventer", "address": "Holterweg 108", "type": "Bemand", "e10": 2.179, "super98": 2.419, "diesel": 2.359},

    # Arnhem
    {"name": "Fieten Olie", "city": "Arnhem", "address": "Westervoortsedijk 71", "type": "Onbemand", "e10": 2.089, "super98": 2.289, "diesel": 2.299},
    {"name": "TinQ", "city": "Arnhem", "address": "Groningensingel 1", "type": "Onbemand", "e10": 2.099, "super98": 2.319, "diesel": 2.299},
    {"name": "BP Express", "city": "Arnhem", "address": "Dr. C. Lelyweg 1", "type": "Onbemand", "e10": 2.129, "super98": 2.339, "diesel": 2.319},
    {"name": "Shell", "city": "Arnhem", "address": "Apeldoornseweg 100", "type": "Bemand", "e10": 2.189, "super98": 2.439, "diesel": 2.369},

    # Utrecht
    {"name": "Tango", "city": "Utrecht", "address": "Nieuwe Houtenseweg 2", "type": "Onbemand", "e10": 2.109, "super98": 2.319, "diesel": 2.299},
    {"name": "TinQ", "city": "Utrecht", "address": "Proostwetering 2", "type": "Onbemand", "e10": 2.119, "super98": 2.329, "diesel": 2.309},
    {"name": "Shell", "city": "Utrecht", "address": "Europalaan 2", "type": "Bemand", "e10": 2.199, "super98": 2.449, "diesel": 2.379},

    # Amsterdam
    {"name": "Tango", "city": "Amsterdam", "address": "Basisweg 32", "type": "Onbemand", "e10": 2.119, "super98": 2.329, "diesel": 2.319},
    {"name": "TinQ", "city": "Amsterdam", "address": "Transformatorweg 31", "type": "Onbemand", "e10": 2.129, "super98": 2.339, "diesel": 2.319},
    {"name": "BP", "city": "Amsterdam", "address": "Haarlemmerweg 365", "type": "Bemand", "e10": 2.219, "super98": 2.469, "diesel": 2.399},

    # Rotterdam
    {"name": "Fieten Olie", "city": "Rotterdam", "address": "Bovendijk 133", "type": "Onbemand", "e10": 2.089, "super98": 2.299, "diesel": 2.289},
    {"name": "Tango", "city": "Rotterdam", "address": "Vierhavensstraat 50", "type": "Onbemand", "e10": 2.099, "super98": 2.309, "diesel": 2.299},
    {"name": "Shell", "city": "Rotterdam", "address": "Stadionweg 45", "type": "Bemand", "e10": 2.199, "super98": 2.449, "diesel": 2.379},

    # Zwolle
    {"name": "TinQ", "city": "Zwolle", "address": "Ceintuurbaan 4", "type": "Onbemand", "e10": 2.089, "super98": 2.299, "diesel": 2.289},
    {"name": "Tango", "city": "Zwolle", "address": "Rieteweg 14", "type": "Onbemand", "e10": 2.099, "super98": 2.309, "diesel": 2.299},
    {"name": "Shell", "city": "Zwolle", "address": "IJsselallee 33", "type": "Bemand", "e10": 2.189, "super98": 2.439, "diesel": 2.369}
]

def build_wasm(output_path: str):
    data_bytes = json.dumps(STATIONS).encode("utf-8")
    data_len = len(data_bytes)
    count = len(STATIONS)

    # 1. Type section (ID 1): type 0: () -> i32
    type_payload = bytes([1, 0x60, 0, 1, 0x7F])
    type_sec = create_section(1, type_payload)

    # 2. Function section (ID 3): 3 functies van type 0
    func_sec = create_section(3, bytes([3, 0, 0, 0]))

    # 3. Memory section (ID 5): 1 memory pagina (64KB)
    mem_sec = create_section(5, bytes([1, 0x00, 0x01]))

    # 4. Export section (ID 7): exporteer memory en 3 functies
    exp_mem = encode_u32(len(b"memory")) + b"memory" + bytes([0x02, 0x00])
    exp_f0 = encode_u32(len(b"get_data_offset")) + b"get_data_offset" + bytes([0x00, 0x00])
    exp_f1 = encode_u32(len(b"get_data_len")) + b"get_data_len" + bytes([0x00, 0x01])
    exp_f2 = encode_u32(len(b"get_station_count")) + b"get_station_count" + bytes([0x00, 0x02])
    export_sec = create_section(7, bytes([4]) + exp_mem + exp_f0 + exp_f1 + exp_f2)

    # 5. Code section (ID 10):
    # func 0: return offset (0)
    body0 = bytes([0x00, 0x41, 0x00, 0x0B])
    # func 1: return data_len
    body1 = bytes([0x00, 0x41]) + encode_s32(data_len) + bytes([0x0B])
    # func 2: return count
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

    print(f"Succes! {output_path} gebouwd ({len(wasm_bytes)} bytes, {count} stations).")

if __name__ == "__main__":
    dir_path = os.path.dirname(os.path.abspath(__file__))
    target = os.path.join(dir_path, "hello.wasm")
    build_wasm(target)
