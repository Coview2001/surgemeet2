from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Student

@csrf_exempt
def create_student(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(data)  # Parse JSON data from request body
            student = Student.objects.create(
                stuId=data['stuId'],
                stuname=data['stuname'],
                gender=data['gender'],
                age=data['age'],
                branch=data['branch'],
                collegeName=data['collegeName'],
                email=data['email']
            )
            return JsonResponse({'message': 'Student created successfully'}, status=201)
        except KeyError as e:
            return JsonResponse({'error': f'Missing field: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


    
def get_all_students(request):
    if request.method == 'GET':
        students = Student.objects.all()
        data = list(students.values())  # Convert queryset to list of dictionaries
        return JsonResponse(data, safe=False)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
def get_student_by_id(request, stuId):
    if request.method == 'GET':
        try:
            student = Student.objects.get(stuId=stuId)
            data = {
                'stuId': student.stuId,
                'stuname': student.stuname,
                'gender': student.gender,
                'age': student.age,
                'branch': student.branch,
                'collegeName': student.collegeName,
                'email': student.email
            }
            return JsonResponse(data, status=200)
        except Student.DoesNotExist:
            return JsonResponse({'error': 'Student not found'}, status=404)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)