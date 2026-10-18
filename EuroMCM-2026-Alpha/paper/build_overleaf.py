"""Export the canonical paper/main.tex and figures to a self-contained Overleaf ZIP."""
from pathlib import Path
import re
import shutil
import zipfile


def main():
    paper = Path(__file__).resolve().parent
    text = (paper / "main.tex").read_text()
    figures = sorted(set(re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", text)))
    export = paper / "overleaf"
    export.mkdir(exist_ok=True)
    files = ["main.tex", "README_zh.md", "RESULT_SOURCES.md"]
    files += ["figures/" + name for name in figures]
    missing = [rel for rel in files if not (paper / rel).is_file()]
    if missing:
        raise FileNotFoundError("Missing paper dependencies: " + ", ".join(missing))
    for rel in files:
        target = export / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(paper / rel, target)
    output = paper / "EuroMCM_Overleaf.zip"
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for rel in files:
            archive.write(paper / rel, arcname=rel)
    with zipfile.ZipFile(output) as archive:
        assert archive.testzip() is None
    print(f"Exported {len(files)} files to {output}")


if __name__ == "__main__":
    main()
