import xml.sax, os, sys, re, pdb
#from nltk.stem.porter import PorterStemmer
#from stemming.porter2 import stem
#import Stemmer
from stemming.porter2 import stem

numberOfDocuments = 0
numberOfFiles = 0
INTMIN = -sys.maxint - 1
idMapping = {}
titles = []
stopwords = {}
outputPath = ""
#stemmer = Stemmer.Stemmer('english')
#stemmer = PorterStemmer()
titleDictionary = {}
infoboxDictionary = {}
bodyDictionary = {}
categoryDictionary = {}
linksDictionary = {}
referencesDictionary = {}

class xmlHandler(xml.sax.ContentHandler):
    def __init__(self):
        xml.sax.ContentHandler.__init__(self)
        self.id = "none"
        self.title = ""
        self.infobox = ""
        self.body = ""
        self.category = ""
        self.links = ""
        self.references = ""
        self.text = ""
        self.content = ""

    def startElement(self, tag, attributes):
        if tag == "page":
            global numberOfDocuments
            numberOfDocuments += 1
            self.id = "none"

    def endElement(self, tag):
        if tag == "page":
            self.process(self.infobox.lower(), "infobox")
            self.process(self.category.lower(), "category")
            self.process(self.references.lower(), "references")
            self.process(self.body.lower(), "body")
            self.process(self.links.lower(), "links")
            self.process(self.title.lower(), "title")
            global numberOfDocuments
            global numberOfFiles
            #if numberOfDocuments % 2000 == 0:
            #    writeToFile()
            #    numberOfFiles += 1
        elif tag == "id":
            if self.id == "none":
                self.id = (self.content)
                global idMapping
                idMapping[self.id] = numberOfDocuments
        elif tag == "title":
            self.title = self.content
            global titles
            titles.append(self.content)
        elif tag == "text":
            self.text = self.content
            self.categorize()
        self.content = ""

    def characters(self, content):
        encodedContent = content.encode("utf-8").strip()
        if encodedContent:
            self.content = self.content + "\n" + encodedContent

    def categorize(self):
        lines = self.text.strip()
        lines = lines.split('\n')
        self.infobox = ""
        self.body = ""
        self.category = ""
        self.links = ""
        self.references = ""
        group = "none"

        '''
        infobox starts with "{{Infobox" and ends with "}}" note: infoboxes are multi-line
        category starts with "[[Category" and ends with "]]"
        external links have "==External links=="
        references have "==References=="
        '''

        for line in lines:
            if line.startswith("{{Infobox"):
                group = "infobox"
                continue
            elif group == "infobox" and line == "}}":
                group = "none"
                continue
            elif line.startswith("==References==") or line.startswith("== References =="):
                group = "references"
                continue
            elif group == "references" and (( line.startswith("==") and line.find("Reference")==-1) or line.startswith("[[Category:") or line.startswith("{{")):
                group = "none"
            elif group == "external" and line.startswith("[[Category:"):
                group = "none"
                continue
            elif line.startswith("==External links=="):
                group = "external"
                continue
            if line.startswith("[[Category:"):
                self.category = self.category + "\n" + line[11:-2]
            elif group == "none":
                self.body = self.body + "\n" + line
            elif group == "infobox":
                self.infobox = self.infobox + "\n" + line
            elif group == "references":
                self.references = self.references + "\n" + line
            elif group == "external":
                self.links = self.links + "\n" + line

    def process(self, data, field):
        listOfWords = [word.strip() for word in re.compile(r'[^a-z]+').split(data) if len(word)>0]
        processedWords = []
        global stopwords
        for word in listOfWords:
            if word not in stopwords:
                processedWords.append(stem(word))
        count = {}
        for word in processedWords:
            if word not in stopwords:
                if word in count:
                    count[word]+=1
                else:
                    count[word]=1
        global idMapping
        if field == "title":
            global titleDictionary
            for (key, value) in count.iteritems():
                if key in titleDictionary:
                    tempList = [idMapping[self.id], value]
                    titleDictionary[key].append(tempList)
                else:
                    titleDictionary[key] = [[idMapping[self.id], value]]
        elif field == "infobox":
            global infoboxDictionary
            for (key, value) in count.iteritems():
                if key in infoboxDictionary:
                    tempList = [idMapping[self.id], value]
                    infoboxDictionary[key].append(tempList)
                else:
                    infoboxDictionary[key] = [[idMapping[self.id], value]]
        elif field == "body":
            global bodyDictionary
            for (key, value) in count.iteritems():
                if key in bodyDictionary:
                    tempList = [idMapping[self.id], value]
                    bodyDictionary[key].append(tempList)
                else:
                    bodyDictionary[key] = [[idMapping[self.id], value]]
        elif field == "category":
            global categoryDictionary
            for (key, value) in count.iteritems():
                if key in categoryDictionary:
                    tempList = [idMapping[self.id], value]
                    categoryDictionary[key].append(tempList)
                else:
                    categoryDictionary[key] = [[idMapping[self.id], value]]
        elif field == "links":
            global linksDictionary
            for (key, value) in count.iteritems():
                if key in linksDictionary:
                    tempList = [idMapping[self.id], value]
                    linksDictionary[key].append(tempList)
                else:
                    linksDictionary[key] = [[idMapping[self.id], value]]
        elif field == "references":
            global referencesDictionary
            for (key, value) in count.iteritems():
                if key in referencesDictionary:
                    tempList = [idMapping[self.id], value]
                    referencesDictionary[key].append(tempList)
                else:
                    referencesDictionary[key] = [[idMapping[self.id], value]]

def writeToFile():
    global titleDictionary
    global infoboxDictionary
    global bodyDictionary
    global categoryDictionary
    global linksDictionary
    global referencesDictionary
    global numberOfFiles
    global outputPath
    fileName = str(outputPath) + "/title" + str(numberOfFiles) + ".txt"
    #fileName = "./IndexFiles/Title/title" + str(numberOfFiles) + ".txt"
    f = open(fileName, "w")
    keys = titleDictionary.keys()
    keys.sort()
    for key in keys:
        entry = key + ":"
        for pair in titleDictionary[key]:
            entry = entry + str(pair[0]) + "," + str(pair[1]) + "|"
        entry = entry[:-1]
        entry += "\n"
        f.write(entry)
    f.close()
    fileName = str(outputPath) + "/infobox" + str(numberOfFiles) + ".txt"
    #fileName = "./IndexFiles/Infobox/infobox" + str(numberOfFiles) + ".txt"
    f = open(fileName, "w")
    keys = infoboxDictionary.keys()
    keys.sort()
    for key in keys:
        entry = key + ":"
        for pair in infoboxDictionary[key]:
            entry = entry + str(pair[0]) + "," + str(pair[1]) + "|"
        entry = entry[:-1]
        entry += "\n"
        f.write(entry)
    f.close()
    fileName = str(outputPath) + "/body" + str(numberOfFiles) + ".txt"
    #fileName = "./IndexFiles/Body/body" + str(numberOfFiles) + ".txt"
    f = open(fileName, "w")
    keys = bodyDictionary.keys()
    keys.sort()
    for key in keys:
        entry = key + ":"
        for pair in bodyDictionary[key]:
            entry = entry + str(pair[0]) + "," + str(pair[1]) + "|"
        entry = entry[:-1]
        entry += "\n"
        f.write(entry)
    f.close()
    fileName = str(outputPath) + "/category" + str(numberOfFiles) + ".txt"
    #fileName = "./IndexFiles/Category/category" + str(numberOfFiles) + ".txt"
    f = open(fileName, "w")
    keys = categoryDictionary.keys()
    keys.sort()
    for key in keys:
        entry = key + ":"
        for pair in categoryDictionary[key]:
            entry = entry + str(pair[0]) + "," + str(pair[1]) + "|"
        entry = entry[:-1]
        entry += "\n"
        f.write(entry)
    f.close()
    fileName = str(outputPath) + "/links" + str(numberOfFiles) + ".txt"
    #fileName = "./IndexFiles/Links/links" + str(numberOfFiles) + ".txt"
    f = open(fileName, "w")
    keys = linksDictionary.keys()
    keys.sort()
    for key in keys:
        entry = key + ":"
        for pair in linksDictionary[key]:
            entry = entry + str(pair[0]) + "," + str(pair[1]) + "|"
        entry = entry[:-1]
        entry += "\n"
        f.write(entry)
    f.close()
    fileName = str(outputPath) + "/references" + str(numberOfFiles) + ".txt"
    #fileName = "./IndexFiles/References/references" + str(numberOfFiles) + ".txt"
    f = open(fileName, "w")
    keys = referencesDictionary.keys()
    keys.sort()
    for key in keys:
        entry = key + ":"
        for pair in referencesDictionary[key]:
            entry = entry + str(pair[0]) + "," + str(pair[1]) + "|"
        entry = entry[:-1]
        entry += "\n"
        f.write(entry)
    f.close()
    titleDictionary.clear()
    infoboxDictionary.clear()
    bodyDictionary.clear()
    categoryDictionary.clear()
    linksDictionary.clear()
    referencesDictionary.clear()

if __name__ == "__main__":
    corpus = sys.argv[1]
    outputPath = sys.argv[2]
    #corpus = "wiki-search-small.xml"
    with open('stopwords.txt') as f:
        for words in f:
            word = words.strip()
            if word:
                stopwords[word] = 1
    xml.sax.parse(open(corpus, "r"), xmlHandler())
    writeToFile()
    numberOfFiles += 1
    counter = 0
    fileName = str(outputPath) + "/idMapping.txt"
    #fileName = "./IndexFiles/idMapping.txt"
    f = open(fileName, "w")
    for (key, value) in idMapping.iteritems():
        titles[counter] = titles[counter].strip()
        entry = str(key) + "|" + str(value) + "|" + titles[counter]
        entry += "\n"
        counter += 1
        f.write(entry)
    f.close
