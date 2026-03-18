import argparse
import os
import shutil
from pathlib import Path
from zipfile import ZipFile

import numpy as np
from numpy.typing import NDArray
from PIL import Image

ASSETS_DIR = "assets"
BLOCKS_DIR = "blocks"

PNG_EXT = ".png"
JAR_EXT = ".jar"
SPECULAR_SUFFIX = "_s"
RGBA_MODE = "RGBA"
ENCODING = "utf-8"

IGNORE_FOLDERS = ["fluids", "crop"]
IGNORE_TOKENS = ["_s", "_n", ".mcmeta"]

MINIMUM_BRIGHTNESS = 75  # 0-255
REFLECTIVENESS = 255  # 0-255


def load_blacklist(file_path: str) -> set[str]:
    with open(file_path, "r", encoding=ENCODING) as f:
        return {line.strip().lower() for line in f if line.strip()}


def is_blacklisted(filename: str, blacklist: set[str] | None) -> bool:
    if not blacklist:
        return False
    base = os.path.splitext(filename)[0].lower()
    return base in blacklist


def is_valid_texture(mod_root: str, filename: str, blacklist: set[str] | None) -> bool:
    if not filename.endswith(PNG_EXT):
        return False
    if any(x in filename for x in IGNORE_TOKENS):
        return False
    if any(x in mod_root for x in IGNORE_FOLDERS):
        return False
    if ASSETS_DIR not in mod_root or BLOCKS_DIR not in mod_root:
        return False
    if is_blacklisted(filename, blacklist):
        return False
    return True


def ensure_base_texture(source: str, destination: str) -> None:
    if not os.path.isfile(destination):
        shutil.copy2(source, destination)


def generate_specular(image: Image.Image) -> Image.Image:
    pixels: NDArray[np.uint8] = np.array(image)

    r = pixels[:, :, 0]
    g = pixels[:, :, 1]
    b = pixels[:, :, 2]
    a = pixels[:, :, 3]

    r = (np.right_shift(r, 2)) + (np.right_shift(g, 2)) + (np.right_shift(b, 2))
    r = np.minimum(r, MINIMUM_BRIGHTNESS).astype(np.uint8)

    g = np.full_like(g, REFLECTIVENESS, dtype=np.uint8)
    b = np.zeros_like(b, dtype=np.uint8)

    specular_pixels = np.dstack((r, g, b, a))
    return Image.fromarray(specular_pixels, mode=RGBA_MODE)


def process_texture(mod_root: str, mod_file: str, output_folder: str) -> None:
    path_parts = mod_root.split(ASSETS_DIR)[-1][1:]
    folder_path = os.path.join(output_folder, ASSETS_DIR, path_parts)

    folder_path = os.path.abspath(folder_path)
    source_texture_path = os.path.abspath(os.path.join(mod_root, mod_file))
    base_texture_path = os.path.join(folder_path, mod_file)

    Path(folder_path).mkdir(parents=True, exist_ok=True)
    ensure_base_texture(source_texture_path, base_texture_path)

    name_without_ext = os.path.splitext(mod_file)[0]
    texture_name = name_without_ext + SPECULAR_SUFFIX + PNG_EXT
    specular_path = os.path.join(folder_path, texture_name)

    print(os.path.join(path_parts, texture_name))

    image = Image.open(source_texture_path).convert(RGBA_MODE)
    specular_image = generate_specular(image)
    specular_image.save(specular_path)


def process_jar(jar_path: str, output_folder: str, blacklist: set[str] | None) -> None:
    print("Processing mod:", os.path.basename(jar_path))

    # Place temp folder in the repo itself
    repo_temp = Path(__file__).parent / "temp"
    if repo_temp.exists():
        shutil.rmtree(repo_temp)
    repo_temp.mkdir(parents=True, exist_ok=True)

    temp_path = str(repo_temp.resolve())

    with ZipFile(os.path.abspath(jar_path)) as jar:
        jar.extractall(temp_path)

    for mod_root, _, files in os.walk(temp_path):
        for file in files:
            if not is_valid_texture(mod_root, file, blacklist):
                continue
            try:
                process_texture(mod_root, file, output_folder)
            except Exception as e:
                print(e)


def get_output_folder(
    source_folder: str, base_name: str, custom_base: str | None = None
) -> str:
    if custom_base:
        folder = Path(custom_base)
    else:
        folder = Path(source_folder) / ".minecraft" / "resourcepacks" / base_name

    counter = 1
    candidate = folder
    while candidate.exists():
        candidate = folder.with_name(f"{folder.name}_{counter}")
        counter += 1
    return str(candidate)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate specular maps for Minecraft textures."
    )
    parser.add_argument(
        "-s", "--source", required=True, help="Path to the Prism Minecraft instance"
    )
    parser.add_argument(
        "-b", "--blacklist", required=False, help="Optional path to blacklist.txt"
    )
    parser.add_argument(
        "-o", "--output", required=False, help="Optional custom output directory"
    )
    args = parser.parse_args()

    source_folder = args.source
    blacklist = load_blacklist(args.blacklist) if args.blacklist else None

    output_folder = get_output_folder(source_folder, "GTNH_LabPBR", args.output)
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    print("Using output folder:", output_folder)

    for root, _, files in os.walk(source_folder):
        for file in files:
            if file.endswith(JAR_EXT):
                process_jar(os.path.join(root, file), output_folder, blacklist)


if __name__ == "__main__":
    main()
