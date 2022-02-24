#!/bin/bash
touch special-batch-file
$MFPYTHON -m pip install daps_utils@git+https://github.com/nestauk/daps_utils@dev --quiet 1> /dev/null
