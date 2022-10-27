#!/usr/bin/env sh
if ! command -v /usr/bin/arti &> /dev/null
then
    echo "No arti binary, running without Tor."
    exit
fi
chmod o-w /home/arti/.local/share/arti

/usr/bin/arti -l debug proxy -p 9150
