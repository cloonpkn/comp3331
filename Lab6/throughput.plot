set xlabel "time [s]"
set ylabel "Throughput [Mbps]"
set key bel
plot  "tcp1.tr" u ($1):($2) t "tcp1" w lp, "tcp2.tr" u ($1):($2) t "tcp2" w lp
pause -1
