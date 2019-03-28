import csv
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
            <MsgId>MSG26022a8fb83cf1a515099ade7bdc3afc</MsgId>
            <CreDtTm>2019-03-27T11:25:44.620Z</CreDtTm>
            <NbOfTxs>1</NbOfTxs>
            <CtrlSum>0.01</CtrlSum>
            <InitgPty>
                <Nm>ALLG. DEUTSCHER FAHRRAD-CLUB KREISVERBAND MÜNCH. ADFC</Nm>
            </InitgPty>
        </GrpHdr>
        <PmtInf>
            <PmtInfId>PIIa671997ba9d14b0085f75f1353e9d008</PmtInfId>
            <PmtMtd>DD</PmtMtd>
            <NbOfTxs>1</NbOfTxs>
            <CtrlSum>0.01</CtrlSum>
            <PmtTpInf>
                <SvcLvl>
                    <Cd>SEPA</Cd>
                </SvcLvl>
                <LclInstrm>
                    <Cd>CORE</Cd>
                </LclInstrm>
                <SeqTp>OOFF</SeqTp>
            </PmtTpInf>
            <ReqdColltnDt>2019-03-29</ReqdColltnDt>
            <Cdtr>
                <Nm>ALLG. DEUTSCHER FAHRRAD-CLUB KREISVERBAND MÜNCH. ADFC</Nm>
            </Cdtr>
            <CdtrAcct>
                <Id>
                    <IBAN>DE62701500000904157781</IBAN>
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
                            <Id>DE44ZZZ00000793122</Id>
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
                        <MndtId>ADFC-M-RFS-2018</MndtId>
                        <DtOfSgntr>2019-03-27</DtOfSgntr>
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
                    <Nm>Vorname Nachname</Nm>
                </Dbtr>
                <DbtrAcct>
                    <Id>
                        <IBAN>DE12341234123412341234</IBAN>
                    </Id>
                </DbtrAcct>
                <RmtInf>
                    <Ustrd>Zweck</Ustrd>
                </RmtInf>
            </DrctDbtTxInf>
        </PmtInf>
    </CstmrDrctDbtInitn>
</Document>
"""

fieldnames = ["Vorname", "Name", "Lastschrift: Name des Kontoinhabers", "Lastschrift: IBAN-Kontonummer", "Betrag", "Zweck"] # adapt to field names in csv file
charset = digits + ascii_uppercase
vorname = fieldnames[0]
name = fieldnames[1]
ktoinh = fieldnames[2]
iban = fieldnames[3]
betrag = fieldnames[4]
zweck = fieldnames[5]

decCtx = getcontext()
decCtx.prec = 7 # 5.2 digits, max=99999.99

class Excel1(csv.Dialect):
    """Describe the usual properties of Excel-generated CSV files."""
    delimiter = ','
    quotechar = '"'
    doublequote = True
    skipinitialspace = False
    lineterminator = '\n'
    quoting = csv.QUOTE_MINIMAL

class Excel2(csv.Dialect):
    """Describe the usual properties of Excel-generated CSV files."""
    delimiter = ';'
    quotechar = '"'
    doublequote = True
    skipinitialspace = False
    lineterminator = '\n'
    quoting = csv.QUOTE_MINIMAL


def addBetraege(entries):
    sum = Decimal("0.00")
    for row in entries:
        sum = sum + row[betrag]
    return sum

def randomId(length):
    r1 = random.choice(ascii_uppercase)  # first a letter
    r2 = [random.choice(charset) for _ in range(length - 1)]  # then any mixture of capitalletters and numbers
    return r1 + ''.join(r2)

class Ebics:
    fieldnames = ["Vorname", "Name", "Lastschrift: Name des Kontoinhabers", "Lastschrift: IBAN-Kontonummer", "Betrag", "Zweck"] # adapt to field names in csv file
    charset = digits + ascii_uppercase
    vorname = fieldnames[0]
    name = fieldnames[1]
    ktoinh = fieldnames[2]
    iban = fieldnames[3]
    betrag = fieldnames[4]
    zweck = fieldnames[5]

    decCtx = getcontext()
    decCtx.prec = 7 # 5.2 digits, max=99999.99

    def __init__(self, inputfilesA, outputfileA, stdbetragA, sepA, stdzweckA, mandatA, ebicsA):
        self.inputFiles = inputfilesA
        self.outputFile = outputfileA
        self.stdbetrag = stdbetragA
        self.sep = sepA
        self.stdzweck = stdzweckA
        self.mandat = mandatA
        self.ebics = ebicsA
        self.nr_einzug = 0
        self.nr_bezahlt = 0
        self.nr_enthalten = 0

    def getStatistics(self):
        return ( self.nr_einzug, self.nr_bezahlt, self.nr_enthalten)

    def parseCSV(self, inputPath):
        vals = []
        csv.register_dialect("excel1", Excel1)
        csv.register_dialect("excel2", Excel2)
        with open(inputPath, 'r', newline='', encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile, None, dialect="excel1" if self.sep == ',' else "excel2")
            for row in reader:
                if not iban in row:
                    continue
                if row[iban] == "" or len(row[iban]) < 22:
                    continue
                self.nr_einzug += 1
                if "bezahlt" in list(row.values()):
                    self.nr_bezahlt += 1
                    continue
                self.nr_enthalten += 1
                if not betrag in row:
                    if self.stdbetrag == "":
                        raise ValueError("Standard-Betrag nicht definiert (mit -b)")
                    row[betrag] = self.stdbetrag
                row[betrag] = Decimal(row[betrag].replace(',', '.'))  # 3,14 -> 3.14
                inh = row[ktoinh]
                if len(inh) < 5 or inh.startswith("dto") or inh.startswith("ditto"):
                    row[ktoinh] = row[vorname] + " " + row[name]
                if not zweck in row:
                    if self.stdzweck == "":
                        raise ValueError("Standard-Verwendungszweck nicht definiert (mit -z)")
                    row[zweck] = self.stdzweck
                vals.append({x:row[x] for x in fieldnames})
        return vals

    def fillinIDs(self):
        msgid = self.xmlt.getElementsByTagName("MsgId")
        val = "MSG" + randomId(32)
        msgid[0].childNodes[0] = self.xmlt.createTextNode(val)
        piid = self.xmlt.getElementsByTagName("PmtInfId")
        val = "PII" + randomId(32)
        piid[0].childNodes[0] = self.xmlt.createTextNode(val)

    def fillinSumme(self, summe, cnt):
        ctrlSum = self.xmlt.getElementsByTagName("CtrlSum")
        for cs in ctrlSum:
            cs.childNodes[0] = self.xmlt.createTextNode(str(summe))
        nbOfTxs = self.xmlt.getElementsByTagName("NbOfTxs")
        for nr in nbOfTxs:
            nr.childNodes[0] = self.xmlt.createTextNode(str(cnt))

    def fillin(self, entries):
        pmtInf = self.xmlt.getElementsByTagName("PmtInf")[0]
        drctDbtTxInf = pmtInf.getElementsByTagName("DrctDbtTxInf")[0]
        x = pmtInf.childNodes.index(drctDbtTxInf)
        drctDbtTxInf = copy.deepcopy(drctDbtTxInf)
        nl1 = pmtInf.childNodes[x - 1]
        nl2 = pmtInf.childNodes[x + 1]
        pmtInf.childNodes = pmtInf.childNodes[0:x]
        for entry in entries:
            newtx = copy.deepcopy(drctDbtTxInf)
            nm = newtx.getElementsByTagName("Nm")
            nm[0].childNodes[0] = self.xmlt.createTextNode(entry[ktoinh])
            ibn = newtx.getElementsByTagName("IBAN")
            ibn[0].childNodes[0] = self.xmlt.createTextNode(entry[iban])
            amt = newtx.getElementsByTagName("InstdAmt")
            amt[0].childNodes[0] = self.xmlt.createTextNode(str(entry[betrag]))
            ustrd = newtx.getElementsByTagName("Ustrd")
            ustrd[0].childNodes[0] = self.xmlt.createTextNode(str(entry[zweck]))
            pmtInf.childNodes.append(newtx)
            pmtInf.childNodes.append(copy.copy(nl1))
            mndtId = newtx.getElementsByTagName("MndtId")
            mndtId[0].childNodes[0] = self.xmlt.createTextNode(self.mandat)
        pmtInf.childNodes[len(pmtInf.childNodes) - 1] = copy.copy(nl2)

    def fillinDates(self):
        creDtTm = self.xmlt.getElementsByTagName("CreDtTm")
        now = datetime.datetime.utcnow()
        d = now.isoformat(timespec="milliseconds") + "Z"
        creDtTm[0].childNodes[0] = self.xmlt.createTextNode(d)
        reqdColltnDt = self.xmlt.getElementsByTagName("ReqdColltnDt")
        day2 = datetime.date.today() + datetime.timedelta(days=2)
        d = day2.isoformat()
        reqdColltnDt[0].childNodes[0] = self.xmlt.createTextNode(d)

    def createEbicsXml(self):
        entries = []
        for inp in self.inputFiles.split(','):
            entries.extend(self.parseCSV(inp))
        if len(entries) == 0:
            return None
        summe = addBetraege(entries)
        template = xmls
        if self.ebics != None and self.ebics != "":
            with open(self.ebics, "r", encoding="utf-8") as f:
                template = f.read()
        self.xmlt = parseString(template)
        self.fillinIDs()
        self.fillinDates()
        self.fillinSumme(summe, len(entries))
        self.fillin(entries)
        # self.xmlt.standalone = True or "yes" has no effect
        pr = self.xmlt.toxml(encoding="utf-8")
        pr = pr[0:36] + b' standalone="yes"' + pr[36:]  # minidom has problems with standalone param
        with open(self.outputFile, "wb") as o:
            o.write(pr)
        return pr