# IPFS analysis

This repository contains the used scripts to collect the trace of DHT requests in the IPFS public network

## Collect data

Run IPFS in debug mode.
The node will connect to a public bootstrap node, get a position in the public Distributed Hash Table.
Therefoe some DHT requests will be received and forwarded by the node and therefore can be saved in a logfile.

```
ìpfs daemon --routing=dht --verbose | grep 'handling message' > mylog.log 
```



## Analysis of the logfile

The logfile contains only date/hour, peerid and cid (file identifier) of the requested file.
The script 2_analyse_ipfs_log.py is designed to try to detect the IP address of the peerid and the filetype of the file corresponding to the cid.



1. Launch an IPFS daemon
```
ìpfs daemon --routing=dht
```

2. Convert the log file into a file that can be imported in a SQL database

First, download the Maxmind databases containing information on IP addresses and Autonomous systems.
This can be done by registering a free license key on https://www.maxmind.com/en/geolite2/signup?lang=en and using the ``geoipupdate`` software program. This downloads the database in /var/lib/GeoIP/ directory.


Then launch the python script to convert the log file into a list of SQL commands.
```
export IPFS_URLS="http://127.0.0.1:5001" # the url to the API of the IPFS node previously launched
python scripts/2_analyse_ipfs_log.py mylog.log > mylog.db
```

## SQL import

The previous output is a file with SQL command that can be then imported in an SQL database (postgresql)

1. Create schema

```
psql database user < scripts/3_schema.sql
```

2. Import previously analysed data
```
psql database user < mylog.db
```

## Graphics generation

```
python scripts/4_generate_graphs.py database user password
```

It generates csv and plot files in /tmp/ folder. The graphs can be then generated using gnuplot executable

 - gnuplot 'graph_days.plot': to generate the graph indicating the number of requests received for each day of the period
 - gnuplot 'graph_requests.plot' to generate the graph showing the number of requests received for each file identifier
 - gnuplot 'graph_replicates.plot' to generate the graph showing the number of replicates for each file identifier


