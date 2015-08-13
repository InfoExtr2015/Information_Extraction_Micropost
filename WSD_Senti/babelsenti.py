import urllib2
import urllib
import json
import gzip
import re
import os
import math
import functools
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt
from nltk.stem.wordnet import WordNetLemmatizer

from StringIO import StringIO
import xml.etree.ElementTree as ET


fp="./home/swn/www/admin/dump/SentiWordNet_3.0.0_20130122.txt" #Path to SentiWordNet file
synid=[]

############################################# PRE-PROCESSING OF TWEETS ################################################
sep=re.compile(r"[ \t,;.?!]+")
hasht = re.compile(r"#[a-zA-Z0-9_]+")
atp = re.compile(r"@[a-zA-Z0-9_]+")

urlStart1  = "(?:https?://|\\bwww\\.)"
commonTLDs = "(?:com|org|edu|gov|net|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|pro|tel|travel|xxx)";
ccTLDs     = '''(?:ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|
    bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|
    er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|
    hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|
    lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|
    nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|sk|
    sl|sm|sn|so|sr|ss|st|su|sv|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|
    va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|za|zm|zw)'''  
urlStart2  = "\\b(?:[A-Za-z\\d-])+(?:\\.[A-Za-z0-9]+){0,3}\\." + "(?:"+commonTLDs+"|"+ccTLDs+")"+"(?:\\."+ccTLDs+")?(?=\\W|$)"
urlBody    = "(?:[^\\.\\s<>][^\\s<>]*?)?"
punctChars = r"['\".?!,:;]"
entity     = "&(?:amp|lt|gt|quot);"
urlExtraBeforeEnd = "(?:"+punctChars+"|"+entity+")+?"
urlEnd     = "(?:\\.\\.+|[<>]|\\s|$)"
url        = re.compile(r"(?:"+urlStart1+"|"+urlStart2+")"+urlBody+"(?=(?:"+urlExtraBeforeEnd+")?"+urlEnd+")")

def splitPairs(word):
   return [(word[:i+1], word[i+1:]) for i in range(len(word))]

def segment(word):
   if not word: return []
   allSegmentations = [[first] + segment(rest)
                       for (first, rest) in splitPairs(word)]
   return max(allSegmentations, key = wordSeqFitness)

class OneGramDist(dict):
    
    def __init__(self):
        self.gramCount = 0
        for line in open('one-grams.txt'):
            (word, count) = line[:-1].split('\t')
            self[word] = int(count)
            self.gramCount += self[word]

    def __call__(self, word):
        if word in self:
            return float(self[word]) / self.gramCount
        else:
            return 1.0 / self.gramCount

singleWordProb = OneGramDist()

def wordSeqFitness(words):
   return functools.reduce(lambda x,y: x+y,
     (math.log10(singleWordProb(w)) for w in words))

def proc(s):
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', s[1:])
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1 \2', s1)
        l=segment(s2)
        s3=""
        for i in l:
            s3+=i+" "
        return s3


def urlextr(u):

        twe = url.split(u)
        newtweet=""
        for l in range(len(twe)):
            if(url.match(twe[l])):
                twe[l]=""
        for a in range(len(twe)):
            newtweet = newtweet+twe[a]+" "

        babelnet(newtweet)

##################################### WSD using Babelfy ######################################################

def babelnet(te):

        try:
        	    synid=[]
        	    service_url = 'https://babelfy.io/v1/disambiguate'

        	    lang = 'EN'
        	    key  = 'Babelfy_key_goes_here'

        	    text = sep.split(te);
        	    
        	    for i in range(len(text)):
        	            if(hasht.match(text[i]) or atp.match(text[i])):
        	                    text[i]=proc(text[i])

        	    tex=""
        	    for i in text:
        	            tex+=i+" "
        	            
        	    params = {
        	    	'text' : tex,
        	    	'lang' : lang,
        	    	'key' : key
        	    }

        	    url = service_url + '?' + urllib.urlencode(params)
        	    request = urllib2.Request(url)
        	    request.add_header('Accept-encoding', 'gzip')
        	    response = urllib2.urlopen(request)

        	    t=""
        	    if response.info().get('Content-Encoding') == 'gzip':
        	    	buf = StringIO(response.read())
        	    	f = gzip.GzipFile(fileobj=buf)
        	    	data = json.loads(f.read())

        	    	# retrieving data
        	    	for result in data:
        	        		# retrieving char fragment
        	                charFragment = result.get('charFragment')
        	                cfStart = charFragment.get('start')
        	                cfEnd = charFragment.get('end')
        	                for i in range(cfStart,cfEnd+1):
        	                        t+=tex[i];

        	                # retrieving BabelSynset ID
        	                synsetId = result.get('babelSynsetID')
        	                lis=[t,str(synsetId)]
        	                synid.append(lis)
        	                t=""
        	    synset(synid)
        except:
                pass    
		
################################# Get matching synset ID for disambiguated term #################################
def synset(li):

        service_url = 'https://babelnet.io/v1/getSynset'

        for i in range(len(li)):
            ids = li[i][1]
            key  = 'Babelfy_key_goes_here'

            params = {
                'id' : ids,
                'key'  : key
            }

            url = service_url + '?' + urllib.urlencode(params)
            request = urllib2.Request(url)
            request.add_header('Accept-encoding', 'gzip')
            response = urllib2.urlopen(request)

            if response.info().get('Content-Encoding') == 'gzip':
                buf = StringIO( response.read())
                f = gzip.GzipFile(fileobj=buf)
                data = json.loads(f.read())

                # retrieving BabelSense data
                wn="nan"
                senses = data['senses']
                for result in senses:
                    lemma = result.get('lemma')
                    language = result.get('language')
                    try:
                        wn = str(result.get('wordNetOffset'))
                        if(not wn=='None'):
                            li[i][0]=wn
                            get_scores(wn)
                            break
                    except:
                        pass


###################################################### SENTI WORDNET ##################################################
def split_line(line):
    cols = line.split("\t")
    return cols

def get_id(cols):
    return str(cols[1])+str(cols[0])
 
def get_words(cols):
    words_ids = cols[4].split(" ")
    words = [w.split("#")[0] for w in words_ids]
    return words
 
def get_positive(cols):
    return str(cols[2])
 
def get_negative(cols):
    return str(cols[3])

def get_gloss(cols):
    return cols[5]

p=[]
n=[]
o=[]
def get_scores(wordid):
    filesenti = open(fp)
    for line in filesenti:
        if not line.startswith("#"):
            cols = split_line(line)
            wnid = get_id(cols)
            
            if(wnid in wordid):
                p.append(get_positive(cols))
                n.append(get_negative(cols))
                ts = float(get_negative(cols))+float(get_positive(cols))
                val = 1.0 - ts
                o.append(str(val))
                break

if __name__=='__main__':

    #This file will contain the three-featured vector representation, which can be converted to a weka .arff file.
    sc = open("Path_to_Output_File","a") 
    
    with open("Path_to_training_or_testing_file","r") as f:
        for line in f:
            l=line.split("\t")
            if(not ("Not Available" in str(l[3]))):
                print total
                urlextr(str(l[3]))
                total=total+1
                sump=0.0
                sumn=0.0
                posit=0.0
                negat=0.0
                obj=0.0
                sumo=0.0
                for i in range(len(p)):
                    sump+=float(p[i])
                for j in range(len(n)):
                    sumn+=float(n[j])
                for k in range(len(o)):
                    sumo+=float(o[k])

                if(len(p)>0):
                    posit=sump/(len(p))
                if(len(n)>0):
                    negat=sumn/(len(n))
                if(len(o)>0):
                    obj=sumo/(len(o))
                sc.write(str(posit)+","+str(negat)+","+str(obj)+","+str(l[2])+"\n") 
                v=""
                p=[]
                n=[]
                o=[]
