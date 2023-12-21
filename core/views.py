from email.mime import image
from django.shortcuts import render
import json
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from accounts.models import User
from core.models import Image, Item, Match, Notification
from core.serializers import ItemSerializer, MatchSerializer, NotificationSerializer
from rest_framework.pagination import PageNumberPagination
from accounts.emailsend import email_send
from rest_framework_simplejwt.tokens import RefreshToken
from matching import match_main
from core.tasks import match_task


@api_view(["POST"])
def register_view(request):
    data = json.loads(request.body)
    print(data)

    try:
        user = User.objects.get(email=data["email"])
        return Response(
            {"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST
        )
    except:
        passwd = data["password"]
        del data["password"]
        user = User.objects.create(**data)
        user.set_password(passwd)
        user.is_active = True
        user.save()
        # email_send(user)
        return Response(
            {"success": "User created successfully"}, status=status.HTTP_201_CREATED
        )

    # return Response({"fname": request.user.fname, "email": request.user.email, "lname": request.user.lname, "is_superuser": request.user.is_superuser, "profile_url": request.user.thumbnail.url if request.user.image else None})


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def get_profile(request):
    return Response(
        {
            "fname": request.user.fname,
            "phone": request.user.phone if request.user.phone else None,
            "email": request.user.email,
            "lname": request.user.lname,
            "is_superuser": request.user.is_superuser,
            "profile_url": request.user.thumbnail.url if request.user.image else None,
        }
    )


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def update_profile(request):
    user = request.user
    data = json.loads(request.body)
    print(data)
    user.fname = data["fname"]
    user.lname = data["lname"]
    user.phone = data["phone"]
    user.email = data["email"]
    user.save()
    obj = request.user

    return Response(
        {
            "user": {
                "id": obj.id,
                "fname": obj.fname,
                "lname": obj.lname,
                "is_superuser": obj.is_superuser,
                "phone": obj.phone if obj.phone else None,
                "email": obj.email,
                "profile_url": obj.thumbnail.url if obj.image else None,
            }
        }
    )


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def update_password(request):
    user = request.user

    if request.user.is_google_user:
        return Response(
            {"message": "You are not allowed to change password"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    data = json.loads(request.body)
    print(data)
    if request.user.check_password(data["password"]):
        user.set_password(data["new_password"])
        user.save()
        return Response(
            {"success": "Password updated successfully"}, status=status.HTTP_200_OK
        )
    else:
        return Response(
            {"message": "Old password is not correct"},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def delete_user(request):
    try:
        request.user.delete()

        logout(request)

        return Response({"success": "User deleted"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def deny_matching(request, id):
    try:
        match = Match.objects.get(id=id)
        if match.found_item.user == request.user:
            fi = match.found_item
            li = match.lost_item
            fi.status = "search"
            fi.save()
            li.status = "search"
            li.save()
            match.delete()
            return Response({"success": "Match deleted"}, status=status.HTTP_200_OK)

        return Response(
            {"success": "You are not allowed to deny this matching"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def accept_matching(request, id):
    try:
        match = Match.objects.get(id=id)
        if match.found_item.user == request.user:
            i = match.lost_item
            user = i.user
            match.founder_phone = request.user.phone
            match.loster_phone = match.lost_item.user.phone
            match.is_accepted = True
            match.found_item.status = "recover"
            match.found_item.save()
            match.lost_item.status = "recover"
            match.lost_item.save()
            match.save()
            serializer = MatchSerializer(match)
            return Response(
                {"success": True, "match": serializer.data, "is_founder": True},
                status=status.HTTP_200_OK,
            )

        else:
            return Response(
                {"success": "You are not allowed to accept this matching"},
                status=status.HTTP_400_BAD_REQUEST,
            )
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def recieved_item(request, id):
    try:
        match = Match.objects.get(id=id)
        if match.lost_item.user == request.user:
            match.is_active = False
            match.found_item.status = "complete"
            match.found_item.save()
            match.lost_item.status = "complete"
            match.lost_item.save()
            match.save()
            return Response(
                {
                    "success": True,
                },
                status=status.HTTP_200_OK,
            )

        else:
            return Response(
                {"success": "You are not allowed"}, status=status.HTTP_400_BAD_REQUEST
            )
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def get_notifications(request):
    try:
        nots = Notification.objects.filter(is_read=False, user=request.user)
        serializer = NotificationSerializer(nots, many=True)
        return Response({"notifications": serializer.data}, status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def mark_notification_as_read(request, id):
    try:
        n = Notification.objects.get(id=id, user=request.user)
        n.is_read = True
        n.save()
        return Response({}, status.HTTP_200_OK)
    except Exception as e:
        return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def create_item(request):
    # data = json.loads(request.body)
    # print(data)
    print(request.POST)
    d = json.loads(json.dumps(request.POST).encode("utf8"))
    print(d, "data for")

    files = request.FILES.getlist("images")
    print(files)
    i = Item.objects.create(
        user=request.user,
        state=request.POST.get("item-state").lower(),
        main_cat=request.POST.get("main_cat").lower(),
        sub_cat=request.POST.get("sub_cat").lower(),
        data=d,
    )
    if request.POST.get("country") != None:
        i.country = (
            request.POST.get("country").lower()
            if request.POST.get("country") != None
            else None
        )
        i.c_state = (
            request.POST.get("state").lower()
            if request.POST.get("state") != None
            else None
        )
        i.city = (
            request.POST.get("city").lower()
            if request.POST.get("city") != None
            else None
        )
    for f in files:
        i.images.add(Image.objects.create(image=f))
        break
    i.save()
    match_main()
    return Response({"message": "item created", "id": i.id, "state": i.state}, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def items_api_lost(request):
    if request.user.is_superuser:
        # paginator = PageNumberPagination()
        # paginator.page_size = 20
        items = Item.objects.filter(state="lost").order_by("-created_at")
        # result_page = paginator.paginate_queryset(items, request)
        serializer = ItemSerializer(items, many=True)
        return Response({"items": serializer.data}, status=status.HTTP_200_OK)
        # return paginator.get_paginated_response(serializer.data)
    else:
        # paginator = PageNumberPagination()
        # paginator.page_size = 20
        items = Item.objects.filter(user=request.user, state="lost").order_by(
            "-created_at"
        )
        # result_page = paginator.paginate_queryset(items, request)
        serializer = ItemSerializer(items, many=True)
        return Response({"items": serializer.data}, status=status.HTTP_200_OK)

        # return paginator.get_paginated_response(serializer.data)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def items_api_found(request):
    if request.user.is_superuser:
        # paginator = PageNumberPagination()
        # paginator.page_size = 20
        items = Item.objects.filter(state="found").order_by("-created_at")
        # result_page = paginator.paginate_queryset(items, request)
        serializer = ItemSerializer(items, many=True)
        return Response({"items": serializer.data}, status=status.HTTP_200_OK)
        # return paginator.get_paginated_response(serializer.data)
    else:
        # paginator = PageNumberPagination()
        # paginator.page_size = 20
        items = Item.objects.filter(user=request.user, state="found").order_by(
            "-created_at"
        )
        # result_page = paginator.paginate_queryset(items, request)
        serializer = ItemSerializer(items, many=True)
        return Response({"items": serializer.data}, status=status.HTTP_200_OK)

        # return paginator.get_paginated_response(serializer.data)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def get_item(request, id):
    if request.user.is_superuser:
        item = Item.objects.get(id=id)
        serializer = ItemSerializer(item)
        return Response({"item": serializer.data}, status=status.HTTP_200_OK)
    else:
        item = Item.objects.get(id=id, user=request.user)
        serializer = ItemSerializer(item)
        return Response({"item": serializer.data})


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def delete_item(request, id):
    item = get_object_or_404(Item, id=id)
    if request.user.is_superuser or item.user == request.user:
        is_lost = True if item.state == "lost" else False
        is_founder = not is_lost
        m = None
        if is_lost:
            matches = Match.objects.filter(lost_item=item)
            for m in matches:
                m.found_item.status = "search"
                m.found_item.matched_with.clear()
                m.found_item.save()
                m.delete()

        else:
            matches = Match.objects.filter(found_item=item)
            for m in matches:
                m.lost_item.status = "search"
                m.lost_item.matched_with.clear()
                m.lost_item.save()
                m.delete()
        item.delete()
        match_main()

        return Response({"success": True})
    return Response({"success": False}, status=status.HTTP_403_FORBIDDEN)


# api for editing item


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def edit_item(request, id):
    # print(data)
    print(request.POST)
    d = json.loads(json.dumps(request.POST).encode("utf8"))

    print(d, "date for update")
    print(type(d), "type of data")
    print(request.POST.get("country"))
    print(request.POST.get("item-state"))
    state = request.POST.get("item-state").lower()
    main_cat = request.POST.get("main_cat").lower()
    sub_cat = request.POST.get("sub_cat").lower()
    print(state, main_cat, sub_cat, "data for update")
    # check status of found or lost

    i = Item.objects.get(id=id)
    if i.state == "lost":
        # check matches
        ms = Match.objects.filter(lost_item=i)
        for m in ms:
            f = m.found_item
            f.status = "search"
            f.matched_with.remove(i)
            f.save()
            m.delete()
    else:
        ms = Match.objects.filter(found_item=i)
        for m in ms:
            f = m.found_item
            f.status = "search"
            f.matched_with.remove(i)
            f.save()
            m.delete()

    i.state = state
    i.main_cat = main_cat
    i.sub_cat = sub_cat
    i.data = d
    i.status = "search"

    # delete previous files

    files = request.FILES.getlist("images")
    old_images = request.POST.get("old_images")
    old_images = json.loads(old_images)

    if request.POST.get("country") != None:
        i.country = (
            request.POST.get("country").lower()
            if request.POST.get("country") != None
            else None
        )
        i.c_state = (
            request.POST.get("state").lower()
            if request.POST.get("state") != None
            else None
        )
        i.city = (
            request.POST.get("city").lower()
            if request.POST.get("city") != None
            else None
        )
    if i.images.all().count() != len(old_images):
        ids = []
        for imgs in old_images:
            ids.append(imgs["id"])
        for ig in i.images.all():
            if ig.id not in ids:
                ig.delete()

    if files:
        for f in files:
            i.images.add(Image.objects.create(image=f))
    print(old_images, "old images")
    i.matched_with.clear()
    i.save()
    match_main()
    

    return Response(
        {"message": "item updated", "id": i.id, "state": i.state},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def get_item_match(request, id):
    item = Item.objects.get(id=id)
    if request.user.is_superuser or item.user == request.user:
        # paginator = PageNumberPagination()
        # paginator.page_size = 20
        is_lost = True if item.state == "lost" else False
        is_founder = not is_lost
        m = None
        if is_lost:
            m = Match.objects.filter(lost_item=item)[0]
        else:
            m = Match.objects.filter(found_item=item)[0]
        if m is not None:
            serializer = MatchSerializer(m)
            return Response(
                {"match": serializer.data, "is_founder": is_founder},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"message": "no match found"}, status=status.HTTP_400_BAD_REQUEST
            )
