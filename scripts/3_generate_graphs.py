import psycopg2
import datetime
import math
import sys

def main_days(host, database, username, password, output_csv, output_gnuplot, output_img):
 """Generate a CSV file (output_csv) and a GNUPLOT file (output_gnuplot) to generate graphbar (output_img) containing the number of requests received each day"""
 sql = psycopg2.connect(host=host, database=database, user=username, password=password)

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



 with open(output_csv, 'w') as f:
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

 with open(output_plot, 'w') as f:
  f.write('reset\n')
  f.write('fontsize = 18\n')
  f.write('set terminal png size 1024,768\n')
  f.write('set encoding utf8\n')
  f.write('set output \'%s\'\n' % (output_img))
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
  f.write('plot \'%s\' using 2:xtic(1) ti "", for [i=3:%d] \'\' using i ti ""\n' % (output_csv, len(vectors_filtered[0])))



 print('ok')

def main_requests(host, database, username, password, output_csv, output_gnuplot, output_img):
 """Generate a CSV file (output_csv) and a GNUPLOT file (output_gnuplot) to generate graphbar (output_img) containing the number of requests received for each CID"""
 sql = psycopg2.connect(host=host, database=database, user=username, password=password)

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

  with open(output_csv, 'w') as f:
   f.write('"File identifier";\t"#requests";\t"mean"\n')
   for i,r in enumerate(points):
    f.write('%s;\t%s;\t%s\n' % (str(i), r, mean_))

 with open(output_gnuplot, 'w') as f:
  f.write('reset\n')
  f.write('fontsize = 18\n')
  f.write('set terminal png size 1024,768\n')
  f.write('set encoding utf8\n')
  f.write('set output \'%s\'\n' % (output_img))
  f.write('set style line 12 lc rgb \'#808080\' lt 0 lw 1\n')
  f.write('set style fill solid 1.00 border 0\n')
  f.write('set style data histogram\n')
  f.write('set grid ytics\n')
  f.write('set xlabel "File identifier (CID)"\n')
  f.write('set ylabel "Number of requests for the file"\n')

  c = 10**(math.ceil(math.log(max_, 10)))
  f.write('set xrange [0:%d]\n' % (len_) )
  f.write('set yrange [0.1:%d]\n' % (c) )

  f.write('unset xtics\n')
  f.write('set logscale y\n')
  f.write('plot \'%s\' using 2 ti "" lt 1 lc rgb \'#849c75\' fillstyle pattern 8 border, \\\n' % (output_csv))
  f.write('\'\' using 3 smooth csplines ti "mean" lt 1 lc rgb \'#0086ee\'\n')


def main_replicates(host, database, username, password, output_csv, output_gnuplot, output_img):
 """Generate a CSV file (output_csv) and a GNUPLOT file (output_gnuplot) to generate graphbar (output_img) containing the number of replicas for each CID"""
 sql = psycopg2.connect(host=host, database=database, user=username, password=password)

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

  with open(output_csv, 'w') as f:
   f.write('"File identifier";\t"#replicas";\t"mean"\n')
   for i,r in enumerate(points):
    f.write('%s;\t%s;\t%s\n' % (str(i), r, mean_))

 with open(output_gnuplot, 'w') as f:
  f.write('reset\n')
  f.write('fontsize = 18\n')
  f.write('set terminal png size 1024,768\n')
  f.write('set encoding utf8\n')
  f.write('set output \'%s\'\n' % (output_img))
  f.write('set style line 12 lc rgb \'#808080\' lt 0 lw 1\n')
  f.write('set style fill solid 1.00 border 0\n')
  f.write('set style data histogram\n')
  f.write('set grid ytics\n')
  f.write('set xlabel "File identifier (CID)"\n')
  f.write('set ylabel "Number of replicas"\n')

  c = 10**(math.ceil(math.log(max_, 10)))
  f.write('set xrange [0:%d]\n' % (len_) )
  f.write('set yrange [0.1:%d]\n' % (c) )

  f.write('unset xtics\n')
  f.write('set logscale y\n')
  f.write('plot \'%s\' using 2 ti "" lt 1 lc rgb \'#849c75\' fillstyle pattern 8 border, \\\n' % (output_csv))
  f.write('\'\' using 3 smooth csplines ti "mean" lt 1 lc rgb \'#0086ee\'\n')


if '__main__' == __name__:
 if len(sys.argv) < 8:
  print('Usage: %s dbhost dbname dbusername dbpassword output_csv output_gnuplot output_img' % (sys.argv[0]), file=sys.stderr)
  sys.exit(1)

 host = sys.argv[1]
 database = sys.argv[2]
 username = sys.argv[3]
 password = sys.argv[4]
 output_csv = sys.argv[5]
 output_gnuplot = sys.argv[6]
 output_img = sys.argv[7]

 output_csv_replicates = "%s_replicates.%s" % (output_csv.split(".")[0], '.'.join(output_csv.split(".")[1:]))
 output_csv_requests = "%s_requests.%s" % (output_csv.split(".")[0], '.'.join(output_csv.split(".")[1:]))
 output_csv_days = "%s_days.%s" % (output_csv.split(".")[0], '.'.join(output_csv.split(".")[1:]))

 output_gnuplot_replicates = "%s_replicates.%s" % (output_gnuplot.split(".")[0], '.'.join(output_gnuplot.split(".")[1:]))
 output_gnuplot_requests = "%s_requests.%s" % (output_gnuplot.split(".")[0], '.'.join(output_gnuplot.split(".")[1:]))
 output_gnuplot_days = "%s_days.%s" % (output_gnuplot.split(".")[0], '.'.join(output_gnuplot.split(".")[1:]))

 output_img_replicates = "%s_replicates.%s" % (output_img.split(".")[0], '.'.join(output_img.split(".")[1:]))
 output_img_requests = "%s_requests.%s" % (output_img.split(".")[0], '.'.join(output_img.split(".")[1:]))
 output_img_days = "%s_days.%s" % (output_img.split(".")[0], '.'.join(output_img.split(".")[1:]))


 main_replicates(host, database, username, password, output_csv_replicates, output_gnuplot_replicates, output_img_replicates)
 main_requests(host, database, username, password, output_csv_requests, output_gnuplot_requests, output_img_requests)
 main_days(host, database, username, password, output_csv_days, output_gnuplot_days, output_img_days)
