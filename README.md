#kv-po-converter

This converter written in python converts localization files in the kv-format of dota from/to the gettext format used in translation software.

## Requirements

* [python Version 3.x](https://www.python.org/)

## Usage

### Converting from dota-kv to pot

Console command:

```bash
python3 kv2po.py <SOURCE-DIRECTORY> <DESTINATION-FILE>
```

Example:

```bash
python3 kv2po.py /path/to/dotaAddon/game/resource/English ./templates.pot
```

### Converting from po to dota-kv

Console command:

```bash
python3 po2kv.py <SOURCE-FILE> <DESTINATION-DIRECTORY>
```

Example:

```bash
python3 po2kv.py ./de.po /path/to/dotaAddon/game/resource/German
```

