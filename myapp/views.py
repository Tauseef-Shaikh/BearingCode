from django.shortcuts import render, redirect
from .models import Entry
from .forms import EntryForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
import os, json
from django.http import HttpResponse, HttpResponseRedirect
import datetime, logging, random, csv
from itertools import zip_longest
from django.conf import settings
from django.contrib.sessions.models import Session
from django.utils.datastructures import MultiValueDictKeyError

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

def login_user(request):
    data_json={}
    data_json = json.dumps(py_dict_list)
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']        
        user = authenticate(request, username=username, password=password)
        
        if user is not None and username != 'admin':
            login(request, user)
            with open (__package__+'/data/'+str(request.user)+'.csv','w') as cf:
                cf.write('GrpEntry,BearingType,SubType,Code,Quantity,DateTime,LastAmt,EntryNo')
                cf.write('\n')

            with open (__package__+'/data/solo_'+str(request.user)+'.csv','w') as cf:
                cf.write('GrpEntry,BearingType,SubType,Code,Quantity,DateTime,LastAmt,EntryNo')
                cf.write('\n')
            
            return redirect('create_entry')

        elif user is not None and username == 'admin':
            login(request, user)            
            return redirect('admin_view')
        else:
            # Handle invalid login credentials here                        
            loginErrMsg = {'errMsg': 'Invalid Username or Password Entered',}

            return render(request, 'myapp/login.html', {'loginErrMsg':loginErrMsg})
            
    
    return render(request, 'myapp/login.html')

def create_entry(request):    

    if not request.user.is_authenticated:
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
        
    global defaultCodeDict, categoryDict, usrDict, offevenExc, offevenInc, usrAdminDict, catDictTotal, sideTotal  
    
    form = ''
    optType = ''
    codeB4Split = ''
    codeNum = ''
    codeVal = 0
    oddevenSubType = ''
    genericSubType = ''
    grpEntry=''
    toEdit=''
    
    DtTm = datetime.datetime.now()
    
    usrDisplayDict = {}
    usrDisplayList = []
    data_json = json.dumps(py_dict_list)
    uFileName = str(request.user)
    
    if request.method == 'POST':
        form = EntryForm(request.POST)
        grpEntry = request.POST.get('grpEntry')
        optType = request.POST.get('folder')
        codeB4Split = request.POST.get('bearing_code')
        codeNum = request.POST.get('brCdSplit')
        codeVal = request.POST.get('amount')
        oddevenSubType = request.POST.get('oddevenSelect')
        genericSubType = request.POST.get('singledouble')
        actionType = request.POST.get('addOrEdit')
        entryNo = request.POST.get('entryNo')
        toEdit = request.POST.get('prevEntry')
        
        usrDisplayDictY={}
        uFileName = str(request.user)
        
        if codeVal is not None:
            codeVal = round(float(codeVal),2)
                
        usrDisplayList =[grpEntry,optType,str(oddevenSubType)+str(genericSubType), codeNum, 0, DtTm.strftime('%Y-%m-%d %H:%M:%S'),codeVal]
        usrDisplayDict['lastEntry'] = usrDisplayList
                
        #usrDisplayList =[optType,str(oddevenSubType)+str(genericSubType), codeNum, 0, DtTm.strftime('%Y-%m-%d %H:%M:%S')]  
        
        if actionType  == 'add':
            usrDict = {} # to avoid double update when copying over usrDict to usrAdminDict
            usrDisplayDict = addEntry(usrDisplayDict, optType, codeB4Split, codeNum, codeVal, oddevenSubType, genericSubType)

            if request.POST.get('folder') != 'ccat':
                for k, v in usrDict.items(): #update admin screen
                    for k1, v1 in usrAdminDict.items():
                        if k == k1:
                            usrAdminDict[k1] += v

            if grpEntry == 'no':
                with open (__package__+'/data/solo_'+uFileName+'.csv','w') as cfSolo:
                    cfSolo.write('GrpEntry,BearingType,SubType,Code,Quantity,DateTime,LastAmt,EntryNo')
                    cfSolo.write('\n')
                    cfSolo.write(grpEntry + ',' + optType + ',' + str(oddevenSubType)+str(genericSubType) +',' + str(codeNum) +',' + str(usrDisplayDict['lastEntry'][4]) +',' + DtTm.strftime('%Y-%m-%d %H:%M:%S') + ',' + str(codeVal) + ',' + entryNo)

                with open (__package__+'/data/'+uFileName+'.csv','w') as cf:
                    cf.write('GrpEntry,BearingType,SubType,Code,Quantity,DateTime,LastAmt,EntryNo')
                    cf.write('\n')
            
                        
        elif actionType  == 'edit':            
            usrAdminDict = editEntry(request, usrAdminDict, usrDict, grpEntry)                
            usrDict = {}

            usrDisplayDict = addEntry(usrDisplayDict, optType, codeB4Split, codeNum, codeVal, oddevenSubType, genericSubType) 

            if request.POST.get('folder') != 'ccat':
                for k, v in usrDict.items(): #update admin screen
                    for k1, v1 in usrAdminDict.items():
                        if k == k1:
                            usrAdminDict[k1] += v
                
        if usrDisplayDict['lastEntry'][4] == 0:
            usrDisplayDict['lastEntry'][4] = codeVal            

        if grpEntry == 'yes':           

            #with open (__package__+'/data/grpEntry.csv','r') as cf:
            with open (__package__+'/data/'+uFileName+'.csv','r') as cf:
                hdr = cf.readline()
                csvrdr = cf.readlines()
            
            #with open (__package__+'/data/grpEntry.csv','w') as cf:                  
            with open (__package__+'/data/'+uFileName+'.csv','w') as cf:
                cf.write('GrpEntry,BearingType,SubType,Code,Quantity,DateTime,LastAmt,EntryNo')
                cf.write('\n')
                
                for lCnt, line in enumerate(csvrdr):                        
                    if lCnt == int(entryNo)-1:                                                
                        #toWrt = grpEntry + ',' + optType + ',' + str(oddevenSubType)+str(genericSubType) +',' + str(codeNum) +',' + str(codeVal * len(codeNum.split('-'))) +',' + DtTm.strftime('%Y-%m-%d %H:%M:%S') + ',' + str(codeVal) + ',' + entryNo
                        toWrt = grpEntry + ',' + optType + ',' + str(oddevenSubType)+str(genericSubType) +',' + str(codeNum) +',' + str(usrDisplayDict['lastEntry'][4]) +',' + DtTm.strftime('%Y-%m-%d %H:%M:%S') + ',' + str(codeVal) + ',' + entryNo
                        cf.write(toWrt)
                        cf.write('\n')                         
                        continue
                    cf.write(line)
                print (usrDisplayDict)
        
        if 'lastEntry' in usrDisplayDict:        
            usrDisplayDict['lastEntry'][4] = str(usrDisplayDict['lastEntry'][4])

        if grpEntry == 'no':
            #with open (__package__+'/data/grpEntry.csv','w') as cf:
            with open (__package__+'/data/'+uFileName+'.csv','w') as cf:
                cf.write('GrpEntry,BearingType,SubType,Code,Quantity,DateTime,LastAmt,EntryNo')

        if grpEntry == 'yes' and actionType  != 'edit':

            fileExistFlag = os.path.isfile(__package__+'/data/grpEntry.csv')

            if not fileExistFlag:
                #with open (__package__+'/data/grpEntry.csv','w') as cf:
                with open (__package__+'/data/'+uFileName+'.csv','w') as cf:
                    cf.write('GrpEntry,BearingType,SubType,Code,Quantity,DateTime,LastAmt,EntryNo')
                    cf.write('\n')

            #with open (__package__+'/data/grpEntry.csv','a') as cf:
            with open (__package__+'/data/'+uFileName+'.csv','a') as cf:     
                toWrt=''
                for icnt, itms in enumerate(usrDisplayList):
                    #print(itms)
                    if icnt == 0:
                        toWrt = str(itms)
                    else:
                        toWrt = toWrt +','+str(itms)                
                toWrt = toWrt +','+str(entryNo)            
                cf.write(toWrt)
                cf.write('\n')
        
        for k, v in categoryDict.items():
            tmpK1=0
            for iV in v:
                iV = str(iV)
                
                for k1, v1 in usrAdminDict.items():
                    if k1 == iV:
                        tmpK1 += usrAdminDict[k1]

                catDictTotal[k] = tmpK1
                #catDictTotal[k] = round(float(tmpK1),2)
        
        oneTwentyVal, ninetyVal, tenVal = 0,0,0
        for n, (k, v) in enumerate(usrAdminDict.items()):
            if n <= 119:
                oneTwentyVal += v
            elif n >= 120 and n <= 209:
                ninetyVal += v
            elif n >= 210:
                tenVal += v
        
        sideTotal['oneTwenty'] = round(float(oneTwentyVal),2)
        sideTotal['ninety'] = round(float(ninetyVal),2)
        sideTotal['ten'] = round(float(tenVal),2)
        sideTotal['allTotal'] = round(oneTwentyVal+ninetyVal+tenVal,2)

        if grpEntry == 'yes': 
            usrDisplayDict={}      
            #with open (__package__+'/data/grpEntry.csv','r') as cf:
            with open (__package__+'/data/'+uFileName+'.csv','r') as cf:
                hdr = cf.readline()
                lines = cf.readlines()
                ln2=[]
                cnt = 1
                for ln in lines:
                    #print('printing each line: -->', ln)
                    for _ in ln.split(',')          :
                        ln2.append(_)
                    usrDisplayDict['LastEntry'+str(cnt)]=ln2                
                    cnt += 1
                    ln2=[]
                    #print(usrDisplayDict)

        if request.POST.get('folder') == 'ccat':
            if codeVal is not None:            
                codeVal = round(float(codeVal),2)
            
            for _ in codeNum.split('-'):
                cCatItems[_] += codeVal                

        elif request.POST.get('addOrEdit')  == 'add' and request.POST.get('grpEntry') == 'yes':
            pass

        elif request.POST.get('addOrEdit')  == 'edit':
            if codeVal is not None:            
                codeVal = round(float(codeVal),2)
            
            if request.POST.get('folder') == 'ccat':
                for _ in codeNum.split('-'):
                    cCatItems[_] -= codeVal

        usrDisplayDict_Json={}        
        usrDisplayDict_Json = usrDisplayDict
        usrDisplayDict_List = []
        usrDisplayDict_List.append(usrDisplayDict_Json)
        
        data_json1 = json.dumps(usrDisplayDict_List)

        tabTotal = 0
        for k, v in usrDisplayDict.items():        
            if v[4] != 'None':            
                tabTotal += float(v[4])

        return render(request, 'myapp/create_entry.html', {'data_json': data_json, 'data_json1': data_json1, 'usrDisplayDict': usrDisplayDict, 'codeVal':codeVal, 'codeB4Split': codeB4Split, 'tabTotal': tabTotal})
    
    else:
        try:
            with open (__package__+'/data/solo_'+uFileName+'.csv','r') as sr:

                hdr = sr.readline()
                lines = sr.readlines()
                ln2=[]
                cnt = 1
                for ln in lines:
                    #print('printing each line: -->', ln)
                    for _ in ln.split(',')          :
                        ln2.append(_)
                    usrDisplayDict['LastEntry'+str(cnt)]=ln2                
                    cnt += 1
                    ln2=[]
        except FileNotFoundError:
                pass
        
        try:
            with open (__package__+'/data/'+uFileName+'.csv','r') as gr:
                hdr = gr.readline()
                lines = gr.readlines()
                ln2=[]
                cnt = 1
                for ln in lines:
                    #print('printing each line: -->', ln)
                    for _ in ln.split(',')          :
                        ln2.append(_)
                    usrDisplayDict['LastEntry'+str(cnt)]=ln2                
                    cnt += 1
                    ln2=[]
        except FileNotFoundError:
            pass
        
        tabTotal=0.0
        for k,v in usrDisplayDict.items():
            tabTotal+=float(usrDisplayDict[k][4])

        return render(request, 'myapp/create_entry.html', {'data_json': data_json, 'usrDisplayDict': usrDisplayDict, 'tabTotal': tabTotal})

    
    return render(request, 'myapp/create_entry.html')
    
def addEntry(usrDisplayDict, optType, codeB4Split, codeNum, codeVal, oddevenSubType, genericSubType):    
    
    if optType.strip() == 'code' or optType.strip() == 'mixbearing' or optType.strip() == 'ccat':
        
        for _ in codeNum.split('-'):            
            if _ in usrDict:
                usrDict[_] = usrDict[_] + codeVal
            else:
                usrDict[_]=codeVal                
            usrDisplayDict['lastEntry'][4] += codeVal             
                    
        
    elif optType.strip() == 'category':
        
        for _ in codeNum.split('-'):#7-8-9
        
            lstC = 1
            
            for tmpBrCd in categoryDict[_]:
                
                tmpBrCd = str(tmpBrCd)
                
                if lstC <= 12:                            
                    
                    if tmpBrCd in usrDict:
                        
                        usrDict[tmpBrCd] = float(usrDict[tmpBrCd]) + float((codeVal*9) / 150)
                        lstC += 1
                    else:
                        usrDict[tmpBrCd] = float((codeVal*9) / 150)
                        lstC += 1                                
                    
                        
                elif lstC >= 13 and lstC <= 21:
                    
                    if tmpBrCd in usrDict:                            
                        usrDict[tmpBrCd] = float(usrDict[tmpBrCd]) + float((codeVal*9) / 300)
                        lstC += 1
                    else:
                        usrDict[tmpBrCd] = float((codeVal*9) / 300)
                        lstC += 1                            
                    
                        
                elif lstC == 22:
                    
                    if tmpBrCd in usrDict:                            
                        usrDict[tmpBrCd] = float(usrDict[tmpBrCd]) + float((codeVal*9) / 900)
                        lstC += 1
                    else:
                        usrDict[tmpBrCd] = float((codeVal*9) / 900)
                        lstC += 1
                            
            usrDisplayDict['lastEntry'][4] += codeVal
                            
                        
                        
    elif optType.strip() == 'singlebearing':
        lstC = 1
        for _ in codeNum.split('-'): #7-8-9
            for tmpCode in _:                  
                for tmpBrCd in categoryDict[tmpCode]:
                    
                    tmpBrCd = str(tmpBrCd)
                    
                    if lstC == 13:
                        lstC = 1
                        break                        
                    
                    if lstC <= 12:
                        
                        if tmpBrCd in usrDict:                            
                            usrDict[tmpBrCd] = usrDict[tmpBrCd] + codeVal                                
                            lstC += 1
                        else:
                            usrDict[tmpBrCd] = codeVal
                            lstC += 1
                            
                        usrDisplayDict['lastEntry'][4] += codeVal
                        
    elif optType.strip() == 'doublebearing':
                        
          for _ in codeNum.split('-'):
              
              for tmpCode in _:
                  
                  for tmpBrCd in categoryDict[tmpCode][12:21]:
                      tmpBrCd = str(tmpBrCd)
                      if tmpBrCd in usrDict:
                          usrDict[tmpBrCd] = usrDict[tmpBrCd] + codeVal                              
                      else:
                          usrDict[tmpBrCd]=codeVal
                          
                          
                      usrDisplayDict['lastEntry'][4] += codeVal    
                          
    elif optType.strip() == 'triplebearing':
                        
          for _ in codeNum.split('-'):
              
              for tmpCode in _:
                  
                  for tmpBrCd in categoryDict[tmpCode][-1:]:
                      tmpBrCd = str(tmpBrCd)
                      if tmpBrCd in usrDict:
                          usrDict[tmpBrCd] = usrDict[tmpBrCd] + codeVal                              
                      else:
                          usrDict[tmpBrCd]=codeVal
                          
                          
                      usrDisplayDict['lastEntry'][4] += codeVal    
                          
          
    elif optType.strip() == 'oddeven' and oddevenSubType == 'exclusion':
                          
          for _ in codeNum.split('-'):
              
              for tmpCode in _:
                  
                  for tmpBrCd in oddevenExc[tmpCode]:
                      tmpBrCd = str(tmpBrCd)
                      if tmpBrCd in usrDict:
                          usrDict[tmpBrCd] = usrDict[tmpBrCd] + codeVal
                          usrDict[tmpBrCd] = codeVal
                          
                      else:
                          usrDict[tmpBrCd] = codeVal
                          
                          
                      usrDisplayDict['lastEntry'][4] += codeVal    
    
    elif optType.strip() == 'oddeven' and oddevenSubType == 'inclusion':
                                  
          for _ in codeNum.split('-'):
              
              for tmpCode in _:
                  
                  for tmpBrCd in oddevenInc[tmpCode]:
                      tmpBrCd = str(tmpBrCd)
                      if tmpBrCd in usrDict:
                          usrDict[tmpBrCd]= usrDict[tmpBrCd] + codeVal
                      else:
                          usrDict[tmpBrCd] = codeVal
                          
                          
                      usrDisplayDict['lastEntry'][4] += codeVal    
    
      
    elif optType.strip() == 'generic' and genericSubType == 'single':              
          for _ in codeNum.split('-'):
              
              for tmpCode in _:
                  
                  for tmpBrCd in genSingle[tmpCode]:
                      tmpBrCd = str(tmpBrCd)
                      if tmpBrCd in usrDict:
                          usrDict[tmpBrCd] = usrDict[tmpBrCd] + codeVal
                      else:
                          usrDict[tmpBrCd] = codeVal
                          
                      usrDisplayDict['lastEntry'][4] += codeVal    
                          
                          
          
    elif optType.strip() == 'generic' and genericSubType == 'double':              
          for _ in codeNum.split('-'):
              
              for tmpCode in _:
                  
                  for tmpBrCd in genDouble[tmpCode]:
                      tmpBrCd = str(tmpBrCd)
                      if tmpBrCd in usrDict:
                          usrDict[tmpBrCd] = usrDict[tmpBrCd] + codeVal
                      else:
                          usrDict[tmpBrCd] = codeVal
                          
                          
                      usrDisplayDict['lastEntry'][4] += codeVal    
          
    elif optType.strip() == 'doubledigit':
        
          for tmpCode in codeNum.split('-'):
              for tmpBrCd in doubleDigit[tmpCode]:
                  tmpBrCd = str(tmpBrCd)
                  if tmpBrCd in usrDict:
                      usrDict[tmpBrCd] = usrDict[tmpBrCd] + codeVal
                  else:
                      usrDict[tmpBrCd] = codeVal
                      
                  usrDisplayDict['lastEntry'][4] += codeVal
                      
    elif optType.strip() == 'settype':        
          for tmpCode in codeNum.split('-'):
              for tmpBrCd in setDict[tmpCode]:
                  tmpBrCd = str(tmpBrCd)
                  if tmpBrCd in usrDict:
                      usrDict[tmpBrCd] = usrDict[tmpBrCd] + codeVal                          
                  else:
                      usrDict[tmpBrCd] = codeVal                          
                      
                  usrDisplayDict['lastEntry'][4] += codeVal     
    
    elif optType.strip() == 'royalclub':
        
        #royalClub = {'128': 1, '123': 1, '137': 1, '268': 1, '236': 1, '367': 1, '678': 1, '178': 1, '245': 2, '240': 2, '290': 2, '259': 2, '470': 2, '457': 2, '579': 2, '790': 2, '380': 3, '880': 3, '335': 3, '330': 3, '588': 3, '358': 3, '100': 5, '600': 5, '155': 5, '556': 5, '560': 5, '150': 5, '489': 4, '448': 4, '344': 4, '899': 4, '399': 4, '349': 4, '146': 6, '114': 6, '669': 6, '466': 6, '119': 6, '169': 6, '227': 7, '277': 7, '777': 7, '222': 7, '129': 8, '124': 8, '147': 8, '179': 8, '246': 8, '467': 8, '679': 8, '269': 8, '890': 9, '390': 9, '458': 9, '480': 9, '340': 9, '589': 9, '359': 9, '570': 10, '250': 10, '255': 10, '557': 10, '200': 10, '700': 10, '138': 11, '368': 11, '336': 11, '133': 11, '688': 11, '188': 11, '660': 12, '115': 12, '110': 12, '566': 12, '156': 12, '160': 12, '778': 13, '278': 13, '237': 13, '223': 13, '228': 13, '377': 13, '499': 14, '449': 14, '444': 14, '999': 14, '120': 15, '170': 15, '157': 15, '567': 15, '256': 15, '125': 15, '670': 15, '260': 15, '139': 16, '189': 16, '148': 16, '468': 16, '346': 16, '369': 16, '689': 16, '134': 16, '247': 17, '477': 17, '779': 17, '279': 17, '229': 17, '224': 17, '445': 18, '459': 18, '599': 18, '990': 18, '490': 18, '440': 18, '300': 19, '800': 19, '580': 19, '558': 19, '355': 19, '350': 19, '337': 20, '378': 20, '238': 20, '288': 20, '788': 20, '233': 20, '166': 21, '116': 21, '111': 21, '666': 21, '130': 22, '180': 22, '158': 22, '568': 22, '680': 22, '135': 22, '356': 22, '360': 22, '379': 23, '239': 23, '478': 23, '248': 23, '289': 23, '347': 23, '234': 23, '789': 23, '167': 24, '117': 24, '112': 24, '126': 24, '266': 24, '667': 24, '149': 25, '144': 25, '446': 25, '199': 25, '699': 25, '469': 25, '400': 26, '900': 26, '455': 26, '559': 26, '590': 26, '450': 26, '220': 27, '225': 27, '770': 27, '577': 27, '257': 27, '270': 27, '388': 28, '338': 28, '333': 28, '888': 28, '140': 29, '190': 29, '159': 29, '569': 29, '456': 29, '145': 29, '690': 29, '460': 29, '230': 30, '280': 30, '258': 30, '235': 30, '357': 30, '578': 30, '780': 30, '370': 30, '249': 31, '244': 31, '799': 31, '299': 31, '447': 31, '479': 31, '348': 32, '334': 32, '339': 32, '488': 32, '889': 32, '389': 32, '168': 33, '136': 33, '113': 33, '668': 33, '366': 33, '118': 33, '122': 34, '677': 34, '177': 34, '127': 34, '267': 34, '226': 34, '550': 35, '500': 35, '555': 35, '0': 35, '345': 9}
        #royalClubRev = {'1': [123,128,137,178,236,268,367,678],
        
        for rcBrCd in codeNum.split('-'): 
            
            rcCat = royalClub[rcBrCd]  #string 128 got int 1
            rcCat = str(rcCat)
            for revCd in royalClubRev[rcCat]:
                
                revCd = str(revCd)
                
                if revCd in usrDict:
                    usrDict[revCd] = usrDict[revCd] + codeVal                        
                else:
                    usrDict[revCd] = codeVal
                    
                usrDisplayDict['lastEntry'][4] += codeVal
                
    return (usrDisplayDict)

def editEntry(request, usrAdminDict, usrDict, grpEntry):

    '''
    optType = request.POST.get('folder')
    codeB4Split = request.POST.get('bearing_code')
    codeNum = request.POST.get('brCdSplit')
    codeVal = request.POST.get('amount')
    oddevenSubType = request.POST.get('oddevenSelect')
    genericSubType = request.POST.get('singledouble')
    actionType = request.POST.get('addOrEdit')
    '''

    toEdit = request.POST.get('prevEntry').split(',') #'yes,12,1-2,1000.0'

    grpEntry = toEdit[0]
    optType = toEdit[1]  
    oddevenSubType = toEdit[2]
    genericSubType = toEdit[2]
    codeB4Split = toEdit[3]
    codeNum = toEdit[4]
    codeVal = toEdit[5]
    
    actionType = request.POST.get('addOrEdit')
    entryNo = request.POST.get('entryNo')    
    
    if codeVal is not None:
        codeVal = round(float(codeVal),2)
        #codeVal = int(codeVal)

    '''
     for prvK in usrDict.keys():
        if grpEntry == 'yes':
            if usrAdminDict[prvK] - usrDict[prvK] == 0:
                usrAdminDict[prvK] = usrDict[prvK]
            else:
                usrAdminDict[prvK] = usrAdminDict[prvK] - (usrAdminDict[prvK] - usrDict[prvK])
        elif grpEntry == 'no':
            usrAdminDict[prvK] = usrAdminDict[prvK] - usrDict[prvK]   
    '''

    if optType.strip() == 'code' or optType.strip() == 'mixbearing':
        for eCd in codeNum.split('-'):
            usrAdminDict[eCd] -= codeVal 


    elif optType.strip() == 'category':
        
        for _ in codeNum.split('-'):#7-8-9
        
            lstC = 1
            
            for tmpBrCd in categoryDict[_]:
                
                tmpBrCd = str(tmpBrCd)
                
                if lstC <= 12:                            
                    
                    if tmpBrCd in usrAdminDict:
                        
                        usrAdminDict[tmpBrCd] = int(usrAdminDict[tmpBrCd]) - int((codeVal*9) / 150)
                        lstC += 1
                    else:
                        usrAdminDict[tmpBrCd] = int((codeVal*9) / 150)
                        lstC += 1                                
                    
                        
                elif lstC >= 13 and lstC <= 21:
                    
                    if tmpBrCd in usrAdminDict:                            
                        usrAdminDict[tmpBrCd] = int(usrAdminDict[tmpBrCd]) - int((codeVal*9) / 300)
                        lstC += 1
                    else:
                        usrAdminDict[tmpBrCd] = int((codeVal*9) / 300)
                        lstC += 1                            
                    
                        
                elif lstC == 22:
                    
                    if tmpBrCd in usrAdminDict:                            
                        usrAdminDict[tmpBrCd] = int(usrAdminDict[tmpBrCd]) - int((codeVal*9) / 900)
                        lstC += 1
                    else:
                        usrAdminDict[tmpBrCd] = int((codeVal*9) / 900)
                        lstC += 1                            
    
    elif optType.strip() == 'singlebearing':
        lstC = 1
        for _ in codeNum.split('-'): #7-8-9
            for tmpCode in _:                  
                for tmpBrCd in categoryDict[tmpCode]:
                    
                    tmpBrCd = str(tmpBrCd)
                    
                    if lstC == 13:
                        lstC = 1
                        break                        
                    
                    if lstC <= 12:
                        
                        if tmpBrCd in usrAdminDict:                            
                            usrAdminDict[tmpBrCd] = usrAdminDict[tmpBrCd] - codeVal                                
                            lstC += 1
                        else:
                            usrAdminDict[tmpBrCd] = codeVal
                            lstC += 1
                        
                        
    elif optType.strip() == 'doublebearing':
                        
        for _ in codeNum.split('-'):
            
            for tmpCode in _:
                
                for tmpBrCd in categoryDict[tmpCode][12:21]:
                    tmpBrCd = str(tmpBrCd)
                    if tmpBrCd in usrAdminDict:
                        usrAdminDict[tmpBrCd] = usrAdminDict[tmpBrCd] - codeVal                              
                    else:
                        usrAdminDict[tmpBrCd]=codeVal
                        
    elif optType.strip() == 'triplebearing':
                        
        for _ in codeNum.split('-'):
            
            for tmpCode in _:
                
                for tmpBrCd in categoryDict[tmpCode][-1:]:
                    tmpBrCd = str(tmpBrCd)
                    if tmpBrCd in usrAdminDict:
                        usrAdminDict[tmpBrCd] = usrAdminDict[tmpBrCd] - codeVal                              
                    else:
                        usrAdminDict[tmpBrCd]=codeVal                          
        
    elif optType.strip() == 'oddeven' and oddevenSubType == 'exclusion':
                        
        for _ in codeNum.split('-'):
            
            for tmpCode in _:
                
                for tmpBrCd in oddevenExc[tmpCode]:
                    tmpBrCd = str(tmpBrCd)
                    if tmpBrCd in usrAdminDict:
                        usrAdminDict[tmpBrCd] = usrAdminDict[tmpBrCd] - codeVal
                        usrAdminDict[tmpBrCd] = codeVal
                        
                    else:
                        usrAdminDict[tmpBrCd] = codeVal                         
    
    elif optType.strip() == 'oddeven' and oddevenSubType == 'inclusion':
                                
        for _ in codeNum.split('-'):
            
            for tmpCode in _:
                
                for tmpBrCd in oddevenInc[tmpCode]:
                    tmpBrCd = str(tmpBrCd)
                    if tmpBrCd in usrAdminDict:
                        usrAdminDict[tmpBrCd]= usrAdminDict[tmpBrCd] - codeVal
                    else:
                        usrAdminDict[tmpBrCd] = codeVal    
    
    elif optType.strip() == 'generic' and genericSubType == 'single':              
        for _ in codeNum.split('-'):           
            
            for tmpCode in _:
                
                for tmpBrCd in genSingle[tmpCode]:
                    tmpBrCd = str(tmpBrCd)
                    if tmpBrCd in usrAdminDict:
                        usrAdminDict[tmpBrCd] = usrAdminDict[tmpBrCd] - codeVal
                    else:
                        usrAdminDict[tmpBrCd] = codeVal                          
        
    elif optType.strip() == 'generic' and genericSubType == 'double':              
        for _ in codeNum.split('-'):
            
            for tmpCode in _:
                
                for tmpBrCd in genDouble[tmpCode]:
                    tmpBrCd = str(tmpBrCd)
                    if tmpBrCd in usrAdminDict:
                        usrAdminDict[tmpBrCd] = usrAdminDict[tmpBrCd] - codeVal
                    else:
                        usrAdminDict[tmpBrCd] = codeVal 
        
    elif optType.strip() == 'doubledigit':
        for tmpCode in codeNum.split('-'):
            for tmpBrCd in doubleDigit[tmpCode]:
                tmpBrCd = str(tmpBrCd)
                if tmpBrCd in usrAdminDict:
                    usrAdminDict[tmpBrCd] = usrAdminDict[tmpBrCd] - codeVal
                else:
                    usrAdminDict[tmpBrCd] = codeVal
                    
    elif optType.strip() == 'settype':                
        for tmpCode in codeNum.split('-'):
            for tmpBrCd in setDict[tmpCode]:
                tmpBrCd = str(tmpBrCd)
                if tmpBrCd in usrAdminDict:
                    usrAdminDict[tmpBrCd] = usrAdminDict[tmpBrCd] - codeVal                          
                else:
                    usrAdminDict[tmpBrCd] = codeVal 
    
    elif optType.strip() == 'royalclub':

        for rcBrCd in codeNum.split('-'): 
            
            rcCat = royalClub[rcBrCd]  #string 128 got int 1
            rcCat = str(rcCat)
            for revCd in royalClubRev[rcCat]:
                
                revCd = str(revCd)
                
                if revCd in usrAdminDict:
                    usrAdminDict[revCd] = usrAdminDict[revCd] - codeVal                        
                else:
                    usrAdminDict[revCd] = codeVal                
    
    elif optType.strip() == 'Ccat':
        for tmpCode in codeNum.split('-'):
            cCatItems[tmpCode] -= codeVal

    return (usrAdminDict)

def admin_view(request):

    print ('came here in admin_view')
    
    if not request.user.is_authenticated:
        print('############################')
        print(request.user.is_authenticated)
        print('############################')
        return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))  
    
    if request.method == 'POST':
        if request.POST['bearingCds'] != "" and request.POST['insCode'] == 'createBreaks':
            create_breaks(request)
        elif 'download_break_file' in request.POST and request.POST['insCode'] == 'dwnBrkFile':            
            retRes = download_break_file(request)
            return (retRes)        
        elif 'delete_all_data' in request.POST and request.POST['insCode'] == 'delAllDatacd':
            retRes = delete_all_data(request)
            return (retRes)
        elif 'download_all_data' in request.POST and request.POST['insCode'] == 'dwnAllData':
            retRes = download_all_data(request)        
            return (retRes)
        
    rowVal = request.POST.getlist('rowVal')
    
    items = list(usrAdminDict.items())
    table_data = [items[i:i+10] for i in range(0, len(items), 10)]
    
    nonZeroCdCnt = 0
    for k, v in usrAdminDict.items():        
        if v > 0:            
            nonZeroCdCnt = nonZeroCdCnt + 1

    cCatTotal = sum(cCatItems.values()) 
    
    context = {'table_data': table_data, 'usrAdminDict': json.dumps(usrAdminDict), 'categoryDict': categoryDict, 'catDictTotal':catDictTotal, 'sideTotal': sideTotal, 'nonZeroCdCnt': nonZeroCdCnt, 'cCatItems': cCatItems, 'cCatTotal': cCatTotal}

    print ('before render....')
    return render(request, 'myapp/admin_view.html', context)    
    
def create_breaks(request):
    
    nonZeroKeyList=[]
    dwnPath = __package__+'/downloads/'
    
    for file in os.listdir(dwnPath):
        if file.endswith('.csv'):            
            try:
                os.rename(dwnPath+file, dwnPath+'/archive/'+file)                  
            except FileExistsError :
                os.remove(dwnPath+file)

    DtTm = datetime.datetime.now().strftime("%Y-%m-%dT%H%M%S")
    flName = dwnPath+'/Create_Breaks_'+ DtTm +'.csv'
    optCsv = open(flName, mode='w', newline='')
    writer = csv.writer(optCsv)

    #nonZeroKeyList = [key for key in usrAdminDict]
    for k, v in usrAdminDict.items():
        if v != 0:
            nonZeroKeyList.append(k)
            #nonZeroKeyList = list(usrAdminDict.keys())
    
    #userInp = '55,55,55,55'    
    userInp = request.POST.get('bearingCds')
    lst2Write, tmplst2Write, finalList, exp_hdr = [],[],[],[]
    lstDict={}
    if userInp is not None:
        
        for hI, rndCnt in enumerate(userInp.split(',')): 
            tmp_sorted_items=[]
            sorted_items=[]   
            
            for rndItems in random.sample(nonZeroKeyList, int(rndCnt)):        
                lst2Write.append(rndItems + '=' + str(usrAdminDict[rndItems]))
                tmplst2Write.append(rndItems)
                nonZeroKeyList.remove(rndItems)
                lstDict[rndItems]= str(usrAdminDict[rndItems])
           
            tmp_sorted_items = sorted(lstDict.items(), key=lambda x: x[1], reverse=True)
            sorted_items = [f"{key}={value}" for key, value in tmp_sorted_items]
            finalList.append(sorted_items)
            lstDict={}
            #exp_hdr.append('Break - '+str(hI+1)) 

        lst=[]
        for lCnt, rndCnt in enumerate(userInp.split(',')):    
            if lCnt == 0:
                lst.append(lst2Write[0:int(rndCnt)])
            else:
                lst.append(lst2Write[int(rndCnt):int(rndCnt)-1+int(rndCnt)])
        lst=[]        

        rC=0
        exp_hdr=[]
        for hI, rI in enumerate(userInp.split(',')):
            rI = int(rI)
            lst.append(lst2Write[rC:rI+rC])            
            rC+=rI
            exp_hdr.append('Break - '+str(hI+1)) 

        #print(lst)
        exp_data = zip_longest(*lst, fillvalue = '')        
        writer.writerow(exp_hdr)
        writer.writerows(exp_data)
        optCsv.close()
    
    return redirect('admin_view')
    #return HttpResponse("All values are now cleared!")

def download_all_data(request):

    with open(__package__+'/downloadall/Bearing_Code_All.csv', 'w') as csvfile:
        iCnt = 0
        ltWrt = ''
        
        for iK, iV in usrAdminDict.items():

            if iCnt == 0:
                ltWrt += iK + "="+ str(iV)
                iCnt += 1
            elif iCnt <=8:
                ltWrt += ',' + iK + "="+ str(iV)
                iCnt += 1
            elif iCnt == 9:
                ltWrt += ',' + iK + "="+ str(iV)
                csvfile.write(ltWrt)
                csvfile.write('\n')
                iCnt = 0
                ltWrt = ''
    
    file_path = __package__+'/downloadall/Bearing_Code_All.csv'
    
    with open(file_path, 'rb') as csv_file:
        print(csv_file.name)
        response = HttpResponse(csv_file.read(), content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
        return response

    return redirect('admin_view')
    
    
def download_break_file(request):
    
    dwnPath = __package__+'/downloads/'
    #print(dwnPath)
    for file in os.listdir(dwnPath):
        if file.endswith('.csv'):
            file_path = os.path.join(dwnPath, file)
            #print(file_path)            
            
            with open(dwnPath+file, 'rb') as csv_file:
                print(csv_file.name)      
                response = HttpResponse(csv_file.read(), content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                return response
    
    return redirect('admin_view')
    #return HttpResponse("download_create_file clicked!")

def delete_all_data(request):
    #print('delete_all_data')
    uFileName = str(request.user)
    for k, v in usrAdminDict.items():
        usrAdminDict[k]=0        
        
    for k, v in catDictTotal.items():
        catDictTotal[k]=0
        
    for k,v in sideTotal.items():
        sideTotal[k]=0

    for k,v in cCatItems.items():
        cCatItems[k]=0

    #os.remove(__package__+'/data/grpEntry.csv')
    #with open (__package__+'/data/grpEntry.csv','w') as cf:
    for fileNames in os.listdir(__package__+'/data/'):        
        with open (__package__+'/data/'+fileNames,'w') as cf:        
            cf.write('GrpEntry,BearingType,SubType,Code,Quantity,DateTime,LastAmt,EntryNo')
            cf.write('\n')
    
    forceLogOutUsers()
    return redirect('admin_view')
    #return HttpResponse("All values are now cleared!")

def forceLogOutUsers():        
    from django.contrib.sessions.models import Session
    from django.utils import timezone
    from django.contrib.auth import get_user_model

    User = get_user_model()

    # Get all active sessions
    active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
    
    # Delete sessions for non-admin users
    for session in active_sessions:
        session_data = session.get_decoded()
        user_id = session_data.get('_auth_user_id')
        session.delete()

def create_new_group(request):
    print('create_entry')
    uFileName = str(request.user)
    for fileNames in os.listdir(__package__+'/data/'):
        with open (__package__+'/data/'+fileNames,'w') as cf:
            cf.write('GrpEntry,BearingType,SubType,Code,Quantity,DateTime,LastAmt,EntryNo')
            cf.write('\n')
    return redirect('create_entry')

defaultCodeDict = {'128': 0, '129': 0, '120': 0, '130': 0, '140': 0, '123': 0, '124': 0, '125': 0, '126': 0, '127': 0,
	'137': 0, '138': 0, '139': 0, '149': 0, '159': 0, '150': 0, '160': 0, '134': 0, '135': 0, '136': 0,
	'146': 0, '147': 0, '148': 0, '158': 0, '168': 0, '169': 0, '179': 0, '170': 0, '180': 0, '145': 0,
	'236': 0, '156': 0, '157': 0, '167': 0, '230': 0, '178': 0, '250': 0, '189': 0, '234': 0, '190': 0,
	'245': 0, '237': 0, '238': 0, '239': 0, '249': 0, '240': 0, '269': 0, '260': 0, '270': 0, '235': 0,
	'290': 0, '246': 0, '247': 0, '248': 0, '258': 0, '259': 0, '278': 0, '279': 0, '289': 0, '280': 0,
	'380': 0, '345': 0, '256': 0, '257': 0, '267': 0, '268': 0, '340': 0, '350': 0, '360': 0, '370': 0,
	'470': 0, '390': 0, '346': 0, '347': 0, '348': 0, '349': 0, '359': 0, '369': 0, '379': 0, '389': 0,
	'489': 0, '480': 0, '490': 0, '356': 0, '357': 0, '358': 0, '368': 0, '378': 0, '450': 0, '460': 0,
	'560': 0, '570': 0, '580': 0, '590': 0, '456': 0, '367': 0, '458': 0, '459': 0, '469': 0, '479': 0,
	'579': 0, '589': 0, '670': 0, '680': 0, '690': 0, '457': 0, '467': 0, '468': 0, '478': 0, '569': 0,
	'678': 0, '679': 0, '689': 0, '789': 0, '780': 0, '790': 0, '890': 0, '567': 0, '568': 0, '578': 0,
	'100': 0, '110': 0, '166': 0, '112': 0, '113': 0, '114': 0, '115': 0, '116': 0, '117': 0, '118': 0,
	'119': 0, '200': 0, '229': 0, '220': 0, '122': 0, '277': 0, '133': 0, '224': 0, '144': 0, '226': 0,
	'155': 0, '228': 0, '300': 0, '266': 0, '177': 0, '330': 0, '188': 0, '233': 0, '199': 0, '244': 0,
	'227': 0, '255': 0, '337': 0, '338': 0, '339': 0, '448': 0, '223': 0, '288': 0, '225': 0, '299': 0,
	'335': 0, '336': 0, '355': 0, '400': 0, '366': 0, '466': 0, '377': 0, '440': 0, '388': 0, '334': 0,
	'344': 0, '499': 0, '445': 0, '446': 0, '447': 0, '556': 0, '449': 0, '477': 0, '559': 0, '488': 0,
	'399': 0, '660': 0, '599': 0, '455': 0, '500': 0, '600': 0, '557': 0, '558': 0, '577': 0, '550': 0,
	'588': 0, '688': 0, '779': 0, '699': 0, '799': 0, '880': 0, '566': 0, '800': 0, '667': 0, '668': 0,
	'669': 0, '778': 0, '788': 0, '770': 0, '889': 0, '899': 0, '700': 0, '990': 0, '900': 0, '677': 0,
	'777': 0, '444': 0, '111': 0, '888': 0, '555': 0, '222': 0, '999': 0, '666': 0, '333': 0, '000': 0}

categoryDict = {'1': [128,137,146,236,245,290,380,470,489,560,579,678,100,119,155,227,335,344,399,588,669,777],	
	'2': [129,138,147,156,237,246,345,390,480,570,589,679,110,200,228,255,336,499,660,688,778,444],
	'3': [120,139,148,157,238,247,256,346,490,580,670,689,166,229,300,337,355,445,599,779,788,111],
	'4': [130,149,158,167,239,248,257,347,356,590,680,789,112,220,266,338,400,446,455,699,770,888],
	'5': [140,159,168,230,249,258,267,348,357,456,690,780,113,122,177,339,366,447,500,799,889,555],
	'6': [123,150,169,178,240,259,268,349,358,367,457,790,114,277,330,448,466,556,600,880,899,222],
	'7': [124,160,179,250,269,278,340,359,368,458,467,890,115,133,188,223,377,449,557,566,700,999],
	'8': [125,134,170,189,260,279,350,369,378,459,468,567,116,224,233,288,440,477,558,800,990,666],
	'9': [126,135,180,234,270,289,360,379,450,469,478,568,117,144,199,225,388,559,577,667,900,333],
	'0': [127,136,145,190,235,280,370,389,460,479,569,578,118,226,244,299,334,488,550,668,677,'000']}

oddevenExc = {'0':[127,136,145,235,370,389,479,569,578],
    '1':[128,146,236,245,290,380,470,489,560],
    '2':[129,138,147,156,237,390,570,589,679],
    '3':[148,238,247,256,346,490,580,670,689],
    '4':[130,149,158,167,239,257,347,356,590],
    '5':[140,168,230,249,258,267,348,690,780],
    '6':[150,169,178,259,349,358,367,457,790],
    '7':[124,160,250,269,278,340,368,458,467],
    '8':[125,134,170,189,279,350,369,378,459],
    '9':[126,180,270,289,360,450,469,478,568]}


oddevenInc = {'0':[190,280,460],
    '1':[137,579,678],
    '2':[246,345,480],
    '3':[120,139,157],
    '4':[248,680,789],
    '5':[159,357,456],
    '6':[123,240,268],
    '7':[179,359,890],
    '8':[260,468,567],
    '9':[135,234,379]}

genSingle={'0':[120,130,140,150,160,170,180,190,230,240,250,260,270,280,290,340,350,360,370,380,390,450,460,470,480,490,560,570,580,590,670,680,690,780,790,890],
    '1':[120,123,124,125,126,127,128,129,130,134,135,136,137,138,139,140,145,146,147,148,149,150,156,157,158,159,160,167,168,169,170,178,179,180,189,190],
    '2':[120,123,124,125,126,127,128,129,230,234,235,236,237,238,239,240,245,246,247,248,249,250,256,257,258,259,260,267,268,269,270,278,279,280,289,290],
    '3':[123,130,134,135,136,137,138,139,230,234,235,236,237,238,239,340,345,346,347,348,349,350,356,357,358,359,360,367,368,369,370,378,379,380,389,390],
    '4':[124,134,140,145,146,147,148,149,234,240,245,246,247,248,249,340,345,346,347,348,349,450,456,457,458,459,460,467,468,469,470,478,479,480,489,490],
    '5':[125,135,145,150,156,157,158,159,235,245,250,256,257,258,259,345,350,356,358,359,357,450,456,457,458,459,560,567,568,569,570,578,579,580,589,590],
    '6':[126,136,146,156,160,167,168,169,236,246,256,260,267,268,269,346,356,360,367,368,369,456,460,467,468,469,560,567,568,569,670,678,679,680,689,690],
    '7':[127,137,147,157,167,170,178,179,237,247,257,267,270,278,279,347,357,367,370,378,379,457,467,470,478,479,567,570,578,579,670,678,679,780,789,790],
    '8':[128,138,148,158,168,178,180,189,238,248,258,268,278,280,289,348,358,368,378,380,389,458,468,478,480,489,568,578,580,589,678,680,689,780,789,890],
    '9':[129,139,149,159,169,179,189,190,239,249,259,269,279,289,290,349,359,369,379,389,390,459,469,479,489,490,569,579,589,590,679,689,690,789,790,890]}


genDouble={
    '0':[100,110,200,220,300,330,400,440,500,550,600,660,700,770,800,880,900,990],
    '1':[100,110,112,113,114,115,116,117,118,119,122,133,144,155,166,177,188,199],
    '2':[112,122,200,220,223,224,225,226,227,228,229,233,244,255,266,277,288,299],
    '3':[113,133,223,233,300,330,334,335,336,337,338,339,344,355,366,377,388,399],
    '4':[114,144,224,244,334,344,400,440,445,446,447,448,449,455,466,477,488,499],
    '5':[115,155,225,255,335,355,445,455,500,550,556,557,558,559,566,577,588,599],
    '6':[116,166,226,266,336,366,446,466,556,566,600,660,667,668,669,677,688,699],
    '7':[117,177,227,277,337,377,447,477,557,577,667,677,700,770,778,779,788,799],
    '8':[118,188,228,288,338,388,448,488,558,588,668,688,778,788,800,880,889,899],
    '9':[119,199,229,299,339,399,449,499,559,599,669,699,779,799,889,899,900,990]}

doubleDigit = {'00':[0,100,200,300,400,500,600,700,800,900],
    '10':[100,110,120,130,140,150,160,170,180,190],
    '11':[110,111,112,113,114,115,116,117,118,119],
    '12':[112,120,122,123,124,125,126,127,128,129],
    '13':[113,123,130,133,134,135,136,137,138,139],
    '14':[114,124,134,140,144,145,146,147,148,149],
    '15':[115,125,135,145,150,155,156,157,158,159],
    '16':[116,126,136,146,156,160,166,167,168,169],
    '17':[117,127,137,147,157,167,170,177,178,179],
    '18':[118,128,138,148,158,168,178,180,188,189],
    '19':[119,129,139,149,159,169,179,189,190,199],
    '20':[120,200,220,230,240,250,260,270,280,290],
    '22':[122,220,222,223,224,225,226,227,228,229],
    '23':[123,223,230,233,234,235,236,237,238,239],
    '24':[124,224,234,240,244,245,246,247,248,249],
    '25':[125,225,235,245,250,255,256,257,258,259],
    '26':[126,226,236,246,256,260,266,267,268,269],
    '27':[127,227,237,247,257,267,270,277,278,279],
    '28':[128,228,238,248,258,268,278,280,288,289],
    '29':[129,229,239,249,259,269,279,289,290,299],
    '30':[130,230,300,330,340,350,360,370,380,390],
    '33':[133,233,330,333,334,335,336,337,338,339],
    '34':[134,234,334,340,344,345,346,347,348,349],
    '35':[135,235,335,345,350,355,356,357,358,359],
    '36':[136,236,336,346,356,360,366,367,368,369],
    '37':[137,237,337,347,357,367,370,377,378,379],
    '38':[138,238,338,348,358,368,378,380,388,389],
    '39':[139,239,339,349,359,369,379,389,390,399],
    '40':[140,240,340,400,440,450,460,470,480,490],
    '44':[144,244,344,440,444,445,446,447,448,449],
    '45':[145,245,345,445,450,455,456,457,458,459],
    '46':[146,246,346,446,456,460,466,467,468,469],
    '47':[147,247,347,447,457,467,470,477,478,479],
    '48':[148,248,348,448,458,468,478,480,488,489],
    '49':[149,249,349,449,459,469,479,489,490,499],
    '50':[150,250,350,450,500,550,560,570,580,590],
    '55':[155,255,355,455,550,555,556,557,558,559],
    '56':[156,256,356,456,556,560,566,567,568,569],
    '57':[157,257,357,457,557,567,570,577,578,579],
    '58':[158,258,358,458,558,568,578,580,588,589],
    '59':[159,259,359,459,559,569,579,589,590,599],
    '60':[160,260,360,460,560,600,660,670,680,690],
    '66':[166,266,366,466,566,660,666,667,668,669],
    '67':[167,267,367,467,567,667,670,677,678,679],
    '68':[168,268,368,468,568,668,678,680,688,689],
    '69':[169,269,369,469,569,669,679,689,690,699],
    '70':[170,270,370,470,570,670,700,770,780,790],
    '77':[177,277,377,477,577,677,770,777,778,779],
    '78':[178,278,378,478,578,678,778,780,788,789],
    '79':[179,279,379,479,579,679,779,789,790,799],
    '80':[180,280,380,480,580,680,780,800,880,890],
    '88':[188,288,388,488,588,688,788,880,888,889],
    '89':[189,289,389,489,589,689,789,889,890,899],
    '90':[190,290,390,490,590,690,790,890,900,990],
    '99':[199,299,399,499,599,699,799,899,990,999]}

setDict = {'30': [128,136,138,147,148,149,158,168,169,247,249,250,257,258,259,269,270,279,350,358,360,368,369,370,380,469,470,479,570,580],
           '40': [124,125,128,129,130,134,140,145,170,178,180,189,230,235,236,239,245,256,289,290,340,346,347,356,367,390,457,458,467,478,568,569,578,589,670,679,689,690,780,790],
           '50': [135,136,137,138,139,146,147,148,149,157,158,159,168,169,179,240,246,247,248,249,250,257,258,259,260,268,269,270,279,280,350,357,358,359,360,368,369,370,379,380,460,468,469,470,479,480,570,579,580,680],
           '70': [120,123,124,125,126,127,128,129,130,134,140,145,150,156,160,167,170,178,180,189,190,230,234,235,236,237,238,239,245,256,267,278,289,290,340,345,346,347,348,349,356,367,378,389,390,450,456,457,458,459,467,478,489,490,560,567,568,569,578,589,590,670,678,679,689,690,780,789,790,890]}
394959

royalClub = {'128': 1, '123': 1, '137': 1, '268': 1, '236': 1, '367': 1, '678': 1, '178': 1, '245': 2, '240': 2, '290': 2, '259': 2, '470': 2, '457': 2, '579': 2, '790': 2, '380': 3, '880': 3, '335': 3, '330': 3, '588': 3, '358': 3, '100': 5, '600': 5, '155': 5, '556': 5, '560': 5, '150': 5, '489': 4, '448': 4, '344': 4, '899': 4, '399': 4, '349': 4, '146': 6, '114': 6, '669': 6, '466': 6, '119': 6, '169': 6, '227': 7, '277': 7, '777': 7, '222': 7, '129': 8, '124': 8, '147': 8, '179': 8, '246': 8, '467': 8, '679': 8, '269': 8, '890': 9, '390': 9, '458': 9, '480': 9, '340': 9, '589': 9, '359': 9, '570': 10, '250': 10, '255': 10, '557': 10, '200': 10, '700': 10, '138': 11, '368': 11, '336': 11, '133': 11, '688': 11, '188': 11, '660': 12, '115': 12, '110': 12, '566': 12, '156': 12, '160': 12, '778': 13, '278': 13, '237': 13, '223': 13, '228': 13, '377': 13, '499': 14, '449': 14, '444': 14, '999': 14, '120': 15, '170': 15, '157': 15, '567': 15, '256': 15, '125': 15, '670': 15, '260': 15, '139': 16, '189': 16, '148': 16, '468': 16, '346': 16, '369': 16, '689': 16, '134': 16, '247': 17, '477': 17, '779': 17, '279': 17, '229': 17, '224': 17, '445': 18, '459': 18, '599': 18, '990': 18, '490': 18, '440': 18, '300': 19, '800': 19, '580': 19, '558': 19, '355': 19, '350': 19, '337': 20, '378': 20, '238': 20, '288': 20, '788': 20, '233': 20, '166': 21, '116': 21, '111': 21, '666': 21, '130': 22, '180': 22, '158': 22, '568': 22, '680': 22, '135': 22, '356': 22, '360': 22, '379': 23, '239': 23, '478': 23, '248': 23, '289': 23, '347': 23, '234': 23, '789': 23, '167': 24, '117': 24, '112': 24, '126': 24, '266': 24, '667': 24, '149': 25, '144': 25, '446': 25, '199': 25, '699': 25, '469': 25, '400': 26, '900': 26, '455': 26, '559': 26, '590': 26, '450': 26, '220': 27, '225': 27, '770': 27, '577': 27, '257': 27, '270': 27, '388': 28, '338': 28, '333': 28, '888': 28, '140': 29, '190': 29, '159': 29, '569': 29, '456': 29, '145': 29, '690': 29, '460': 29, '230': 30, '280': 30, '258': 30, '235': 30, '357': 30, '578': 30, '780': 30, '370': 30, '249': 31, '244': 31, '799': 31, '299': 31, '447': 31, '479': 31, '348': 32, '334': 32, '339': 32, '488': 32, '889': 32, '389': 32, '168': 33, '136': 33, '113': 33, '668': 33, '366': 33, '118': 33, '122': 34, '677': 34, '177': 34, '127': 34, '267': 34, '226': 34, '550': 35, '500': 35, '555': 35, '0': 35, '345': 9}
royalClubRev = {'1': [123,128,137,178,236,268,367,678],
'2': [240,245,259,290,457,470,579,790],
'3': [330,335,358,380,588,880],
'4': [344,349,399,448,489,899],
'5': [100,150,155,556,560,600],
'6': [114,119,146,169,466,669],
'7': [222,227,277,777],
'8': [124,129,147,179,246,269,467,679],
'9': [340,345,359,390,458,480,589,890],
'10': [200,250,255,557,570,700],
'11': [133,138,188,336,368,688],
'12': [110,115,156,160,566,660],
'13': [223,228,237,278,377,778],
'14': [444,449,499,999],
'15': [120,125,157,170,256,260,567,670],
'16': [134,139,148,189,346,369,468,689],
'17': [224,229,247,279,477,779],
'18': [440,445,459,490,599,990],
'19': [300,350,355,558,580,800],
'20': [233,238,288,337,378,788],
'21': [111,116,166,666],
'22': [130,135,158,180,356,360,568,680],
'23': [234,239,248,289,347,379,478,789],
'24': [112,117,126,167,266,667],
'25': [144,149,199,446,469,699],
'26': [400,450,455,559,590,900],
'27': [220,225,257,270,577,770],
'28': [333,338,388,888],
'29': [140,145,159,190,456,460,569,690],
'30': [230,235,258,280,357,370,578,780],
'31': [244,249,299,447,479,799],
'32': [334,339,348,389,488,889],
'33': [113,118,136,168,366,668],
'34': [122,127,177,226,267,677],
'35': [0,500,550,555]}

py_dict_list=[defaultCodeDict, categoryDict, doubleDigit, setDict]
    
usrDict = {}
usrAdminDict = {}
cCatItems = {'1':0,'2':0,'3':0,'4':0,'5':0,'6':0,'7':0,'8':0,'9':0,'0':0}
usrAdminDict = defaultCodeDict
catDictTotal = {'1':0,'2':0,'3':0,'4':0,'5':0,'6':0,'7':0,'8':0,'9':0,'0':0}
sideTotal = {'oneTwenty':0,'ninety':0,'ten':0,'allTotal':0}


with open (__package__+'/data/grpEntry.csv','w') as cf:
    cf.write('GrpEntry,BearingType,SubType,Code,Quantity,DateTime,LastAmt,EntryNo')
    cf.write('\n')
