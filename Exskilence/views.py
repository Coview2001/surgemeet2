import calendar
from decimal import Decimal
import json
import math
import random
import re
from django.http import HttpResponse
from Exskilencebackend160924.settings import *
from rest_framework.decorators import api_view
from datetime import date, datetime, time, timedelta
from Exskilence.models import *
from Exskilencebackend160924.Blob_service import download_blob2, get_blob_service_client, download_list_blob2
import pyodbc
from Exskilence.sqlrun import *
from django.core.cache import cache

CONTAINER ="internship"
# Create your views here.

@api_view(['GET'])   
def home(request):
    return HttpResponse("Welcome to the Home Page of Exskilence 07")

@api_view(['POST'])
def fetch(request):
    try:
        data = request.body
        data = json.loads(data)
        if request.method == "POST": 
            user = login_data.objects.get(User_emailID=data.get('Email'))
            return HttpResponse(json.dumps({ "StudentId" : str(user.User_ID),"user_category" : user.User_catagory  }), content_type='application/json')
        else :
            return HttpResponse('Error! Invalid Request',status=400)
    except login_data.DoesNotExist:
        return HttpResponse('Error! User does not exist', status=404)
# from django.views.decorators.cache import cache_page
    
@api_view(['POST'])
# @cache_page(60 * 15)
def getcourse(req):
    try:
        data = json.loads(req.body)
        user = StudentDetails.objects.get(StudentId=data.get('StudentId'))
        userscore = StudentDetails_Days_Questions.objects.filter(Student_id=data.get('StudentId')).first()
        if userscore is None:
            userscore = StudentDetails_Days_Questions.objects.create(
                Student_id = data.get('StudentId'),
                Start_Course = {}, # {data.get('Course'):str(datetime.utcnow().__add__(timedelta(hours=5,minutes=30)))},
                Days_completed = {}, # {data.get('Course'):0},
                Qns_lists = { },
                Qns_status = { },
                Ans_lists = { },
                Score_lists = {}) # {data.get('Course')+'Score':[]}  )
                
        Scolist = [str(l).replace("Score","") for l in list(userscore.Score_lists.keys())]
        if Scolist.__contains__("HTML") or Scolist.__contains__("CSS"):
            if Scolist.__contains__("HTML"):
                Scolist.remove("HTML")
            if Scolist.__contains__("CSS"):
                Scolist.remove("CSS")
            Scolist.append("HTMLCSS")
        if len(Scolist)  != len(user.Courses):
            for i in user.Courses:
                if i == "HTMLCSS":
                    if userscore.Score_lists.get("HTMLScore",None) is None:
                        userscore.Score_lists.update({ "HTMLScore":"0/0"})
                    if userscore.Score_lists.get("CSSScore",None) is None:
                        userscore.Score_lists.update({ "CSSScore":"0/0"})
                else:
                    if userscore.Score_lists.get(str(i)+"Score",None) is None:
                        userscore.Score_lists.update({str(i)+"Score":"0/0"})
            userscore.save()
        out = {}
        intcourse ={
            "Sub":[],
            "SubScore":[],
            "Score":[],
        }
        Enrolled_courses = []
        Total_Score = 0
        Total_Score_Outof = 0
        if user:
            def getdays(date):
                    date = datetime.strptime(str(date), "%Y-%m-%d %H:%M:%S")
                    day = int(date.strftime("%d"))
                    month = int(date.strftime("%m"))
                    if 4 <= day <= 20 or 24 <= day <= 30:
                        suffix = "TH"
                    else:
                        suffix = ["ST", "ND", "RD"][day % 10 - 1]
                    formatted_date =  (f"{day}{suffix} {calendar.month_abbr[month]}")
                    return formatted_date
            courses=CourseDetails.objects.filter().order_by('SubjectId').values()
            timestart = user.Course_StartTime
            for course in courses:
                if course.get('SubjectName') in user.Courses  :
                    starttime = timestart.get(course.get('SubjectName')).get('Start')
                    endtime = timestart.get(course.get('SubjectName')).get('End')
                    Enrolled_courses.append({
                        "SubjectId":course.get('SubjectId')  ,
                        "SubjectName":course.get('SubjectName') ,
                        "Name":course.get('Discription')  ,
                        "Duration":str(getdays(starttime))+" to "+str(getdays(endtime)) ,
                        'Progress':'10',
                        'Assignment':'0/10',
                        })
                    if course.get('SubjectName') == "HTMLCSS":
                        intcourse.get('Sub').append("HTMLCSS")
                        htmldata=userscore.Score_lists.get("HTMLScore").split('/')
                        cssdata=userscore.Score_lists.get("CSSScore").split('/')
                        intcourse.get('SubScore').append(str(int(htmldata[0])+int(cssdata[0]))+"/"+str(int(htmldata[1])+int(cssdata[1])))
                        Total_Score = int(Total_Score) + int(intcourse.get('SubScore')[-1].split('/')[0])
                        Total_Score_Outof = int(Total_Score_Outof) + int(intcourse.get('SubScore')[-1].split('/')[1])
                    else:
                        intcourse.get('Sub').append(course.get('SubjectName'))
                        intcourse.get('SubScore').append(userscore.Score_lists.get(str(course.get('SubjectName'))+'Score'))
                        Total_Score = int(Total_Score) + int(str(userscore.Score_lists.get(str(course.get('SubjectName'))+'Score')).split('/')[0])
                        Total_Score_Outof = int(Total_Score_Outof) + int(str(userscore.Score_lists.get(str(course.get('SubjectName'))+'Score')).split('/')[1])

            intcourse.get('Score').append(str(Total_Score)+"/"+str(Total_Score_Outof))
            out.update({"Courses":Enrolled_courses,
                        "Intenship":intcourse,
                        "Prograss":{
                            'Start_date': "10/09/2022",
                            'End_date': "19/10/2022",
                            "Score": "10/10"
                        },
                        "StudentName":user.firstName})
            return HttpResponse(json.dumps(out), content_type='application/json')
        else:
            return HttpResponse('Error! User does not exist', status=404)
    except Exception as e:
        return HttpResponse(f"An error occurred: {e}", status=500)




@api_view(['POST'])
def getdays(req):
    try:
        data =json.loads(req.body)
        blob_data = download_blob2('Internship_days_schema/'+data.get('Course')+'/Days.json',CONTAINER)
        json_content = json.loads(blob_data)
        user = StudentDetails_Days_Questions.objects.filter(Student_id = data.get('StudentId')).first()
        QNans = QuestionDetails_Days.objects.filter(Student_id = data.get('StudentId'),Subject = data.get('Course')).all() 
        ScoreList =[]
        if user:
            if user.Start_Course.get(data.get('Course'),0) == 0:
                for day in range(1,json_content.get('Total_Days')+1):
                    qnsdata = download_list_blob2('Internship_days_schema/'+data.get('Course')+'/Day_'+str(day)+'/','',CONTAINER)
                    user.Qns_lists.update({data.get('Course')+'_Day_'+str(day):random.sample([j.get('Qn_name') for j in qnsdata], len(qnsdata))})
                    user.Qns_status.update({data.get('Course')+'_Day_'+str(day):{i:0 for i in user.Qns_lists.get(data.get('Course')+'_Day_'+str(day))}})
                # user.Qns_status.get(data.get('Course')+'_Day_'+str(data.get('Day'))).update({j:0 for j in user.Qns_lists.get(data.get('Course')+'_Day_'+str(data.get('Day')))})
                user.Start_Course.update({data.get('Course'):str(datetime.utcnow().__add__(timedelta(hours=5,minutes=30)))})
                user.Days_completed.update({data.get('Course'):0})
                user.Score_lists.update({data.get('Course')+'Score':"0/0"})
                user.save()
            for i in range(json_content.get('Total_Days')):#range(user.Days_completed.get(data.get('Course'),0)+1):
                    dayscore =getDaysScore(data.get('Course'),user,QNans,i+1)
                    ScoreList.append({'Score':dayscore[0],'Qn_Ans':dayscore[1]})            
        else:
            user = createStdQnDays(data)
            for day in range(1,json_content.get('Total_Days')+1):
                    qnsdata = download_list_blob2('Internship_days_schema/'+data.get('Course')+'/Day_'+str(day)+'/','',CONTAINER)
                    user.Qns_lists.update({data.get('Course')+'_Day_'+str(day):random.sample([j.get('Qn_name') for j in qnsdata], len(qnsdata))})
                    user.Qns_status.update({data.get('Course')+'_Day_'+str(day):{i:0 for i in user.Qns_lists.get(data.get('Course')+'_Day_'+str(day))}})
            user.Start_Course.update({data.get('Course'):str(datetime.utcnow().__add__(timedelta(hours=5,minutes=30)))})
            user.Days_completed.update({data.get('Course'):0})
            user.Score_lists.update({data.get('Course')+'Score':"0/0"})
            user.save()
        for i in range(json_content.get('Total_Days')):#range(user.Days_completed.get(data.get('Course'),0)+1):
                    dayscore =getDaysScore(data.get('Course'),user,QNans,i+1)
                    ScoreList.append({'Score':dayscore[0],'Qn_Ans':dayscore[1]})
        daysdata = json_content.get('Days')
        date_obj = datetime.strptime(user.Start_Course.get(data.get('Course'),str(datetime.utcnow().__add__(timedelta(hours=5,minutes=30)))), "%Y-%m-%d %H:%M:%S.%f")
        for i in daysdata:
            Uqnlist =user.Qns_lists.get(data.get('Course')+'_Day_'+str(i.get('Day_no')).split('-')[1],[]) 
            Uanslist =user.Ans_lists.get(data.get('Course')+'_Day_'+str(i.get('Day_no')).split('-')[1],[])

            if int (str(i.get('Day_no')).split('-')[1]) > user.Days_completed.get(data.get('Course'),0)+1:
                Status ="Locked"
            elif int (str(i.get('Day_no')).split('-')[1]) == user.Days_completed.get(data.get('Course'),0) +1 :
                if len(Uanslist) == 0:
                    Status ="Start"
                else:
                    Status ="In Progress"
            elif len(Uqnlist) == len(Uanslist) :
                Status ="Done"
            elif len(Uqnlist) != len(Uanslist) and int (str(i.get('Day_no')).split('-')[1]) < user.Days_completed.get(data.get('Course'),0)+1:
                Status ="Attempted"
            else:
                Status ="Locked"
            i.update({'Due_date':str(date_obj.__add__(timedelta(hours=24,minutes=00)).strftime("%d-%m-%Y")).split(' ')[0],
                      'Status':Status
                      })
            date_obj = date_obj.__add__(timedelta(hours=24,minutes=00))
        json_content.update({'Days':daysdata})
        date_obj = datetime.strptime(date_obj.__add__(timedelta(hours=24,minutes=00)).strftime("%Y-%m-%d"),"%Y-%m-%d")
        current_time = datetime.utcnow() + timedelta(hours=5, minutes=30)
        json_content.update({'Days_left' : (date_obj - current_time).days if (date_obj - current_time).days > 0 else 0,
                'Day_User_on' : user.Days_completed.get(data.get('Course'),0),
                'ScoreList':ScoreList 
                })
        return HttpResponse(json.dumps(json_content), content_type='application/json')
    except Exception as e:  
        return HttpResponse(f"An error occurred: {e}", status=500)


def getDaysScore(Course,user,Qnslists,day):

    try:
        anslists = user.Ans_lists.get(Course+'_Day_'+str(day),[])
        Qnnams = user.Qns_lists.get(Course+'_Day_'+str(day),[])
        levels = [str(i)[-4] for i in Qnnams]
        
        TotalScore = levels.count('E')*5+levels.count('M')*10+levels.count('H')*15
        score = 0
        if anslists:
            for i in  Qnslists :
                if i.Qn in anslists:
                    score += i.Score
        return [str(score)+'/'+str(TotalScore),str(len(anslists))+'/'+str(len(Qnnams))]
    except Exception as e:  
        return f"An error occurred: {e}"
    
def createStdQnDays(data):
    try:
            user = StudentDetails_Days_Questions.objects.create(
                Student_id = data.get('StudentId'),
                Start_Course = {data.get('Course'):str(datetime.utcnow().__add__(timedelta(hours=5,minutes=30)))},
                Days_completed = {data.get('Course'):0},
                Qns_lists = { },
                Qns_status = { },
                Ans_lists = { },
                Score_lists = {data.get('Course')+'Score':"0/0"}  )
                
            return user
    except Exception as e:
        return f"An error occurred: {e}"
@api_view(['POST'])
def getQnslist(req):
    try:
        data =json.loads(req.body)
        course = data.get('Course')
        qnsdata = download_list_blob2('Internship_days_schema/'+course+'/Day_'+str(data.get('Day'))+'/','',CONTAINER)
        anslist = QuestionDetails_Days.objects.filter(Student_id = data.get('StudentId'),Subject = course).all()
        user = StudentDetails_Days_Questions.objects.filter(Student_id = data.get('StudentId')).first()
        if user is None:
            user = user = createStdQnDays(data)
        Qlist = user.Qns_lists.get(course+'_Day_'+str(data.get('Day')),None)
        if user.Qns_status.get(data.get('Course')+'_Day_'+str(data.get('Day'))) is None:
            user.Qns_status.update({data.get('Course')+'_Day_'+str(data.get('Day')):{}})
        if Qlist is None:
            user.Qns_lists.update({data.get('Course')+'_Day_'+str(data.get('Day')):random.sample([j.get('Qn_name') for j in qnsdata], len(qnsdata))})
            user.Qns_status.update({data.get('Course')+'_Day_'+str(data.get('Day')):{}})
            user.Qns_status.get(data.get('Course')+'_Day_'+str(data.get('Day'))).update({j:0 for j in user.Qns_lists.get(data.get('Course')+'_Day_'+str(data.get('Day')))})
            user.save()
        Qnslist = []
        def getDayScore(anslist,QName):
            u = anslist.filter(Qn = QName).first()
            if u:
                return u.Score
            return 0
        for i in qnsdata:
            level = str(i.get("Qn_name"))[-4]
            outof =''
            if level == 'E':
                level = 1
                outof = 5
            elif level == 'M':
                level = 2
                outof = 10
            elif level == 'H':
                level = 3
                outof = 15
            Qnslist.append({"Level":level,
                            "Qn_name":i.get("Qn_name"),
                            "Qn":i.get("Qn"),
                            "Status":user.Qns_status.get(data.get('Course')+'_Day_'+str(data.get('Day'))).get(i.get("Qn_name")),
                            "Score":str(getDayScore(anslist,i.get("Qn_name")))+'/'+str(outof)})
        
        if Qlist:
            arranged_list = sorted(Qnslist, key=lambda x: Qlist.index(x['Qn_name']))
            Qnslist = arranged_list
        out = {}
        dayinfo = getDaysScore(data.get('Course'),user,anslist,data.get('Day'))
        out.update({
            'Qnslist' : Qnslist,
            'Day_Score' : dayinfo[0],
            'Completed' : dayinfo[1],
        })
        return HttpResponse(json.dumps(out), content_type='application/json')
    
    except Exception as e:  
        return HttpResponse(f"An error occurred: {e}", status=500)
@api_view(['POST']) 
def getQn(req):
    try:
        data = json.loads(req.body)
        course = data.get('Course')
        mainUser = StudentDetails_Days_Questions.objects.filter(Student_id = data.get('StudentId')).first()
        if mainUser is None:
            mainUser = createStdQnDays(data)
        if mainUser.Qns_status.get(data.get('Course')+'_Day_'+str(data.get('Day'))) is None:
            mainUser.Qns_status.update({data.get('Course')+'_Day_'+str(data.get('Day')):{}})
        if mainUser.Qns_status.get(data.get('Course')+'_Day_'+str(data.get('Day'))).get(data.get('Qn_name'),0) < 1:
            mainUser.Qns_status.get(data.get('Course')+'_Day_'+str(data.get('Day'))).update({data.get('Qn_name'):1})
        if mainUser.Qns_lists.get(data.get('Course')+'_Day_'+str(data.get('Day')),None) is None:
            mainUser.Qns_lists.update({data.get('Course')+'_Day_'+str(data.get('Day')):[]})
        if mainUser.Qns_lists.get(data.get('Course')+'_Day_'+str(data.get('Day'))).count(data.get('Qn_name')) < 1:
            mainUser.Qns_lists.get(data.get('Course')+'_Day_'+str(data.get('Day'))).append(data.get('Qn_name'))
        mainUser.save()
        user = QuestionDetails_Days.objects.filter(Student_id = data.get('StudentId'),Subject = course,Qn = data.get('Qn_name')).first()
        qnsdata = download_blob2('Internship_days_schema/'+course+'/Day_'+str(data.get('Day'))+'/'+data.get('Qn_name')+'.json',CONTAINER)
        qnsdata = json.loads(qnsdata)
        qnsdata.update({"Qn_name":data.get('Qn_name'),
                        "Qn_No": int(mainUser.Qns_lists.get(data.get('Course')+'_Day_'+str(data.get('Day'))).index(data.get('Qn_name')))+1,})
        if user:
            qnsdata.update({"UserAns":user.Ans })
            qnsdata.update({"UserSubmited":"Yes" })
        else:
            qnsdata.update({"UserAns":'' })
            qnsdata.update({"UserSubmited":'No' })
        out = {}
        if data.get('Course') == 'SQL':
                tabs =  get_tables(qnsdata.get('Table'))
                out.update({"Tables":tabs,"Question":qnsdata})
        else:
                out.update({"Question":qnsdata})
        return HttpResponse(json.dumps(out), content_type='application/json')

    except Exception as e:  
        return HttpResponse(f"An error occurred: {e}", status=500)

@api_view(['POST'])
def submit(request)  :
    try:
        data = request.body
        jsondata = json.loads(data)
        result = add_daysQN_db(jsondata)
        return HttpResponse(json.dumps( result), content_type='application/json')
    except Exception as e:  
        return HttpResponse(f"An error occurred: {e}", status=500)

def Scoring_logic(passedcases,data):
    attempt = data.get("Attempt")
    if str(data.get('Qn'))[-4]=="E":
        if attempt == 1:
            score = 5
        elif attempt == 2:
            score = 3
        elif attempt == 3:
            score = 2
        else:
            score = 0
    elif str(data.get('Qn'))[-4]=="M":
        if attempt == 1 or attempt == 2:
            score = 10
        elif attempt == 3:
            score = 8
        elif attempt == 4:
            score = 6
        elif attempt == 5:
            score = 4
        elif attempt == 6:
            score = 2
        else:
            score = 0
    elif str(data.get('Qn'))[-4]=="H":
        if attempt == 1 or attempt == 2 or attempt == 3:
            score = 15
        elif attempt == 4 or attempt == 5:
            score = 12
        elif attempt == 6 :
            score = 10
        elif attempt == 7:
            score = 8
        elif attempt == 8:
            score = 6
        elif attempt == 9:
            score = 4
        elif attempt == 10:
            score = 2
        else:
            score = 0
    return math.floor(score*passedcases)

def add_daysQN_db(data):
    try:
        res = data.get("Result")
        attempt = data.get("Attempt")
        i = 0 
        passedcases = 0
        totalcases = 0
        result = {}
        if data.get("Subject") == 'HTML' or data.get("Subject") == 'CSS' or data.get("Subject") == 'Java Script':
                requirements = int(str(data.get("Score")).split('/')[0])/int(str(data.get("Score")).split('/')[1])
                score = Scoring_logic(requirements,{ "Attempt":1, "Qn":data.get("Qn") })
                result = res
                attempt = 1
        else:
            for r in res:
                i += 1
                if r.get("TestCase" + str(i)) == 'Passed' or r.get("TestCase" + str(i)) == 'Failed':
                    totalcases += 1
                    if r.get("TestCase" + str(i)) == 'Passed':
                        passedcases += 1
                    result.update(r)
                if r.get("Result") == 'True' or r.get("Result") == 'False':
                    result.update(r)
            if passedcases == totalcases and passedcases ==0:
                score = 0
            else:
                score = Scoring_logic(passedcases/totalcases,data)

        user = QuestionDetails_Days.objects.filter(Student_id=str(data.get("StudentId")),Subject=str(data.get("Subject")),Qn=str(data.get("Qn"))).first()
        mainuser = StudentDetails_Days_Questions.objects.filter(Student_id=str(data.get("StudentId"))).first()
        if mainuser is None:
            mainuser = StudentDetails_Days_Questions(
                Student_id=str(data.get("StudentId")),   
                Days_completed = {data.get("Subject"):0},
                Qns_lists = {data.get("Subject")+'_Day_'+str(int(data.get("Day_no"))):[]},
                Qns_status = {data.get("Subject")+'_Day_'+str(int(data.get("Day_no"))):{}},
                Ans_lists = {data.get("Subject")+'_Day_'+str(int(data.get("Day_no"))):[]},
                Score_lists = {data.get("Subject")+'Score':"0/0"},
            )   
            mainuser.save()
        if user is  None:

            q = QuestionDetails_Days(
                Student_id=str(data.get("StudentId")),
                Subject=str(data.get("Subject")),
                Score=score,
                Attempts=attempt,
                DateAndTime=datetime.utcnow().__add__(timedelta(hours=5,minutes=30)),
                Qn = str(data.get("Qn")),
                Ans = str(data.get("Ans")),
                Result = {"TestCases":result}
                )
            q.save()
            if mainuser.Qns_status.get(data.get('Subject')+'_Day_'+str(data.get('Day_no'))) is None:
                mainuser.Qns_status.update({data.get('Subject')+'_Day_'+str(data.get('Day_no')):{}})
            if mainuser.Ans_lists.get(data.get("Subject")+'_Day_'+str(int(data.get("Day_no")))) is None:
                mainuser.Ans_lists.update({data.get("Subject")+'_Day_'+str(int(data.get("Day_no"))):[]}) #mainuser.Ans_lists[data.get("Subject")+'_Day_'+str(int(data.get("Day_no")))]=[]
            if mainuser.Score_lists.get(data.get("Subject")+'Score') is None or mainuser.Score_lists.get(data.get("Subject")+'Score')==[]:
                mainuser.Score_lists.update({data.get("Subject")+'Score':"0/0"}) #mainuser.Score_lists[data.get("Subject")+'Score']=0
            oldscore =  mainuser.Score_lists.get(data.get("Subject")+'Score',"0/0").split('/')[0]
            totaloff =  mainuser.Score_lists.get(data.get("Subject")+'Score',"0/0").split('/')[1]
            if str(data.get("Qn"))[-4]=="E":
                outoff  = 5
            elif str(data.get("Qn"))[-4]=="M":
                outoff  = 10
            else:
                outoff  = 15
            if data.get("Qn") not in mainuser.Ans_lists.get(data.get("Subject")+'_Day_'+str(int(data.get("Day_no")))):
                mainuser.Score_lists.update({data.get("Subject")+'Score':str(int(oldscore)+int(score))+"/"+str(int(totaloff)+int(outoff))}) #if mainuser.Score_lists.get(data.get("Subject")+'Score') is None else mainuser.Score_lists[data.get("Subject")+'Score'] = (mainuser.Score_lists[key] if mainuser.Score_lists.get(key) else 0 )+ score
                mainuser.Ans_lists[data.get("Subject")+'_Day_'+str(int(data.get("Day_no")))].append(data.get("Qn"))
                if result.get("Result") == 'True':
                    mainuser.Qns_status.get(data.get("Subject")+'_Day_'+str(int(data.get("Day_no")))).update({data.get("Qn"):3}) 
                else:
                    mainuser.Qns_status.get(data.get("Subject")+'_Day_'+str(int(data.get("Day_no")))).update({data.get("Qn"):2}) 
                mainuser.save()
        
        return {'Result':"Answer has been submitted successfully"}
    except Exception as e:
        return 'An error occurred'+str(e)


@api_view(['POST'])
def nextQn(req):
    try:
        data = json.loads(req.body)
        mainuser = StudentDetails_Days_Questions.objects.filter(Student_id=str(data.get("StudentId"))).first()
        qlist = mainuser.Qns_lists[data.get("Subject")+'_Day_'+str(int(data.get("Day_no")))]
        if str(data.get('NextQn')) == 'N':
            nextQn = int(qlist.index(data.get("Qn")))+1
        else:
            nextQn = int(qlist.index(data.get("Qn")))-1
        if nextQn == len(qlist) or nextQn == -1:
            return HttpResponse(json.dumps({"Question":None }), content_type='application/json')
        qnsdata = download_blob2('Internship_days_schema/'+data.get("Subject")+'/Day_'+str(data.get('Day_no'))+'/'+qlist[nextQn]+'.json',CONTAINER)
        qnsdata = json.loads(qnsdata)
        qnsdata.update({"Qn_name":qlist[nextQn],
                        "Qn_No": nextQn+1,})
        user = QuestionDetails_Days.objects.filter(Student_id=str(data.get("StudentId")),Subject=str(data.get("Subject")),Qn=str(qlist[nextQn])).first()
        if user:
            qnsdata.update({"UserAns":user.Ans })
            qnsdata.update({"UserSubmited":"Yes" })
        else:
            qnsdata.update({"UserAns":'' })
            qnsdata.update({"UserSubmited":'No' })
        if mainuser.Qns_status.get(data.get('Subject')+'_Day_'+str(data.get('Day_no'))).get(qlist[nextQn],0) < 1:
            mainuser.Qns_status.get(data.get('Subject')+'_Day_'+str(data.get('Day_no'))).update({qlist[nextQn]:1})
            mainuser.save()
        out = {}
        if data.get('Subject') == 'SQL':
                tabs =  get_tables(qnsdata.get('Table'))
                out.update({"Tables":tabs,"Question":qnsdata})
        else:
                out.update({"Question":qnsdata})
        return HttpResponse(json.dumps(out), content_type='application/json')
    except Exception as e:
        return HttpResponse('An error occurred'+str(e), status=500)
@api_view(['POST']) 
def daycomplete(req):
    try:
        data = json.loads(req.body)
        mainuser = StudentDetails_Days_Questions.objects.filter(Student_id=str(data.get("StudentId"))).first()
        if mainuser is None:
            mainuser = StudentDetails_Days_Questions(Student_id=str(data.get("StudentId")))
            mainuser.Days_completed.update({data.get("Course"):0}) #mainuser.Days_completed[data.get("Course")] = 0
            mainuser.save()
        days_completed = mainuser.Days_completed.get(data.get("Course"),0)
        if days_completed < data.get("Day_no"):
            days_completed = data.get("Day_no")
            mainuser.Days_completed.update({data.get("Course"):days_completed}) #mainuser.Days_completed[data.get("Course")] = days_completed
            mainuser.save()
        return HttpResponse(json.dumps({"Result":"Success"}), content_type='application/json')
    except Exception as e:
        return HttpResponse(json.dumps({"Result":"Failure"}), content_type='application/json')
@api_view(['POST'])
def updatestatues(req):
    try:
        data = json.loads(req.body)
        mainuser = StudentDetails_Days_Questions.objects.filter(Student_id=str(data.get("StudentId"))).first()
        if mainuser is None:
            HttpResponse('No data found')
        # mainuser.Qns_status.update(data.get("Data"))
        # mainuser.save()
        for category, values in mainuser.Qns_status .items():

            for key, value in values.items():
               user = QuestionDetails_Days.objects.filter(Student_id=str(data.get("StudentId")),Qn=str(key)).first()
               if user:
                    if (user.Result.get('TestCases').get('Result',0))=="True":
                        mainuser.Qns_status.get(category).update({key:3})
                    else:
                        mainuser.Qns_status.get(category).update({key:2})
        # mainuser.save()
        return HttpResponse(json.dumps( mainuser.Qns_status ), content_type='application/json')
    except Exception as e:
        return HttpResponse('An error occurred'+str(e))
@api_view(['GET'])
def getSTdDaysdetailes(req):
    try:
        mainuser = StudentDetails_Days_Questions.objects.all().values( )
        if mainuser is None:
            HttpResponse('No data found')
        return HttpResponse(json.dumps( list(mainuser) ), content_type='application/json')    
    except Exception as e:
        return HttpResponse('An error occurred'+str(e))
    
def get_tables(tables):
    try:
                tabs = []
                connection_string = (f'Driver={MSSQL_DRIVER};'f'Server={MSSQL_SERVER_NAME};'f'Database={MSSQL_DATABASE_NAME};'f'UID={MSSQL_USERNAME};'f'PWD={MSSQL_PWD};')    
                conn = pyodbc.connect(connection_string)
                cursor = conn.cursor()
                tables = str(tables).split(',')
                for table in tables:
                    cursor.execute("SELECT * FROM " + table)
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    data = extract_table_rows(rows, columns)
                    
                    tabs.append({"tab_name": table, "data": data})
                return tabs
    except Exception as e:  
        return "Error getting tables: " + str(e)