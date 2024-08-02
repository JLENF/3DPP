## temperature_tower

python script to insert in gcode files all steps of temperatute tower.

#### Example of use:

```bash
# 8: Every 8mm the temperature will change
# 255: First step temperature in degrees °C
# 5: Temperature steps in °C

python3 temperature_tower.py Temperature_Tower.gcode 8 255 5
```

#### Output:

```bash
Height 8 mm: temperature set to 255°C
Height 16 mm: temperature set to 250°C
Height 24 mm: temperature set to 245°C
Height 32 mm: temperature set to 240°C
Height 40 mm: temperature set to 235°C
Height 48 mm: temperature set to 230°C
Height 56 mm: temperature set to 225°C
Height 64 mm: temperature set to 220°C
Height 72 mm: temperature set to 215°C
Height 80 mm: temperature set to 210°C
```

#### Links:
[STL file](https://www.thingiverse.com/thing:3127899)

[Oliv github](https://gist.github.com/Oliv4945/6fc57ba41e442a1c0fe78b6d830da9ee)