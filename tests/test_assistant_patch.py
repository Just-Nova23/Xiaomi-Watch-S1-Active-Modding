import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools.patch_native_assistant_text_capacity import (
    CAPACITY_INSTRUCTION_OFFSET,
    EXPECTED_CONTEXT,
    EXPECTED_CONTEXT_OFFSET,
    NEW_INSTRUCTION,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "patch_native_assistant_text_capacity.py"


class AssistantPatchTests(unittest.TestCase):
    def test_exactly_one_synthetic_byte_changes(self):
        image = bytearray(EXPECTED_CONTEXT_OFFSET + len(EXPECTED_CONTEXT) + 32)
        image[EXPECTED_CONTEXT_OFFSET : EXPECTED_CONTEXT_OFFSET + len(EXPECTED_CONTEXT)] = EXPECTED_CONTEXT
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.bin"
            output = Path(directory) / "output.bin"
            source.write_bytes(image)
            subprocess.run([sys.executable, str(SCRIPT), str(source), str(output)], check=True, capture_output=True)
            patched = output.read_bytes()
        changed = [index for index, pair in enumerate(zip(image, patched)) if pair[0] != pair[1]]
        self.assertEqual(changed, [CAPACITY_INSTRUCTION_OFFSET + 2])
        self.assertEqual(patched[CAPACITY_INSTRUCTION_OFFSET : CAPACITY_INSTRUCTION_OFFSET + 4], NEW_INSTRUCTION)

    def test_wrong_context_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "wrong.bin"
            output = Path(directory) / "output.bin"
            source.write_bytes(bytes(EXPECTED_CONTEXT_OFFSET + len(EXPECTED_CONTEXT)))
            result = subprocess.run([sys.executable, str(SCRIPT), str(source), str(output)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
