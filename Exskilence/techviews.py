from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import QuestionDetails_Days, StudentDetails, StudentDetails_Days_Questions
from django.core.exceptions import ValidationError
import json
from django.views.decorators.http import require_POST
from  Exskilencebackend160924.Blob_service import *
from rest_framework.decorators import api_view 
@csrf_exempt
def create_student_details(request):
    if request.method == 'POST':
        try:
            # Parse the request body as JSON
            data = json.loads(request.body)

            # Create a new StudentDetails instance
            student = StudentDetails(
                StudentId=data.get('StudentId'),
                firstName=data.get('firstName'),
                lastName=data.get('lastName'),
                college_Id=data.get('college_Id'),
                CollegeName=data.get('CollegeName'),
                Center=data.get('Center'),
                email=data.get('email'),
                whatsApp_No=data.get('whatsApp_No'),
                mob_No=data.get('mob_No'),
                sem=data.get('sem'),
                branch=data.get('branch'),
                status=data.get('status'),
                user_category=data.get('user_category'),
                reg_date=data.get('reg_date'),
                exp_date=data.get('exp_date'),
                score=data.get('score'),
                progress_Id=data.get('progress_Id', {}),
                Assignments_test=data.get('Assignments_test', {}),
                Courses=data.get('Courses', []),
                Course_StartTime=data.get('Course_StartTime', {})
            )

            # Validate and save the student instance
            student.full_clean()
            student.save()

            return JsonResponse({"message": "Student details created successfully"}, status=201)

        except ValidationError as e:
            return JsonResponse({"error": str(e)}, status=400)
        except Exception as e:
            return JsonResponse({"error": "An error occurred: " + str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def create_student_details_days_questions(request):
    if request.method == 'POST':
        try:
            # Parse the request body as JSON
            data = json.loads(request.body)

            # Create a new StudentDetails_Days_Questions instance
            student_days_questions = StudentDetails_Days_Questions(
                Student_id=data.get('Student_id'),
                Days_completed=data.get('Days_completed', {}),
                Qns_lists=data.get('Qns_lists', {}),
                Qns_status=data.get('Qns_status', {}),
                Ans_lists=data.get('Ans_lists', {}),
                Score_lists=data.get('Score_lists', {}),
                Start_Course=data.get('Start_Course', {})
            )

            # Validate and save the student_days_questions instance
            student_days_questions.full_clean()
            student_days_questions.save()

            return JsonResponse({"message": "Student days and questions created successfully"}, status=201)

        except ValidationError as e:
            return JsonResponse({"error": str(e)}, status=400)
        except Exception as e:
            return JsonResponse({"error": "An error occurred: " + str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def frontpagedeatialsmethod(request):
    try:
        student_details = StudentDetails.objects.all().values(
            'StudentId',
            'firstName',
            'college_Id',
            'branch',
        )
        mainuser = StudentDetails_Days_Questions.objects.all().values()
        userprogress = []

        for student in mainuser:
            student_ID = student['Student_id']
            scores = {
                "id": student_ID,
                "totalScore": scorescumulation(student),
                "totalNumberOFQuesAns": totalnumberofsquesntionscompleted(student)
            }
            userprogress.append(scores)

        if not student_details:
            return JsonResponse({'message': 'No data found'}, status=404)

        result = [{'id': item['StudentId'], 'name': item['firstName'], 'College': item['college_Id'], 'Branch': item['branch']} for item in student_details]
        combinedData = combine_data(result, userprogress)
        print("\n\ncombined data", combinedData)
        return JsonResponse(combinedData, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def combine_data(result, userprogress):
    userprogress_dict = {item['id']: item for item in userprogress}
    combined = []
    for student in result:
        student_id = student['id']
        if student_id in userprogress_dict:
            combined_entry = {**student, **userprogress_dict[student_id]}
        else:
            combined_entry = student
        combined.append(combined_entry)

    return combined
def scorescumulation(student):
    score_sum = 0
    score_lists = student.get('Score_lists', {})
    for value in score_lists.values():
        try:
            if isinstance(value, str) and '/' in value:
                score_sum += int(value.split("/")[0])
            elif isinstance(value, int):
                score_sum += value
        except ValueError:
            continue
    return score_sum

def questions_ans_count(student, category):
    ans_count = 0
    qns_status = student.get('Qns_status', {}).get(category, {})

    for value in qns_status.values():
        if value >= 2:
            ans_count += 1

    return ans_count


def totalnumberofsquesntionscompleted(student):
    categories = [ "CSS", "Python", "SQL"]
    return sum(questions_ans_count(student, category) for category in categories)
@api_view(['GET'])
def getSTdDaysdetailes(req):
    try:
        mainuser = StudentDetails_Days_Questions.objects.all().values( )
        if mainuser is None:
            HttpResponse('No data found')
        return HttpResponse(json.dumps( list(mainuser) ), content_type='application/json')    
    except Exception as e:
        return HttpResponse('An error occurred'+str(e))

@csrf_exempt
@require_POST
def per_student_html_CSS_data(request):
    try:
        data = json.loads(request.body)
        student_id = data.get('student_id')
        student = StudentDetails_Days_Questions.objects.filter(pk=student_id).values()
        studenttsdata = studentdata(student_id)
        print(studenttsdata)
        studentQuesList = []
        if "HTMLCSS" in student[0]['Qns_lists']:
            studentQuesList.append(student[0]['Qns_lists']['HTMLCSS'])

        studentsHTMLStatus = []
        studentCSSStatus = []

        if "HTML" in student[0]['Qns_status'].keys():
            for i in student[0]['Qns_status']['HTML'].values():
                studentsHTMLStatus.append(i)
        if "CSS" in student[0]['Qns_status'].keys():
            for i in student[0]['Qns_status']['CSS'].values():
                studentCSSStatus.append(i)



        # print("the student details are " +str(studentQuesList))
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    if not student_id:
        return JsonResponse({'error': 'student_id is required'}, status=400)
    return JsonResponse({
        'student_id': student[0]['Student_id'],
        'Name':studenttsdata['name'],
        'college':studenttsdata['college'],
        'branch':studenttsdata['branch'],
        'studentQuesList': studentQuesList,
        "htmlStatus":studentsHTMLStatus,
        "cssStatus":studentCSSStatus
    })

@csrf_exempt
@require_POST
def per_student_JS_data(request):
    try:
        data = json.loads(request.body)
        student_id = data.get('student_id')
        student = StudentDetails_Days_Questions.objects.filter(pk=student_id).values()
        studenttsdata = studentdata(student_id)
        print(studenttsdata)
        studentQuesList = []
        if "Java_Script" in student[0]['Qns_lists']:
            studentQuesList.append(student[0]['Qns_lists']['Java_Script'])
        studentsJava_ScriptStatus = []
        if "Java_Script" in student[0]['Qns_status'].keys():
            for i in student[0]['Qns_status']['Java_Script'].values():
                studentsJava_ScriptStatus.append(i)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    if not student_id:
        return JsonResponse({'error': 'student_id is required'}, status=400)
    return JsonResponse({
        'student_id': student[0]['Student_id'],
        'Name':studenttsdata['name'],
        'college':studenttsdata['college'],
        'branch':studenttsdata['branch'],
        'studentQuesList': studentQuesList,
        "Javascript":studentsJava_ScriptStatus,
    })



@csrf_exempt
@require_POST
def per_student_ques_detials(request):
    try:
        data = json.loads(request.body)
        student_id = data.get('student_id')
        question_id = data.get('question_id')
        if not student_id or not question_id:
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        studenttsdata = studentdata(student_id)
        studenthtml_queryset = QuestionDetails_Days.objects.filter(
            Student_id=student_id,
            Qn=question_id,
            Subject="HTML"
        ).values()
        studentCSS_queryset = QuestionDetails_Days.objects.filter(
            Student_id=student_id,
            Qn=question_id,
            Subject="CSS"
        ).values()
        stduentHTMLAns = {}
        studentCSSAns = {}
        if  len(studenthtml_queryset)>0:
            stduentHTMLAns = studenthtml_queryset[0]
            HTMLdict = {
                'question':get_questions(question_id,"HTMLCSS"),
                'Attempts': stduentHTMLAns["Attempts"],
                'Score':stduentHTMLAns["Score"],
                'subject':"HTML",
                'ans':stduentHTMLAns["Ans"]
            }
            stduentHTMLAns = HTMLdict
            # print(stduentHTMLAns)
        else :
            print("no data found" + str(stduentHTMLAns))

        if len(studentCSS_queryset)>0:
            studentCSSAns = studentCSS_queryset[0]
            CSSdict = {
                'Attempts': studentCSSAns["Attempts"],
                'Score':studentCSSAns["Score"],
                'subject':"CSS",
                'ans':studentCSSAns["Ans"]
            }
            studentCSSAns = CSSdict
            # print(studentCSSAns)
        else :
            print("no data found" + str(studentCSSAns))
        return JsonResponse({
                'student_id': student_id,
                'Name':studenttsdata['name'],
                'college':studenttsdata['college'],
                'branch':studenttsdata['branch'],
                'question_id': question_id,
                'htmlans': stduentHTMLAns,
                'CSSans':studentCSSAns
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

@csrf_exempt
@require_POST
def per_student_JS_ques_detials(request):
    try:
        data = json.loads(request.body)
        student_id = data.get('student_id')
        question_id = data.get('question_id')
        if not student_id or not question_id:
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        studenttsdata = studentdata(student_id)
        studentJS_queryset = QuestionDetails_Days.objects.filter(
            Student_id=student_id,
            Qn=question_id,
            Subject="Java_Script"
        ).values()
        stduentJavaScriptAns = {}
        if  len(studentJS_queryset)>0:
            stduentJavaScriptAns = studentJS_queryset[0]
            JSdict = {
                'question':get_questions(question_id,"Java_Script"),
                'Attempts': stduentJavaScriptAns["Attempts"],
                'Score':stduentJavaScriptAns["Score"],
                'subject':"Java_Script",
                'ans':stduentJavaScriptAns["Ans"]
            }
            stduentJavaScriptAns = JSdict
            print(stduentJavaScriptAns)
        else :
            print("no data found" + str(stduentJavaScriptAns))
        return JsonResponse({
                'student_id': student_id,
                'Name':studenttsdata['name'],
                'college':studenttsdata['college'],
                'branch':studenttsdata['branch'],
                'question_id': question_id,
                'JSAns': stduentJavaScriptAns,
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)



def get_questions(questionid,course):
    CONTAINER ="internship"
    qnsdata = download_blob2('Internship_days_schema/'+course+ '/'+questionid+'.json',CONTAINER)
    qnsdata = json.loads(qnsdata)
    return qnsdata["Qn"]

def studentdata(studentid):
    try:
        stduent = StudentDetails.objects.filter(pk=studentid).values()
        stduentsendData = {
            'id': stduent[0]['StudentId'],
            'name': stduent[0]['firstName'],
            'college': stduent[0]['college_Id'],
            'branch': stduent[0]['branch'],
        }
        # print("++++++++++++++++the stduent i student \t"+str(stduentsendData))

        return stduentsendData
    except Exception as e:
        return {}

def getquestion(questionid):
    pass






































     # print("HTML student is "+str(student_ID)+"\t"+str(htmlquestionsanscount(student)))
            # print("css student is "+str(student_ID)+"\t"+str(cssquestionsanscount(student)))
            # print("python student is "+str(student_ID)+"\t"+str(pythonquestionsanscount(student)))
            # print("SQL student is "+str(student_ID)+"\t"+str(SQLquestionsanscount(student))+"\n\n")