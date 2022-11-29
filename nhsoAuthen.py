# -*- coding: utf-8 -*-
"""
Created on Mon May  2 08:31:13 2022

@author: BT
"""
from distutils.log import error
import requests
import configparser
from datetime import datetime
from win32printing import Printer
import getData
import logging
import urllib.request
import time
#URL API AuthenCode
url_read_only ="http://127.0.0.1:8189/api/smartcard/read-card-only?readImageFlag=false"
url_read="http://127.0.0.1:8189/api/smartcard/read?readImageFlag=false"
url_confirm_save="http://127.0.0.1:8189/api/nhso-service/confirm-save"
url_save_draft="http://127.0.0.1:8189/api/nhso-service/save-as-draft"
url_lasted_authen_code="http://127.0.0.1:8189/api/nhso-service/latest-authen-code/"
url_terminal="http://127.0.0.1:8189/api/smartcard/terminals"

config = configparser.RawConfigParser()
config.read('app-config.ini')
HospCode = config.get('HOSxP', 'HOSPCODE')
insertdb = config.get('HOSxP', 'insertdb')
#activeprint = config.get('ClaimType', 'insertdb')
 
logging.basicConfig(filename='authen.log',level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')
logging.FileHandler('authen.log', mode='w')

def checkTerminal():
    while True:
        try:
            response = requests.get(url_terminal, verify=False,timeout=2)
            result = response.json()
            #logging.info(response.status_code)
            print(result)

        except requests.exceptions.Timeout as e:
            logging.info(e)
            return False

        else:
            if response.status_code ==200:
                return result
            elif response.status_code ==500:
                logging.info("HTTP response status codes 500")
                return False


def readCard():
    while True:
        try:
            response = requests.get(url_read, verify=False,timeout=2)
            result = response.json()
            #logging.info(response.status_code)
            #print(result)

        except requests.exceptions.Timeout as e:
            logging.info(e)
            print(e)
            #return False

        else:
            if response.status_code ==200:
                return result
            elif response.status_code ==500:
                logging.info("HTTP response status codes 500")
                #return False



def confirmSave(hometel,cid,hn):
    config.read('app-config.ini')
    claimType = config.get('ClaimType', 'code')
    while True:
        try:
            response = requests.get(url_read, verify=False,timeout=2)
            result = response.json()
            #logging.info("[INFO][url_read] Response Status Code",response.status_code)
          
        except requests.exceptions.Timeout as e:
                logging.critical(e)

        else:
            if response.status_code ==200:
                cid = result["pid"]
                correLation =result["correlationId"]
                cliamJson = {
                    "pid": cid,
                    "claimType": claimType,
                    "mobile": hometel,
                    "correlationId": correLation,
                    "hn": hn,
                    "hcode": HospCode
                            }
                try:
                    response_save = requests.post(url_confirm_save, json = cliamJson,timeout=2)
                    result_save = response_save.json()
                    #print(result_save)

                    if "error" in result_save:
                        print(result_save['errors'][0]['defaultMessage'])
                        error_msg=result_save['errors'][0]['defaultMessage']
                        return result_save #กรณีไม่สามารถ Authen ซ้ำในวันเดียวกันมากกว่า 2 ครั้ง

                    if response_save.status_code ==200:
                        
                        #print(result_save)
                        print("----------------------------------------")
                        print("[pid:]",result_save['pid'])
                        print("[cliamType:]",result_save['claimType'])
                        print("claimCode:",result_save["claimCode"])
                        print("[createDate:]",result_save['createdDate'])
                        print("----------------------------------------")

                        pid = result_save['pid']
                        printClaimType = result_save['claimType']
                        printClaimCode= result_save['claimCode']
                        printCreatedDate = result_save['createdDate']
                        
                        #if activeprint =="Y":
                           #toPrinter(printClaimType,printClaimCode,printCreatedDate)
                        if insertdb =="Y":
                            getData.insertDB(pid,printClaimType,printClaimCode,printCreatedDate) 
                        return result_save


                    elif response_save.status_code ==400:                        
                        logging.warning(result_save["errors"][0]["defaultMessage"])
                        return True

                    else:
                       logging.critical("ไม่สามารถติดต่อกับ Service สปสช. ได้")
                       return True
                        

                except requests.exceptions.Timeout as e:
                    logging.warning(e)

            else:
                logging.critical("ไม่สามารถติดต่อกับ Service สปสช. ได้")
                return True 



def checkLatedAuthen(cid):
    config.read('app-config.ini')
    claimType = config.get('ClaimType', 'code')
    while True:
        try:
            response_lasted = requests.get(url_lasted_authen_code+cid,timeout=2)
            result_lasted = response_lasted.json()

            if "claimCode" in result_lasted: #ถ้ามีรหัส claimCode
                print("---------------------------------------------")
                print("LastClaimCode:",result_lasted["claimType"])
                print("claimCode:",result_lasted["claimCode"])
                print("claimDateTime:" ,result_lasted["claimDateTime"])
                print("---------------------------------------------")

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
            logging.critical(e)

def returnLatedAuthen(cid):
    while True:
        try:
            response_lasted = requests.get(url_lasted_authen_code+cid,timeout=2)
            result_lasted = response_lasted.json()

            if "claimCode" in result_lasted: #ถ้ามีรหัส claimCode
                print("---------------------------------------------")
                print("LastClaimCode:",result_lasted["claimType"])
                print("claimCode:",result_lasted["claimCode"])
                print("claimDateTime:" ,result_lasted["claimDateTime"])
                print("---------------------------------------------")              

                return result_lasted
        except requests.exceptions.Timeout as e:
            logging.critical(e)

def toPrinter(cliamType,printClaimCode,CreatedDate):
    font = {
    "height": 18,
}
    with Printer(linegap=2) as printer:
        printer.text("ประเภท  "+cliamType, font_config=font)
        printer.text("วันที่"+CreatedDate, font_config=font)
        printer.text("ClaimCode"+printClaimCode, font_config=font)
        printer.text(" ", font_config=font)
        printer.text(" ", font_config=font)
        printer.text(" ", font_config=font)
        
        printer.new_page()
#returnLatedAuthen('3729900095098')
#toPrinter('1234','1234','1234')


    
