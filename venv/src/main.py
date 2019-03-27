import sys
import argparse
import ebics

parser = argparse.ArgumentParser(description="Erzeuge EBICS-Datei aus csv-Datei")
parser.add_argument("-i", "--input", dest="input", help="Liste von Input-Dateien im CSV-Format, durch Komma getrennt")
parser.add_argument("-e", "--ebics", dest="ebics", default="", help="EBICS-Template-Datei im XML-Format")
parser.add_argument("-o", "--output", dest="output", default="ebics.xml", help="Output-Datei im EBICS-Format")
parser.add_argument("-s", "--separator", dest="sep", default=",", help="Trenner in CSV-Datei: , oder ;")
parser.add_argument("-b", "--betrag", dest="stdbetrag", default="", help="Geldbetrag, falls nicht in Tabelle enthalten (Betrag)")
parser.add_argument("-z", "--zweck", dest="zweck", default="", help="Verwendungszweck, falls nicht in Tabelle enthalten (Zweck)")
parser.add_argument("-m", "--mandat", dest="mandat", default="ADFC-M-RFS-2018", help="Mandatsid, falls nicht ADFC-M-RFS-2018")
args = parser.parse_args()
if len(sys.argv) <= 1:
    parser.print_usage()
    sys.exit()

eb = ebics.Ebics(args.input, args.output, args.stdbetrag, args.sep, args.zweck, args.mandat, args.ebics)

pr = eb.createEbicsXml()
print(pr)