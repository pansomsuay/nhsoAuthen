import pymysql.cursors  
import configparser
 
# Function return a connection.



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
 
getConnection()

 
