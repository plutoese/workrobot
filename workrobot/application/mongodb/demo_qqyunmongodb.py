# coding = UTF-8

from libs.imexport.class_mongodb import MongoDB, MonDatabase
from pymongo import MongoClient
from sshtunnel import SSHTunnelForwarder

'''
server = SSHTunnelForwarder(
    ('123.207.185.126',22),
    ssh_username="ubuntu",
    ssh_password="z1Yh2900",
    remote_bind_address=('10.66.131.25', 27017)
)

server.start()

print(server.local_bind_port)  # show assigned local port
# work with `SECRET SERVICE` through `server.local_bind_port`.
conn_str = 'mongodb://mongouser:z1Yh2900@127.0.0.1:{}/admin'.format(server.local_bind_port)
print(conn_str)

mongo = MongoDB(conn_str=conn_str)
#print(mongo.database_names)

server.stop()'''

mongo = MongoDB(conn_str='mongodb://mongouser:z1Yh2900@123.207.185.126:27017/')
print(mongo.database_names)