# sbbs1k_mod
Basic Python script for modding Super Baseball Simulator 1000 teams.

~This utility has no dependencies and should just work (tm).~
This utility has a dependency on pillow for the team logo import/export.

## How to use
Export the teams from the original US Version of the ROM with

```
python3 sbbs1k_mod.py --export path/to/export/to path/to/rom.smc
```

Adjust stats however you see fit and import modified data into the original rom

```
python3 sbbs1k_mod.py --import path/to/import/from --output modified_rom.smc path/to/orig/rom.smc
```

Load the modified rom in an emulator or a flash cart and enjoy.

The `import_test` folder contains an example with modified `Team Power` and `Team Heroes`.
