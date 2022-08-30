# -*- coding: utf-8 -*-
"""
Created on Mon May  2 08:31:13 2022

@author: BT
"""
import requests
import time
import configparser
from datetime import datetime
#from win32printing import Printer
#URL API AuthenCode
url_read_only ="http://127.0.0.1:8189/api/smartcard/read-card-only?readImageFlag=false"
url_read="http://127.0.0.1:8189/api/smartcard/read?readImageFlag=false"
url_confirm_save="http://127.0.0.1:8189/api/nhso-service/confirm-save"
url_save_draft="http://127.0.0.1:8189/api/nhso-service/save-as-draft"
url_lasted_authen_code="http://127.0.0.1:8189/api/nhso-service/latest-authen-code/"

config = configparser.RawConfigParser()
config.read('app-config.ini')
HospCode = config.get('HOSxP', 'HOSPCODE')

def readCard():
    while True:
        try:
            response = requests.get(url_read, verify=False,timeout=2)
            result = response.json()
            print("[INFO][url_read] Response Status Code",response.status_code)
            #print(result)

        except requests.exceptions.Timeout as e:
                print(e)

        else:
            if response.status_code ==200:
                cid = result["pid"]
                panme = result["fname"]
                panme = result["lname"]
                subInscl = result["subInscl"]
                age = result["age"]
                correLation =result["correlationId"]
                return result
            elif response.status_code ==500:
                print("500")
                return False



def confirmSave(hometel,cid):
    claimType = config.get('ClaimType', 'code')
    while True:
        try:
            response = requests.get(url_read, verify=False,timeout=2)
            result = response.json()
            print("[INFO][url_read] Response Status Code",response.status_code)
            #print(result)

        except requests.exceptions.Timeout as e:
                print(e)

        else:
            if response.status_code ==200:
                cid = result["pid"]
                correLation =result["correlationId"]
                cliamJson = {
                    "pid": cid,
                    "claimType": claimType,
                    "mobile": hometel,
                    "correlationId": correLation,
                    "hn": "string",
                    "hcode": HospCode
                            }
                try:
                    response_save = requests.post(url_confirm_save, json = cliamJson,timeout=1)
                    result_save = response_save.json()
                    #print(result_save)
                    if "error" in result_save:
                        return False #กรณีไม่สามารถ Authen ซ้ำในวันเดียวกันมากกว่า 2 ครั้ง

                    if response_save.status_code ==200:
                        
                        #print(result_save)
                        print("----------------------------------------")
                        print("[pid:]",result_save['pid'])
                        print("[cliamType:]",result_save['claimType'])
                        print("claimCode:",result_save["claimCode"])
                        print("[createDate:]",result_save['createdDate'])
                        print("----------------------------------------")

                        printClaimType = result_save['claimType']
                        printClaimCode= result_save['claimCode']
                        printCreatedDate = result_save['createdDate']
                        #toPrinter(printClaimType,printClaimCode,printCreatedDate)
                        #print(result_save["claimCode"])
                        #playsound('authenSuccess.mp3')
                        return result_save


                    if response_save.status_code ==400:
                        print(result_save["errors"][0]["defaultMessage"])
                        

                except requests.exceptions.Timeout as e:
                    print(e)
def saveDraft(hometel,cid):
    config.read('app-config.ini')
    claimType = config.get('ClaimType', 'code')
    while True:
        try:
            response = requests.get(url_read, verify=False,timeout=2)
            result = response.json()
            print("[INFO][url_read] Response Status Code",response.status_code)
            #print(result)

        except requests.exceptions.Timeout as e:
                print(e)

        else:
            if response.status_code ==200:
                cid = result["pid"]
                correLation =result["correlationId"]

                cliamJson = {
                    "pid": cid,
                    "claimType": claimType,
                    "mobile": hometel,
                    "correlationId": correLation,
                    "hn": "string",
                    "hcode": HospCode
                            }
                try:
                    response_save = requests.post(url_save_draft, json = cliamJson,timeout=1)
                    result_save = response_save.json()
                    #print(result_save)
                    if response_save.status_code ==200:
                        print("----------------------------------------")
                        print("[pid:]",result_save['pid'])
                        print("[cliamType:]",result_save['claimType'])
                        print("[createDate:]",result_save['createdDate'])
                        print("----------------------------------------")
                        #print(result_save["claimCode"])
                        printPid = result_save['pid']
                        printClaimType = result_save['claimType']
                        printCreatedDate = result_save['createdDate']

                        #toPrinter(printPid,printClaimType,printCreatedDate)
                        #playsound('authenSuccess.mp3')
                        return result_save


                    if response_save.status_code ==400:
                        print(result_save["errors"][0]["defaultMessage"])

                except requests.exceptions.Timeout as e:
                    print(e)

def checkLatedAuthen(cid):
    config.read('app-config.ini')
    claimType = config.get('ClaimType', 'code')
    while True:
        try:
            response_lasted = requests.get(url_lasted_authen_code+cid,timeout=1)
            result_lasted = response_lasted.json()

            if "claimCode" in result_lasted: #ถ้ามีรหัส claimCode
                print("---------------------------------------------")
                print("LastClaimCode:",result_lasted["claimType"])
                print("claimCode:",result_lasted["claimCode"])
                print("claimDateTime:" ,result_lasted["claimDateTime"])
                print("---------------------------------------------")


                printClaimType = result_lasted['claimType']
                printClaimCode = result_lasted['claimCode']
                printClaimDateTime = result_lasted['claimDateTime']

                lastDate = result_lasted['claimDateTime'].split(sep='T')[0]
                nowDate =str(datetime.date(datetime.now()))

                #print(nowDate)
                #print(lastDate)
                if lastDate != nowDate: #ไม่มีการขอ Authen
                    print("[INFO] ไม่มีการขอ Authen Code ในวันนี้")
                    return False

                elif result_lasted["claimType"] == claimType and lastDate ==nowDate: #มีการขอ Authen

                    print("[INFO] มีการขอ Authen แล้ว")
                    #toPrinter(printClaimType,printClaimCode,printClaimDateTime)
                    

                    return True
                elif result_lasted["claimType"] != claimType and lastDate ==nowDate: #มีการขอ Authen แต่คนละประเภท
                    print("[INFO] มีการขอ Authen Code แล้วในวันนี้ แต่คนละ ClaimType")
                    return False


            else:
                print("[INFO]ไม่พบรหัส ClaimCode")
                return False

        except requests.exceptions.Timeout as e:
            print(e)

def returnLatedAuthen(cid):
    claimType = config.get('ClaimType', 'code')
    while True:
        try:
            response_lasted = requests.get(url_lasted_authen_code+cid,timeout=1)
            result_lasted = response_lasted.json()

            if "claimCode" in result_lasted: #ถ้ามีรหัส claimCode
                print("---------------------------------------------")
                print("LastClaimCode:",result_lasted["claimType"])
                print("claimCode:",result_lasted["claimCode"])
                print("claimDateTime:" ,result_lasted["claimDateTime"])
                print("---------------------------------------------")              

                return result_lasted
        except requests.exceptions.Timeout as e:
            print(e)

#returnLatedAuthen('3729900095098')