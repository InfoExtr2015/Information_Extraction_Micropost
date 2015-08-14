# -*- coding: utf-8 -*-
import urllib2
import urllib
import json
import gzip
import re
import os
import math
import functools
from wordsegment import segment

from StringIO import StringIO
import xml.etree.ElementTree as ET

from DatumBox import DatumBox
datum_box = DatumBox('bfddf74008bd09951f8ad059a586d9fe')
##################### TWEET PRE-PROCESSING AND REGEX ########################
synid=[]
sep=re.compile(r"[ \t,.:;?!-/]+")
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
##############################################################################

################## Extracting Hashtags and URLs###############################
def info_extract(u):
		
        final_string = ""
        twe=url.split(u)

        newtweet=""
        for a in range(len(twe)):
            newtweet = newtweet+twe[a]+" "

        text = sep.split(newtweet);
        tex=""    
        for i in range(len(text)):
                if(hasht.match(text[i]) or atp.match(text[i])):
                        m=text[i][1:]
                        text[i]=segment(m.lower())
                        n=""
                        for j in text[i]:
                            n=n+j+" "
                        text[i]=n
                tex+=text[i]+" "

        final_string=final_string+categorize(tex)+"####"
        final_string=final_string+babelnet(tex)+"####"
        twee = url.search(u)
        try:
            urls = str(twee.group(0))
            final_string=final_string+url_categ(urls)+"<br>"
        except:
            pass
        final_string=final_string+twe_cat(tex)+"####"
        final_string=final_string+senti(u)+"####"
        return final_string
#################################################################################        

################################ Getting Tweet Topics ###########################
def categorize(cat):

    rst=""
    service_url="http://access.alchemyapi.com/calls/text/TextGetRankedTaxonomy"
    key='dadd5c3c67a71082146dffcfe48e5cf90f24e85f'
    outpt='json'
    params = {
                'apikey': key,
                'text': cat,
                'outputMode': outpt
            }
    url = service_url + '?' + urllib.urlencode(params)
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    buf = response.read()
    data = json.loads(buf)

    l = data["taxonomy"]
    for i in l:
        rst=rst+i["label"]+"\n"
    return rst
##################################################################################

############################ Getting Information from URLs #######################
def url_categ(u):

    sretn = ""
    service_url="http://access.alchemyapi.com/calls/url/URLGetRankedConcepts"
    key='dadd5c3c67a71082146dffcfe48e5cf90f24e85f'
    outpt='json'
    params = {
                'apikey': key,
                'url': u,
                'outputMode': outpt
            }
    url = service_url + '?' + urllib.urlencode(params)
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    buf = response.read()
    data = json.loads(buf)
    try:
        l = data["concepts"]
        for i in l:
            sretn=sretn+i["text"]+"\n"
        return sretn
    except:
        pass
######################################################################################

############################## Getting Tweet Concepts ################################
def twe_cat(t):

    sretn = ""
    service_url="http://access.alchemyapi.com/calls/text/TextGetRankedConcepts"
    key='dadd5c3c67a71082146dffcfe48e5cf90f24e85f'
    outpt='json'
    params = {
                'apikey': key,
                'text': t,
                'outputMode': outpt
            }
    url = service_url + '?' + urllib.urlencode(params)
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    buf = response.read()
    data = json.loads(buf)
    try:
        l = data["concepts"]
        # print ("Tweet Concepts:\n")
        for i in l:
            sretn=sretn+i["text"]+"\n"
            #print i["text"]
        return sretn
    except:
        pass
######################################################################################

############################# Getting Named Entities #################################
def babelnet(te):

        # try:
            synid=[]
            service_url = 'https://babelfy.io/v1/disambiguate'

            lang = 'EN'
            key  = '3be45dc5-0d48-48f0-8fcc-3a17d745a893'
            annType = 'NAMED_ENTITIES'

            params = {
            	'text' : te,
            	'lang' : lang,
                'annType':annType,
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
                                t+=te[i];

                        # retrieving BabelSynset ID
                        synsetId = result.get('babelSynsetID')
                        lis=[t,str(synsetId)]
                        synid.append(lis)
                        t=""
            return str(synid)
            
def senti(s):
	
	res = datum_box.twitter_sentiment_analysis(s)
	return str(res)
            
############################## END OF TWEET PROCESSING #############################


############################## PYTHON FLASK ROUTING ################################
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
	return "Hello World"

@app.route('/submit/<path:text>')
def analyze(text):
	dat = info_extract(text.encode('utf-8'))
	return dat

# starting the app	
if __name__ == '__main__':
	app.run(host='0.0.0.0',debug=True)
	
############################ END OF PYTHON FLASK ROUTING ###########################
