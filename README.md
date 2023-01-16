# IPFS analysis

This repository contains the used scripts to collect the trace of DHT requests in the IPFS public network

## Collect data

Run IPFS in debug mode and save the DHT logs

```
ìpfs daemon --routing=dht --verbose | grep 'handling message' > mylog.log 
```


## Analysis of the logfile


1. Launch an IPFS daemon
```
ìpfs daemon --routing=dht
```

2. Convert the file

Place 

```
export IPFS_URLS="http://127.0.0.1:5001" # the url to the API of the IPFS node previously launched
python 2_analyse_ipfs_log.py mylog.log > mylog.db
```

The output is a file with SQL command that can be then imported in an SQL database (postgresql)

## SQL Import

1. Create schema



```
psql database user < 3_schema.sql
```

2. Import previously analysed data
```
psql database user < mylog.db
```

## Graph generation

```
python 4_generate_graphs.py database user password
```

It generates csv and plot files in /tmp/ folder. The graphs can be then generated using gnuplot executable

 - gnuplot 'graph_days.plot': to generate the graph indicating the number of requests received for each day of the period
 - gnuplot 'graph_requests.plot' to generate the graph showing the number of requests received for each file identifier
 - gnuplot 'graph_replicates.plot' to generate the graph showing the number of replicates for each file identifier


