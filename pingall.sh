#!/bin/bash

for h in $(cat host-IPs.txt)
do
	ip=$(echo $h | cut -d ',' -f 2)
	host=$(echo $h | cut -d ',' -f 1)
	ping -c 1 -W 1 "$ip" | grep '1 received' > /dev/null \
	&& echo -n $host '' \
	|| echo -n X ''
done
echo
