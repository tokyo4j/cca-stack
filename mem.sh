while true; do
  if read -t 1 -r input; then
    UPTIME=$(cat /proc/uptime | awk '{printf "%d\n", $1 * 1000}')
    if [[ $input == "ksm on" ]]; then
      echo "$UPTIME Starting ksm"
      cat /sys/kernel/mm/ksm/run
      echo 1 > /sys/kernel/mm/ksm/run
      cat /sys/kernel/mm/ksm/run
    else
      echo "$UPTIME $input"
    fi
  fi

  MEM_TOTAL_KB=$(grep MemTotal /proc/meminfo | awk '{print $2}')
  MEM_AVL_KB=$(grep MemAvailable /proc/meminfo | awk '{print $2}')
  MEM_USED_KB=$((MEM_TOTAL_KB - MEM_AVL_KB))

  UPTIME=$(cat /proc/uptime | awk '{printf "%d\n", $1 * 1000}')

  echo "$UPTIME FreeMemory $MEM_USED_KB"
done
