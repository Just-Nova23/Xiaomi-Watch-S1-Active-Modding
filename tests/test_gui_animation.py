import unittest

from tools.gui_animation import build_record, split_record


class GuiAnimationTests(unittest.TestCase):
    def test_round_trip_preserves_packets(self):
        path = b"nand/asset/synthetic.bin"
        chunks = [b"first", bytes(range(32)), b""]
        record = build_record(path, 1, chunks)
        parsed_path, version, parsed_chunks = split_record(record)
        self.assertEqual(parsed_path, path)
        self.assertEqual(version, 1)
        self.assertEqual(parsed_chunks, chunks)
        self.assertEqual(build_record(parsed_path, version, parsed_chunks), record)

    def test_bad_crc_is_rejected(self):
        record = bytearray(build_record(b"nand/asset/test.bin", 1, [b"payload"]))
        record[5] ^= 1
        with self.assertRaisesRegex(ValueError, "path CRC"):
            split_record(bytes(record))


if __name__ == "__main__":
    unittest.main()
