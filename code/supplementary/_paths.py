from pathlib import Path
def package_paths(script_file):
    code_dir = Path(script_file).resolve().parent
    root = code_dir.parent
    data_dir = root / "data"
    output_dir = root / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    return root, data_dir, output_dir
