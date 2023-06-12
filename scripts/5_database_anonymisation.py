import psycopg2
import sys
import uuid
import concurrent.futures

def collect_peerid(sql):
 peerid_matching = {}
 for request in ["select distinct id from peer", "select distinct peerid from activity", "select distinct peerid from storage"]:
  with sql.cursor() as cur:
   cur.execute(request)
   for v in cur:
    peerid = v[0]
    if peerid not in peerid_matching:
     peerid_matching[peerid] = str(uuid.uuid4())
  sql.commit()
 return peerid_matching

def collect_cid(sql):
 cid_matching = {}
 for request in ["select distinct cid from files", "select distinct cid from activity", "select distinct cid from storage"]:
  with sql.cursor() as cur:
   cur.execute(request)
   for v in cur:
    cid = v[0]
    if cid not in cid_matching:
     cid_matching[cid] = str(uuid.uuid4())
  sql.commit()
 return cid_matching

def collect_addr(sql):
 addr_matching = {}
 for request in ["select distinct addr from ip"]:
  with sql.cursor() as cur:
   cur.execute(request)
   for v in cur:
    addr = v[0]
    if addr not in addr_matching:
     addr_matching[addr] = str(uuid.uuid4())
  sql.commit()
 return addr_matching

def anonymise_cid(sql, old_cid, new_cid):
 print("cid %s -> %s" % (old_cid, new_cid), file=sys.stderr)
 with sql.cursor() as cur:
  cur.execute("update files set cid=%s where cid=%s", (new_cid, old_cid))
  cur.execute("update activity set cid=%s where cid=%s", (new_cid, old_cid))
  cur.execute("update storage set cid=%s where cid=%s", (new_cid, old_cid))
 sql.commit()

def anonymise_peerid(sql, old_peerid, new_peerid):
 print("peerid %s -> %s" % (old_peerid, new_peerid), file=sys.stderr)
 with sql.cursor() as cur:
  cur.execute("update peer set id=%s where id=%s", (new_peerid, old_peerid))
  cur.execute("update activity set peerid=%s where peerid=%s", (new_peerid, old_peerid))
  cur.execute("update storage set peerid=%s where peerid=%s", (new_peerid, old_peerid))
 sql.commit()

def anonymise_addr(sql, old_addr, new_addr):
 print("addr %s -> %s" % (old_addr, new_addr), file=sys.stderr)
 with sql.cursor() as cur:
  cur.execute("update ip set addr=%s where addr=%s", (new_addr, old_addr))
  cur.execute("update peer set addr=%s where addr=%s", (new_addr, old_addr))
 sql.commit()


def main(database, username):
 sql = psycopg2.connect(host='127.0.0.1', database=database, user=username, password=username)
# sql.set_session(autocommit=False)

 with sql.cursor() as cur:
  cur.execute("alter table activity drop constraint activity_cid_fkey;")
 sql.commit()

 with sql.cursor() as cur:
  cur.execute("alter table storage drop constraint storage_cid_fkey;")
 sql.commit()

 with sql.cursor() as cur:
  cur.execute("alter table peer drop constraint peer_addr_fkey;")
 sql.commit()

 peerid_matching = collect_peerid(sql)
 cid_matching = collect_cid(sql)
 addr_matching = collect_addr(sql)

 # clear the cid
 synclist = []
 with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
  for cid in cid_matching:
   synclist.append(executor.submit(anonymise_cid, sql, cid, cid_matching[cid]))
   if len(synclist) == 100:
    for e in synclist:
     e.result()
    synclist = []

 # clear the peerid
 synclist = []
 with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
  for peerid in peerid_matching:
   synclist.append(executor.submit(anonymise_peerid, sql, peerid, peerid_matching[peerid]))
   if len(synclist) == 100:
    for e in synclist:
     e.result()
    synclist = []

 # clear the cid
 synclist = []
 with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
  for addr in addr_matching:
   synclist.append(executor.submit(anonymise_addr, sql, addr, addr_matching[addr]))
   if len(synclist) == 100:
    for e in synclist:
     e.result()
    synclist = []

 # clear the ip address
 with sql.cursor() as cur:
  print("clear ip addresses", file=sys.stderr)
  cur.execute("update ip set city=null;")
  cur.execute("update ip set reverse=null;")
 sql.commit()


if '__main__' == __name__:
 main(sys.argv[1], sys.argv[2])
