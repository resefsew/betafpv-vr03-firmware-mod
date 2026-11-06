#!/usr/bin/env python3
"""
VR03 mod v1.0 (testing stage) for BETAFPV VR03 goggles: battery voltage on screen, MOD SETTINGS menu, boot splash.

Put this file next to a dump of YOUR OWN goggles' SPI flash (256 KiB .bin) and run:  python3 vr03_mod.py
It creates a modified COPY (<name>_modded.bin); the original file is never changed.
Contains only the bytes that differ from the stock image, no vendor firmware.
Not affiliated with BETAFPV or ARK Micro. License: MIT, (c) 2026 Resefsew.
"""
import hashlib, os, sys

VERSION = "1.0"
CODE_END = 0xC400
CODE_MD5 = "496ff35c43027384513f03bf409c83bd"
RESULT_CODE_MD5 = "5da5386ce6d1be15594a8835f8ea0ef7"
SIZE = 262144

WARNING = """
==================================================================================
 WARNING
==================================================================================
 1. This tool creates a MODIFIED copy of your goggles' firmware (.bin).
 2. THIS MOD IS STILL IN THE TESTING STAGE. Not every function has been tested.
 3. You flash it at your own risk. You alone are responsible for your device.
    The author is NOT responsible for a bricked device or any other damage.
 4. Make sure you have a backup of the ORIGINAL firmware stored somewhere else
    (another drive / cloud), not only next to this script.
==================================================================================
"""

# (offset, bytes as hex)
PATCH = [
    (0x003AB0, "12c5690000"),
    (0x003AC7, "02c578"),
    (0x004962, "4d4f443e"),
    (0x004993, "4d4f443e"),
    (0x0049C0, "4d4f443e"),
    (0x004E0C, "c900"),
    (0x004FAA, "1e"),
    (0x004FBC, "01"),
    (0x004FBE, "c4b5"),
    (0x004FD7, "c400"),
    (0x008149, "02c4db00"),
    (0x00C400, "123847e57845777001227808900200e6f0a308b87ff912c4267808900200e0f6a308b87ff92290003de0b401057f0302c0019000a9e0c0e07f0312c3087f057d0112a93812c48825e025e0fa90cf4093"),
    (0x00C451, "ea240193feea240293fdea240393fc127bc090fb2374e0f090fb20e0547f4480f012c4937d007f001295207f0312c064d0e0"),
    (0x00C484, "12c3082290003fe0b404004001e4221200068e2f8f30c3ef9463ee9401400fc3ef947cee940140037b02227b04227b012290003ee0b401012202b2c8900094e0c394104005b404004001e422e0b40103e480027401f022900094e0c394105018e064047009ef640370047410f022ef14700302817e02814d12c4c0feef601914600714602214602322ee04b404004001e42410900094f022eeb403077404900094f0227d0180067d0080027d01ee700890003e12c4d08029b4010890003d12c4d0801eb4021e12c488fced600aec04b404004009e48006ec700274041490003ff012c31822900094e0c394105005e4"),
    (0x00C574, "029e6822900094e0c394105006900094023aca753d"),
    (0x00C58A, "753ece753fc07b027d007f00125fc612c4c07a00b400027a0290003ee0b40103ea04faea75f014a42400f53fe434cdf53e753d"),
    (0x00C5BE, "7b057d007f01125fc612c4c07a00b401027a0290003de0b40103ea04faea75f014a42450f53fe434cdf53e753d"),
    (0x00C5EC, "7b057d007f02125fc612c4c07a00b402027a0412c4882a75f014a424a0f53fe434cdf53e753d"),
    (0x00C613, "7b057d007f03125fc612c4c0b4030474018001e475f014a42470f53fe434cef53e753d"),
    (0x00C637, "7b057d007f04125fc6023cc1"),
    (0x00C900, "12a5c79000a9e0c0e07f0312c3087f167d0212a9387ff67e007ddc7c00127bc090fb2374a4f090fb20e0547f4480f0753d"),
    (0x00C932, "753ecf753f007b027d007f00125fc6753d"),
    (0x00C944, "753ecf753f207b067d007f01125fc67f0312c0647f147e0512be347f0312c001d0e0"),
    (0x00C967, "12c30822"),
    (0x00CD00, "20204265657020616c65727420204f4e202000"),
    (0x00CD14, "20204265657020616c65727420204f46462000"),
    (0x00CD28, "3e3e4265657020616c65727420204f4e202000"),
    (0x00CD3C, "3e3e4265657020616c65727420204f46462000"),
    (0x00CD50, "2020566f6c742073686f772020204f4e202000"),
    (0x00CD64, "2020566f6c742073686f772020204f46462000"),
    (0x00CD78, "3e3e566f6c742073686f772020204f4e202000"),
    (0x00CD8C, "3e3e566f6c742073686f772020204f46462000"),
    (0x00CDA0, "2020566f6c7420706f7320202020424c202000"),
    (0x00CDB4, "2020566f6c7420706f7320202020544c202000"),
    (0x00CDC8, "2020566f6c7420706f73202020204243202000"),
    (0x00CDDC, "2020566f6c7420706f73202020204252202000"),
    (0x00CDF0, "3e3e566f6c7420706f7320202020424c202000"),
    (0x00CE04, "3e3e566f6c7420706f7320202020544c202000"),
    (0x00CE18, "3e3e566f6c7420706f73202020204243202000"),
    (0x00CE2C, "3e3e566f6c7420706f73202020204252202000"),
    (0x00CE70, "20204261636b20202020202020202020202000"),
    (0x00CE84, "3e3e4261636b20202020202020202020202000"),
    (0x00CEC0, "20204d4f442053455454494e47532020202000"),
    (0x00CEE0, "20202020202020202020202020202020202020202000"),
    (0x00CF00, "2020204d6f642062792052657365667365772020202000"),
    (0x00CF20, "204669726d776172652076657273696f6e20312e302000"),
    (0x00CF40, "1e00c4011e0019006d01c401ce02c401"),
]


def md5(b):
    return hashlib.md5(b).hexdigest()


def find_dump(folder):
    found = []
    for name in sorted(os.listdir(folder)):
        path = os.path.join(folder, name)
        if name.lower().endswith(".bin") and not name.lower().endswith("_modded.bin") \
                and os.path.isfile(path) and os.path.getsize(path) == SIZE:
            found.append(path)
    return found


def consent():
    print(WARNING)
    try:
        answer = input('Type  I AGREE  to accept and continue (anything else cancels): ')
    except EOFError:
        return False
    return answer.strip().upper() == "I AGREE"


def main():
    print("VR03 mod v%s (testing stage)" % VERSION)
    folder = os.path.dirname(os.path.abspath(__file__))
    paths = [sys.argv[1]] if len(sys.argv) > 1 else find_dump(folder)
    if not paths:
        sys.exit("No %d-byte .bin file found next to this script." % SIZE)
    for path in paths:
        data = open(path, "rb").read()
        print("Checking %s" % os.path.basename(path))
        if len(data) != SIZE or md5(data[:CODE_END]) != CODE_MD5 or any(x != 0xFF for x in data[CODE_END:0xE000]):
            print("  skipped: not the supported stock firmware.")
            continue
        dst = os.path.splitext(path)[0] + "_modded.bin"
        if os.path.exists(dst):
            sys.exit("%s already exists - move or delete it first." % dst)
        if not consent():
            sys.exit("Cancelled. Nothing was written.")
        out = bytearray(data)
        for off, hx in PATCH:
            b = bytes.fromhex(hx)
            out[off:off + len(b)] = b
        if md5(out[:0xE000]) != RESULT_CODE_MD5:
            sys.exit("Internal error, nothing written.")
        open(dst, "wb").write(out)
        print("OK -> %s" % os.path.basename(dst))
        print("Flash with erase -> write -> verify. To go back, write your original backup.")
        return
    sys.exit("No supported stock dump found.")


if __name__ == "__main__":
    main()
