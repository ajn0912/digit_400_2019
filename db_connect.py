import pymysql

def connection():
    conn = pymysql.connect(host='localhost',
                          user='root', 
                          passwd='mandy15641',
                          db='demo')
    c = conn.cursor()
    
    return c, conn