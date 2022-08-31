# -*- coding: utf-8 -*-
"""
Created on Mon May  2 11:34:10 2022

@author: BT
"""
import mydb
from smartcard.Exceptions import NoCardException
from smartcard.System import readers
from smartcard.util import HexListToBinString, toHexString, toBytes
from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.util import toHexString
from smartcard.CardConnectionObserver import ConsoleCardConnectionObserver
from smartcard.sw.SWExceptions import SWException, WarningProcessingException
import configparser
import pymysql.cursors


try :
    SELECT = [0x00, 0xA4, 0x04, 0x00, 0x08] # Check card
    THAI_CARD = [0xA0, 0x00, 0x00, 0x00, 0x54, 0x48, 0x00, 0x01]
    CMD_CID = [0x80, 0xb0, 0x00, 0x04, 0x02, 0x00, 0x0d] # CID
    CMD_THFULLNAME = [0x80, 0xb0, 0x00, 0x11, 0x02, 0x00, 0x64] # TH Fullname
    CMD_ENFULLNAME = [0x80, 0xb0, 0x00, 0x75, 0x02, 0x00, 0x64] # EN Fullname
    CMD_BIRTH = [0x80, 0xb0, 0x00, 0xD9, 0x02, 0x00, 0x08] # Date of birth
    CMD_GENDER = [0x80, 0xb0, 0x00, 0xE1, 0x02, 0x00, 0x01] # Gender
    CMD_ISSUER = [0x80, 0xb0, 0x00, 0xF6, 0x02, 0x00, 0x64] # Card Issuer
    CMD_ISSUE = [0x80, 0xb0, 0x01, 0x67, 0x02, 0x00, 0x08] # Issue Date
    CMD_EXPIRE = [0x80, 0xb0, 0x01, 0x6F, 0x02, 0x00, 0x08] # Expire Date
    CMD_ADDRESS = [0x80, 0xb0, 0x15, 0x79, 0x02, 0x00, 0x64] # Address 
except:
    pass 

def thai2unicode(data):
    result = ''
    result = bytes(data).decode('tis-620')
    return result.strip()#strip()หมายถึงไม่เอา string ที่ไม่ต้องการ

def getData(cmd, req = [0x00, 0xc0, 0x00, 0x00]):
    r = readers()
    print ("Available readers:", r)
    reader = r[0]
    connection = reader.createConnection()
    connection.connect()
    atr = connection.getATR()
    try:
        data, sw1, sw2 = connection.transmit(cmd)
        data, sw1, sw2 = connection.transmit(req + [cmd[-1]])
   
    except SWException as e:
        print(str(e))  
        connection.disconnect()  
        print("ERR")
    return [data, sw1, sw2];

# define the APDUs used in this script
# https://github.com/chakphanu/ThaiNationalIDCard/blob/master/APDU.md
def checkCard():
    cid=""
    TH=""
    r = readers()
    #print ("[Available readers ]", r)
    reader = r[0]
    #print ("[Using ]", reader)

    for reader in readers():
            try:
                connection = reader.createConnection()
                connection.connect()
                
            except NoCardException:
                print(reader, 'no card inserted')
                
                continue
            else:
                atr = connection.getATR()
                print ("ATR: " + toHexString(atr))
                if (atr[0] == 0x3B & atr[1] == 0x67):
                    req = [0x00, 0xc0, 0x00, 0x01]
                else :
                    req = [0x00, 0xc0, 0x00, 0x00]                
                try:    
                    data, sw1, sw2 = connection.transmit(SELECT + THAI_CARD)
                    print ("Select Applet: %02X %02X" % (sw1, sw2))
                    count = []#เก็บข้อมูลตัวเลข และวันที่แปลงเป็นตัวหนังสือ 
                     # CID
                    data = getData(CMD_CID, req)
                    cid = thai2unicode(data[0])
                    count.append(cid)
                    print ("เลขประจำตัวประชาชน: " + cid)
                    return cid
                    
                except SWException as e:
                    print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                    print(str(e))                  
  
def getMobilePhone(cid):
    try:
        connection = mydb.getConnection()
        cursor = connection.cursor()
        sql = "SELECT REPLACE(p.hometel,'-','') as hometel FROM patient p WHERE p.cid =%s"
        cursor.execute(sql, (cid))
        
    except pymysql.InternalError as error:
        print("[ Wanning ] No Connecttion Database!!!")
    
    else:
        results = cursor.fetchall()
        for row in results:
            hometel = row['hometel']
    return hometel

def getHn(cid):
    try:
        connection = mydb.getConnection()
        cursor = connection.cursor()
        sql = "SELECT REPLACE(p.hn,'-','') as hn FROM patient p WHERE p.cid =%s"
        cursor.execute(sql, (cid))
        
    except pymysql.InternalError as error:
        print("[ Wanning ] No Connecttion Database!!!")
    
    else:
        results = cursor.fetchall()
        for row in results:
            hn = row['hn']
    return hn


