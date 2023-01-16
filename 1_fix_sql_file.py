import sys
import re


def main(filename):
 pattern = re.compile(r'^insert into (.+);$')

 with open(filename, 'rb') as f:
  for line in f.readlines():
   l = None
   try:
    l = line.decode()
   except:
    continue
   ok = pattern.match(l)
   if ok:
    print(l.replace('"', "'").replace("'None'", "null"))


if '__main__' == __name__:
 main(sys.argv[1])
