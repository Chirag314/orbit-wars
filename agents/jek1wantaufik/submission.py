from pathlib import Path
import shutil
import tarfile

MODEL_DIR = Path("/kaggle/input/models/jek1wantaufik/buddy/other/orbit-wars/5/submission")
BUILD_DIR = Path("build")
ARCHIVE_PATH = Path("submission.tar.gz")

shutil.rmtree(BUILD_DIR, ignore_errors=True)
BUILD_DIR.mkdir()

shutil.copy2(MODEL_DIR / "main.py", BUILD_DIR / "main.py")
shutil.copytree(MODEL_DIR / "orbit_lite", BUILD_DIR / "orbit_lite")

with tarfile.open(ARCHIVE_PATH, "w:gz") as tar:
    tar.add(BUILD_DIR, arcname="")

print("Created:", ARCHIVE_PATH)