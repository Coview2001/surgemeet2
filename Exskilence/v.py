from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.db.models import F
from datetime import datetime, timedelta
import json
import calendar
from .models import *

@api_view(['POST'])
def getcourse(req):
    try:
        data = json.loads(req.body)
        student_id = data.get('StudentId')
        user = StudentDetails.objects.get(StudentId=student_id)

        # Use get_or_create to reduce database hits
        userscore, created = StudentDetails_Days_Questions.objects.get_or_create(
            Student_id=student_id,
            defaults={
                'Start_Course': {},
                'Days_completed': {},
                'Qns_lists': {},
                'Qns_status': {},
                'Ans_lists': {},
                'Score_lists': {}
            }
        )

        # Initialize scores if not present
        for course in user.Courses:
            if course == "HTMLCSS":
                userscore.Score_lists.setdefault("HTMLScore", "0/0")
                userscore.Score_lists.setdefault("CSSScore", "0/0")
            else:
                userscore.Score_lists.setdefault(f"{course}Score", "0/0")
        
        userscore.save()  # Save if new scores were added

        out = {
            "Courses": [],
            "Intenship": {
                "Sub": [],
                "SubScore": [],
                "Score": []
            },
            "Prograss": {
                'Start_date': "10/09/2022",
                'End_date': "19/10/2022",
                "Score": "10/10"
            },
            "StudentName": user.firstName
        }

        # Retrieve enrolled courses with reduced database hits
        courses = CourseDetails.objects.filter(
            SubjectName__in=user.Courses
        ).values('SubjectId', 'SubjectName', 'Discription')

        Total_Score = 0
        Total_Score_Outof = 0

        def format_date(date):
            day = date.day
            month = date.month
            suffix = "TH" if 4 <= day <= 20 or 24 <= day <= 30 else ["ST", "ND", "RD"][day % 10 - 1]
            return f"{day}{suffix} {calendar.month_abbr[month]}"

        for course in courses:
            starttime = user.Course_StartTime.get(course['SubjectName'])
            if starttime:
                enrolled_course = {
                    "SubjectId": course['SubjectId'],
                    "SubjectName": course['SubjectName'],
                    "Name": course['Discription'],
                    "Duration": f"{format_date(starttime['Start'])} to {format_date(starttime['End'])}",
                    'Progress': '10',
                    'Assignment': '0/10'
                }
                out["Courses"].append(enrolled_course)

                if course['SubjectName'] == "HTMLCSS":
                    htmldata = map(int, userscore.Score_lists["HTMLScore"].split('/'))
                    cssdata = map(int, userscore.Score_lists["CSSScore"].split('/'))
                    combined_score = sum(htmldata) + sum(cssdata)
                    combined_out_of = 2  # 1 for each subject, can adjust if needed
                    out["Intenship"]["Sub"].append("HTMLCSS")
                    out["Intenship"]["SubScore"].append(f"{combined_score}/{combined_out_of}")
                    Total_Score += combined_score
                    Total_Score_Outof += combined_out_of
                else:
                    score = userscore.Score_lists[f"{course['SubjectName']}Score"]
                    out["Intenship"]["Sub"].append(course['SubjectName'])
                    out["Intenship"]["SubScore"].append(score)
                    score_values = map(int, score.split('/'))
                    Total_Score += sum(score_values)
                    Total_Score_Outof += 1  # Assuming out of 1 for each non-HTMLCSS subject

        out["Intenship"]["Score"].append(f"{Total_Score}/{Total_Score_Outof}")
        return JsonResponse(out)
    
    except StudentDetails.DoesNotExist:
        return JsonResponse({'error': 'User does not exist'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
