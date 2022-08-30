from __future__ import print_function
from asyncio.windows_events import NULL
from itertools import count
from turtle import bgcolor, color
from smartcard.CardMonitoring import CardMonitor, CardObserver
#from smartcard.util import toHexString

from PIL import Image
from smartcard.System import readers
from smartcard.util import HexListToBinString, toHexString, toBytes
from smartcard.CardMonitoring import CardMonitor, CardObserver
from smartcard.CardConnectionObserver import ConsoleCardConnectionObserver

from smartcard.Exceptions import NoCardException
from smartcard.util import toHexString
from smartcard.sw.SWExceptions import SWException, WarningProcessingException

from tkinter import *
from time import sleep
import configparser

import getData
import nhsoAuthen
from tkinter import ttk
 
# a simple card observer that prints inserted/removed cards
class PrintObserver(CardObserver):
    """A simple card observer that is notified
    when cards are inserted/removed from the system and
    prints the list of cards    """
    def __init__(self, tv_cid,tv_name,tv_birth,tv_pttype,tv_hometel,tv_claimtype,tv_claimcode,tv_createdate,tv_status):
        self.observer = ConsoleCardConnectionObserver()
        self.tv_cid = tv_cid
        self.tv_name = tv_name
        self.tv_birth = tv_birth
        self.tv_pttype = tv_pttype
        self.tv_hometel = tv_hometel
        self.tv_claimtype = tv_claimtype
        self.tv_claimcode = tv_claimcode
        self.tv_createdate = tv_createdate
        self.tv_status = tv_status
        self.tv_status.set("กรุณาเสียบบัตรประจำตัวประชาชน")
        self.tv_claim = tv_status
        
    def update(self, observable, actions):
        
        (addedcards, removedcards) = actions

        for card in addedcards:
             
                 
                print("+Inserted: ", toHexString(card.atr))    

                self.tv_status.set("----กำลังอ่านข้อมูลจากบัตร---")
                cid = getData.checkCard()   #อ่าน CID จาก SmartCard 
                readcard_api = nhsoAuthen.readCard() #อ่าน CID จาก API
                if readcard_api == False:
                    self.tv_status.set("ไม่สามารถติดต่อกับ สปสช.ได้ กรุณาลองอีกครั้ง") 
                    break
                hometel = getData.getMobilePhone(cid)
                
                if hometel.isnumeric() and len(hometel)==10:
                    statusLastAuthen =nhsoAuthen.checkLatedAuthen(cid) #เช็คการขอ Authen ล่าสุดในวันนี้
                    print(statusLastAuthen)
                else:
                    print("[INFO:] Hometel is Error")
                    #nhsoAuthen.playsound("noHomeTel.mp3")
                    self.tv_status.set("!!ไม่พบหมายเลขโทรศัพท์ในฐานข้อมูล!!")
                if statusLastAuthen is True:
                    #nhsoAuthen.playsound('authenRepeat.mp3')
                    print("[Warnning:] ไม่สามารถขอ Authen ซ้ำในวันเดียวกันได้")
                    lastDataAuthen=nhsoAuthen.returnLatedAuthen(cid)
                    self.tv_status.set("!!ไม่สามารถขอ Authen ซ้ำในวันเดียวกันได้!!")
                    self.tv_cid.set(cid)
                    self.tv_name.set(readcard_api['fname']+' '+readcard_api['lname'])
                    self.tv_birth.set(readcard_api['age'])
                    self.tv_pttype.set(readcard_api['subInscl'])
                    self.tv_hometel.set(hometel)
                    self.tv_claimtype.set(lastDataAuthen['claimType'])
                    self.tv_claimcode.set(lastDataAuthen['claimCode'])
                    self.tv_createdate.set(lastDataAuthen['claimDateTime'])
                    self.tv_status.set("!!ไม่สามารถขอ Authen ซ้ำในวันเดียวกันได้!!")
                else:
                   
                    AuthenDetial=nhsoAuthen.confirmSave(hometel, cid)
                    print("รายการ",AuthenDetial)
                    #AuthenDetial = nhsoAuthen.saveDraft(hometel,cid)
                    if AuthenDetial == False: #Authen มากกว่า 2 ครั้ง
                        lastDataAuthen = nhsoAuthen.returnLatedAuthen(cid)
                         
                        self.tv_cid.set(cid)
                        self.tv_name.set(readcard_api['fname']+' '+readcard_api['lname'])
                        self.tv_birth.set(readcard_api['age'])
                        self.tv_pttype.set(readcard_api['subInscl'])
                        self.tv_hometel.set(hometel)
                        self.tv_claimtype.set(lastDataAuthen['claimType'])
                        self.tv_claimcode.set(lastDataAuthen['claimCode'])
                        self.tv_createdate.set(lastDataAuthen['claimDateTime'])
                        self.tv_status.set("!!ไม่สามารถขอ Authen มากกว่า 2 ครั้งในวันได้!!")
                    else:
                        self.tv_cid.set(cid)
                        self.tv_name.set(readcard_api['fname']+' '+readcard_api['lname'])
                        self.tv_birth.set(readcard_api['age'])
                        self.tv_pttype.set(readcard_api['subInscl'])
                        self.tv_hometel.set(hometel)
                        
                        self.tv_claimtype.set(AuthenDetial['claimType'])
                        self.tv_claimcode.set(AuthenDetial['claimCode'])
                        self.tv_createdate.set(AuthenDetial['claimDateTime']) 
                        self.tv_status.set("ยืนยันตัวตนเรียบร้อยแล้ว")        
                   

        for card in removedcards:

            #เป็นส่วนของการ clear text box 
            self.tv_cid.set("")
            self.tv_name.set("")
            self.tv_birth.set("")
            self.tv_pttype.set("")
            self.tv_hometel.set("")
            self.tv_claimtype.set("")
            self.tv_claimcode.set("")
            self.tv_createdate.set("")
            self.tv_status.set("กรุณาเสียบบัตรประจำตัวประชาชน")
            
            print("-Removed: ", toHexString(card.atr))



def gui():

    def selection():  
        config = configparser.RawConfigParser()
        config.read('app-config.ini')
        config.set('ClaimType','CODE',radio.get())
        with open('app-config.ini', 'w') as configfile:
            config.write(configfile)
    
    root = Tk()
    root.geometry('515x580')
    root['bg']='#235D3A'
    root.title("ระบบยืนยันตัวตนเข้ารับบริการ [AuthenNHSO]")
    tv_cid = StringVar()
    tv_name = StringVar()
    tv_birth = StringVar()
    tv_pttype = StringVar()
    tv_hometel = StringVar()
    tv_claimtype = StringVar()
    tv_claimcode = StringVar()
    tv_createdate = StringVar()
    tv_status = StringVar()
    tv_claimtype_code = StringVar()
    radio = StringVar()
    
    #ส่วนของการแสดงผลข้อมูลบัตรประชาชน
    labelframe = LabelFrame(root, text="ข้อมูลบัตรประชาชน",font=("bold",14),width='475',height='220', bg='#235D3A',fg='#fff')
    labelframe.place(x=15,y=80)

    label_cid = Label(root, text="เลขประจำตัวประชาชน",width=20,font=("bold", 12),bg='#235D3A',fg='#C0EDD0',anchor='e')
    label_cid.place(x=20,y=120)
    label_name = Label(root, text="ชื่อ-นามสกุล",width=20,font=("bold", 12),bg='#235D3A' ,fg='#C0EDD0',anchor='e')
    label_name.place(x=20,y=150)
    label_birth = Label(root, text="อายุ",width=20,font=("bold", 12),bg='#235D3A',fg='#C0EDD0',anchor='e')
    label_birth.place(x=20,y=180)
    label_pttype = Label(root, text="สิทธิการรักษา",width=20,font=("bold", 12),bg='#235D3A',fg='#C0EDD0',anchor='e')
    label_pttype.place(x=20,y=210)
    label_hometel = Label(root, text="เบอร์โทรศัพท์",width=20,font=("bold", 12),bg='#235D3A',fg='#C0EDD0',anchor='e')
    label_hometel.place(x=20,y=240)
    #
    lbl_cid = Label(root, width=20, textvariable=tv_cid,font=("bold", 12),bg='#74927A',fg='#fff')
    lbl_cid.place(x=250,y=120)
    lbl_name = Label(root, width=20, textvariable=tv_name,font=("bold", 12),bg='#74927A',fg='#fff')
    lbl_name.place(x=250,y=150)
    lbl_birth = Label(root, width=20, textvariable=tv_birth,font=("bold", 12),bg='#74927A',fg='#fff')
    lbl_birth.place(x=250,y=180)
    lbl_pttype = Label(root, width=20, textvariable=tv_pttype,font=("bold", 12),bg='#74927A',fg='#fff')
    lbl_pttype.place(x=250,y=210)
    lbl_hometel = Label(root, width=20, textvariable=tv_hometel,font=("bold", 12),bg='#74927A',fg='#fff')
    lbl_hometel.place(x=250,y=240)
    
    #ส่วนของการแสดงผลข้อมูลยืนยันตัวตน
    labelframe = LabelFrame(root, text="ข้อมูลยืนยันตัวตน",font=("bold",14),width='475',height='150', bg='#235D3A',fg='#fff')
    labelframe.place(x=15,y=320)
    #
    label_claimType = Label(root, text="ประเภทการเข้ารับบริการ",width=20,font=("bold", 12),bg='#235D3A',fg='#C0EDD0',anchor='e')
    label_claimType.place(x=20,y=350)
    label_claimCode = Label(root, text="claimCode",width=20,font=("bold", 12),bg='#235D3A' ,fg='#C0EDD0',anchor='e')
    label_claimCode.place(x=20,y=380)
    label_datetime = Label(root, text="วันที่เข้ารับบริการ",width=20,font=("bold", 12),bg='#235D3A',fg='#C0EDD0',anchor='e')
    label_datetime.place(x=20,y=410)
    #
    lbl_claimtype = Label(root, width=20, textvariable=tv_claimtype,font=("bold", 12),bg='#74927A',fg='#fff')
    lbl_claimtype.place(x=250,y=350)
    lbl_claimcode = Label(root, width=20, textvariable=tv_claimcode,font=("bold", 12),bg='#74927A',fg='#fff')
    lbl_claimcode.place(x=250,y=380)
    lbl_createdate = Label(root, width=20, textvariable=tv_createdate,font=("bold", 12),bg='#74927A',fg='#fff')
    lbl_createdate.place(x=250,y=410)

    #สถานะบัต่รประชาชน
    lbl_status = Label(root, width=30, textvariable=tv_status,font=("bold", 20),bg='#235D3A',fg='#fff')
    lbl_status.place(x=10,y=20)
    
    
    
    #ประเภทการเข้ารับบริการ claim type
    R1 = Radiobutton(root, text="OPD/ IPD/ PP", variable=radio,bg='#73C088', value='PG0060001',
                  command=selection)
    R1.place(x=20,y=480)  
    R1.select()

    R2 = Radiobutton(root, text="Home Isolation", variable=radio,bg='#73C088', value='PG0090001' ,  
                  command=selection)  
    R2.place(x=120,y=480)   
    R3 = Radiobutton(root, text="Self Isolation", variable=radio,bg='#73C088',value='PG0110001' ,  
                  command=selection)  
    R3.place(x=225,y=480)
    
    R4 = Radiobutton(root, text="HD", variable=radio,bg='#73C088',value='PG0130001' ,  
                  command=selection)  
    R4.place(x=312,y=480) 

    R4 = Radiobutton(root, text="UCEP PLUS", variable=radio,bg='#73C088', value='PG0120001' ,  
                  command=selection)  
    R4.place(x=350,y=480) 


    #เชื่อมต่อ CardMonitor
    cardmonitor = CardMonitor()
    cardobserver = PrintObserver(tv_cid,tv_name,tv_birth,tv_pttype,tv_hometel,tv_claimtype,tv_claimcode,tv_createdate,tv_status)
    cardmonitor.addObserver(cardobserver)
    root.mainloop()


def main():
    gui()

if __name__ == "__main__":    
    gui()