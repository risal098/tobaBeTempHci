import sqlite3
import hashlib
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
import hashlib
import base64
import random
from cryptography.fernet import Fernet
def stringhash_sha256(input_data:str): #-> string 
    input_data = input_data.encode('utf-8')
    sha256_hash = hashlib.sha256(input_data).hexdigest()
    return sha256_hash
def binaryhash_sha256(input_data): #-> BYTE 
    input_data = input_data.encode('utf-8')
    sha256_hash = hashlib.sha256(input_data)
    print(sha256_hash.hexdigest())
    return sha256_hash.digest()
def makeKey_sha256(input_data:str): #-> BYTE 
    hesh=binaryhash_sha256(input_data)
    
    return base64.urlsafe_b64encode(hesh)
def msgToByteEncryptDecrypt(msg:str):  #-> BYTE 
    return msg.encode("utf-8")
def encryptDataString(data:str,key:str): #-> BYTE 
    key=makeKey_sha256(key)
    fernet=Fernet(key)
    enc_msg=fernet.encrypt(msgToByteEncryptDecrypt(data))
    return enc_msg
def storeFirstComer(deviceId:str,username:str,password:str):
  hashData=stringhash_sha256(deviceId+username)
  conn=sqlite3.connect("DB.db")
  cur=conn.cursor()
  cur.execute("INSERT INTO account (deviceId,password,username,tokenString) VALUES (?,?,?,?)",(deviceId,password,username,hashData))
  print(deviceId+username)
  print(hashData)
  conn.commit()
  conn.close()


def decryptByPrivKey(data):#param -> string
  with open("./privKeyByte.pem", "rb") as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=None,
    )
   # print(bytes(bytelist))
    plaintext = private_key.decrypt(
      #tes,
      #bytes(data),
      base64.urlsafe_b64decode(data),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    key_file.close()
    return (plaintext.decode("utf-8"))
def doLogin(password,bearerToken):
 # try:
    conn=sqlite3.connect("DB.db")
    cur=conn.cursor()
  
    cur.execute("SELECT username,deviceId FROM account WHERE tokenString=? AND password=?",(bearerToken,password))
    retrieve=cur.fetchone()
    username=retrieve[0]
    key=retrieve[1]
    print(username)
    conn.close()
    return encryptDataString(username,key)
  #except:
 #   return b"invalid login",403


def basicFernet(msg,bearerToken):
  conn=sqlite3.connect("DB.db")
  cur=conn.cursor()
  print(bearerToken)
  cur.execute("SELECT deviceId FROM account WHERE tokenString=? ",(bearerToken,))
  retrieve=cur.fetchone()
  key=retrieve[0]
  msg=msg+" from server"+str(random.randint(0,19))
  return encryptDataString(msg,key)
  
def serverSign():
  message=b"dari server for real cuy"
  with open("./privKeyByte.pem", "rb")  as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=None,
    )
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature
