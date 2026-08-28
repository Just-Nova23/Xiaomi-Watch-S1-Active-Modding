import struct
import unittest

from tools.tsc_frame_image import HEADER, TSCFrameImage, frame_size


class TSCFrameImageTests(unittest.TestCase):
    def test_known_60_by_60_size(self):
        self.assertEqual(frame_size(60, 60), 2700)

    def test_round_trip_preserves_frames(self):
        frames = (bytes(12), bytes(range(12)))
        image = TSCFrameImage(4, 4, frames)
        encoded = image.to_bytes()
        self.assertEqual(encoded[: HEADER.size], struct.pack("<HHI", 4, 4, 2))
        self.assertEqual(TSCFrameImage.from_bytes(encoded), image)

    def test_bad_frame_size_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "expected 12"):
            TSCFrameImage(4, 4, (bytes(11),)).to_bytes()

    def test_truncated_body_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "header requires 12"):
            TSCFrameImage.from_bytes(struct.pack("<HHI", 4, 4, 1) + bytes(11))

    def test_dimensions_must_match_tsc_blocks(self):
        with self.assertRaisesRegex(ValueError, "multiples of four"):
            frame_size(6, 4)


if __name__ == "__main__":
    unittest.main()
