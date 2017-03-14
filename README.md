#kv-po-converter

This converter written in python converts localization files in the kv-format of dota from/to the gettext format used in translation software.

## Requirements

* [python Version 3.x](https://www.python.org/)

## Usage

### Converting from dota-kv to pot

Console command:

```
usage: kv2po.py [-h] [-o] [-O] [-e INPUT_EXTENSION [INPUT_EXTENSION ...]]
                [-E OUTPUT_EXTENSION]
                SOURCE DESTINATION

Convert from kv-format to po-format.

positional arguments:
  SOURCE                if --one_file_in is set, then source file, otherwise
                        source directory.
  DESTINATION           if --one_file_out is set, then destination file,
                        otherwise destination directory.

optional arguments:
  -h, --help            show this help message and exit
  -o, --one_file_in     Should the files be processed from a single file?
  -O, --one_file_out    Should the files be processed into a single file?
  -e INPUT_EXTENSION [INPUT_EXTENSION ...], --input_extensions INPUT_EXTENSION [INPUT_EXTENSION ...]
                        one or more file extensions for input file, for
                        example '.txt'.
  -E OUTPUT_EXTENSION, --output_extension OUTPUT_EXTENSION
                        file extension for output file, for example '.pot'.
```

Examples:

```
python3 kv2po.py /path/to/dotaAddon/game/resource/English .
python3 kv2po.py -O /path/to/dotaAddon/game/resource/English ./templates.pot
python3 kv2po.py -oO /path/to/dotaAddon/game/resource/en.txt ./en.pot
```

### Converting from po to dota-kv

Console command:

```
usage: po2kv.py [-h] [-o] [-O] [-e INPUT_EXTENSION [INPUT_EXTENSION ...]]
                [-E OUTPUT_EXTENSION]
                SOURCE DESTINATION

Convert from po-format to kv-format.

positional arguments:
  SOURCE                if --one_file_in is set, then source file, otherwise
                        source directory.
  DESTINATION           if --one_file_out is set, then destination file,
                        otherwise destination directory.

optional arguments:
  -h, --help            show this help message and exit
  -o, --one_file_in     Should the files be processed from a single file?
  -O, --one_file_out    Should the files be processed into a single file?
  -e INPUT_EXTENSION [INPUT_EXTENSION ...], --input_extensions INPUT_EXTENSION [INPUT_EXTENSION ...]
                        one or more file extensions for input file, for
                        example '.po'.
  -E OUTPUT_EXTENSION, --output_extension OUTPUT_EXTENSION
                        file extension for output file, for example '.txt'.

```

Examples:

```
python3 po2kv.py . /path/to/dotaAddon/game/resource/German
python3 po2kv.py -o ./de.po /path/to/dotaAddon/game/resource/German
python3 po2kv.py -oO ./de.po /path/to/dotaAddon/game/resource/de.txt
```

