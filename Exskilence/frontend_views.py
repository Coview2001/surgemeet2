


import json
import math
import random
from datetime import date, datetime, time, timedelta
from django.http import HttpResponse
from Exskilence.models import *
from rest_framework.decorators import api_view
from Exskilencebackend160924.Blob_service import download_blob2,download_list_blob2
from .views import Scoring_logic, createStdQnDays
CONTAINER ="internship"


@api_view(['POST'])
def frontend_Questions_page(req):
    try:
        data = json.loads(req.body)
        Subject = data.get("Subject")
        qnsdata = download_list_blob2('Internship_days_schema/'+Subject+'/','',CONTAINER)
        user = StudentDetails_Days_Questions.objects.filter(Student_id=str(data.get("StudentId"))).first()
        if user is None:
            data.update({"Course":Subject})
            user = createStdQnDays(data)
        if user.Qns_lists.get(Subject,None) is None:
            Easy = [j.get('Qn_name') for j in qnsdata if str(j.get('Qn_name'))[-4] == 'E']
            Medium = [j.get('Qn_name') for j in qnsdata if str(j.get('Qn_name'))[-4] == 'M']
            Hard = [j.get('Qn_name') for j in qnsdata if str(j.get('Qn_name'))[-4] == 'H']
            Easy = random.sample(Easy, len(Easy))
            Medium = random.sample(Medium, len(Medium))
            Hard = random.sample(Hard, len(Hard))
            qlist =[]
            [qlist.append(i) for i in Easy]
            [qlist.append(i) for i in Medium]   
            [qlist.append(i) for i in Hard]

            user.Qns_lists.update({Subject:qlist})
            if Subject == "HTMLCSS":
                user.Qns_status.update({"HTML":{i:0 for i in qlist}})
                user.Qns_status.update({"CSS":{i:0 for i in qlist}})
            else:
                user.Qns_status.update({Subject:{i:0 for i in qlist}})
            user.Days_completed.update({Subject:0})
            user.Start_Course.update({Subject:str(datetime.utcnow().__add__(timedelta(hours=5,minutes=30)))})
            user.save()
        else:
            qlist = user.Qns_lists.get(Subject)
        arranged_list = sorted(qnsdata, key=lambda x: qlist.index(x['Qn_name']))
        Qnslist = arranged_list
        anslist = QuestionDetails_Days.objects.filter(Student_id = data.get('StudentId')).all()
        out = []
        def getDayScore(anslist,QName):
            u = anslist.filter(Qn = QName).first()
            if u:
                return u.Score
            return 0
        for i in Qnslist:
            if i.get('Qn_name')[-4] == 'E':
                outoff = 5
                level1 = 1
            elif i.get('Qn_name')[-4] == 'M':
                outoff = 10
                level1 = 2
            elif i.get('Qn_name')[-4] == 'H':
                outoff = 15
                level1 = 3
            if Subject == "HTMLCSS":
                HTMLstatus =user.Qns_status.get("HTML").get(i.get('Qn_name'),0)
                CSSstatus =user.Qns_status.get("CSS").get(i.get('Qn_name'),0)
                if HTMLstatus == 0 and CSSstatus == 0:
                    HTCSstatus = 0
                elif HTMLstatus == 1 or CSSstatus == 1:
                    HTCSstatus = 1
                elif HTMLstatus == 2 or CSSstatus == 2:
                    HTCSstatus = 2
                elif HTMLstatus == 3 and CSSstatus == 3:
                    HTCSstatus = 3
                htmlscore = getDayScore(anslist.filter( Subject = "HTML"),i.get("Qn_name"))
                cssscore = getDayScore(anslist.filter( Subject = "CSS"),i.get("Qn_name"))
                htcscore = math.floor((htmlscore+cssscore)/2)
                out.append({
                "Level":level1,
                "Qn_name":i.get('Qn_name'),
                "Qn":i.get('Qn'),
                "Status":HTCSstatus,
                "Score":str( htcscore)+'/'+str(outoff),
                })
            else:
                out.append({
                "Level":level1,
                "Qn_name":i.get('Qn_name'),
                "Qn":i.get('Qn'),
                "Status":user.Qns_status.get(Subject).get(i.get('Qn_name'),0),
                "Score":str(getDayScore(anslist.filter( Subject = Subject),i.get("Qn_name")))+'/'+str(outoff),
                })
        dayinfo = getDaysScore(Subject,user,anslist )
        output = {
            'Qnslist' : out,
            'Day_Score' : dayinfo[0],
            'Completed' : dayinfo[1],
        }
        return HttpResponse(json.dumps(output), content_type='application/json')
    except Exception as e:
        return HttpResponse(f"An error occurred: {e}", status=500)
        
                
def getDaysScore(Course,user,Qnslists):
    try:
        anslists = user.Ans_lists.get(Course ,[])
        Qnnams = user.Qns_lists.get(Course ,[])
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


def add_daysQN_db(data):
    try:
        res = data.get("Result")
        if data.get("Subject") == 'HTML' or data.get("Subject") == 'CSS' or data.get("Subject") == 'Java Script' or data.get("Subject") == 'Java_Script':
                requirements = int(str(data.get("Score")).split('/')[0])/int(str(data.get("Score")).split('/')[1])
                score = Scoring_logic(requirements,{ "Attempt":1, "Qn":data.get("Qn") })
                result = res
                attempt = 1
        user = QuestionDetails_Days.objects.filter(Student_id=str(data.get("StudentId")),Subject=str(data.get("Subject")),Qn=str(data.get("Qn"))).first()
        mainuser = StudentDetails_Days_Questions.objects.filter(Student_id=str(data.get("StudentId"))).first()
        if mainuser is None:
            mainuser = StudentDetails_Days_Questions(
                Student_id=str(data.get("StudentId")),   
                Days_completed = {data.get("Subject"):0},
                Qns_lists = {data.get("Subject"):[]},
                Qns_status = {data.get("Subject"):{}},
                Ans_lists = {data.get("Subject"):[]},
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
                Result = {"TestCases":{'Testcase':result,
                          "Result":str(str(result).split('/')[0] == str(result).split('/')[1])}}
                )
            q.save()
            if str(data.get("Qn") )[-4] == 'E':
                outoff = 5
            elif str(data.get("Qn") )[-4] == 'M':
                outoff = 10
            elif str(data.get("Qn") )[-4] == 'H':
                outoff = 15
            if mainuser.Qns_status.get(data.get('Subject') ) is None:
                mainuser.Qns_status.update({data.get('Subject') :{}})
            if mainuser.Ans_lists.get(data.get("Subject")) is None:
                mainuser.Ans_lists.update({data.get("Subject"):[]}) #mainuser.Ans_lists[data.get("Subject")]=[]
            if mainuser.Score_lists.get(data.get("Subject")+'Score') is None or mainuser.Score_lists.get(data.get("Subject")+'Score')==[]:
                mainuser.Score_lists.update({data.get("Subject")+'Score':"0/0"}) #mainuser.Score_lists[data.get("Subject")+'Score']=0
            oldscore =  mainuser.Score_lists.get(data.get("Subject")+'Score',"0/0").split('/')[0]
            totaloff = mainuser.Score_lists.get(data.get("Subject")+'Score',"0/0").split('/')[1]
            if data.get("Qn") not in mainuser.Ans_lists.get(data.get("Subject")):
                mainuser.Score_lists.update({data.get("Subject")+'Score':str(int(oldscore)+int(score))+'/'+str(int(totaloff)+int(outoff))})
                mainuser.Ans_lists[data.get("Subject")].append(data.get("Qn"))
                if str(result).split('/')[0] == str(result).split('/')[1]:
                    mainuser.Qns_status.get(data.get("Subject")).update({data.get("Qn"):3}) 
                else:
                    mainuser.Qns_status.get(data.get("Subject")).update({data.get("Qn"):2})
                mainuser.save() 
                   
        return {'Result':"Answer has been submitted successfully"}
    except Exception as e:
        return 'An error occurred'+str(e)

@api_view(['POST']) 
def frontend_getQn(req):
    try:
        data = json.loads(req.body)
        course = data.get('Course')
        mainUser = StudentDetails_Days_Questions.objects.filter(Student_id = data.get('StudentId')).first()
        if mainUser is None:
            mainUser = createStdQnDays(data)
        if course == 'HTMLCSS':
            if mainUser.Qns_status.get("HTML") is None:
                mainUser.Qns_status.update({"HTML":{}})
            if mainUser.Qns_status.get("CSS") is None:
                mainUser.Qns_status.update({"CSS":{}})
            if mainUser.Qns_status.get("HTML").get(data.get('Qn_name'),0) < 1:
                mainUser.Qns_status.get("HTML").update({data.get('Qn_name'):1})
            if mainUser.Qns_status.get("CSS").get(data.get('Qn_name'),0) < 1:
                mainUser.Qns_status.get("CSS").update({data.get('Qn_name'):1})
        else:
            if mainUser.Qns_status.get(data.get('Course')) is None:
                mainUser.Qns_status.update({data.get('Course'):{}})
            if mainUser.Qns_status.get(data.get('Course')).get(data.get('Qn_name'),0) < 1:
                mainUser.Qns_status.get(data.get('Course')).update({data.get('Qn_name'):1})
        if mainUser.Qns_lists.get(data.get('Course') ,None) is None:
            mainUser.Qns_lists.update({data.get('Course') :[]})
        if mainUser.Qns_lists.get(data.get('Course') ).count(data.get('Qn_name')) < 1:
            mainUser.Qns_lists.get(data.get('Course') ).append(data.get('Qn_name'))

        mainUser.save()
        user = QuestionDetails_Days.objects.filter(Student_id = data.get('StudentId'),Subject = course,Qn = data.get('Qn_name')).first()
        qnsdata = download_blob2('Internship_days_schema/'+course+ '/'+data.get('Qn_name')+'.json',CONTAINER)
        qnsdata = json.loads(qnsdata)
        qnsdata.update({"Qn_name":data.get('Qn_name'),
                        "Qn_No": int(mainUser.Qns_lists.get(data.get('Course')).index(data.get('Qn_name')))+1,})
        if course == 'HTMLCSS':
            user = QuestionDetails_Days.objects.filter(Student_id = data.get('StudentId'), Qn = data.get('Qn_name')) 
            htmluser = user.filter(Subject = 'HTML').first()
            if htmluser :
                qnsdata.update({"UserAnsHTML":htmluser.Ans })
                qnsdata.update({"UserSubmitedHTML":"Yes" })
            else:
                qnsdata.update({"UserAnsHTML":'' })
                qnsdata.update({"UserSubmitedHTML":'No' })
            cssuser = user.filter(Subject = 'CSS').first()
            if cssuser:
                qnsdata.update({"UserAnsCSS":cssuser.Ans })
                qnsdata.update({"UserSubmitedCSS":"Yes" })
            else:
                qnsdata.update({"UserAnsCSS":'' })
                qnsdata.update({"UserSubmitedCSS":'No' })
        else:
            if user:
                qnsdata.update({"UserAns":user.Ans })
                qnsdata.update({"UserSubmited":"Yes" })
            else:
                qnsdata.update({"UserAns":'' })
                qnsdata.update({"UserSubmited":'No' })
        out = {}       
        out.update({"Question":qnsdata})
        return HttpResponse(json.dumps(out), content_type='application/json')

    except Exception as e:  
        return HttpResponse(f"An error occurred: {e}", status=500)
    
@api_view(['POST'])
def frontend_nextQn(req):
    try:
        data = json.loads(req.body)
        mainuser = StudentDetails_Days_Questions.objects.filter(Student_id=str(data.get("StudentId"))).first()
        qlist = mainuser.Qns_lists.get(data.get("Subject") ,None)
        if data.get("NextQn") == 'N':
            nextQn = int(qlist.index(data.get("Qn")))+1
        else:
            nextQn = int(qlist.index(data.get("Qn"))-1)
        if nextQn == len(qlist) or nextQn == -1:
            return HttpResponse(json.dumps({"Question":None }), content_type='application/json')
        qnsdata = download_blob2('Internship_days_schema/'+data.get("Subject")+ '/'+qlist[nextQn]+'.json',CONTAINER)
        qnsdata = json.loads(qnsdata)
        qnsdata.update({"Qn_name":qlist[nextQn],
                        "Qn_No": nextQn+1,})
        user = QuestionDetails_Days.objects.filter(Student_id = data.get('StudentId'),Subject = data.get("Subject"),Qn = qlist[nextQn]).first()
        course = data.get('Subject')
        if course == 'HTMLCSS':
            user = QuestionDetails_Days.objects.filter(Student_id = data.get('StudentId'), Qn =  qlist[nextQn]) 
            htmluser = user.filter(Subject = 'HTML').first()
            if htmluser :
                qnsdata.update({"UserAnsHTML":htmluser.Ans })
                qnsdata.update({"UserSubmitedHTML":"Yes" })
            else:
                qnsdata.update({"UserAnsHTML":'' })
                qnsdata.update({"UserSubmitedHTML":'No' })
                
            cssuser = user.filter(Subject = 'CSS').first()
            if cssuser:
                qnsdata.update({"UserAnsCSS":cssuser.Ans })
                qnsdata.update({"UserSubmitedCSS":"Yes" })
            else:
                qnsdata.update({"UserAnsCSS":'' })
                qnsdata.update({"UserSubmitedCSS":'No' })
            if mainuser.Qns_status.get("HTML").get(qlist[nextQn],0) < 1:
                mainuser.Qns_status.get("HTML").update({qlist[nextQn]:1})
            if mainuser.Qns_status.get("CSS").get(qlist[nextQn],0) < 1:
                mainuser.Qns_status.get("CSS").update({qlist[nextQn]:1})
        else:
            if user:
                qnsdata.update({"UserAns":user.Ans })
                qnsdata.update({"UserSubmited":"Yes" })
            else:
                qnsdata.update({"UserAns":'' })
                qnsdata.update({"UserSubmited":'No' })
            if mainuser.Qns_status.get(data.get('Subject') ).get(qlist[nextQn],0) < 1:
                mainuser.Qns_status.get(data.get('Subject') ).update({qlist[nextQn]:1})
                mainuser.save()
        out = {}
        out.update({"Question":qnsdata})
        return HttpResponse(json.dumps(out), content_type='application/json')
    except Exception as e:
       return HttpResponse('An error occurred'+str(e), status=500)
    


