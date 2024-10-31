def FindFamilyRelationshipsStand(classified_text, ID, Relfile, FRstart ):

#text1=NER(raw_text)
#for word in text1.ents:
#    print(word.text,word.label_)


   #tokenized_text = word_tokenize(raw_text)
   #classified_text = st.tag(tokenized_text)

   #print(classified_text)
   relTags = ['boyfriend','girlfriend','father and mother-in-law','father-in-law','mother-in-law','aunt','aunts','uncle','uncles','grandchild','grandchildren','daughter','daughters','son','sons','child','children','stepdaughter','stepdaughters','stepchild','stepchildren','wife','husband','brother','brothers','brotherinlaw','brothersinlaw','sister','sisters','sisterinlaw','sistersinlaw','sistersinlaws','spouse','niece','nieces','nephew','nephews','nieces and nephews','father','mother','parent','parents','greatgrandchild','greatgrandchildren','grandson','grandsons','granddaughter','granddaughters','greatgranddaughter','greatgranddaughters','greatgrandson','greatgrandson','greatgreatgrandchild','greatgreatgrandchildren','greatgreatgrandson','greatgreatgrandsons','greatgreatgranddaughter','greatgreatgranddaughters','stepsons','stepson','sibling','siblings','grandparent','grandparents','grandfather','grandmother','greatgrandparents','greatgrandfather','greatgrandmother','great-grandparents','great-grandfather','great-grandmother','great grandparents','great grandfather','great grandmother','son-in-law','daughter-in-law','sons-in-law','daughters-in-law','fatherinlaw','motherinlaw','soninlaw','daughterinlaw','sonsinlaw','daughtersinlaw','daughter in law']
   if FRstart == 'surv':
       FR_Dec = 0
       FR_Dec_Next = 0
   elif FRstart == 'unkn':
       FR_Dec = 9
       FR_Dec_Next = 9
   else:
       FR_Dec = 1
       FR_Dec_Next = 1

   max_word = len(classified_text)
   ind_list=[]
   for idx,item in enumerate(classified_text):
      #if re.search(rf"\b(?=\w){item[0]}\b(?!\w)", relTags, re.IGNORECASE):
      if item[0].lower() in relTags:
         #print(idx, item)
         ind_list.append(idx)
   #print(max_word)
   ind_list.append(max_word -1)
   #print(classified_text[max_word-1])
   #print(ind_list)
   for i in ind_list:
       #print(classified_text[i])
       spouseName=''
   for idx,i in enumerate(ind_list[:-1]):
      textList=classified_text[i:ind_list[idx+1]]
      #print("textlist =",textList, idx)
       #first one has to be the relastion ship
       #making assumption that person name, then location(maybe) Next encounter of person is new line.
      for idw,word in enumerate(textList):
          #print(idw, word)
          #print("FR_dec = ", FR_Dec)
          if word[0] == 'preceded':
             FR_Dec_Next = 1
             if name == '':
                FR_Dec =1
             #print("FR_Dec1 set in loop idx = ",idx,"idw = ",idw,word)
          if word[0] == 'survived':
             FR_Dec_Next = 0
             if name == '':
                FR_Dec =0
          if word[0] == 'Survivors':
             FR_Dec_Next = 0
             if name == '':
                FR_Dec =0
          #print(FR_Dec, idx, idw)
          #print(spouseName) 
          if idw==0:
             relationship = word[0]
             prev = ''
             name = ''
             spouseName = ''
             city = ''
             origName = ''
             parenName=False
          elif prev=='PERSON' and word[1]=='PERSON':
             name += ' '
             name += word[0]
          elif word[0] =='(':
             #print( 'in 1p')
             parenName = True
             origName = name
             name = ''
          elif word[0] == ')':
             #print('in 2p')
             #print(name)
             spouseName = name;
             #print(spouseName)
             prev = 'PERSON'
             name = origName
             parenName = False
          elif parenName:
             name += word[0]
          elif word[1]=='PERSON':
             #new perso
             #print("person spouse: %s" % (spouseName))
             #print("name: %s" % (name))
             if name:
               # print("%d \t %s \t %s \t %s \t %s \t %s \n" % (ID, relationship, name, spouseName, city, FR_Dec ))
                Relfile.write("%d \t %s \t %s \t %s \t %s \t %s \n" % (ID, relationship, name, spouseName, city, FR_Dec ))
                FR_Dec = FR_Dec_Next
             name=word[0]
             spouseName = ''
             prev='PERSON'
             city = ''
          elif prev=='LOCATION' and word[1]=='LOCATION':
             city += ' '
             city += word[0]
          elif word[0] ==',' and  prev=='LOCATION':
             city += word[0]
          elif word[1]=='LOCATION':
             #new person
             city=word[0]
             #spouseName = ''
             prev='LOCATION'
          else:
             prev=''
             #print("else spouse: %s" % (spouseName))
             #print(name) 
             #print(spouseName)
             #hprint(city)    
             #print("%s %s %s %s" % (relationship,name,spouseName,city)) 
       #print(textList)
      if name: 
         #print("%d \t %s \t %s \t %s \t %s \t %s \n" % (ID, relationship, name, spouseName, city, FR_Dec ))        
         Relfile.write("%d \t %s \t %s \t %s \t %s \t %s \n" % (ID, relationship, name, spouseName, city, FR_Dec ))
         FR_Dec = FR_Dec_Next

         #print("%s %s %s %s" % (relationship,name,spouseName,city))
    
    
    
