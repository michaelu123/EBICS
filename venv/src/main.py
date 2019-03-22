import csv
import argparse
import random
import copy
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

fieldnames = ["Name", "IBAN", "Betrag"] # adapt to field names in csv file
charset = digits + ascii_uppercase
name = fieldnames[0]
iban = fieldnames[1]
betrag = fieldnames[2]
decCtx = getcontext()
decCtx.prec = 7 # 5.2 digits, max=99999.99

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
    csv.register_dialect("excel2", excel2)
    with open(inputPath, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames, dialect="excel2")
        for row in reader:
            if row[betrag] == betrag:
                continue
            row[betrag] = Decimal(row[betrag].replace(',', '.'))  # 3,14 -> 3.14
            vals.append(row)
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
        nm[0].childNodes[0] = xmlt.createTextNode(entry[name])
        ibn = newtx.getElementsByTagName("IBAN")
        ibn[0].childNodes[0] = xmlt.createTextNode(entry[iban])
        amt = newtx.getElementsByTagName("InstdAmt")
        amt[0].childNodes[0] = xmlt.createTextNode(str(entry[betrag]))
        pmtInf.childNodes.append(newtx)
        pmtInf.childNodes.append(copy.deepcopy(nl1))
    pmtInf.childNodes[len(pmtInf.childNodes) - 1] = copy.deepcopy(nl2)

parser = argparse.ArgumentParser(description="Erzeuge EBICS-Datei aus csv-Datei")
parser.add_argument("-i", "--input", dest="input", help="Input-Datei im CSV-Format")
parser.add_argument("-o", "--output", dest="output", default="ebics.xml", help="Output-Datei im EBICS-Format")
args = parser.parse_args()
inputFile = args.input
outputFile = args.output

entries = parseCSV(inputFile)
summe = addBetraege(entries)
xmlt = parseString(xmls)
fillinIDs(xmlt)
fillinSumme(xmlt, summe, len(entries))
fillin(entries)
pr = xmlt.toxml()
print(pr)

