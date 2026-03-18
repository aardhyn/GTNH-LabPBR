# GTNH LabPBR Pack

Python script to generate a LabPBR pack compatible with **Complementary 4.x** and **Angelica** for use in **GregTech: New Horizons**.

Based on the work by Rodney and Sampsa.

## Installation

### Quick

Install the appropriate resource pack from [Releases](https://github.com/aardhyn/GTNH_LabPBR/releases) and place it in the `resourcepacks` directory of your GTNH instance installation.

Boot the pack, enable the Resource Pack, then switch from **Integrated PBR** to **LabPBR** in your shader configuration within Angelica.

If you want to modify which blocks are reflective, you can either delete them from the Resource Pack, or use the Custom installation method below to regenerate the pack.

### Custom

This section assumes you are familiar with Python and how to install and run Python scripts. Programming knowledge is **not required** to use the script.

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the script to generate the LabPBR pack from your Prism Minecraft instance:

```bash
python main.py -s /path/to/Prism/instance/.minecraft
```

### Flags

| Flag                      | Description                                                                             | Default Behavior                                                                     |
| ------------------------- | --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| `-s / --source <file>     | Path to your GTNH installation                                                          | Required                                                                             |
| `-b / --blacklist <file>` | Path to a blacklist text file listing textures to exclude from specular map generation. | All textures are processed if not provided.                                          |
| `-o / --output <path>`    | Custom output folder for the resource pack.                                             | `<source>/resourcepacks/GTNH_LabPBR`, deduplicated automatically (`_1`, `_2`, etc.). |

For example

```bash
python main.py -s "/path/to/Prism/instance/.minecraft" -b blacklist.txt -o "/path/to/custom/output"
```
