#!/bin/bash
rm /tmp/baresip_fifo          
mkfifo /tmp/baresip_fifo      


baresip < /tmp/baresip_fifo &
BARESIP_PID=$!
echo "/about" > /tmp/baresip_fifo

sleep 3

for num in "$@"
do
  echo "/dial $num" > /tmp/baresip_fifo
  sleep 1
done

sleep 30
echo "/quit" > /tmp/baresip_fifo
wait $BARESIP_PID
rm /tmp/baresip_fifo



