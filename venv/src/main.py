import csv
import argparse
import random
import copy
import datetime
from string import digits, ascii_uppercase
from xml.dom.minidom import *
from decimal import Decimal,getcontext

xmls = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.008.001.02" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="urn:iso:std:iso:20022:tech:xsd:pain.008.001.02 pain.008.001.02.xsd">
    <CstmrDrctDbtInitn>
        <GrpHdr>
            <MsgId>12345678901234567890123456789012345</MsgId>
            <CreDtTm>2019-03-18T06:21:51.788Z</CreDtTm>
            <NbOfTxs>2</NbOfTxs>
            <CtrlSum>0.02</CtrlSum>
            <InitgPty>
                <Nm>Mustermann, Max</Nm>
            </InitgPty>
        </GrpHdr>
        <PmtInf>
            <PmtInfId>PII12345678901234567890123456789012</PmtInfId>
            <PmtMtd>DD</PmtMtd>
            <NbOfTxs>2</NbOfTxs>
            <CtrlSum>0.02</CtrlSum>
            <PmtTpInf>
                <SvcLvl>
                    <Cd>SEPA</Cd>
                </SvcLvl>
                <LclInstrm>
                    <Cd>B2B</Cd>
                </LclInstrm>
                <SeqTp>OOFF</SeqTp>
            </PmtTpInf>
            <ReqdColltnDt>2019-03-21</ReqdColltnDt>
            <Cdtr>
                <Nm>Mustermann, Max</Nm>
            </Cdtr>
            <CdtrAcct>
                <Id>
                    <IBAN>DE97701500000000123456</IBAN>
                </Id>
            </CdtrAcct>
            <CdtrAgt>
                <FinInstnId>
                    <BIC>SSKMDEMMXXX</BIC>
                </FinInstnId>
            </CdtrAgt>
            <ChrgBr>SLEV</ChrgBr>
            <CdtrSchmeId>
                <Id>
                    <PrvtId>
                        <Othr>
                            <Id>DE98ZZZ09999999999</Id>
                            <SchmeNm>
                                <Prtry>SEPA</Prtry>
                            </SchmeNm>
                        </Othr>
                    </PrvtId>
                </Id>
            </CdtrSchmeId>
            <DrctDbtTxInf>
                <PmtId>
                    <EndToEndId>NOTPROVIDED</EndToEndId>
                </PmtId>
                <InstdAmt Ccy="EUR">0.01</InstdAmt>
                <DrctDbtTx>
                    <MndtRltdInf>
                        <MndtId>heins</MndtId>
                        <DtOfSgntr>2019-01-01</DtOfSgntr>
                    </MndtRltdInf>
                </DrctDbtTx>
                <DbtrAgt>
                    <FinInstnId>
                        <Othr>
                            <Id>NOTPROVIDED</Id>
                        </Othr>
                    </FinInstnId>
                </DbtrAgt>
                <Dbtr>
                    <Nm>Hans Eins</Nm>
                </Dbtr>
                <DbtrAcct>
                    <Id>
                        <IBAN>DE15700202702530131478</IBAN>
                    </Id>
                </DbtrAcct>
                <RmtInf>
                    <Ustrd>test1</Ustrd>
                </RmtInf>
            </DrctDbtTxInf>
        </PmtInf>
    </CstmrDrctDbtInitn>
</Document>
"""

fieldnames = ["Vorname", "Name", "Lastschrift: Name des Kontoinhabers", "Lastschrift: IBAN-Kontonummer", "Betrag", "Verwendungszweck"] # adapt to field names in csv file
charset = digits + ascii_uppercase
vorname = fieldnames[0]
name = fieldnames[1]
ktoinh = fieldnames[2]
iban = fieldnames[3]
betrag = fieldnames[4]
zweck = fieldnames[5]

decCtx = getcontext()
decCtx.prec = 7 # 5.2 digits, max=99999.99
sep = ','

class excel1(csv.Dialect):
    """Describe the usual properties of Excel-generated CSV files."""
    delimiter = ','
    quotechar = '"'
    doublequote = True
    skipinitialspace = False
    lineterminator = '\n'
    quoting = csv.QUOTE_MINIMAL

class excel2(csv.Dialect):
    """Describe the usual properties of Excel-generated CSV files."""
    delimiter = ';'
    quotechar = '"'
    doublequote = True
    skipinitialspace = False
    lineterminator = '\n'
    quoting = csv.QUOTE_MINIMAL


def parseCSV(inputPath):
    vals = []
    csv.register_dialect("excel1", excel1)
    csv.register_dialect("excel2", excel2)
    with open(inputPath, 'r', newline='', encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile, None, dialect="excel1" if sep == ',' else "excel2")
        for row in reader:
            if not iban in row:
                continue
            if row[iban] == "" or len(row[iban]) < 22:
                continue
            if not betrag in row:
                if stdbetrag == "":
                    raise ValueError("Standard-Betrag nicht definiert (mit -b)")
                row[betrag] = stdbetrag
            row[betrag] = Decimal(row[betrag].replace(',', '.'))  # 3,14 -> 3.14
            inh = row[ktoinh]
            if len(inh) < 5 or inh.startswith("dto") or inh.startswith("ditto"):
                row[ktoinh] = row[vorname] + " " + row[name]
            if not zweck in row:
                if stdzweck == "":
                    raise ValueError("Standard-Verwendungszweck nicht definiert (mit -z)")
                row[zweck] = stdzweck
            vals.append({x:row[x] for x in fieldnames})
    return vals

def addBetraege(entries):
    sum = Decimal("0.00")
    for row in entries:
        sum = sum + row[betrag]
    return sum

def randomId(length):
    r1 = random.choice(ascii_uppercase) # first a letter
    r2 = [ random.choice(charset) for _ in range(length - 1)] # then any mixture of capitalletters and numbers
    return r1 + ''.join(r2)

def fillinIDs(xmlt):
    msgid = xmlt.getElementsByTagName("MsgId")
    val = randomId(35)
    msgid[0].childNodes[0] = xmlt.createTextNode(val)
    piid = xmlt.getElementsByTagName("PmtInfId")
    val = "PII" + randomId(32)
    piid[0].childNodes[0] = xmlt.createTextNode(val)

def fillinSumme(xmlt, summe, cnt):
    ctrlSum = xmlt.getElementsByTagName("CtrlSum")
    for cs in ctrlSum:
        cs.childNodes[0] = xmlt.createTextNode(str(summe))
    nbOfTxs = xmlt.getElementsByTagName("NbOfTxs")
    for nr in nbOfTxs:
        nr.childNodes[0] = xmlt.createTextNode(str(cnt))

def fillin(entries):
    pmtInf = xmlt.getElementsByTagName("PmtInf")[0]
    drctDbtTxInf = pmtInf.getElementsByTagName("DrctDbtTxInf")[0]
    x = pmtInf.childNodes.index(drctDbtTxInf)
    nl1 = pmtInf.childNodes[x - 1]
    nl2 = pmtInf.childNodes[x + 1]
    pmtInf.childNodes = pmtInf.childNodes[0:x]
    for entry in entries:
        newtx = copy.deepcopy(drctDbtTxInf)
        mndtId = newtx.getElementsByTagName("MndtId")
        mndtId[0].childNodes[0] = xmlt.createTextNode("xxx")  # ???
        nm = newtx.getElementsByTagName("Nm")
        nm[0].childNodes[0] = xmlt.createTextNode(entry[ktoinh])
        ibn = newtx.getElementsByTagName("IBAN")
        ibn[0].childNodes[0] = xmlt.createTextNode(entry[iban])
        amt = newtx.getElementsByTagName("InstdAmt")
        amt[0].childNodes[0] = xmlt.createTextNode(str(entry[betrag]))
        ustrd = newtx.getElementsByTagName("Ustrd")
        ustrd[0].childNodes[0] = xmlt.createTextNode(str(entry[zweck]))
        pmtInf.childNodes.append(newtx)
        pmtInf.childNodes.append(copy.copy(nl1))
    pmtInf.childNodes[len(pmtInf.childNodes) - 1] = copy.copy(nl2)

def fillinDates(xmlt):
    creDtTm = xmlt.getElementsByTagName("CreDtTm")
    now = datetime.datetime.now()
    d = now.isoformat(timespec="milliseconds") + "Z"
    creDtTm[0].childNodes[0] = xmlt.createTextNode(d)
    reqdColltnDt = xmlt.getElementsByTagName("ReqdColltnDt")
    today = datetime.date.today()
    d = today.isoformat()
    reqdColltnDt[0].childNodes[0] = xmlt.createTextNode(d)


parser = argparse.ArgumentParser(description="Erzeuge EBICS-Datei aus csv-Datei")
parser.add_argument("-i", "--input", dest="input", help="Input-Datei im CSV-Format")
parser.add_argument("-o", "--output", dest="output", default="ebics.xml", help="Output-Datei im EBICS-Format")
parser.add_argument("-s", "--separator", dest="sep", default=",", help="Trenner in CSV-Datei: , oder ;")
parser.add_argument("-b", "--betrag", dest="stdbetrag", default="", help="Geldbetrag falls nicht in Tabelle enthalten")
parser.add_argument("-z", "--zweck", dest="zweck", default="", help="Verwendungszweck, falls nicht in Tabelle enthalten")
args = parser.parse_args()
inputFile = args.input
outputFile = args.output
stdbetrag = args.stdbetrag
sep = args.sep
stdzweck = args.zweck

entries = parseCSV(inputFile)
summe = addBetraege(entries)
xmlt = parseString(xmls)
fillinIDs(xmlt)
fillinDates(xmlt)
fillinSumme(xmlt, summe, len(entries))
fillin(entries)
pr = xmlt.toxml()
with open(outputFile, "w") as o:
    o.write(pr)
print(pr)

