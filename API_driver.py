##control module
##How to handle the python 2.7 code?
        ## see -> https://stackoverflow.com/questions/27863832/calling-python-2-script-from-python-3

#This project takes advantage of existing APIs found at
#https://research.stlouisfed.org/docs/api/fred/

from urllib.request import urlopen
import operator
import datetime
import json
import csv

import FRBapi
import fred_API
#import python27api
import scratchAPI


def writeMeta(l, fname): #collects and writes meta data

    mname=fname[:fname.rfind('.')]+'Meta.txt'
    print('writing to: ', mname)

    with open(mname, 'w') as file:
        file.write('Accessed ' + str(datetime.date.today())+'\n'+'\n'+'\n')
        for ID in l:
            key="&api_key=3b7e7d31bcc6d28556c82c290eb3572e&file_type=json"
            url='https://api.stlouisfed.org/fred/series?series_id='+ID+key
            response=urlopen(url)
            content=response.read()
            data=json.loads(content.decode('utf8'))
            file.write(ID+'\n')
            file.write(data['seriess'][0]['title']+'\n')
            file.write(data['seriess'][0]['seasonal_adjustment']+ '\n'+ 'frequency: ' +
                        data['seriess'][0]['frequency']+' units: '+ data['seriess'][0]['units']+'\n')
            file.write('start: '+ data['seriess'][0]['observation_start']+ ' end:'+
                       data['seriess'][0]['observation_end']+
                       '\n \n ---------------- \n ---------------- \n')
        file.close()

00
def collectDates(obs, op):
#TODO fred_API dictionary returned from get obs does not have "date" key but has timestamp
#TODO may need to switch to using timestamp

        dates=set()
        for k in obs.keys():
            tempDates= set()
            for item in obs[k]:
                tempDates.add(item['date']) #TODO should just use list comprehension
            if dates==set():
                dates = dates.union(tempDates)
            else:
                dates = op(dates, tempDates)

        return dates
#TODO refactor this -> really ugly

def printCSV(obs): #prints csv

    print('Would you like to record for all dates (A) or all compatible dates (C)?')
    if input().upper()=='C': op=operator.and_
    else: op=operator.or_

    fileName=input("Enter file name to write to: ")
    with open(fileName, "w") as file:
        wr=csv.writer(file)

        keys=["dates"]
        for k in obs.keys(): keys.append(k)
        wr.writerow(keys)

        dates=collectDates(obs, op)
        if dates==[] and op==operator.and_:
                print("No compatible dates; recording all dates.")
                dates=collectDates(obs, operator.or_)

        for d in dates:
            l = [d]
            for series in obs.keys():
                for ob in obs[series]:
                    if ob['date'] in dates:
                        l.append(ob['value'])
            wr.writerow(l)

        if input('Would you like to record meta data?(Y/N): ').upper()=='Y':
            writeMeta(list(obs.keys()), fileName)#defaults to no


def printSearchResults(searchRes):

    index=1
    for item in searchRes:
        print(str(index)+') '+item[0])
        index+=1
        if index > 50:
            break


def mainLoop(): #main loop

    obs, more={}, True

    APIs = {'1' : FRBapi, '2' : fred_API,
             '3' : scratchAPI} #TODO add way to call python 27 api
    #TODO Each module will have get series method and get obs method

    api_choice = None

    while(api_choice not in APIs.keys()):
        print("Select API")
        print(" 1) FRB 2) FRED 3) scratch")
        api_choice = input()

    api = APIs[api_choice]
    lucky = (input('Feeling lucky? (Y/N): ').upper()=='Y')

    while(more):
        titles = input("Enter search keys: ").split(' ')
        for t in titles:
            #obs.update(searchMethod(t, feelingLucky)) #TODO refactor search methods to return dictionary
            searhRes = api.searchTitle(t)
            printSearchResults(searhRes)
            selections = input("Enter Selections: ").split(' ') #TODO doesn't handle two word keys (like "european union)"
            for i in selections:
                obs.update(api.getObs(searhRes[int(i)][1])) ##TODO update to receive {series: (date : value)}
        more = (input("Search Again(Y/N): ").upper() == 'Y')

    if obs!={}: printCSV(obs) #TODO
    else: print('no data recorded -> good bye :)')

if __name__=="__main__":
    mainLoop()
