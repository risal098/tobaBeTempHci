import random
from flask import Flask,request
import sqlite3
from flask_cors import CORS
import json
import math
import re
from collections import Counter
import hashlib
import time
from datetime import datetime, timezone
import functional as fu


app=Flask(__name__)
CORS(app)
WORD = re.compile(r"\w+")
listOfDays=[
  "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    ]
weeklyStats={
  "Sunday":0,
  "Monday":0,
  "Tuesday":0,
  "Wednesday":0,
  "Thursday":0,
  "Friday":0,
  "Saturday":0,
}

#----------fungsional helper

def stringhash(input_data:str): #-> string 
  input_data = input_data.encode('utf-8')
  sha256_hash = hashlib.sha256(input_data).hexdigest()
  return sha256_hash

def getDateNow():
  utc_now = datetime.utcnow()
  return (str(utc_now))
def getDayNameNow():
  utc_now = datetime.utcnow().strftime("%A")
  return (str(utc_now))
def getUnixNow():
  unix=time.time()
  return (int(unix))
def getStartingDayUnix():
   utc_unix=int(time.time())
   utc_now = datetime.utcnow()
   utc_hour=int(utc_now.strftime('%H'))
   utc_min=int(utc_now.strftime('%M'))
   utc_sec=int(utc_now.strftime('%S'))
   decriment=60*utc_min+3600*utc_hour+utc_sec
   return utc_unix-decriment
#---------end fungsional helper

#-------------fungsional personalisasi-----
def getUserIdFromAuth(username:str,email:str):
  conn=sqlite3.connect("DB.db")
  cur=conn.cursor()
  cur.execute("SELECT userId FROM authorizationBasic WHERE username=? AND email=?",(username,email))
  userId=cur.fetchone()[0]
  conn.close()
  return userId

def isRegistered(password:str,username:str,email:str):
  conn=sqlite3.connect("DB.db")
  cur=conn.cursor()
  password=stringhash(password)
  cur.execute("SELECT username FROM authorizationBasic WHERE username=?",(username,))
  if cur.fetchone()==None:
    cur.execute("SELECT email FROM authorizationBasic WHERE email=?",(email,))
    if cur.fetchone()==None:
      cur.execute("INSERT INTO authorizationBasic(username,password,email) VALUES(?,?,?)",(username,password,email))
      
      conn.commit()
      conn.close()
      return [True,"account registered"]
    else:
      conn.close()
      return [False,"account already registered"]
  else:
    conn.close()
    return [False,"choose another username"]
def insertFirst(userId,username,email,firstComeday,isPrem,firstComeUnix,deadlineAccesUnix):
      conn=sqlite3.connect("DB.db")
      cur=conn.cursor()
      cur.execute("INSERT INTO accountData(userId,username,email,firstComeday,isPrem,firstComeUnix,deadlineAccesUnix) VALUES(?,?,?,?,?,?,?)",(userId,username,email,firstComeday,isPrem,firstComeUnix,deadlineAccesUnix))
      conn.commit()
      conn.close()
def insetAccountStat(userId):
  conn=sqlite3.connect("DB.db")
  cur=conn.cursor()
  activeDays=0
  ActiveDayStreak=0
  totalReplay=0
  points=0
  playedSong=0
  playedIelts=0
  cur.execute("INSERT INTO accountStatistic(userId,activeDays,ActiveDayStreak,totalReplay,points,playedSong,playedIelts) VALUES(?,?,?,?,?,?,?)",(userId,activeDays,ActiveDayStreak,totalReplay,points,playedSong,playedIelts))
  conn.commit()
  conn.close()
def insetTempDataStat(userId):
  global weeklyStats
  global listOfDays
  conn=sqlite3.connect("DB.db")
  cur=conn.cursor()
  tempActiveDayStreak=0
  currentDayUnix=getStartingDayUnix()
  startDay=getStartingDayUnix()
  weeklyTarget=0
  weeklyProgress=0
  weeklyStat=json.dumps(weeklyStats)
  today=getDayNameNow()
  todayIndex=listOfDays.index(today)
  lastDayUnix=currentDayUnix+(3600*24*(7-todayIndex))
  cur.execute("INSERT INTO tempDataStat(userId,tempActiveDayStreak,lastDayUnix,weeklyTarget,firstDayWeekUnix ,weeklyProgress,weeklyStat,lastDayStatUnix) VALUES(?,?,?,?,?,?,?,?)",(userId,tempActiveDayStreak,currentDayUnix,weeklyTarget,startDay,weeklyProgress,weeklyStat,lastDayUnix))
  conn.commit()
  conn.close()


#-------------------atomic functional stat--------------------
def setNewPlayedSongData(userId):
  conn=sqlite3.connect("DB.db")
  cur=conn.cursor()
  cur.execute("SELECT playedSong FROM accountStatistic WHERE userId=?",(userId,))
  playedSong=cur.fetchone()[0]+1
  cur.execute("UPDATE accountStatistic SET playedSong=? WHERE userId=?",(playedSong,userId))
  conn.commit()
  conn.close()
  
def setNewPlayedIeltsData(userId):
  conn=sqlite3.connect("DB.db")
  cur=conn.cursor()
  cur.execute("SELECT playedIelts FROM accountStatistic WHERE userId=?",(userId,))
  playedIelts=cur.fetchone()[0]+1
  cur.execute("UPDATE accountStatistic SET playedIelts=? WHERE userId=?",(playedIelts,userId))
  conn.commit()
  conn.close()
def setNewActiveDayData(userId):
  conn=sqlite3.connect("DB.db")
  cur=conn.cursor()
  cur.execute("SELECT lastDayUnix FROM tempDataStat WHERE userId=?",(userId,))
  data=cur.fetchone()
  currentDayUnix=getUnixNow()
  #getStartingDayUnix()
  #getUnixNow()
  if currentDayUnix>(data[0]+(3600*24)):
    cur.execute("SELECT activeDays FROM accountStatistic WHERE userId=?",(userId,))
    activeDays=cur.fetchone()[0]+1
    cur.execute("UPDATE accountStatistic SET activeDays=? WHERE userId=?",(activeDays,userId))
    
  conn.commit()
  conn.close()
  
def setNewActiveDayStreakData(userId):
  conn=sqlite3.connect("DB.db")
  cur=conn.cursor()
  cur.execute("SELECT tempActiveDayStreak,lastDayUnix FROM tempDataStat WHERE userId=?",(userId,))
  data=cur.fetchone()
  currentDayUnix=getUnixNow()
  #getStartingDayUnix()
  #getUnixNow()
  if currentDayUnix>(data[1]+(3600*24)) and currentDayUnix<(data[1]+(3600*48)):
    
    setNewActiveDayData(userId)
    tempActiveDayStreak=data[0]+1
    startCurrentDayUnix=getStartingDayUnix()
    cur.execute("UPDATE tempDataStat SET tempActiveDayStreak=?,lastDayUnix=? WHERE userId=?",(tempActiveDayStreak,startCurrentDayUnix,userId))
    cur.execute("SELECT activeDayStreak FROM accountStatistic WHERE userId=?",(userId,))
    if cur.fetchone()[0]<tempActiveDayStreak:
      cur.execute("UPDATE accountStatistic SET activeDayStreak=? WHERE userId=?",(tempActiveDayStreak,userId))
      
              
  elif currentDayUnix>=(data[1]+(3600*48)):
    startCurrentDayUnix=getStartingDayUnix()
    cur.execute("UPDATE tempDataStat SET tempActiveDayStreak=?,lastDayUnix=? WHERE userId=?",(0,startCurrentDayUnix,userId))
  
    
    
  conn.commit()
  conn.close()

def setNewPointsData(userId,points):
  conn=sqlite3.connect("DB.db")
  cur=conn.cursor()
  cur.execute("SELECT points FROM accountStatistic WHERE userId=?",(userId,))
  points=cur.fetchone()[0]+points
  cur.execute("UPDATE accountStatistic SET points=? WHERE userId=?",(points,userId))
  conn.commit()
  conn.close()

def setNewReplayData(userId,replays):
  conn=sqlite3.connect("DB.db")
  cur=conn.cursor()
  cur.execute("SELECT totalReplay FROM accountStatistic WHERE userId=?",(userId,))
  replays=cur.fetchone()[0]+replays
  cur.execute("UPDATE accountStatistic SET totalReplay=? WHERE userId=?",(replays,userId))
  conn.commit()
  conn.close()
 
  #
def setNewWeeklyProgressData(userId):
  
  #getStartingDayUnix()
  #getUnixNow()
  '''
  tempDataStat
  weeklyTarget
  weeklyProgress
  weeklyStat 
  lastDayUnix
  firstDayWeekUnix
  '''
  conn=sqlite3.connect("DB.db")
  cur=conn.cursor()
  currentUnixDay=getUnixNow()
  cur.execute("SELECT weeklyProgress,firstDayWeekUnix FROM tempDataStat WHERE userId=?",(userId,))
  data=cur.fetchone()
  weeklyProgress=data[0]
  firstDayWeekUnix=data[1]
  if currentUnixDay<=(firstDayWeekUnix+(3600*24*7)):
    weeklyProgress=weeklyProgress+1
    cur.execute("UPDATE tempDataStat SET weeklyProgress=? WHERE userId=?",(weeklyProgress,userId))
  else:
    weeklyProgress=0
    firstDayWeekUnix=getStartingDayUnix()
    cur.execute("UPDATE tempDataStat SET weeklyProgress=?,firstDayWeekUnix=? WHERE userId=?",(weeklyProgress,firstDayWeekUnix,userId))
    
  conn.commit()
  conn.close()
def setNewWeeklyTargetData(userId,newWeeklyTarget):
  #getStartingDayUnix()
  #getUnixNow()
  conn=sqlite3.connect("DB.db")
  cur=conn.cursor()
  cur.execute("UPDATE tempDataStat SET weeklyTarget=? WHERE userId=?",(newWeeklyTarget,userId))
  conn.commit()
  conn.close()
def setNewweeklyStatData(userId):
  global weeklyStats
  global listOfDays
  #getStartingDayUnix()
  #getUnixNow()
  #getDateNow()
  conn=sqlite3.connect("DB.db")
  cur=conn.cursor()
  currentUnixDay=getUnixNow()
  cur.execute("SELECT weeklyStat,firstDayWeekUnix FROM tempDataStat WHERE userId=?",(userId,))
  data=cur.fetchone()
  weeklyStat=json.loads(data[0])
  cur.execute("SELECT lastDayStatUnix FROM tempDataStat WHERE userId=?",(userId,))
  lastDayUnix=cur.fetchone()[0]
  if currentUnixDay<=(lastDayUnix):
    currentDay=getDayNameNow()
    newWeeklyStat=weeklyStat
    newWeeklyStat[currentDay]+=1
    cur.execute("UPDATE tempDataStat SET weeklyStat=? WHERE userId=?",(json.dumps(newWeeklyStat),userId))

  else:
    
    
    firstDayWeekUnix=getStartingDayUnix()
    today=getDayNameNow()
    todayIndex=listOfDays.index(today)
    lastDayUnix=firstDayWeekUnix+(3600*24*(7-todayIndex))
    newWeeklyStat=json.dumps(weeklyStats)
    cur.execute("UPDATE tempDataStat SET weeklyStat=?,firstDayWeekUnix=?,lastDayStatUnix=? WHERE userId=?",(newWeeklyStat,firstDayWeekUnix,userId,lastDayUnix))
    
  conn.commit()
  conn.close()

#-------------------end atomic functional stat--------------------
#------------end fungsional personalisasi---------
#-----------------fungsional umum-----
status=1
def showTop20():
  global status
  if(status!=-1):
    conn=sqlite3.connect("DB.db")
    cur=conn.cursor()
    cur.execute("SELECT * FROM [leaderboardtop20]")
    data=cur.fetchall()
    conn.close()
    return json.dumps(data),200
  return "cant",403
def whereAmI(userId):
  conn=sqlite3.connect("DB.db")
  cur=conn.cursor()
  cur.execute("SELECT userId FROM [leaderboardtop1000]")
  data=cur.fetchall()
  
  urutan=1
  for x in data:
    if x[0]==int(userId):
      cur.execute("SELECT * FROM [leaderboardtop1000] WHERE userId=?",(int(userId),))
      data=cur.fetchall()
      data=list(data[0])
    #  print("hm",data)
      conn.close()
      data.append(urutan)
      return data  
    urutan+=1
  conn.close()
  return [-1]

def get_cosine(vec1, vec2):
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x] ** 2 for x in list(vec1.keys())])
    sum2 = sum([vec2[x] ** 2 for x in list(vec2.keys())])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator


def text_to_vector(text):
    words = WORD.findall(text)
    return Counter(words)



def comparisonText(text1,text2):
  vector1 = text_to_vector(text1)
  vector2 = text_to_vector(text2)

  cosine = get_cosine(vector1, vector2)
  return cosine
def getBasicSongList():
  conn=sqlite3.connect("DB.db")
  cur=conn.cursor()
  cur.execute("SELECT * FROM songUmum")
  items=cur.fetchall()
  conn.close()
  return items
def getBasicIeltsList():
  conn=sqlite3.connect("DB.db")
  cur=conn.cursor()
  cur.execute("SELECT * FROM ieltsUmum")
  items=cur.fetchall()
  conn.close()
  return items
def get_audio(title,audioColumn,difficulty): #byte
  con = sqlite3.connect("DB.db")
  cursor = con.cursor()
  query = "SELECT %s FROM %s WHERE getTitle='%s'"%(audioColumn,difficulty,title)
  cursor.execute(query)
  data = cursor.fetchone()[0]

  con.close()

  return data
def get_lyric(title,difficulty): #byte
  con = sqlite3.connect("DB.db")
  cursor = con.cursor()
  query = "SELECT lyric1,lyric2,lyric3 FROM %s WHERE getTitle='%s'"%(difficulty,title)
  cursor.execute(query)
  data = cursor.fetchone()

  con.close()

  return data
#-----------------end fungsional umum-----
#-----------TESTING AREA--------------------------
@app.route("/",methods=["GET"])
def hello():
 
  return "hello",200
@app.route("/me",methods=["POST"])
def give():
  time.sleep(10)
  return "ok",200
#-----------END TESTING AREA--------------------------

#------------------------------
@app.before_request
def load_user():
  if request.endpoint=="login":
    pass
#-----------MANDATORY AREA---------------------------
@app.route("/updateDataBySong",methods=["POST"])
def updateDataBySong():
  #[userId,points,replays]
  data=json.loads(request.data)
  userId=data[0]
  points=data[1]
  replays=data[2]
  setNewweeklyStatData(userId)
  setNewWeeklyProgressData(userId)
  setNewReplayData(userId,replays)
  setNewPointsData(userId,points)
  setNewActiveDayData(userId)
  setNewActiveDayStreakData(userId)
  
  setNewPlayedSongData(userId)
  return "whatever",200
  '''
    setNewweeklyStatData(userId)
    setNewWeeklyProgressData(userId)
    setNewReplayData(userId,replays)
    setNewPointsData(userId,points)
    setNewActiveDayStreakData(userId)
    setNewActiveDayData(userId)
    setNewPlayedSongData(userId)
  ###################
    setNewPlayedIeltsData(userId)
    setNewPlayedSongData(userId)
    '''
  return "wait"
@app.route("/updateDataByIelts",methods=["POST"])
def updateDataByIelts():
  #[userId,points,replays]
  data=json.loads(request.data)
  userId=data[0]
  points=data[1]
  replays=data[2]
  setNewweeklyStatData(userId)
  setNewWeeklyProgressData(userId)
  setNewReplayData(userId,replays)
  setNewPointsData(userId,points)
  setNewActiveDayData(userId)
  setNewActiveDayStreakData(userId)
  
  setNewPlayedIeltsData(userId)
  return "whatever",200
  '''
    setNewweeklyStatData(userId)
    setNewWeeklyProgressData(userId)
    setNewReplayData(userId,replays)
    setNewPointsData(userId,points)
    setNewActiveDayStreakData(userId)
    setNewActiveDayData(userId)
  ###################
    setNewPlayedIeltsData(userId)
    setNewPlayedSongData(userId)
    '''
 # return "wait"
@app.route("/giveTop20",methods=["GET"])
def giveTop20():
  return showTop20()
@app.route("/giveWhereAmI",methods=["POST"])
def giveTopMe():
  userId=request.data
 # print(userId)
 # print("res",json.dumps(whereAmI(userId)))
  return json.dumps(whereAmI(userId))
@app.route("/login",methods=["POST"])
def login():
  #[username,password]
  conn=sqlite3.connect("DB.db")
  cur=conn.cursor()
  data=json.loads(request.data)
  username=data[0]
  password=data[1]
  password=stringhash(password)
  cur.execute("SELECT * FROM authorizationBasic WHERE username=? AND password=?",(username,password))
  result=cur.fetchone()
  conn.close()
  if result==None:
    return "invalid login",403
  return json.dumps([result[0],result[3]]),200
  
  
  return "wait"
@app.route("/register",methods=["POST"])
def register():
  #[email.username,password]
  data=json.loads(request.data)
  password=data[2]
  username=data[1]
  email=data[0]
  
  regis=isRegistered(password,username,email)
  if(regis[0]==True):
    userId=getUserIdFromAuth(username,email)
    firstComeDay=getDateNow()
    firstComeUnix=getUnixNow()
    firstMidnight=getStartingDayUnix()
    deadlineAcces=firstMidnight+864000
    isPrem=0
    insertFirst(userId,username,email,
                firstComeDay,isPrem,firstComeUnix,deadlineAcces)

    insetAccountStat(userId)
    insetTempDataStat(userId)
    return json.dumps(regis),200
    
    
    
  
  
  #false register
  return json.dumps(regis),403
@app.route("/getBasicSongList",methods=["GET"])
def getBasicSong():
  data=getBasicSongList()
  return json.dumps(data),200
@app.route("/getBasicIeltsList",methods=["GET"])
def getBasicIelts():
  data=getBasicIeltsList()
  return json.dumps(data),200
@app.route("/getAudio/<title>&<audioColumn>&<difficulty>",methods=["GET"])
def getAudio(title,audioColumn,difficulty):
  return get_audio(title,audioColumn,difficulty)
@app.route("/getLyric/<title>&<difficulty>",methods=["GET"])
def getLyric(title,difficulty):
  return json.dumps(get_lyric(title,difficulty))
@app.route("/getComparisonAnswerPoint",methods=["POST"])
def getPointsAnswer():
  #request = [[lyric1,lyric2,lyric3]
    #        [userly1,userly2,userly3]]
  data=json.loads(request.data)
  result=[]
  lyric1=data[0][0].replace(",","").replace(".","").replace("?","").replace("!","").replace("'","").replace("\n","").lower()
  lyric2=data[0][1].replace(",","").replace(".","").replace("?","").replace("!","").replace("'","").replace("\n","").lower()
  lyric3=data[0][2].replace(",","").replace(".","").replace("?","").replace("!","").replace("'","").replace("\n","").lower()
  userly1=data[1][0].replace(",","").replace(".","").replace("?","").replace("!","").replace("'","").replace("\n","").lower()
  userly2=data[1][1].replace(",","").replace(".","").replace("?","").replace("!","").replace("'","").replace("\n","").lower()
  userly3=data[1][2].replace(",","").replace(".","").replace("?","").replace("!","").replace("'","").replace("\n","").lower()
  result.append(comparisonText(lyric1,userly1))
  result.append(comparisonText(lyric2,userly2))
  result.append(comparisonText(lyric3,userly3))
  return json.dumps(result) #[point1,point2,point3]
app.run(host='0.0.0.0',port=8080,debug=True)

