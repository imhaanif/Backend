import urllib.parse
import json
from time import time
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
import os
from django.utils import timezone

from accounts.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime
from django.conf import settings
from django.contrib import messages
from accounts.serializers import UserSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from accounts.models import User
from random import randint
import requests

from accounts.emailsend import email_send, email_send_mfa
from rest_framework_simplejwt.tokens import RefreshToken

# http://
import environ
import os

env = environ.Env()


def google_login(request):
    redirect_uri = "%s://%s%s" % (
        request.scheme, request.get_host(), reverse('google_login')
    )
    print(redirect_uri)
    if ('code' in request.GET):
        params = {
            'grant_type': 'authorization_code',
            'code': request.GET.get('code'),
            'redirect_uri': redirect_uri,
            'client_id': env('CLIENT_ID'),
            'client_secret':  env('SECRET')
        }
        url = 'https://accounts.google.com/o/oauth2/token'
        response = requests.post(url, data=params)
        url = 'https://www.googleapis.com/oauth2/v1/userinfo'
        access_token = response.json().get('access_token')
        response = requests.get(url, params={'access_token': access_token})
        user_data = response.json()
        email = user_data.get('email')
        if email:
            print(user_data, 'userdata')
            try:
                obj = User.objects.get(email=email)
            except User.DoesNotExist:
                # create user
                obj = User.objects.create(email=email,
                                          fname=user_data.get('given_name'),
                                          lname=user_data.get('family_name'),
                                          is_active=True,
                                          is_google_user=True,
                                          google_profile_img=user_data.get(
                                              'picture'),
                                          google_id=user_data.get('id'),
                                          )
            if obj:
                refresh = RefreshToken.for_user(obj)
                print(refresh, "tokens")

                data = {
                    'access': str(refresh.access_token),
                }

                data = urllib.parse.urlencode(data)
                if env('DEPLOYED'):
                    return redirect('https://www.bawsala.me/auth/login?'+data)

                
                else:
                    return redirect('http://localhost:3000/auth/login?'+data)



            # user.backend = settings.AUTHENTICATION_BACKENDS[0]
            # login(request, user)
        else:
            messages.error(
                request,
                'Unable to login with Gmail Please try again'
            )
        return redirect('/')
    else:
        url = "https://accounts.google.com/o/oauth2/auth?client_id=%s&response_type=code&scope=%s&redirect_uri=%s&state=google"
        scope = [
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email",


        ]
        scope = " ".join(scope)
        url = url % (env('CLIENT_ID'), scope, redirect_uri)
        return redirect(url)


@api_view(["POST"])
def login_view(request):
    data = json.loads(request.body)
    print(data)
    email = data['email']
    passwd = data['password']
    obj = authenticate(email=email, password=passwd)
    print(obj, 'user obj')
    if obj is not None:
        if obj.is_active:
            refresh = RefreshToken.for_user(obj)
            print(refresh, "tokens")
            return Response({'refresh': str(refresh),
                             'access': str(refresh.access_token), 'user': {"id": obj.id, "fname": obj.fname, "lname": obj.lname, "is_google":obj.is_google_user, "is_superuser": obj.is_superuser, 'phone': obj.phone if obj.phone else None,  "email": obj.email,  "profile_url": obj.thumbnail.url if obj.image else None, }}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'inactive'}, status=status.HTTP_403_FORBIDDEN)
    else:
        return Response({'status': 'authentication error'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(["POST"])
@permission_classes((IsAuthenticated, ))
def get_user(request):

    obj = request.user

    if obj is not None:
        if obj.is_active:
            refresh = RefreshToken.for_user(obj)
            print(refresh, "tokens")
            return Response({'refresh': str(refresh),
                             'access': str(refresh.access_token), 'user': {"id": obj.id, "fname": obj.fname, "is_google":obj.is_google_user, "lname": obj.lname, "is_superuser": obj.is_superuser, 'phone': obj.phone if obj.phone else None,  "email": obj.email,  "profile_url": obj.thumbnail.url if obj.image else None, }}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'inactive'}, status=status.HTTP_403_FORBIDDEN)
    else:
        return Response({'status': 'authentication error'}, status=status.HTTP_401_UNAUTHORIZED)


# def forgot_pass_view(request):


#     return render(request, "register/forgot.html", {})
# def resend_email(request, slug):
#     now = timezone.now()

#     user = User.objects.get(slug=slug)
#     # slug = utils.unique_key_generator(user)
#     # user.slug = slug
#     # user.save()
#     user.email_ac_timestamp = now
#     user.save()
#     link = f"https://app.bulkmailverifier.com/accounts/email/activate/{user.slug}"
#     email = user.email
#     username = user.username
#     try:
#         email_send(useremail=email, username=username, activation_link=link)
#     except Exception as e:
#         print(e)
#         messages.error(request, 'Something Went wrong.')
#         return redirect("/accounts/login/")

#     messages.info(request, 'Email is sent check your email adresss')
#     return redirect("/accounts/login/")


# def email_verify(request, slug):
#     try:
#         user = User.objects.get(slug=slug)

#     except:
#         pass
#     if user:
#         if user.is_active:
#             login(request, user)
#             return redirect("/")
#             # return("User is already active")
#         else:
#             now = timezone.now()

#             pt = user.email_ac_timestamp
#             print(now)
#             print(pt)
#             td = now - pt
#             if td > datetime.timedelta(days=1):
#                 return HttpResponse("Email time has passed <button>Resend Email</button>")
#             user.is_active = True
#             user.save()
#             return redirect("/accounts/")

# @login_required(login_url="/accounts/")
# def verify_phone(request):
#     if request.user.is_phone:
#         return redirect("/")
#     if request.method == "POST":
#         form = Phone_Form(request.POST)
#         print(form)
#         if form.is_valid():
#             code = form.cleaned_data.get("code")
#             code = code.split(" ")
#             code = code[1]
#             number = form.cleaned_data.get("number")
#             print(number)
#             print(code)
#             try:
#                 p = Phone.objects.create(code=code, number=number)
#                 request.user.phone = p
#                 request.user.save()
#             except IntegrityError:

#                 return HttpResponse(f"This phone is already in use")
#             except Exception as e:
#                 return HttpResponse(f"{e}")


#             number = str(code) + str(number)
#             print("Sending sms", number)
#             if send_sms(number):
#                 return redirect("/accounts/phone-code-verify/")
#             print("trying again")
#             if send_sms(number):
#                 return redirect("/accounts/phone-code-verify/")
#             return HttpResponse("Error sending Message Try Again")


#     #GET REQUEST
#     x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
#     if x_forwarded_for:
#        ip = x_forwarded_for.split(',')[0]
#     else:
#        ip = request.META.get('REMOTE_ADDR')
#     access_token = 'be55b883237a3f'
#     try:
#         handler = ipinfo.getHandler(access_token)
#         details = handler.getDetails(ip)
#         print(details.country)
#         c = str(details.country)
#     except:
#         return HttpResponse("I-Info Error")
#     try:
#         url2 = f'https://restcountries.eu/rest/v2/alpha/{c}'
#         r = requests.get(url2)
#     except:
#         return HttpResponse("Error Getting Country Code ")
#     data2 = r.json()
#     pc = data2['callingCodes']
#     code=c + " " + "+"+pc[0]
#     form = Phone_Form({'code':code})
#     form.code = code

#     return render(request, 'phoneverify.html', {'form' : form})

# @login_required
# def phonecodeverify(request):
#     if request.user.is_phone:
#         return redirect("/")
#     if request.method == "POST":
#         code = request.POST['code']
#         print('code', code)
#         if check_sms(code=code, phone=request.user.phone):
#             request.user.is_phone = True
#             request.user.save()
#             return redirect("/")
#         else:
#             return redirect(to="phoneverify")


#     return render(request, 'phoneverifycode.html', {})

# @login_required
# def change_pass(request):
#     form = Change_Password_Form()
#     if request.method == "POST":
#         form = Change_Password_Form(request.POST)
#         print(form)
#         if form.is_valid():
#             pass1 = form.cleaned_data.get("password1")
#             pass2 = form.cleaned_data.get("password2")
#             if pass1 != pass2:
#                 return render(request, 'changepassword.html', {'form' : form, 'is_error': True })
#             request.user.set_password(pass1)
#             request.user.save()
#             return redirect("/")

#     return render(request, 'changepassword.html', {'form' : form})


# def forgot_pass(request):
#     if request.method == "POST":

#         if "rrrr" in request.session:
#             retries = request.session["rrrr"]
#             print(retries)
#             request.session["rrrr"] = str(int(retries) + 1)
#             if int(request.session["rrrr"]) > 3:
#                 return HttpResponse("Retry Limit Reached. Retry Later")
#         else:
#             request.session["rrrr"] = "1"
#         email = request.POST['email']
#         try:
#             user = User.objects.get(email=email)
#         except:
#             user = None
#         if user != None :
#             del request.session["rrrr"]
#             slg = urlsafe_base64_encode(force_bytes(user.slug))
#             tkn = default_token_generator.make_token(user)
#             link = f"{settings.ROOT_URL}accounts/forgotpass/chngpass/{slg}/{tkn}"
#             user.email_ac_timestamp = timezone.now()
#             user.save()
#             email_forgot_send(useremail=user.email, username=user.username, activation_link=link)
#             return render(request, 'forgotpass.html', {'email_Sent':True})
#         return render(request, 'forgot.html', {'email_Sent':False, 'user_not':True})

#     return render(request, 'forgot.html', {'normal': True})

# def forgot_change_pass(request, slug, token):
#     try:

#         slg = force_text(urlsafe_base64_decode(slug))
#         user = User.objects.get(slug=slg)
#         if not default_token_generator.check_token(user, token):
#             return HttpResponse("Your Link is Expired")


#     except:
#         user = None
#     if user != None:
#             now = timezone.now()
#             pt = user.email_ac_timestamp
#             print(now)
#             print(pt)
#             td = now - pt
#             if td > datetime.timedelta(days=1):
#                 return HttpResponse("Your Link is Expired")
#             form = Change_Password_Form()
#             if request.method == "POST":
#                 form = Change_Password_Form(request.POST)
#                 print(form)
#                 if form.is_valid():
#                     pass1 = form.cleaned_data.get("password1")
#                     pass2 = form.cleaned_data.get("password2")
#                     if pass1 != pass2:
#                         return render(request, 'changepassword.html', {'form' : form, 'is_error': True })
#                     user.set_password(pass1)
#                     user.save()
#                     return redirect("/")

#             return render(request, 'changepassword.html', {'form' : form})
# @login_required
# def profile_view(request):
#     if not request.user.is_phone:
#         return redirect('/accounts/phone-verify/')
#     if request.method == "POST":
#         try:
#             pass1 = request.POST.get('password')
#             pass2 = request.POST.get('repassword')
#         except:
#             pass
#         if pass1 != '':
#             if pass1 == pass2:
#                 request.user.set_password(pass1)
#                 request.user.save()
#                 update_session_auth_hash(request, request.user)  # Important!
#                 return render(request, 'profile.html', {'email' : request.user.email, 'username' : request.user.username, 'phone' : request.user.phone, 'message' : 'Your password was changed successfully'  })
#             else:
#                 return render(request, 'profile.html', {'email' : request.user.email, 'username' : request.user.username, 'phone' : request.user.phone, 'error' : True })

#         else:
#             usr = request.POST.get('username')
#             if usr == request.user.username:
#                 return render(request, 'profile.html', {'email' : request.user.email, 'username' : request.user.username, 'phone' : request.user.phone})
#             else:
#                 request.user.username = usr
#                 request.user.save()
#                 return render(request, 'profile.html', {'email' : request.user.email, 'username' : request.user.username, 'phone' : request.user.phone, 'message' : 'Your username was changed successfully'  })
#     return render(request, 'profile.html', {'email' : request.user.email, 'username' : request.user.username, 'phone' : request.user.phone })
# @login_required
# def delete_profile(request):
#     if not request.user.is_phone:
#         return redirect('/accounts/phone-verify/')
#     user = request.user
#     d =  DelUser.objects.create(email = user.email, phone = user.phone)
#     # user.delete()
#     user.email = None
#     user.phone = None
#     user.del_user = d
#     user.is_active = False
#     user.is_phone = False
#     user.save()
#     logout(request)
#     return redirect('/')

# # email = email.lower()
# # d = email.split('@')
# # u = d[0]
# # d = d[-1]
# # sel = d.split('.')[0]
# # sel = sel + '.'
# # if sel in SELENIUM_LIST:
#     # mx_record = resolver.query(str(email).split('@')[-1], 'MX')
#     # mail_exchangers = [rdata.exchange for rdata in mx_record]
#     # mx = mail_exchangers[0]
#     # x = get_email.check_email_in_db(email)
#     # if x != 0:
#         # Logs.objects.create(user = user, log_type = 'credit', old_credit = user.credit  + 1, new_credit = user.credit,  reason = f"you used 1 credit to verify {email}." )
#         # return JsonResponse({'email' : email, 'error': False, 'status' : x[0][0], 'sub_status' : 'None', 'Disposable' : 'False', 'syntax' : 'True', 'domain' : d, 'catch_all' : 'False', 'user' :  u, 'mx' : str(mx), 'time' : time})
#     # result = get_email(email, email)
#     # if result['status'] == "Valid Email":
#         # Logs.objects.create(user = user, log_type = 'credit', old_credit = user.credit  + 1, new_credit = user.credit,  reason = f"you used 1 credit to verify {email}." )
#         # return JsonResponse({'email' : email, 'error': False, 'status' : 'valid', 'sub_status' : 'None', 'Disposable' : 'False', 'syntax' : 'True', 'domain' : d, 'catch_all' : 'False', 'user' :  u, 'mx' : str(mx), 'time' : time})
#     # elif result['status'] == "Invalid Email":
#         # Logs.objects.create(user = user, log_type = 'credit', old_credit = user.credit  + 1, new_credit = user.credit,  reason = f"you used 1 credit to verify {email}." )
#         # return JsonResponse({'email' : email, 'error': False, 'status' : 'invalid', 'sub_status' : 'None', 'Disposable' : 'False', 'syntax' : 'True', 'domain' : d, 'catch_all' : 'False', 'user' :  u, 'mx' : str(mx), 'time' : time})
#     # else:
#         # Logs.objects.create(user = user, log_type = 'credit', old_credit = user.credit  + 1, new_credit = user.credit,  reason = f"you used 1 credit to verify {email}." )
#         # return JsonResponse({'email' : email, 'error': False, 'status' : 'valid', 'sub_status' : 'None', 'Disposable' : 'False', 'syntax' : 'True', 'domain' : d, 'catch_all' : 'False', 'user' :  u, 'mx' : str(mx), 'time' : time})
# # elif d in ['gmail.com', 'googlemail.com']:
#     # mx_record = resolver.query(str(email).split('@')[-1], 'MX')
#     # mail_exchangers = [rdata.exchange for rdata in mx_record]
#     # mx = mail_exchangers[0]
#     # x = get_email.check_email_in_db(email)
#     # if x != 0:
#         # Logs.objects.create(user = user, log_type = 'credit', old_credit = user.credit  + 1, new_credit = user.credit,  reason = f"you used 1 credit to verify {email}." )
#         # return JsonResponse({'email' : email, 'error': False, 'status' : x[0][0], 'sub_status' : 'None', 'Disposable' : 'False', 'syntax' : 'True', 'domain' : d, 'catch_all' : 'False', 'user' :  u, 'mx' : str(mx), 'time' : time})
#     # ip = verify.get_ip()
#     # source_addr = 'mf141460@gmail.com'
#     # source_pass = 'Pakistan@123'
#     # source_mx = 'smtp.gmail.com'
#     # v = Verifier(source_addr=source_addr,source_pass=source_pass,source_mx=source_mx,source_address=(ip, 25))
#     # result = v.verify(str(email), port = 25)
#     # if result['message']:
#         # if 'Invalid Adress' in result['message'] or 'Recipient address rejected' in result['message'] or 'The email account that you tried to reach does not exist' in result['message']:
#             # Logs.objects.create(user = user, log_type = 'credit', old_credit = user.credit  + 1, new_credit = user.credit,  reason = f"you used 1 credit to verify {email}." )
#             # return JsonResponse({'email' : email, 'error': False, 'status' : 'invalid', 'sub_status' : 'None', 'Disposable' : 'False', 'syntax' : 'True', 'domain' : d, 'catch_all' : 'False', 'user' :  u, 'mx' : str(mx), 'time' : time})
#     # elif not result['deliverable']:
#         # Logs.objects.create(user = user, log_type = 'credit', old_credit = user.credit  + 1, new_credit = user.credit,  reason = f"you used 1 credit to verify {email}." )
#         # return JsonResponse({'email' : email, 'error': False, 'status' : 'invalid', 'sub_status' : 'None', 'Disposable' : 'False', 'syntax' : 'True', 'domain' : d, 'catch_all' : 'False', 'user' :  u, 'mx' : str(mx), 'time' : time})
#     # elif result['deliverable']:
#         # Logs.objects.create(user = user, log_type = 'credit', old_credit = user.credit  + 1, new_credit = user.credit,  reason = f"you used 1 credit to verify {email}." )
#         # return JsonResponse({'email' : email, 'error': False, 'status' : 'valid', 'sub_status' : 'None', 'Disposable' : 'False', 'syntax' : 'True', 'domain' : d, 'catch_all' : 'False', 'user' :  u, 'mx' : str(mx), 'time' : time})
# # else:
#     # x = get_email.check_email_in_db(email)
#     # if x != 0:
#         # Logs.objects.create(user = user, log_type = 'credit', old_credit = user.credit  + 1, new_credit = user.credit,  reason = f"you used 1 credit to verify {email}." )
#         # return JsonResponse({'email' : email, 'error': False, 'status' : x[0][0], 'sub_status' : 'None', 'Disposable' : '   ', 'syntax' : 'True', 'domain' : d, 'catch_all' : '   ', 'user' :  u, 'mx' : str(mx), 'time' : time})
#     # data = {'email' : email, 'error': False, 'status' : 'None', 'sub_status' : 'None', 'Disposable' : 'False', 'syntax' : 'True', 'domain' : None, 'catch_all' : 'False', 'user' :  u, 'mx' : 'None', 'time' : time}
#     # ip = verify.get_ip()
#     # data = real_ip_verification(email, data, ip)
#     # Logs.objects.create(user = user, log_type = 'credit', old_credit = user.credit  + 1, new_credit = user.credit,  reason = f"you used 1 credit to verify {email}." )
#     # return JsonResponse(data)
# def restart_scritps(request):
#     if request.user.is_superuser:
#         os.system("supervisorctl restart all")


#         return HttpResponse("Restarted")
#     else:
#         HttpResponse("Hehe")
