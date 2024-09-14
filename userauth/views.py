# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from .models import UserDetails, UserLogin
# from django.contrib.auth.models import User
# from django.utils import timezone
# from . import utils


# def authenticate_or_create_user(user_email):
#     print(f"Attempting to authenticate or create user with email: {user_email}")
#     try:
#         user = UserDetails.objects.get(email=user_email)
#         user_id = user.userID
#         user_cat = user.category
#         if(user.status == 'inactive'):
#             print(f"User with email {user_email} is inactive.")
#             return {"message": "User is inactive", "userID": user_id, "exist": False}
#         print(f"User with email {user_email} exists.")
#         return {"message": "User exists", "userID": user_id, "user_cat": user_cat, "exist": True}
#     except UserDetails.DoesNotExist:
#         print(f"User with email {user_email} does not exist.")
#         return {"message": "User does not exists", "exist": False}


# class LoginWithGoogle(APIView):
#     def post(self, request):
#         print("Received POST request to /userauth/login-with-google/")
#         if 'code' in request.data.keys():
#             code = request.data['code']
#             print(f"Received code: {code}")
#             credentials = utils.get_id_token_with_code_method_2(code)
#             id_token = credentials.id_token
#             print(f"ID token: {id_token}")
#             access_token = {
#                 "access_token": credentials.access_token,
#                 "refresh_token": credentials.refresh_token,
#                 "token_uri": credentials.token_uri,
#                 "client_id": credentials.client_id,
#                 "client_secret": credentials.client_secret,
#                 "scopes": list(credentials.scopes),
#                 "token_expiry": credentials.token_expiry.isoformat() if credentials.token_expiry else None,
#                 "id_token": credentials.id_token,
#             }
#             user_email = id_token['email']
#             user_name = id_token['name']
#             user_pic = id_token['picture']
#             print(f"User details - Email: {user_email}, Name: {user_name}, Picture: {user_pic}")
#             user_id = authenticate_or_create_user(user_email)
#             if user_id['exist']:
#                 print(f"User exists. Saving or updating user login for email: {user_email}")
#                 UserLogin.save_or_update(user_email, access_token)
#                 return Response({
#                     "Userid": user_id['userID'],
#                     "email": user_email,
#                     "user_name": user_name,
#                     "user_picture": user_pic,
#                     "user_cat": user_id['user_cat'],
#                     "exists": True
#                 })
#             else:
#                 print(f"User does not exist or is inactive: {user_id['message']}")
#                 return Response({"message": user_id['message'], "exists": False})

#         print("Code parameter missing in request.")
#         return Response(status=status.HTTP_400_BAD_REQUEST)


# class ClearUserLoginData(APIView):
#     def post(self, request):
#         print("Received POST request to /userauth/clear-user-login-data/")
#         if 'email' in request.data.keys():
#             user_email = request.data['email']
#             print(f"Clearing login data for email: {user_email}")
#             try:
#                 user_login = UserLogin.objects.get(email=user_email)
#                 user_login.delete()

#                 # Delete user activity when logging out
#                 try:
#                     user = User.objects.get(email=user_email)
#                     UserActivity.objects.filter(user=user).delete()
#                 except User.DoesNotExist:
#                     print(f"User with email {user_email} does not exist. Skipping activity deletion.")

#                 return Response({"message": "User login data cleared successfully", "status": "success"})
#             except UserLogin.DoesNotExist:
#                 print(f"User login data for email {user_email} not found.")
#                 return Response({"message": "User login data not found", "status": "failure"})

#         print("Email parameter missing in request.")
#         return Response({"message": "Email parameter missing", "status": "error"}, status=status.HTTP_400_BAD_REQUEST)
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import UserDetails, UserLogin
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
# from rest_framework_simplejwt.tokens import AccessToken

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


@csrf_exempt
@api_view(['POST'])
def login_with_google(request):
    if 'code' in request.data.keys():
        code = request.data['code']
        print("step1 received code\t", code)
        
        # Uncomment and implement your utility functions and logic here
        # credentials = get_id_token_with_code_method_2(code)
        # print("step 2:credentials\n", credentials)
        return JsonResponse({"it works": "fdgdfgfdgdfg"})
        
        # id_token = credentials.id_token
        # access_token = {
        #     "access_token": credentials.access_token,
        #     "refresh_token": credentials.refresh_token,
        #     "token_uri": credentials.token_uri,
        #     "client_id": credentials.client_id,
        #     "client_secret": credentials.client_secret,
        #     "scopes": list(credentials.scopes),
        #     "token_expiry": credentials.token_expiry.isoformat() if credentials.token_expiry else None,
        #     "id_token": credentials.id_token,
        # }
        # print("received access token also \n\n\n\n", access_token)
        # user_email = id_token['email']
        # user_name = id_token['name']
        # user_pic = id_token['picture']
        # user_id = authenticate_or_create_user(user_email)
        # if user_id['exist']:
        #     UserLogin.save_or_update(user_email, access_token)
        #     return Response({
        #         "Userid": user_id['userID'],
        #         "email": user_email,
        #         "user_name": user_name,
        #         "user_picture": user_pic,
        #         "user_cat": user_id['user_cat'],
        #         "exists": True
        #     })
        # else:
        #     print("he is not found")
        #     return Response({"message": user_id['message'], "exists": False})

    return Response(status=status.HTTP_400_BAD_REQUEST)
 
class ClearUserLoginData(APIView):

    def post(self, request):
        if 'email' in request.data.keys():
            user_email = request.data['email']
            print("logout was triggered")
            try:
                user_login = UserLogin.objects.get(email=user_email)
                user_login.delete()
                return Response({"message": "User login data cleared successfully", "status": "success"})
            except UserLogin.DoesNotExist:
                return Response({"message": "User login data not found", "status": "failure"})
        
        return Response({"message": "Email parameter missing", "status": "error"}, status=status.HTTP_400_BAD_REQUEST)





