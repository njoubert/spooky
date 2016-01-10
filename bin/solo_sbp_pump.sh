#!/bin/bash

ABS_PATH=$(cd `dirname "${BASH_SOURCE[0]}"` && cd .. && pwd)

cd ${ABS_PATH%%/}/src/
python -m solo_sbp_pump.main "$@"
