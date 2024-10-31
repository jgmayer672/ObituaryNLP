import os
from datetime import datetime
from pathlib import Path
from dateutil.parser import parse
from dateparser.search import search_dates
import re
import xml.etree.ElementTree as ET
import nltk
import spacy
import getopt as gto
import sys
import locationtagger
from nltk.tree import Tree
from nltk.tokenize import word_tokenize
import FamRelFunct as FRF
from nltk.tag import StanfordNERTagger
NER=spacy.load("en_core_web_sm")
st = StanfordNERTagger('english.all.3class.distsim.crf.ser.gz')
outPath = "/work/June2023/"

#relTags = ['grandchild','grandchildren','daughter','daughters','son','sons','child','children','wife','husband','brother','brothers','brotherinlaw','brothersinlaw','sister','sisters','sisterinlaw','sistersinlaw','sistersinlaws','spouse','niece','nieces','nephew','nephews','father','mother','parents','parents','greatgrandchild','greatgrandchildren','granddaughter','granddaughters','greatgranddaughter','greatgranddaughters','greatgrandson','greatgrandson','greatgreatgrandchild','greatgreatgrandchildren','stepsons','sibling','siblings']

#inpPath = "D:\EC2021"

#outPath = "D:\EC2021\Results"

#dir_list = os.listdir(inpPath)

#print(dir_list)
def ReplaceMonths(inText):
   inText = inText.replace("Jan.","January")
   inText = inText.replace("Feb.","Febuary")
   inText = inText.replace("Mar.","March")
   inText = inText.replace("Apr.","April")
   inText = inText.replace("Jun.","June")
   inText = inText.replace("Jul.","July")
   inText = inText.replace("Aug.","August")
   inText = inText.replace("Sept.","September")
   inText = inText.replace("Sep.","September")
   inText = inText.replace("Oct.","October")
   inText = inText.replace("Nov.","November")
   inText = inText.replace("Dec.","December")
   return(inText)

def GetFamilyRelat(ID, txtStr, relat):
   #https://unbiased-coder.com/extract-names-python-nltk/#Find_Names_In_Text_Using_NLTK
   #print('inFR')
   #print(relat)
   #print(txtStr)
   if not txtStr:
      return
 
#   nltk_results = nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(txtStr)))
#   for nltk_result in nltk_results:
#      if type(nltk_result) == Tree:
#         name = ''
#         for nltk_result_leaf in nltk_result.leaves(): 
#            name += nltk_result_leaf[0] + ' '
         #print('Type: ', nltk_result.label(), 'Name: ', name)   
   try:
      nameStr = txtStr.split(',') 
   except Exception as e:
      print('name str ', e)
   for name in nameStr:
#      print(nameStr)
#      print('name',name)
      nameSplt = name.split('and')
#      print(nameSplt)
      for prtName in nameSplt:
         prtNameCity = ''
         if (prtName and prtName.strip()):
#            print('print name =', prtName)
            #check for city
            nameofSplt = prtName.split('of')
            if len(nameofSplt) == 1:
                prtName2 = nameofSplt[0]
            if len(nameofSplt) == 2:
                prtName2 = nameofSplt[0]
                prtNameCity = nameofSplt[1]

#            print('nameofSplt = ',nameofSplt)
            #SpRes = re.search(r"\(.*?\)",prtName2) 
            #SpRes = re.search(r"\((.*?)\)",prtName2)
            prnCheck = prtName2.find("(")
            #print(prtName2)
            #print(prnCheck)
            
            if prnCheck != -1:
               #prtSpouse = ("%s" % (SpRes.group(0)))
               prtSpouse = prtName2[prtName2.find("(")+1:prtName2.find(")")]
               editName = re.sub("[\(].*?[\)]", "", prtName2) 
            else:
               prtSpouse = ""
               editName = prtName2
            Relatfile.write("%d \t %s \t %s \t %s \t %s \t %s \n" % (ID, prtName2, editName, relat, prtNameCity, prtSpouse))

def ReplaceStateAbbrvs(txtTmp):
    newStr = txtTmp.replace('Minn.','Minnesota')
    newStr2 = newStr.replace('Wis','Wisconsin')
    return newStr3 

def ReplacePunc(txtRep):
    retStr1 = txtRep.replace('\.\,','\,')
    retStr2 = retStr1.replace('\.;',';')
    retStr3 = retStr2.replace('-','')
    return retStr3

def SpecFixes(txtFix):
    newFix = txtFix.replace('Minn.','Minnesota;')
    newFix2 = newFix.replace('brothers and sisters','siblings')
    newFix3 = newFix2.replace('Wis.','Wisconsin')
    newFix4 = newFix3.replace('Ark.','Arkansas')
    newFix5 = newFix4.replace('WI','Wisconsin')
    newFix6 = newFix5.replace('MN','Minnesota')
    return newFix6 
	

def DOBProc(ID, txtStrbody):
   DOB = ""
   DOB2 = ""
   DOBstr = ""
   DOBoutStr = ""
   DOBoutStr2 = ""
   sentTok = nltk.sent_tokenize(txtStrbody)
   for txtStrDOB in sentTok:
      try:
          if DOBoutStr !="":
             break;
          DOB = ""
          DOB2 = ""
          DOBstr = ""
          DOBoutStr = ""
          DOBoutStr2 = ""
          foundBorn = True
          try:
            #bornStr, DOBstr = txtStrDOB.split('born')
              bornStr, DOBstr = re.split('born', txtStrDOB, flags=re.IGNORECASE)
          except Exception as e:
              ##print('born ', e)
              foundBorn = False
          try:
              DOB = parse(DOBstr, fuzzy_with_tokens=True)
              DOBoutStr = DOB[0].strftime("%m/%d/%Y")
          except Exception as e:
              #print('DOB ', e)
              DOBoutStr = ""
          try:
              DOB2 = search_dates(DOBstr)
              DOB2_1 = DOB2[0]
              DOBoutStr2 = DOB2_1[1].strftime("%m/%d/%Y")
          except Exception as e:
              #print('DOB2 ', e)
              DOBoutStr2 = ""
          try:
              #look for parents
              if foundBorn:
                 bornPars = re.split(r"\bto\b", txtStrDOB, flags=re.IGNORECASE)
                 parNames = bornPars[1].split('and')
                 i=0
                 for cName in parNames:
                    prtName2 = cName
                    editName = ""
                 #Assuming first name is father
                    if i == 0:
                       relat='Father'
                    else:
                       relat = 'Mother'
                    prtNameCity=""
                    prtSpouse=""
                    Relatfile.write("%d %s \t %s \t %s \t %s \t %s \n" % (ID, relat, prtName2, prtSpouse,  prtNameCity))              
                    i+=1
          except Exception as e:
               #print('DOB Name exception',e)   
             pass
      except Exception as e:
          pass
          #print('DOBProc exception ', e)
   return DOBoutStr, DOBoutStr2

def DODProc(txtStrbody):
   DOD = ""
   DOD2 = ""
   DODstr = ""
   DODoutStr = ""
   DODoutStr2 = ""
   diedStr = ""
   sentTok = nltk.sent_tokenize(txtStrbody)
   for txtStrDOD in sentTok:
      try:
          if DODoutStr !="":
             break; 
          DOD = ""
          DOD2 = ""
          DODstr = ""
          DODoutStr = ""
          DODoutStr2 = ""
          diedStr = ""
          try:
              diedStr, DODstr = txtStrDOD.split("passed away", 1)
          except Exception as e:
              pass
              #print('passed away ', e)
              try:
                  diedStr, DODstr = txtStrDOD.split("died", 1)
              except Exception as e:
                  pass
                  #print('dies ', e)
                  try:
                      diedStr, DODstr = txtStrDOD.split("heavenly vacation", 1)
                  except Exception as e:
                     # print('heavenly vacation', e)
                     pass
          try:
              #print("DODstr")
               #print(DODstr)
              DOD = parse(DODstr, fuzzy_with_tokens=True)
              DODoutStr = DOD[0].strftime("%m/%d/%Y")
          except Exception as e:
              #print('DOD ', e)
              DODoutStr = ""
          try:
              DOD2 = search_dates(DODstr)
              DOD2_1 = DOD2[0]
              DODoutStr2 = DOD2_1[1].strftime("%m/%d/%Y")
          except Exception as e:
              #print('DOD2 ', e)
              DODoutStr2 = ""
      except Exception as e:
         pass
          # print('DODProc exception ', e)
   return DODoutStr, DODoutStr2

def SecTextValid(inText):
   SecTerms = ['OBIT','OBITUARIES','Death Notice - Classified','OBITUARY','Obituary','LOCAL / OBITAURIES','OBITUARY','Death notices'
,'News - Obituaries','Obits','Death Notices','OBITUARY','Obituaries/','Deaths March','OBITUARY','Deaths'
,'OBITUARY','Obituari','LOCAL / OBITUARIES','LOCAL, OBITUARIES','OBITUARIES','Death','Deaths Jan'
,'obituaries','Death Notice','Death Noti Ces','LOCAL / OBTUARIES','Local / OBITUARIES']
   if inText in SecTerms:
      return True
   else:
      return False

# first is dir, second is fileext, 3rd is patid start
arg_dir = sys.argv[1]
arg_fileExt = sys.argv[2]
arg_patID = sys.argv[3]




Resfile = open(outPath + "obitResultsApr2023FullRun" + arg_fileExt + ".txt", "w")
Otherfile = open(outPath + "otherResultsApr2023FullRun" + arg_fileExt + ".txt", "w")
Relatfile = open(outPath + "FamilyRelationsApr2023FullRun" + arg_fileExt + ".txt", "w")

Resfile.write("patID \t dateText \t paperText \t nameLast \t nameFirst \t nameMiddle \t nameMiddle2 \t cityStr \t DOBoutStr \t DOBoutStr2 \t DODoutStr \t  DODoutStr2 \t MinDate \t MaxDate \t Suffix \t Nickname \t FullName \n")
            
Otherfile.write("patID \t dateText \t paperText \t nameLast \t nameFirst \t nameMiddle \t nameMiddle2 \t cityStr \t DOBoutStr \t DOBoutStr2 \t DODoutStr \t DODoutStr2 \t MinDate \t MaxDate \t Suffix \t Nickname \t FullName \n")

Relatfile.write("patID \t nameString \t FullName \t Relation \t City \t Spouse \t FR_Dec \n")


patID = int(sys.argv[3])
#for root, dirs, files in os.walk('/data/TomahJournal/2021/01/01/'):
for root, dirs, files in os.walk('/data/' + arg_dir):
   for file in files:
      with open(os.path.join(root, file), "r") as auto:
         xmlTree = ET.parse(auto) 
         xmlRoot = (xmlTree.getroot())
         try:
            secText = xmlRoot.find("SEC").text
         except Exception as e:
            #print(e)
            secText = "Missing"
         try:
            hedTextorig = xmlRoot.find("HED").text
         except Exception as e:
            #print(e)
            hedText = ""
         try:
            bodyText = xmlRoot.find("SBODY").text
         except Exception as e:
            #print(e)
            bodyText = ""

         #nameText = xmlRoot.find("DECE").text
         paperText = xmlRoot.find("PAP").text
         dateText = xmlRoot.find("YMD").text
         hedTextDate = re.sub(r'(\d{4} - \d{4})','',hedTextorig)
         hedTextAge = re.sub(r'(\d{2})','',hedTextDate)
         hedText = hedTextAge
         DaysofWeek=['Monday,','Tuesday,','Wednesday,','Thursday,','Friday,','Saturday,','Sunday,']
         try:
            bodyTextTmp = bodyText.split()
         except Exception as e:
            #print(e)
            bodyTextTmp = ""

         #remove days of week from text.  Don't need them and they mess with the date search procedure.
         resultBody = [word for word in bodyTextTmp if word not in DaysofWeek]
         bodyText = ' '.join(resultBody)
         bodyText = ReplaceMonths(bodyText)
         #print(bodyText)
         dateResList=search_dates(bodyText)
         #remove numbers from potential name text.  Usually year or age
        
         try:
            if hedText.find('death')>-1 or hedText.find('service')>-1:
               nameText, nameJunk = bodyText.split(',',1)
            else:
               nameTextOrig = xmlRoot.find("DECE").text
               nameTextDate = re.sub(r'(\d{4} - \d{4})','',nameTextOrig)
               nameTextAge = re.sub(r'(\d{2})','',nameTextDate)
               nameText = nameTextAge

         except Exception as e:
            #print(e)
            nameText = bodyText.split(',',1)

#         #print(secText)
#         print(hedText)
         #Get city name
         newDate=[]
         
         if dateResList: 
            for item in dateResList:
             #newDate.append(item[1].strftime("%m/%d/%Y"))
               newDate.append(item[1].date())
      #newDate = list(map(time.strftime("%m/%d/%Y"),dateResList))
            newDateRemove=[i for i in newDate if i <= datetime.strptime(dateText, '%Y-%m-%d').date()]
         else:
             newDateRemove = []
         try:
            minDate = min(newDateRemove)
         except Exception as e:
            minDate = ""
         try:
            maxDate = max(newDateRemove)
         except Exception as e:
            maxDate = ""

         try:
            cityStr, strJunk = bodyText.split('-', 1)
            if len(cityStr) >=40:
               cityStr2, strJunk = cityStr.split(' ',1)
               cityStr = cityStr2
         except Exception as e:
            #print(e)
            cityStr = ""
         #print(cityStr) 
         #get DOB, DOD
         DOBoutStr, DOBoutStr2 = DOBProc(patID, bodyText)
         DODoutStr, DODoutStr2 = DODProc(bodyText)
         
         #get name text
         nameFirst = ""
         nameMiddle = ""
         nameMiddle2 = ""
         nameLast = ""
         suffix = ""
         nickname = ""
         try:
             if (re.search('Jr\.',nameText)):
                suffix = 'Jr.'
                nameText = nameText.replace('Jr.','')
             if (re.search('Sr\.',nameText)):
                suffix = 'Sr.'
                nameText = nameText.replace('Sr.','')
             if (re.search(r'(["])(?:(?=(\\?))\2.)*?\1',nameText)):
                #nickname = re.findall('(["])(?:(?=(\\?))\2.)*?\1',nameText)
                nickname = nameText.split("'")[1]
                nameText = re.sub(r'(["])(?:(?=(\\?))\2.)*?\1','',nameText)
             if (re.search(r"(['])(?:(?=(\\?))\2.)*?\1",nameText)):
                #for reasons unknown, this does not work to extract the text
                #nickname = re.findall("(['])(?:(?=(\\?))\2.)*?\1",nameText)
                nickname = nameText.split("'")[1]
                nameText = re.sub(r"(['])(?:(?=(\\?))\2.)*?\1",'',nameText)
             numNames = len(nameText.split())
         except Exception as e:
             #print(e)
             numNames = len(nameText)
         #print ("numNames = ",numNames)

         if (numNames == 2):
             try:
                 nameLast, nameFirst = nameText.split(',', 1)
             except:
                 if type(nameText) == 'List':
                    nameLast = nameText[0]
                 else:
                    try:
                       nameFirst, nameLast = nameText.split()
                    except Exception as e:
                       print(e)
                       nameFirst = ""
                       nameLast = ""
 
         elif numNames == 3:
             try:
                 nameLast, restNames = nameText.split(',', 1)
                 nameFirst, nameMiddle = restNames.split()
             except:
                 nameFirst, nameMiddle, nameLast = nameText.split()
         elif numNames == 4:
             try:
                 nameLast, restNames = nameText.split(',', 1)
                 nameFirst, nameMiddle, nameMiddle2 = restNames.split()
             except:
                 nameFirst, nameMiddle, nameMiddle2, nameLast = nameText.split()
         else:
            pass
            # handle errors
              #nprint("Name str appears to not be name")
              #print(hedText)
         #search for relatives
         #bodyTextSt = ReplaceStateAbbrvs(bodyText)
         #print('return state str')
         #print(bodyText)
         wordCount = nltk.FreqDist(bodyText)
#         print('survived count =')
#         print(bodyText.count("survived by"))
         #survCnt = bodyText.count("survived by")
#         print('preceded  count =')
#         print(bodyText.count("preceded in death"))
         #precCnt = bodyText.count("preceded in death")
         #remove everything after in lieu of flowers ro A memorial service.
         
         bt1 = bodyText.split('In lieu of flowers', 1)[0]
         bt2 = bt1.split('in lieu of flowers', 1)[0]
         bt3 = bt2.split('A memorial service', 1)[0]
         bt4 = bt3.split('A funeral service', 1)[0]
         bt5 = bt4.split('family wishes to', 1)[0]
         bt6 = bt5.split('Funeral services', 1)[0]
         bt7 = bt6.split('A celebration of', 1)[0]
         bt8 = bt7.split('Mass of Christian Burial',1)[0]
         bt9 = bt8.split('A service will be held',1)[0]
         bt10 = bt9.split('A service was be held l',1)[0]
         bodyText2=SpecFixes(bt10)

         sb_ind = bodyText2.find('survived by')
         sb_ind2 =  bodyText2.find('Survivors include')
         pi_ind = bodyText2.find('preceded in death')
         #jprint(sb_ind2)
         #print(bodyText2)
         # if sb_ind is -1, any vaule of sb_ind2 is good
         if sb_ind == -1:
            sb_ind = sb_ind2
         elif sb_ind2 > 0:
            if sb_ind > sb_ind2:
               sb_ind = sb_ind2

         #get parents
         born_txt= bodyText2.partition("born")[2].partition(".")[0]
         tokenized_born_text = word_tokenize(born_txt)
         classified_born_text = st.tag(tokenized_born_text)

         bbornfound = False
         bornstrtpl = []
         #print(classified_born_text)
         for bpar in classified_born_text:
            #print(bpar)
            if bpar[1] == 'PERSON' or bbornfound == True:
                bbornfound=True
                bornstrtpl.append( list(bpar) )
         #find parents
         bper = ''
         brpFound = False
         for bword in bornstrtpl:
             if (bword[1] == 'PERSON') | (bword[0] == '(') | (bword[0] == ')') | (brpFound == True):
                 if brpFound == True:
                    bper = bper + bword[0] + ' '
                    broFound = False
                 else:
                    bper = bper + bword[0] + ' '
                 if bword[0] == ')':
                    brpFound = True
             else:
                 if bper != '':
                    Relatfile.write("%d \t %s \t %s \t %s \t %s \n" % (patID, 'Parent', bper.strip(), '', '' )) 
                    bper = ''
         if bper != '':
            Relatfile.write("%d \t %s \t %s \t %s \t %s \n" % (patID, 'Parent', bper.strip(), '', '' ))

         #get marriagejh
         mar_txt= bodyText2.partition("married")[2].partition(".")[0]
         if mar_txt == '':
            mar_txt= bodyText2.partition("marriage")[2].partition(".")[0] 
         tokenized_mar_text = word_tokenize(mar_txt)
         classified_mar_text = st.tag(tokenized_mar_text)

         bmarfound = False
         marstrtpl = []
         #print(classified_born_text)
         for mpar in classified_mar_text:
            print(mpar)
            if mpar[1] == 'PERSON' or bmarfound == True:
                bmarfound=True
                marstrtpl.append( list(mpar) )
         #find spouse 
         mper = ''
         brpFound = False
         for bword in marstrtpl:
             if (bword[1] == 'PERSON')  | (bword[0] == '(') | (bword[0] == ')') | (brpFound == True):
                 if brpFound == True:
                    mper = mper + bword[0] + ' '
                    broFound = False
                 else:
                    mper = mper + bword[0] + ' '
                 if bword[0] == ')':
                    brpFound = True
             else:
                 if mper != '':
                    Relatfile.write("%d \t %s \t %s \t %s \t %s \n" % (patID, 'spouse', mper.strip(), '', '' ))
                    mper = ''
         if mper != '':
            Relatfile.write("%d \t %s \t %s \t %s \t %s \n" % (patID, 'spouse', mper.strip(), '', '' ))
         FRstart = 'unkn'
         if sb_ind == -1 and pi_ind == -1:
            raw_text_red = bodyText2 
            FRstart = 'unkn'
         elif sb_ind == -1:
            raw_text_red = bodyText2[pi_ind:]
            FRstart = 'prec'
         elif pi_ind == -1:
            raw_text_red = bodyText2[sb_ind:]
            FRstart = 'surv'
         elif sb_ind < pi_ind:
            raw_text_red = bodyText2[sb_ind:]
            FRstart = 'surv'
         else:
            raw_text_red = bodyText2[pi_ind:]
            FRstart = 'prec'

         #sentTok = nltk.sent_tokenize(bodyText)
         raw_text_red = raw_text_red.replace('-','')
         tokenized_text = word_tokenize(raw_text_red)
         FR_text = st.tag(tokenized_text)

         #jfor sentTxt in sentTok:
          #  try:
              #print(bodyText)
              #survText, survRest = bodyText.split("survived by", 1)
          #    survRest = sentTxt
              #print("survText")
              #print(survText)
#              print("survRest")
#              print(survRest)
          #j  except Exception as e:
           #   print('survived not found ', e)
         try:
              #daugtText, daugtRest = survRest.split("daughters",1)
              #this fails after doing the state replacemnt.  Works fine without it.

         #  for curRel in relTags:
         #     regStr = r'\b' + curRel + r'\b(.*?)[\;\.] '
                 #print('regStr = ',regStr)
                 #if not regStr:
                    #This is to capture the last group that ends the sentence
                 #   regStr = r'\b' + curRel + r'\b(.*?)\. '
                 #   print('regStr . = ',regStr)
                 #print(curRel)
                 #print('regStr = ', regStr)
           #survRestFix = SpecFixes(survRest)
           #survRestRep = ReplacePunc(survRestFix)
                 #print('surRestRep = ',survRestRep)
           #relatStr = re.findall(regStr,survRestRep)
                 #print('relatStr = ',relatStr)
           #if relatStr:
              #GetFamilyRelat(patID, relatStr[0], curRel)
           #print("call FindFamil")
           FRF.FindFamilyRelationshipsStand(FR_text, patID, Relatfile, FRstart )
                 #else:
                    #This is to capture the last group that ends the sentence
                 #   regStr = r'\b' + curRel + r'\b(.+?)\. '
                 #   relatStr = re.findall(regStr,survRest) 
                 #   if relatStr:
                 #      GetFamilyRelat(patID, relatStr[0], curRel)

              #print('before locStr')
              #locStr = locationtagger.find_locations(text = relatStr)
              #print('locStr is') 
              #print(locStr.regions)
              #print(locStr.cities)
              #print("daugtRest = ")
              #print(daugtRest)
              #print('daughRest end')
              #print("daugthStr = ")
              #print(daugthStr)
              #print('daugStr end')

         except Exception as e:
            print('search exception in family relat', e)

         if SecTextValid(secText): 
            Resfile.write("%d \t %s \t %s \t %s \t %s \t %s \t %s \t %s \t %s \t %s \t %s \t %s \t %s \t %s \t %s \t %s \t %s \n" % (patID, dateText, paperText, nameLast, nameFirst, nameMiddle, nameMiddle2,  cityStr, DOBoutStr, DOBoutStr2, DODoutStr, DODoutStr2,minDate,maxDate,suffix,nickname,nameTextOrig))
         else:
            Otherfile.write("%d \t %s \t %s \t %s \t %s \t %s \t %s \t %s \t %s \t %s \t %s \t %s \t %s \t %s \t %s \t %s \t %s \n" % (patID, dateText, paperText, nameLast, nameFirst, nameMiddle, nameMiddle2, cityStr, DOBoutStr, DOBoutStr2, DODoutStr, DODoutStr2,minDate,maxDate,suffix,nickname,nameTextOrig))
      patID += 1 
Resfile.close()
Otherfile.close()
Relatfile.close()
