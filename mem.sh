while true
do
  sleep 1
  cat /proc/meminfo | grep MemAvailable
done