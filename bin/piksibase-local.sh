#!/bin/bash

ABS_PATH=$(cd `dirname "${BASH_SOURCE[0]}"` && cd .. && pwd)

cd ${ABS_PATH%%/}/src/
python -m piksibase.main --ident 127.0.0.1 --network NETWORK-local "$@"
