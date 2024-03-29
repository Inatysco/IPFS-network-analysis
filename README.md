# IPFS analysis

This repository contains the scripts used to collect the trace of DHT requests in the IPFS public network

## Collect data

Run IPFS in debug mode.
The node will connect to a public bootstrap node, get a position in the public Distributed Hash Table.
Therefore some DHT requests will be received and forwarded by the node and therefore can be saved in a logfile.

```
ìpfs daemon --routing=dht --verbose | grep 'handling message' > mylog.log 
```



## Analysis of the logfile

The logfile contains only date/hour, PEERID and CID (file identifier) of the requested file.
The script `scripts/1_ipfs_log_analysis.py` is designed to try to detect the IP address of the PEERID and the filetype of the file corresponding to the CID.


1. Launch an IPFS daemon that will be used to associate IP address, filetype, ... from the PEERID and CID collected in the logfile
```
ìpfs daemon --routing=dht
```

2. Convert the log file into a file that can be imported in a SQL database

First, download the Maxmind databases containing information on IP addresses and Autonomous systems.
This can be done by registering a free license key on https://www.maxmind.com/en/geolite2/signup?lang=en and using the ``geoipupdate`` software program.
The script looks for the file in the `/var/lib/GeoIP/` directory,
but the path of the different files can be specified using the `GEOLITE_COUNTRY`, `GEOLITE_CITY` and ``GEOLITE_ASN` environment variables.

Then launch the python script to convert the log file into a list of SQL commands.
```
export IPFS_URLS="http://127.0.0.1:5001" # the url to the API of the IPFS node previously launched
python scripts/1_ipfs_log_analysis.py mylog.log > mylog.db
```

## SQL import

The previous output is a file with SQL commands that can be then imported into a SQL database (postgresql)

1. Create schema

```
psql database user < scripts/2_schema.sql
```

2. Import previously analysed data
```
psql database user < mylog.db
```

## Graphics generation

```
python scripts/3_graphs_generation.py database user password graph.csv graph.plot graph.png
```

It generates csv and plot files. The graphs can be then generated using gnuplot executable:

 - gnuplot 'graph_requests.plot': to generate the graph indicating the number of requests received for each day of the period
 - gnuplot 'graph_days.plot' to generate the graph showing the number of requests received for each file identifier
 - gnuplot 'graph_replicates.plot' to generate the graph showing the number of replicates for each file identifier


## Provided database

The `database/` folder contains two files that are the databases we built during our own collect:
 - `gcp_20211217_20230101.db` contains the records collected between the 17th December 2021 and the 01st January 2023 from a node hosted on Google Cloud.
 - `aws_20211210_20221120.db` contains the records collected between the 10th December 2021 and the 20th November 2022 from a node hosted on Amazon Web Services.

The databases have been anonymised using the script `scripts/4_database_anonymisation.py`. The script replaces the CID, PEERID and IP Adresses contained in the database by random UUID values.

