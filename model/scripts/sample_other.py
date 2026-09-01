# scripts/sample_other.py
import random, pathlib

def trim_folder_in_place(folder: str, keep_n: int = 200, seed: int = 42):
    random.seed(seed)
    files = list(pathlib.Path(folder).glob("*.jpg"))
    if len(files) <= keep_n:
        return
    to_delete = random.sample(files, len(files) - keep_n)
    for f in to_delete:
        f.unlink()
    print(f"{folder}: kept {keep_n}, deleted {len(to_delete)}")

if __name__ == "__main__":
    trim_folder_in_place("raw_downloads/asdid/potassium_deficiency", keep_n=200)
    trim_folder_in_place("raw_downloads/asdid/downey_mildew", keep_n=200)