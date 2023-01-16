create table if not exists ip (
 addr text not null,
 country text,
 city text,
 asn int,
 autonomous_system text,
 reverse text,
 primary key(addr)
);

create table if not exists files(
 cid text not null,
 mimetype text,
 description text,
 primary key(cid)
);

create table if not exists peer(
 id text not null,
 addr text,
 port text,
 foreign key(addr) references ip(addr),
 unique(id, addr, port)
);

create table if not exists activity(
 peerid text not null,
 cid text not null,
 date timestamp not null,
-- foreign key(peerid) references peer(id),
 foreign key(cid) references files(cid),
 unique(peerid, cid, date)
);

create table if not exists storage(
 peerid text not null,
 cid text not null,
 date timestamp not null,
-- foreign key(peerid) references peer(id),
 foreign key(cid) references files(cid),
 unique(peerid, cid, date)
);

