-- Table IP containing information on an IP address
create table if not exists ip (
 addr text not null,
 country text,
 city text,
 asn int,
 autonomous_system text,
 reverse text,
 primary key(addr)
);

-- Table file containing information on a CID
create table if not exists files(
 cid text not null,
 mimetype text,
 description text,
 primary key(cid)
);

-- Table peer containing information on a PEERID
create table if not exists peer(
 id text not null,
 addr text,
 port text,
 foreign key(addr) references ip(addr),
 unique(id, addr, port)
);

-- Table containing the list of DHT requests received (PEERID at the source of the request, CID looked up)
create table if not exists activity(
 peerid text not null,
 cid text not null,
 date timestamp not null,
 foreign key(cid) references files(cid),
 unique(peerid, cid, date)
);

-- Table containing the list of PEERID storing a replica of CID
create table if not exists storage(
 peerid text not null,
 cid text not null,
 date timestamp not null,
 foreign key(cid) references files(cid),
 unique(peerid, cid, date)
);

