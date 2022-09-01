import pymysql.cursors  
import configparser
 
# Function return a connection.

def chkConnection(host,user,password,db):
    
    connection = pymysql.connect(host=host,
                             user=user,
                             password=password,                             
                             db=db,
                             charset='tis620',
                             cursorclass=pymysql.cursors.DictCursor)
    return connection

def getConnection():
    config = configparser.RawConfigParser()
    config.read('app-config.ini')
    IP = config.get('HOSxP', 'IP')
    USER = config.get('HOSxP', 'USER')
    PASSWORD = config.get('HOSxP', 'PASSWORD')
    DB = config.get('HOSxP', 'DB')
    
    
    # You can change the connection arguments.
    
    connection = pymysql.connect(host=IP,
                             user=USER,
                             password=PASSWORD,                             
                             db=DB,
                             charset='tis620',
                             cursorclass=pymysql.cursors.DictCursor)
    
    return connection
 
def testConnectDB():
        try:
            connection = getConnection()
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION()")
            results = cursor.fetchone()
            print ("CONNECTION SUCCESSFULL")     
        except:
            print ("ERROR IN CONNECTION")
            return False

 
