from pyvox.parser import VoxParser
from nbtschem import SchematicFile
from colors import color

INPUT_FILE = "hitmonchan_one.vox"
OUTPUT_FILE = "model.schematic"

colors = {}

vox_file = VoxParser(INPUT_FILE).parse()

length, width, height = vox_file.models[0].size
sf = SchematicFile(shape=(height, length, width),offsetY=10)

for voxel in vox_file.models[0].voxels:
    x, y, z, vox_color = voxel
    if vox_color not in colors:
        r, g, b, a = vox_file.palette[voxel.c]
        hex_code = '#%02x%02x%02x' % (r, g, b)
        inverted = '#%02x%02x%02x' % (255-r, 255-g, 255-b)
        print(f"found color: {color(hex_code, inverted, hex_code)} ({vox_color})")
        colors[vox_color] = input("Enter block name: > ")

    sf.set_block((z,x,y),colors[vox_color])
print(colors)
sf.save(OUTPUT_FILE)
