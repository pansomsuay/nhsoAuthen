from __future__ import print_function
from asyncio.windows_events import NULL
from itertools import count
from multiprocessing.sharedctypes import Value
from tkinter.messagebox import showerror, showinfo, showwarning
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
import mydb
import getData
import nhsoAuthen
from tkinter import ttk
from functools import partial  

config = configparser.RawConfigParser()
config.read('app-config.ini')
config.set('ClaimType','code','PG0060001')
with open('app-config.ini', 'w') as configfile:
            config.write(configfile)

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
                hn= getData.getHn(cid)
                
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
                    print("XXXX")
                    AuthenDetial=nhsoAuthen.confirmSave(hometel, cid, hn)
                    #AuthenDetial = nhsoAuthen.saveDraft(hometel,cid)
                    print(AuthenDetial)

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
                        self.tv_status.set("!!มีการขอ Authen ผิดเงื่อนไข สปสช.!!")

                    elif AuthenDetial == True: #ไม่สามารถเชื่อมต่อ Server ได้
                        self.tv_status.set("!!ไม่สามารถเชื่อมต่อ Service สปสช. ได้!!")

                    else:
                        self.tv_cid.set(cid)
                        self.tv_name.set(readcard_api['fname']+' '+readcard_api['lname'])
                        self.tv_birth.set(readcard_api['age'])
                        self.tv_pttype.set(readcard_api['subInscl'])
                        self.tv_hometel.set(hometel)
                        
                        self.tv_claimtype.set(AuthenDetial['claimType'])
                        self.tv_claimcode.set(AuthenDetial['claimCode'])
                        if "createDate" in AuthenDetial:
                            self.tv_createdate.set(AuthenDetial['createDate'])
                        elif "createdDate" in AuthenDetial:
                            self.tv_createdate.set(AuthenDetial['createdDate'])

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

def dbSettingGui():
     
    def settingClose():
        dbWindows.destroy()

    def dbSubmit(): 
        config = configparser.RawConfigParser()
        config.read('app-config.ini')
        config.set('HOSxP','ip',host_var.get())
        config.set('HOSxP','db',database_var.get())
        config.set('HOSxP','user',user_var.get())
        config.set('HOSxP','password',pass_var.get())
        config.set('HOSxP','hn',hn_var.get())
        config.set('HOSxP','hospcode',hospcode_var.get())
        with open('app-config.ini', 'w') as configfile:
            config.write(configfile)
        settingClose()

    def testConnectDB():
        host = host_var.get()
        user = user_var.get()
        password = pass_var.get()
        db = database_var.get()
        try:
            connection =mydb.chkConnection(host,user,password,db)
            connection = mydb.getConnection()
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION()")
            results = cursor.fetchone()
            showinfo("nhsoAuthen","CONNECTION SUCCESSFULL")
            print ("CONNECTION SUCCESSFULL")     
        except:
            showwarning("nhsoAuthen","CONNECTION ERRORc!!")
            print ("ERROR IN CONNECTION")
            return False



    dbWindows=Tk()
    dbWindows.geometry('320x280')
    dbWindows['bg']='#235D3A'
    dbWindows.title("Database Connection")
    host_var =StringVar(dbWindows)
    database_var =StringVar(dbWindows)
    user_var =StringVar(dbWindows)
    pass_var =StringVar(dbWindows)
    hn_var =StringVar(dbWindows)
    hospcode_var=StringVar(dbWindows)
   
    config = configparser.RawConfigParser()
    config.read('app-config.ini')
    ip =config.get('HOSxP','ip')
    db =config.get('HOSxP','db')
    user =config.get('HOSxP','user')
    password =config.get('HOSxP','password')
    hn = config.get('HOSxP','hn')
    hospcode =  config.get('HOSxP','hospcode')
    
    host_var.set(ip)
    database_var.set(db)
    user_var.set(user)
    pass_var.set(password)
    hn_var.set(hn)
    hospcode_var.set(hospcode)


        #ส่วนของการแสดงผลข้อมูลบัตรประชาชน
    labelframe = LabelFrame(dbWindows, text="ตั้งค่าการเชื่อมต่อฐานข้อมูล",font=("bold",10),width='300',height='210', bg='#235D3A',fg='#fff')
    labelframe.place(x=10,y=10)
    label_host = Label(dbWindows, text="Host",width=10,font=("bold", 10),bg='#235D3A',fg='#C0EDD0',anchor='e')
    label_host.place(x=15,y=40)
    label_database = Label(dbWindows, text="Databasae",width=10,font=("bold", 10),bg='#235D3A',fg='#C0EDD0',anchor='e')
    label_database.place(x=15,y=70)
    label_user = Label(dbWindows, text="user",width=10,font=("bold", 10),bg='#235D3A',fg='#C0EDD0',anchor='e')
    label_user.place(x=15,y=100)
    label_pass = Label(dbWindows, text="password",width=10,font=("bold", 10),bg='#235D3A',fg='#C0EDD0',anchor='e')
    label_pass.place(x=15,y=130)
    label_hn = Label(dbWindows, text="จำนวนหลัก HN",width=10,font=("bold", 10),bg='#235D3A',fg='#C0EDD0',anchor='e')
    label_hn.place(x=15,y=160)
    label_hospcode = Label(dbWindows, text="รหัสโรงพยาบาล",width=10,font=("bold", 10),bg='#235D3A',fg='#C0EDD0',anchor='e')
    label_hospcode.place(x=15,y=190)

    host_entry = Entry(dbWindows,textvariable = host_var,font=("bold", 10))
    
    host_entry.place(x=120,y=40)
    database_entry = Entry(dbWindows,textvariable = database_var,font=("bold", 10))
    database_entry.place(x=120,y=70)
    user_entry = Entry(dbWindows,textvariable = user_var,font=("bold", 10))
    user_entry.place(x=120,y=100)
    password_entry = Entry(dbWindows,textvariable = pass_var,font=("bold", 10),show="*")
    password_entry.place(x=120,y=130)
    hn_entry = Entry(dbWindows,textvariable = hn_var,font=("bold", 10))
    hn_entry.place(x=120,y=160)
    hn_hospcode = Entry(dbWindows,textvariable = hospcode_var,font=("bold", 10))
    hn_hospcode.place(x=120,y=190)

    sub_btn=Button(dbWindows,text = 'บันทึก',font=("bold", 12),command=dbSubmit)
    sub_btn.place(x=220,y=230)
    sub_btn=Button(dbWindows,text = 'ทดสอบการเชื่อมต่อ',font=("bold", 12),command=testConnectDB)
    sub_btn.place(x=60,y=230)
    
     
    
def gui():
    
    def handle_focus(event):
        if event.widget == root:
            root.focus_set()
            
    def selection():  
        config = configparser.RawConfigParser()
        config.read('app-config.ini')
        config.set('ClaimType','CODE',radio.get())
        with open('app-config.ini', 'w') as configfile:
            config.write(configfile)
    #Main Windows
    root = Tk()
    root.geometry('540x300+500+300')
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
    labelframe = LabelFrame(root, text="ข้อมูลบัตรประชาชน",font=("bold",12),width='300',height='190', bg='#235D3A',fg='#fff')
    labelframe.place(x=15,y=60)

    label_cid = Label(root, text="เลขบัตรประชาชน",width=10,font=("bold", 10),bg='#235D3A',fg='#C0EDD0',anchor='e')
    label_cid.place(x=20,y=90)
    label_name = Label(root, text="ชื่อ-นามสกุล",width=10,font=("bold", 10),bg='#235D3A' ,fg='#C0EDD0',anchor='e')
    label_name.place(x=20,y=120)
    label_birth = Label(root, text="อายุ",width=10,font=("bold", 10),bg='#235D3A',fg='#C0EDD0',anchor='e')
    label_birth.place(x=20,y=150)
    label_pttype = Label(root, text="สิทธิการรักษา",width=10,font=("bold", 10),bg='#235D3A',fg='#C0EDD0',anchor='e')
    label_pttype.place(x=20,y=180)
    label_hometel = Label(root, text="เบอร์โทรศัพท์",width=10,font=("bold", 10),bg='#235D3A',fg='#C0EDD0',anchor='e')
    label_hometel.place(x=20,y=210)
    #
    lbl_cid = Label(root, width=20, textvariable=tv_cid,font=("bold", 10),bg='#74927A',fg='#fff')
    lbl_cid.place(x=120,y=90)
    lbl_name = Label(root, width=20, textvariable=tv_name,font=("bold", 10),bg='#74927A',fg='#fff')
    lbl_name.place(x=120,y=120)
    lbl_birth = Label(root, width=20, textvariable=tv_birth,font=("bold", 10),bg='#74927A',fg='#fff')
    lbl_birth.place(x=120,y=150)
    lbl_pttype = Label(root, width=20, textvariable=tv_pttype,font=("bold", 10),bg='#74927A',fg='#fff')
    lbl_pttype.place(x=120,y=180)
    lbl_hometel = Label(root, width=20, textvariable=tv_hometel,font=("bold", 10),bg='#74927A',fg='#fff')
    lbl_hometel.place(x=120,y=210)
    
    #ส่วนของการแสดงผลข้อมูลยืนยันตัวตน
    labelframe = LabelFrame(root, text="ข้อมูลยืนยันตัวตน",font=("bold",12),width='200',height='190', bg='#235D3A',fg='#fff')
    labelframe.place(x=320,y=60)
    #
    label_claimType = Label(root, text="ClaimType",width=10,font=("bold", 10),bg='#235D3A',fg='#C0EDD0',anchor='e')
    label_claimType.place(x=330,y=90)
    label_claimCode = Label(root, text="claimCode",width=10,font=("bold", 10),bg='#235D3A' ,fg='#C0EDD0',anchor='e')
    label_claimCode.place(x=330,y=120)
    label_datetime = Label(root, text="วันที่เข้ารับบริการ",width=10,font=("bold", 10),bg='#235D3A',fg='#C0EDD0',anchor='e')
    label_datetime.place(x=330,y=150)
    #
    lbl_claimtype = Label(root, width=10, textvariable=tv_claimtype,font=("bold", 10),bg='#74927A',fg='#fff')
    lbl_claimtype.place(x=420,y=90)
    lbl_claimcode = Label(root, width=10, textvariable=tv_claimcode,font=("bold", 10),bg='#74927A',fg='#fff')
    lbl_claimcode.place(x=420,y=120)
    lbl_createdate = Label(root, width=10, textvariable=tv_createdate,font=("bold", 10),bg='#74927A',fg='#fff')
    lbl_createdate.place(x=420,y=150)

    #สถานะบัต่รประชาชน
    lbl_status = Label(root, width=30, textvariable=tv_status,font=("bold", 16),bg='#235D3A',fg='#fff')
    lbl_status.place(x=90,y=15)
    
    #ประเภทการเข้ารับบริการ claim type
    R1 = Radiobutton(root, text="OPD/ IPD/ PP", variable=radio,bg='#73C088', value='PG0060001',
                  command=selection)
    R1.place(x=20,y=260)  
    R1.select()

    R2 = Radiobutton(root, text="Home Isolation", variable=radio,bg='#73C088', value='PG0090001' ,  
                  command=selection)  
    R2.place(x=120,y=260)   
    R3 = Radiobutton(root, text="Self Isolation", variable=radio,bg='#73C088',value='PG0110001' ,  
                  command=selection)  
    R3.place(x=225,y=260)
    
    R4 = Radiobutton(root, text="HD", variable=radio,bg='#73C088',value='PG0130001' ,  
                  command=selection)  
    R4.place(x=312,y=260) 

    R4 = Radiobutton(root, text="UCEP PLUS", variable=radio,bg='#73C088', value='PG0120001' ,  
                  command=selection)  
    R4.place(x=350,y=260) 
 
    img = PhotoImage(file="image/icons8-config-32.png")
    #canvas.create_image(0,0, anchor=NW, image=img)
    
    bt_setting=Button(root, image = img,compound = LEFT,relief=GROOVE,bd=0,command=dbSettingGui)
    bt_setting.place(x=480,y=260) 
    #เชื่อมต่อ CardMonitor
    cardmonitor = CardMonitor()
    cardobserver = PrintObserver(tv_cid,tv_name,tv_birth,tv_pttype,tv_hometel,tv_claimtype,tv_claimcode,tv_createdate,tv_status)
    cardmonitor.addObserver(cardobserver)
    root.lift()
    root.attributes("-topmost", True)
    root.bind("<FocusIn>", handle_focus)
    root.mainloop()


def main():
    gui()

if __name__ == "__main__":    
    main()