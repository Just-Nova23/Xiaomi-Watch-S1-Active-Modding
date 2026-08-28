import unittest

from tools.gui_asset_record import append_record, build_record, crc32_xiaomi


class GuiAssetRecordTests(unittest.TestCase):
    def test_builds_generic_wrapped_record(self):
        path = b"nand/asset/example.bin"
        body = b"native-file-body"
        record = build_record(path, body)
        payload = 9 + len(path)
        self.assertEqual(record[:4], b"\x01\x00\x00\x00")
        self.assertEqual(record[4], len(path))
        self.assertEqual(record[5:9], crc32_xiaomi(path))
        self.assertEqual(record[payload], 2)
        self.assertEqual(record[payload + 1 : payload + 5], len(body).to_bytes(4, "big"))
        self.assertEqual(record[payload + 5 : payload + 9], crc32_xiaomi(body))
        self.assertEqual(record[payload + 9 :], body)

    def test_append_refuses_duplicate_path(self):
        original = build_record(b"nand/asset/example.bin", b"first")
        duplicate = build_record(b"nand/asset/example.bin", b"second")
        with self.assertRaisesRegex(ValueError, "already contains"):
            append_record(original, duplicate)

    def test_append_preserves_existing_component(self):
        original = build_record(b"nand/asset/first.bin", b"first")
        second = build_record(b"nand/asset/second.bin", b"second")
        self.assertEqual(append_record(original, second), original + second)


if __name__ == "__main__":
    unittest.main()
