import psycopg2
import datetime
import math
import sys

def main_days():
 sql = psycopg2.connect(host='127.0.0.1', database=sys.argv[1], user=sys.argv[2], password=sys.argv[3])

 peerid = []
 date_min = None
 date_max = None
 delta = datetime.timedelta(days=1)

 with sql.cursor() as cur:
  cur.execute("select distinct peerid from activity;");
  for v in cur:
   peerid.append(v[0])
 with sql.cursor() as cur:
  cur.execute("select min(date), max(date) from activity;");
  for v in cur:
   date_min, date_max = v[0].date(), v[1].date()

 print(len(peerid))

 vectors = []
 vector_total = [0 for i in range(len(peerid))]
 vectors_filtered = []

 max_ = 0

 d = date_min
 while d <= date_max:
  vector = [0 for i in range(len(peerid))]
  with sql.cursor() as cur:
   cur.execute("select peerid, count(distinct cid) from activity where date >= %s and date < %s group by peerid;", (d.strftime("%Y-%m-%d"), (d+delta).strftime("%Y-%m-%d")))
   nb_requests_date = 0
   for v in cur:
    peer = v[0]
    nb_request = v[1]
    id = peerid.index(peer)
    vector[id] = nb_request
    vector_total[id] += nb_request
    nb_requests_date += nb_request
   max_ = max(max_, nb_requests_date)
  vectors.append(vector)
  d += delta

 for date in range(len(vectors)):
  vector_filtered = []
  for peer in range(len(peerid)):
   if vector_total[peer] > 1350:
    vector_filtered.append(str(vectors[date][peer]))
  vectors_filtered.append(vector_filtered)



 with open('/tmp/graph_days.csv', 'w') as f:
  f.write('"Peer identifier";\t%s\n' % (';\t'.join(["\"Nb requests peer %d\"" % (i) for i in range(len(vectors_filtered))])))
  d = date_min
  i = 0
  while d <= date_max:
   xlabel = d.strftime("%d/%m/%Y") if i==0 or i==date_max or d.day==1 else ''
   f.write("\"%s\";\t%s\n" % (xlabel, ';\t'.join(vectors_filtered[i])))
   i += 1
   d += delta

 colors = ["#000000", "#FFFF00", "#1CE6FF", "#FF34FF", "#FF4A46", "#008941", "#006FA6", "#A30059",
           "#FFDBE5", "#7A4900", "#0000A6", "#63FFAC", "#B79762", "#004D43", "#8FB0FF", "#997D87",
           "#5A0007", "#809693", "#FEFFE6", "#1B4400", "#4FC601", "#3B5DFF", "#4A3B53", "#FF2F80",
           "#61615A", "#BA0900", "#6B7900", "#00C2A0", "#FFAA92", "#FF90C9", "#B903AA", "#D16100",
           "#DDEFFF", "#000035", "#7B4F4B", "#A1C299", "#300018", "#0AA6D8", "#013349", "#00846F",
           "#372101", "#FFB500", "#C2FFED", "#A079BF", "#CC0744", "#C0B9B2", "#C2FF99", "#001E09",
           "#00489C", "#6F0062", "#0CBD66", "#EEC3FF", "#456D75", "#B77B68", "#7A87A1", "#788D66",
           "#885578", "#FAD09F", "#FF8A9A", "#D157A0", "#BEC459", "#456648", "#0086ED", "#886F4C",

           "#34362D", "#B4A8BD", "#00A6AA", "#452C2C", "#636375", "#A3C8C9", "#FF913F", "#938A81",
           "#575329", "#00FECF", "#B05B6F", "#8CD0FF", "#3B9700", "#04F757", "#C8A1A1", "#1E6E00",
           "#7900D7", "#A77500", "#6367A9", "#A05837", "#6B002C", "#772600", "#D790FF", "#9B9700",
           "#549E79", "#FFF69F", "#201625", "#72418F", "#BC23FF", "#99ADC0", "#3A2465", "#922329",
           "#5B4534", "#FDE8DC", "#404E55", "#0089A3", "#CB7E98", "#A4E804", "#324E72", "#6A3A4C",
           "#83AB58", "#001C1E", "#D1F7CE", "#004B28", "#C8D0F6", "#A3A489", "#806C66", "#222800",
           "#BF5650", "#E83000", "#66796D", "#DA007C", "#FF1A59", "#8ADBB4", "#1E0200", "#5B4E51",
           "#C895C5", "#320033", "#FF6832", "#66E1D3", "#CFCDAC", "#D0AC94", "#7ED379", "#012C58",

           "#7A7BFF", "#D68E01", "#353339", "#78AFA1", "#FEB2C6", "#75797C", "#837393", "#943A4D",
           "#B5F4FF", "#D2DCD5", "#9556BD", "#6A714A", "#001325", "#02525F", "#0AA3F7", "#E98176",
           "#DBD5DD", "#5EBCD1", "#3D4F44", "#7E6405", "#02684E", "#962B75", "#8D8546", "#9695C5",
           "#E773CE", "#D86A78", "#3E89BE", "#CA834E", "#518A87", "#5B113C", "#55813B", "#E704C4",
           "#00005F", "#A97399", "#4B8160", "#59738A", "#FF5DA7", "#F7C9BF", "#643127", "#513A01",
           "#6B94AA", "#51A058", "#A45B02", "#1D1702", "#E20027", "#E7AB63", "#4C6001", "#9C6966",
           "#64547B", "#97979E", "#006A66", "#391406", "#F4D749", "#0045D2", "#006C31", "#DDB6D0",
           "#7C6571", "#9FB2A4", "#00D891", "#15A08A", "#BC65E9", "#FFFFFE", "#C6DC99", "#203B3C",

           "#671190", "#6B3A64", "#F5E1FF", "#FFA0F2", "#CCAA35", "#374527", "#8BB400", "#797868",
           "#C6005A", "#3B000A", "#C86240", "#29607C", "#402334", "#7D5A44", "#CCB87C", "#B88183",
           "#AA5199", "#B5D6C3", "#A38469", "#9F94F0", "#A74571", "#B894A6", "#71BB8C", "#00B433",
           "#789EC9", "#6D80BA", "#953F00", "#5EFF03", "#E4FFFC", "#1BE177", "#BCB1E5", "#76912F",
           "#003109", "#0060CD", "#D20096", "#895563", "#29201D", "#5B3213", "#A76F42", "#89412E",
           "#1A3A2A", "#494B5A", "#A88C85", "#F4ABAA", "#A3F3AB", "#00C6C8", "#EA8B66", "#958A9F",
           "#BDC9D2", "#9FA064", "#BE4700", "#658188", "#83A485", "#453C23", "#47675D", "#3A3F00",
           "#061203", "#DFFB71", "#868E7E", "#98D058", "#6C8F7D", "#D7BFC2", "#3C3E6E", "#D83D66",

           "#2F5D9B", "#6C5E46", "#D25B88", "#5B656C", "#00B57F", "#545C46", "#866097", "#365D25",
           "#252F99", "#00CCFF", "#674E60", "#FC009C", "#92896B"]

 with open('/tmp/graph_days.plot', 'w') as f:
  f.write('reset\n')
  f.write('fontsize = 18\n')
#  f.write('set term postscript enhanced color eps size 3.25in,2.5in level3\n')
  f.write('set terminal png size 1024,768\n')
#  f.write('set terminal pdf\n')
  f.write('set encoding utf8\n')
  f.write('set output \'/tmp/graph_days.png\'\n')
  f.write('set style line 12 lc rgb \'#808080\' lt 0 lw 1\n')
  f.write('set style fill solid 1.00 border 0\n')
  f.write('set style histogram rowstacked\n')
  f.write('set style data histogram\n')
  f.write('set grid ytics\n')
  f.write('set xlabel "Days"\n')
  f.write('set ylabel "Number of requests"\n')

  for ll in range(math.ceil(len(vectors_filtered[0])/len(colors))):
   for k,color in enumerate(colors):
    f.write('set lt %d lc rgb \'%s\'\n' % (((ll*len(colors))+(k+1)), color))

  c = 10**(math.ceil(math.log(max_, 10)))
  f.write('set yrange [0:%d]\n' % (max_) )
  f.write('set xtics rotate\n')
  f.write('plot \'/tmp/graph_days.csv\' using 2:xtic(1) ti "", for [i=3:%d] \'\' using i ti ""\n' % (len(vectors_filtered[0])))



 print('ok')

def main_requests():
 sql = psycopg2.connect(host='127.0.0.1', database=sys.argv[1], user=sys.argv[2], password=sys.argv[3])

 mean_ = 0
 max_ = 0
 len_ = 100
 points = []

 with sql.cursor() as cur:
  cur.execute("select cid, count(*) requests from activity group by cid order by requests desc;")
  for i,r in enumerate(cur):
   points.append(float(r[1]))
  len_ = len(points)
  mean_ = sum(points)/len_
  max_ = max(points)
  sql.commit()

  with open('/tmp/graph_requests.csv', 'w') as f:
   f.write('"File identifier";\t"#requests";\t"mean"\n')
   for i,r in enumerate(points):
    f.write('%s;\t%s;\t%s\n' % (str(i), r, mean_))

 with open('/tmp/graph_requests.plot', 'w') as f:
  f.write('reset\n')
  f.write('fontsize = 18\n')
#  f.write('set term postscript enhanced color eps size 3.25in,2.5in level3\n')
  f.write('set terminal png size 1024,768\n')
#  f.write('set terminal pdf\n')
  f.write('set encoding utf8\n')
  f.write('set output \'/tmp/graph_requests.png\'\n')
  f.write('set style line 12 lc rgb \'#808080\' lt 0 lw 1\n')
  f.write('set style fill solid 1.00 border 0\n')
#set style fill pattern 8 border
#  f.write('set style histogram errorbars gap 2 lw 1')
  f.write('set style data histogram\n')
  f.write('set grid ytics\n')
  f.write('set xlabel "File identifier (CID)"\n')
  f.write('set ylabel "Number of requests for the file"\n')

  c = 10**(math.ceil(math.log(max_, 10)))
  f.write('set xrange [0:%d]\n' % (len_) )
  f.write('set yrange [0.1:%d]\n' % (c) )

  f.write('unset xtics\n')
  f.write('set logscale y\n')
  f.write('plot \'/tmp/graph_requests.csv\' using 2 ti "" lt 1 lc rgb \'#849c75\' fillstyle pattern 8 border, \\\n')
  f.write('\'\' using 3 smooth csplines ti "mean" lt 1 lc rgb \'#0086ee\'\n')


def main_replicates():
 sql = psycopg2.connect(host='127.0.0.1', database=sys.argv[1], user=sys.argv[2], password=sys.argv[3])

 mean_ = 0
 max_ = 0
 len_ = 100
 points = []

 with sql.cursor() as cur:
  cur.execute("select cid, count(distinct peerid) replicas from storage group by cid order by replicas desc;")
  for i,r in enumerate(cur):
   points.append(float(r[1]))
  len_ = len(points)
  mean_ = sum(points)/len_
  max_ = max(points)
  sql.commit()

  with open('/tmp/graph_replicates.csv', 'w') as f:
   f.write('"File identifier";\t"#replicas";\t"mean"\n')
   for i,r in enumerate(points):
    f.write('%s;\t%s;\t%s\n' % (str(i), r, mean_))

 with open('/tmp/graph_replicates.plot', 'w') as f:
  f.write('reset\n')
  f.write('fontsize = 18\n')
#  f.write('set term postscript enhanced color eps size 3.25in,2.5in level3\n')
  f.write('set terminal png size 1024,768\n')
#  f.write('set terminal pdf\n')
  f.write('set encoding utf8\n')
  f.write('set output \'/tmp/graph_replicates.png\'\n')
  f.write('set style line 12 lc rgb \'#808080\' lt 0 lw 1\n')
  f.write('set style fill solid 1.00 border 0\n')
#set style fill pattern 8 border
#  f.write('set style histogram errorbars gap 2 lw 1')
  f.write('set style data histogram\n')
  f.write('set grid ytics\n')
  f.write('set xlabel "File identifier (CID)"\n')
  f.write('set ylabel "Number of replicas"\n')

  c = 10**(math.ceil(math.log(max_, 10)))
  f.write('set xrange [0:%d]\n' % (len_) )
  f.write('set yrange [0.1:%d]\n' % (c) )

  f.write('unset xtics\n')
  f.write('set logscale y\n')
  f.write('plot \'/tmp/graph_replicates.csv\' using 2 ti "" lt 1 lc rgb \'#849c75\' fillstyle pattern 8 border, \\\n')
  f.write('\'\' using 3 smooth csplines ti "mean" lt 1 lc rgb \'#0086ee\'\n')
#plot 'contributions/imgs/chap3/local/network_local/read.dat' using 2:3:xtic(1) ti "IPFS seul (approche par défaut)" lt 1 lc rgb "#849c75" fillstyle pattern 8 border,\
#     ''                using 4:5 ti "IPFS déployé au-dessus de RozoFS" lt 1 lc rgb "#0086ee" fillstyle pattern 7 border, \
#     ''                using 6:7 ti "IPFS with metadata in a Cloud" lt 1 lc rgb "#cd210f" fillstyle pattern 5 border




if '__main__' == __name__:
 main_replicates()
 main_requests()
 main_days()
