from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import UserDetails, UserLogin
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from . import utils


def authenticate_or_create_user(user_email):
    try:
        user = UserDetails.objects.get(email=user_email)
        user_id = user.userID
        user_cat = user.category
        if(user.status=='inactive'):
            return {"message": "User is inactive", "userID": user_id,"exist":False}
        return {"message": "User exists", "userID": user_id,"user_cat":user_cat,"exist":True}
    except UserDetails.DoesNotExist:
        return {"message": "User does not exists","exist":False}

@method_decorator(csrf_exempt, name='dispatch')
class LoginWithGoogle(APIView):
    def options(self, request, *args, **kwargs):
        response = HttpResponse()
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

    def post(self, request):
        if 'code' in request.data:
            code = request.data['code']
            print("step1 received code\t", code)
            try:
                credentials = utils.get_id_token_with_code_method_2(code)
                print("step 2:credentials\n", credentials)
                id_token = credentials.id_token
                access_token = {
                    "access_token": credentials.access_token,
                    "refresh_token": credentials.refresh_token,
                    "token_uri": credentials.token_uri,
                    "client_id": credentials.client_id,
                    "client_secret": credentials.client_secret,
                    "scopes": list(credentials.scopes),
                    "token_expiry": credentials.token_expiry.isoformat() if credentials.token_expiry else None,
                    "id_token": credentials.id_token,
                }
                print("received access token also \n\n\n\n", access_token)
                user_email = id_token['email']
                user_name = id_token['name']
                user_pic = id_token['picture']
                user_id = authenticate_or_create_user(user_email)
                if user_id['exist']:
                    UserLogin.save_or_update(user_email, access_token)
                    response_data = {
                        "Userid": user_id['userID'],
                        "email": user_email,
                        "user_name": user_name,
                        "user_picture": user_pic,
                        "user_cat": user_id['user_cat'],
                        "exists": True
                    }
                else:
                    print("he is not found")
                    response_data = {"message": user_id['message'], "exists": False}
                
                response = Response(response_data)
                response["Access-Control-Allow-Origin"] = "*"
                return response
            except Exception as e:
                print(f"Error processing Google login: {str(e)}")
                response = Response({"message": "Error processing Google login", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                response["Access-Control-Allow-Origin"] = "*"
                return response
        response = Response({"message": "Code parameter missing"}, status=status.HTTP_400_BAD_REQUEST)
        response["Access-Control-Allow-Origin"] = "*"
        return response

@method_decorator(csrf_exempt, name='dispatch')
class ClearUserLoginData(APIView):
    def options(self, request, *args, **kwargs):
        response = HttpResponse()
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

    def post(self, request):
        if 'email' in request.data:
            user_email = request.data['email']
            result = utils.clear_user_data(user_email)
            response = Response(result)
        else:
            response = Response({"message": "Email parameter missing", "status": "error"}, status=status.HTTP_400_BAD_REQUEST)
        
        response["Access-Control-Allow-Origin"] = "*"
        return response