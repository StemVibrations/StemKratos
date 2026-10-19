import zipfile
import os
from pathlib import Path


zip_folder = Path(r"path\to\zip\files")  # folder containing the zip files
output_folder = Path(r"path\to\zip\files\release")  # folder where all files will go

output_folder.mkdir(exist_ok=True)

# unzip all zip files in the zip_folder and extract their contents into the output_folder
for zip_path in zip_folder.glob("*.zip"):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file in zip_ref.namelist():
            if not file.endswith("/"):  # skip directories
                filename = Path(file).name
                target_path = output_folder / filename

                with zip_ref.open(file) as source, open(target_path, "wb") as target:
                    target.write(source.read())

print("All zip files extracted into one folder.")