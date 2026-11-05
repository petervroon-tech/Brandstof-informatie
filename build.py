#!/usr/bin/env python3
"""
WASM Compiler Script
Assembleert de WebAssembly instructies naar een valide binary .wasm bestand.
"""
import os

def encode_u32(val: int) -> bytes:
    """Encodeert een integer naar LEB128 (formaat gebruikt door WebAssembly)."""
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

def create_section(section_id: int, payload: bytes) -> bytes:
    return bytes([section_id]) + encode_u32(len(payload)) + payload

def build_wasm(output_path: str):
    # 1. Type section (ID 1)
    # Type 0: (i32, i32) -> ()  voor geïmporteerde popup functie
    # Type 1: () -> ()          voor de 'run' functie
    type_payload = (
        bytes([2]) + 
        bytes([0x60, 2, 0x7F, 0x7F, 0]) + 
        bytes([0x60, 0, 0])
    )
    type_sec = create_section(1, type_payload)

    # 2. Import section (ID 2): importeer env.show_popup
    mod_name = b"env"
    field_name = b"show_popup"
    import_payload = bytes([1]) + (
        encode_u32(len(mod_name)) + mod_name +
        encode_u32(len(field_name)) + field_name +
        bytes([0x00, 0x00]) # func import, type 0
    )
    import_sec = create_section(2, import_payload)

    # 3. Function section (ID 3): koppelt func #1 aan type 1 () -> ()
    func_sec = create_section(3, bytes([1, 1]))

    # 4. Memory section (ID 5): 1 memory pagina (min=1, geen max)
    mem_sec = create_section(5, bytes([1, 0x00, 0x01]))

    # 5. Export section (ID 7): exporteer "memory" en "run"
    export_mem = encode_u32(len(b"memory")) + b"memory" + bytes([0x02, 0x00])
    export_run = encode_u32(len(b"run")) + b"run" + bytes([0x00, 0x01])
    export_sec = create_section(7, bytes([2]) + export_mem + export_run)

    # 6. Code section (ID 10): de bytecode van 'run'
    # i32.const 0, i32.const 11, call 0, end
    func_body = bytes([
        0x00,       # 0 lokale variabelen
        0x41, 0x00, # i32.const 0 (geheugenoffset)
        0x41, 0x0B, # i32.const 11 (lengte "Hello World")
        0x10, 0x00, # call 0 (show_popup)
        0x0B        # end opcode
    ])
    code_sec = create_section(10, bytes([1]) + encode_u32(len(func_body)) + func_body)

    # 7. Data section (ID 11): slaat "Hello World" op op adres 0
    text = b"Hello World"
    data_seg = bytes([0x00, 0x41, 0x00, 0x0B]) + encode_u32(len(text)) + text
    data_sec = create_section(11, bytes([1]) + data_seg)

    # Magic header: \0asm versie 1
    wasm_bytes = (
        b"\x00asm\x01\x00\x00\x00" +
        type_sec +
        import_sec +
        func_sec +
        mem_sec +
        export_sec +
        code_sec +
        data_sec
    )

    with open(output_path, "wb") as f:
        f.write(wasm_bytes)
    
    print(f"Succes! {output_path} gebouwd ({len(wasm_bytes)} bytes).")

if __name__ == "__main__":
    dir_path = os.path.dirname(os.path.abspath(__file__))
    target = os.path.join(dir_path, "hello.wasm")
    build_wasm(target)
