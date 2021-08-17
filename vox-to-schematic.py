from pyvox.parser import VoxParser
from nbtschem import SchematicFile
import json
import math
import numpy as np

INPUT_FILE = "model.vox"
OUTPUT_FILE = "model.schem"

colors = {}
blockjson = json.load(open('block.json'))

vox_file = VoxParser(INPUT_FILE).parse()

length, width, height = vox_file.models[0].size
sf = SchematicFile(shape=(height, length, width),offsetY=10)

for voxel in vox_file.models[0].voxels:
    x, y, z, vox_color = voxel
    r,g,b,a = vox_file.palette[voxel.c]
    closest = min(blockjson, key=lambda k: math.sqrt(sum((np.array((r,g,b,a)) - np.array(blockjson[k]))**2)))
    sf.set_block((z,x,y),closest)
    print(x,y,z)

sf.save(OUTPUT_FILE)
