import psycopg2
import sys
import uuid
import concurrent.futures

MAX_WORKERS=50

def collect_peerid(sql):
 """Establish the list of PEERID that we can found in the whole database and associate each of them with a random UUID"""
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
 """Establish the list of CID that we can found in the whole database and associate each of them with a random UUID"""
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
 """Establish the list of IP addresses that we can found in the whole database and associate each of them with a random UUID"""
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
 """Replace each CID with its corresponding UUID"""
 print("cid %s -> %s" % (old_cid, new_cid), file=sys.stderr)
 with sql.cursor() as cur:
  cur.execute("update files set cid=%s where cid=%s", (new_cid, old_cid))
  cur.execute("update activity set cid=%s where cid=%s", (new_cid, old_cid))
  cur.execute("update storage set cid=%s where cid=%s", (new_cid, old_cid))
 sql.commit()

def anonymise_peerid(sql, old_peerid, new_peerid):
 """Replace each PEERID with its corresponding UUID"""
 print("peerid %s -> %s" % (old_peerid, new_peerid), file=sys.stderr)
 with sql.cursor() as cur:
  cur.execute("update peer set id=%s where id=%s", (new_peerid, old_peerid))
  cur.execute("update activity set peerid=%s where peerid=%s", (new_peerid, old_peerid))
  cur.execute("update storage set peerid=%s where peerid=%s", (new_peerid, old_peerid))
 sql.commit()

def anonymise_addr(sql, old_addr, new_addr):
 """Replace each IP address with its corresponding UUID"""
 print("addr %s -> %s" % (old_addr, new_addr), file=sys.stderr)
 with sql.cursor() as cur:
  cur.execute("update ip set addr=%s where addr=%s", (new_addr, old_addr))
  cur.execute("update peer set addr=%s where addr=%s", (new_addr, old_addr))
 sql.commit()


def main(host, database, username, password):
 sql = psycopg2.connect(host=host, database=database, user=username, password=password)

 try:
  with sql.cursor() as cur:
   cur.execute("alter table activity drop constraint activity_cid_fkey;")
  sql.commit()
 except Exception as e:
  pass
 try:
  with sql.cursor() as cur:
   cur.execute("alter table storage drop constraint storage_cid_fkey;")
  sql.commit()
 except Exception as e:
  pass
 try:
  with sql.cursor() as cur:
   cur.execute("alter table peer drop constraint peer_addr_fkey;")
  sql.commit()
 except Exception as e:
  pass

 peerid_matching = collect_peerid(sql)
 cid_matching = collect_cid(sql)
 addr_matching = collect_addr(sql)

 # clear the cid
 synclist = []
 with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
  for cid in cid_matching:
   synclist.append(executor.submit(anonymise_cid, sql, cid, cid_matching[cid]))
   if len(synclist) == 100:
    for e in synclist:
     e.result()
    synclist = []

 # clear the peerid
 synclist = []
 with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
  for peerid in peerid_matching:
   synclist.append(executor.submit(anonymise_peerid, sql, peerid, peerid_matching[peerid]))
   if len(synclist) == 100:
    for e in synclist:
     e.result()
    synclist = []

 # clear the cid
 synclist = []
 with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
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
 if len(sys.argv) < 5:
  print("Usage: %s dbhost dbname dbusername dbpassword" % (sys.argv[0]))
  sys.exit(1)
 main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
