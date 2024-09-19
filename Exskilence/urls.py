from django.urls import path
from .techviews import *
from .sqlpythonview import *
urlpatterns = [
    path('student-details/', create_student_details, name='student-details-create'),
    path('student-details-days-questions/', create_student_details_days_questions, name='student-details-days-questions-create'),
    path('testest/',frontpagedeatialsmethod,name='testest'),
    path('jjjjj/',getSTdDaysdetailes,name='jjjjj'),
    path('per-student-data/',per_student_html_CSS_data,name='per-student-data'),
    path('per-student-JavaScript-data/',per_student_JS_data,name='per-student-JS-data'),
    path('per_ques_stu/',per_student_ques_detials,name='per_ques_stu'),    
    path('per_ques_JavaScript_stu/',per_student_JS_ques_detials,name='per_ques_stu'),    
    path('students/', student_list, name='student-list'),
    path('filter-options/', filter_options, name='filter-options'),
    path('student-details-day/<str:student_id>/<str:course>/', student_details_day, name='student-details-day'),
    path('report/<str:student_id>/<str:course>/<str:day>/', getreport, name='getreport'),
]
