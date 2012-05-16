import sys, collections

dfs = {'operations':2484,'gates':1087,'aquatic':144,'olympiad':14,'marguerite':644,'office':12256,'cdc':435,'course':7305,'planning':2923,'cs223a':15,'ecorner':172,'134':137,'facts':1356,'chair':1997,'fellows':3407,'centers':7097,'apple':502,'dining':931,'group':11561,'searchable':587,'maps':12019,'interesting':867,'admission':2838,'courserank':20,'lake':372,'environment':8244,'to':79117,'absence':399,'program':23160,'degrees':2158,'systems':10645,'hennessy':373,'listing':928,'snap':143,'cardinal':827,'ccrma':552,'hoover':1699,'2012':19472,'eateries':72,'activities':5177,'food':3777,'dan':1143,'papers':7080,'masters':777,'skilling':119,'shuttle':818,'game':1094,'ssh':137,'knuth':82,'hall':6464,'essential':1034,'school':20875,'hello':600,'bytes':277,'crypto':41,'helloworld':4,'leave':1436,'courses':10521,'cs246':14,'schwarz':55,'cs348b':38,'managemen':3,'athletics':587,'crossword':11,'page':29057,'auditorium':1862,'google':6881,'art':4348,'fair':1398,'map':14236,'bump':88,'spring':3396,'energy':10042,'library':15390,'oval':192,'memes':3,'computer':9188,'276':83,'parking':1594,'calendar':12513,'ballot':83,'probability':523,'linear':2406,'ridge':463,'scholarships':445,'for':68780,'assignments':1126,'manning':212,'goel':44,'artificial':916,'research':33547,'avery':103,'cs361b':2,'slac':10609,'ra':549,'medicine':6209,'international':11869,'ike\'s':14,'patenting':20,'email':20186,'math':1593,'football':194,'theory':3701,'degree':3661,'schedule':4086,'internship':626,'corn':116,'processing':2346,'radiohead':3,'free':6981,'hours':5098,'its':12414,'explore':3859,'arrillaga':408,'advisor':1566,'directions':13484,'modeling':2064,'entrepreneurship':1838,'keith':435,'tower':393,'coupons':41,'prabhakar':55,'cheriton':50,'dates':1346,'defense':946,'language':8293,'discount':386,'of':85567,'raghavan':26,'sheets':329,'cs142':12,'108':326,'cs140':28,'david':5139,'filter':753,'credit':1816,'admit':175,'registrar':3056,'massive':302,'luck':125,'antibody':99,'options':4606,'software':6303,'consulting':1608,'huang':1480,'cancer':1479,'koller':111,'mscs':12,'berkeley':2514,'ppl':17,'cs248':31,'chris':1374,'jasper':355,'learning':5166,'village':298,'cs':2769,'financial':4662,'dsp':57,'hamster':6,'forms':4181,'statistics':1909,'sheet':908,'famous':381,'introduction':4065,'data':12880,'hospital':4430,'explorecourses':467,'recruiting':501,'ee':929,'bases':344,'handbook':1227,'intelligence':1061,'ux':40,'cs276':6,'john':6258,'halls':143,'mining':341,'highrise':4,'shopping':558,'kalman':67,'club':1691,'quillen':18,'gym':84,'courseware':47,'andrew':1358,'afternoons':58,'admissions':7197,'bookstore':402,'everywhere':222,'agent':546,'229':100,'escondido':538,'cs224m':4,'dorm':266,'piazza':43,'applied':2997,'multi':1712,'molecular':1952,'room':9389,'stanford':71203,'ricker':29,'science':15855,'myvideosu':3,'database':4235,'classes':3723,'publications':17752,'ms':2623,'gis':210,'assu':389,'aid':2135,'ta':791,'frosoco':86,'coursework':1195,'daphne':109,'booking':119,'probablistic':3,'gspb':22,'boneh':77,'nlp':214,'ranking':165,'ai':472,'graphene':48,'cs155':20,'graphical':451,'coterm':210,'ap':473,'engineering':11206,'at':50897,'finalists':122,'ship':181,'lagunita':297,'technology':9285,'campus':10234,'information':29470,'cafe':670,'requirements':5677,'infolab':43,'bursar':2,'rains':93,'redwood':612,'ugrad':7,'ng':443,'graduate':12486,'machine':1704,'application':5078,'cantor':792,'electrical':2033,'digital':3040,'online':8138,'depatment':19461,'colloquium':1047,'scpd':261,'axess':1744,'events':24867,'afs':489,'development':12539,'lectures':2536,'draw':440,'express':659,'143':126,'book':8124,'algebra':318,'models':2871,'coursera':2,'jure':120,'english':4613,'ousterhout':29,'lab':7869,'phd':3889,'cs103':12,'important':4671,'cs106a':23,'cs107':25,'student':15659,'services':10984,'weekend':660,'class':7712,'ashish':62,'jazz':340,'building':11099,'cs341':5,'natural':2143,'center':30068,'rodin':166,'leskovec':119,'medical':7259,'housing':1530,'alumni':15656,'cs229':22,'retrieval':293,'academic':9765,'gsb':2424,'green':4828,'agenda':1184,'sets':1135,'professional':3330,'physics':6280,'bulletin':2096,'cs161':14}

class CorpusInfo:
  def __init__(self):
    self.average_doc_length = 257.564193216
    self.num_docs = 98998
    self.doc_freq = collections.defaultdict(lambda : 1)
    self.doc_freq.update(dfs)

  def get_num_docs(self):
    return self.num_docs

  def get_average_doc_length(self):
    return self.average_doc_length

  def get_doc_freqs(self):
    return self.doc_freq
  