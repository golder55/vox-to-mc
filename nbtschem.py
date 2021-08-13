import nbtlib as nbt
from nbtlib.tag import Int, Compound, ByteArray,Short
from typing import Tuple
import numpy as np

# I think this is modified code from nbtschematic but I really don't remember what I did here

class SchematicFile(nbt.File):
    def __init__(self, shape: Tuple[int, int, int] = (1, 1, 1), offsetX="center",offsetY="center",offsetZ="center"):
        super().__init__({'Schematic': Compound({
            'Metadata': Compound({
                'WEOffsetX': Int(),
                'WEOffsetY': Int(),
                'WEOffsetZ': Int()
            }),
            'Palette': Compound({'minecraft:air':Int(0)}),
            'PaletteMax': Int(1),
            'Version': Int(2),
            'Length': Short(1),
            'Width': Short(1),
            'Height': Short(1),
            'DataVersion': Int(2580),
            'BlockData': ByteArray()
        })})
        self.offset = {'X': offsetX, 'Y': offsetY, 'Z': offsetZ}
        self.gzipped = True
        self.byteorder = 'big'
        self.resize(shape)


    def set_block(self, pos, block):
        if block not in self.root['Palette']:
            self.add_block_to_pallete(block)
        x, y, z = pos
        self.blocks[x, y, z] = self.root['Palette'][block]

    def resize(self, shape: Tuple[int, int, int]) -> None:
        """
        Resize the schematic file

        Resizing the schematic clears the blocks and data

        :param shape: New dimensions for the schematic, as a tuple of
               ``(n_y, n_z, n_x)``.
        """

        self.root['Height'] = nbt.Short(shape[0])
        self.root['Length'] = nbt.Short(shape[1])
        self.root['Width'] = nbt.Short(shape[2])
        self.blocks = np.zeros(shape, dtype=np.uint8, order='C')
        for coord, offset in self.offset.items():
            if offset == 'center':
                if coord == 'X':
                    offset_value = self.root['Length']
                elif coord == 'Y':
                    offset_value = self.root['Height']
                else:
                    offset_value = self.root['Width']

                if offset_value % 2 == 0:
                    self.offset[coord] = -self.root['Length'] / 2

                else:
                    self.offset[coord] = -(self.root['Length'] - 1) / 2
                self.root['Metadata']["WEOffset"+coord] = Int(self.offset[coord])
            else:
                self.root['Metadata']["WEOffset" + coord] = Int(offset)
    def add_block_to_pallete(self, block):
        self.root['Palette'][block] = Int(self.root['PaletteMax'])
        self.root['PaletteMax'] = Int(self.root['PaletteMax'] + 1)

    @property
    def blocks(self) -> np.array:
        """ Block IDs

        Entries in this array are the block ID at each coordinate of
        the schematic. This method returns an nbtlib type, but you may
        coerce it to a pure numpy array with ``numpy.asarray()``

        :return: 3D array which contains a view into the block IDs.
                 Array indices are in ``Y``, ``Z``, ``X`` order.
        """
        return self.root['BlockData'].reshape(self.shape, order='C').view()

    @blocks.setter
    def blocks(self, value):
        if not np.all(value.shape == self.shape):
            raise ValueError("Input shape %s does not match schematic shape %s"
                             % (value.shape, self.shape))

        self.root['BlockData'] = nbt.ByteArray(value.reshape(-1))

    @property
    def shape(self) -> Tuple[nbt.Short, nbt.Short, nbt.Short]:
        """ Schematic shape

        :return: Shape of the schematic, as a tuple of ``Y``, ``Z``, and ``X``
                 size.
        """
        return self.root['Height'], self.root['Length'], self.root['Width']

    @classmethod
    def load(cls, filename, gzipped=True, byteorder='big') -> 'SchematicFile':
        """
        Load a schematic file from disk

        If the schematic file is already loaded into memory, use the
        :meth:`~from_buffer()` method instead.

        :param filename: Path to a schematic file on disk.
        :param gzipped: Schematic files are always stored gzipped. This option
               defaults to True
        :param byteorder: Schematic files are always stored in big endian
               number format.
        :return: Loaded schematic
        """
        return super().load(filename=filename,
                            gzipped=gzipped, byteorder=byteorder)
