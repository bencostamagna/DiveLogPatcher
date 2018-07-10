import csv
from xml.dom import minidom


def fillCylinder(node, start, end):
    node.attributes['size'] = '12.0 l'
    node.attributes['workpressure'] = '200.0 bar'
    node.attributes['description'] = '12ℓ 200 bar'
    if start != 0:
        node.attributes['start'] = formatPres(start)
        node.attributes['end'] = formatPres(end)

def fillWeight(node, weight):
    node.attributes['description'] = 'belt'
    node.attributes['weight'] = formatWeight(weight)

def formatTime(t):
    return "%02d:%02d min" % (t/60, t%60)
def formatPres(pres):
    return "%d bar" % (pres)
def formatWeight(w):
    return "%d kg" % (w)
def formatTemp(t):
    return "%d C" % (t)

duration={}
bar_start={}
bar_end={}
weight={}
temp={}
divemaster={}
boat={}
buddy={}
notes={}

with open('depthtable.csv', 'r') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=';', quotechar='\"')
    for row in spamreader:
        duration[row[0]]=float(row[1])
        bar_start[row[0]]=int(row[2])
        bar_end[row[0]]=int(row[3])
        weight[row[0]]=float(row[4])
        temp[row[0]]=int(row[5])
        divemaster[row[0]]=row[6]
        boat[row[0]]=row[7]
        buddy[row[0]]=row[8]
        notes[row[0]]=row[9]


xmldoc = minidom.parse('logbook.udcf')
itemlist = xmldoc.getElementsByTagName('dive')

for s in itemlist:
    print("Processing dive "+s.attributes['number'].value+"...")
    dive_number=s.attributes['number'].value

    #Fix for duration and boat tag
    if (s.attributes['number'].value not in duration):
        print("dive "+dive_number+" not found")
        continue
    s.attributes['duration'] = formatTime(duration[dive_number])
    s.attributes['tags'] = boat[dive_number]
#    print(dive_number+" -> "+s.attributes['duration'].value)

    #Fix for buddy, divemaster and notes
    if len(divemaster[dive_number])>0:
        node=xmldoc.createElement("divemaster")
        txt=xmldoc.createTextNode(divemaster[dive_number])
        node.appendChild(txt)
        s.appendChild(node)
    if len(buddy[dive_number])>0:
        node=xmldoc.createElement("buddy")
        txt=xmldoc.createTextNode(buddy[dive_number])
        node.appendChild(txt)
        s.appendChild(node)
    if len(notes[dive_number])>0:
        node=xmldoc.createElement("notes")
        txt=xmldoc.createTextNode(notes[dive_number])
        node.appendChild(txt)
        s.appendChild(node)

    #Fix for cylinder
    #  <cylinder size='12.0 l' workpressure='200.0 bar' description='12ℓ 200 bar' start='200.0 bar' end='70.0 bar' />

    hasCyl=False
    for child in s.childNodes:
        if (child.nodeName == "cylinder"):
            fillCylinder(child, bar_start[dive_number], bar_end[dive_number])
            hasCyl=True
    if not hasCyl:
        node = xmldoc.createElement("cylinder")
        fillCylinder(node, bar_start[dive_number], bar_end[dive_number])
        s.appendChild(node)

    #Fix for weightsystem
    #  <weightsystem weight='0.0 kg' description='belt' />
    hasWeight=False
    for child in s.childNodes:
        if (child.nodeName == "weightsystem"):
            fillWeight(child, weight[dive_number])
            hasWeight=True
    if not hasWeight:
        node = xmldoc.createElement("weightsystem")
        fillWeight(node, weight[dive_number])
        s.appendChild(node)

    #Fix for temperature
    #  <divetemperature water='24.0 C'/>
    if temp[dive_number] != 0:
        hasTemp=False
        for child in s.childNodes:
            if (child.nodeName == "divetemperature"):
                child.attributes['water'] = formatTemp(temp[dive_number])
                hasTemp=True
        if not hasTemp:
            node = xmldoc.createElement("divetemperature")
            node.attributes['water'] = formatTemp(temp[dive_number])
            s.appendChild(node)
    else:
        print ("No data about water temperature, skipping.")

    #Fix for profiles
    for comp in s.childNodes:
        if (comp.nodeName == "divecomputer"):
            max_depth=""

            for child in comp.childNodes:
                if (child.nodeName == "depth"):
                    max_depth=child.attributes['max'].value
                if (child.nodeName == "sample"):
                    comp.removeChild(child)
            print("Max depth is "+max_depth)

            if (len(max_depth) > 0):
                # <sample time='41:27 min' depth='5.0 m' />
                sample=xmldoc.createElement("sample")
                sample.attributes['time'] = '0:00 min'
                sample.attributes['depth'] = '0.0 m'
                comp.appendChild(sample)

                sample=xmldoc.createElement("sample")
                sample.attributes['time'] = '1:00 min'
                sample.attributes['depth'] = max_depth
                comp.appendChild(sample)

                sample=xmldoc.createElement("sample")
                sample.attributes['time'] = formatTime(duration[dive_number]-300)
                sample.attributes['depth'] = max_depth
                comp.appendChild(sample)

                sample=xmldoc.createElement("sample")
                sample.attributes['time'] = formatTime(duration[dive_number]-180)
                sample.attributes['depth'] = "5.0 m"
                comp.appendChild(sample)

                sample=xmldoc.createElement("sample")
                sample.attributes['time'] = formatTime(duration[dive_number]-10)
                sample.attributes['depth'] = "5.0 m"
                comp.appendChild(sample)

                sample=xmldoc.createElement("sample")
                sample.attributes['time'] = formatTime(duration[dive_number])
                sample.attributes['depth'] = "0.0 m"
                comp.appendChild(sample)

with open("new_logbook.udcf", "w") as f:
    xmldoc.writexml(f)
