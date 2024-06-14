from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins

from accounts.models.UserModel import UserProfile, User

from accounts.serializers.ProfileSerializer import ProfileSerializer

from accounts.permissions import IsSameUser


class Profile(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    http_method_names = ["get", "put", "post"]
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated, IsSameUser]
    queryset = UserProfile.objects.all()

    def get_serializer_class(self):
        return ProfileSerializer

    def get_serializer(self, *args, **kwargs):
        try:
            (kwargs["context"]).update(self.get_serializer_context())
        except:
            kwargs["context"] = self.get_serializer_context()

        serializer_class = self.get_serializer_class()
        return serializer_class(*args, **kwargs)

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = {"request": self.request, "format": self.format_kwarg, "view": self}
        return context

    def get_data(self, user, request):
        return {
            "user": {'user':self.request.user.user},
            "email": request.data.get("email") if (request.data.get("email") is not None) else user.email,
            "phone": request.data.get("phone") if (request.data.get("phone") is not None) else user.phone,
            "first_name": request.data.get("first_name") if (request.data.get("first_name") is not None) else user.first_name,
            "last_name": request.data.get("last_name") if (request.data.get("last_name") is not None) else user.last_name,
            "gender": request.data.get("gender") if (request.data.get("gender") is not None) else user.gender,
            "birthday": request.data.get("birthday") if (request.data.get("birthday") is not None) else user.birthday,
        }

    def retrieve(self, request, pk):
        user = User.objects.filter(user=pk)
        if len(user):
            serializer = self.get_serializer(user[0].user_profile)
            return Response(serializer.data)
        return Response("No User Found", status=status.HTTP_404_NOT_FOUNDs)

    def update(self, request, pk):
        data = self.get_data(user=request.user.user_profile, request=request)
        profile_image = request.FILES.get("profile_image")
        data["profile_image"] = {"image": profile_image}
        serializer = self.get_serializer(data=data, context={'request':request})

        if serializer.is_valid(raise_exception=True):
            serializer.update(instance=request.user, data=data)
        return Response("Your Account Detail Has Been Updated", status.HTTP_200_OK)


class UsersPosts(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    http_method_names = ["get", "put", "post", "delete"]
    # serializer_class = ClientPostSerializer
    # queryset = ClientPost.objects.all()
    permission_classes = [IsAuthenticated, IsSameUser]

    def get_serializer_class(self):
        return self.serializer_class

    def get_serializer(self, *args, **kwargs):
        try:
            (kwargs["context"]).update(self.get_serializer_context())
        except:
            kwargs["context"] = self.get_serializer_context()

        serializer_class = self.get_serializer_class()
        return serializer_class(*args, **kwargs)

    def get_serializer_context(self):
        return {"request": self.request, "format": self.format_kwarg, "view": self}

    def validate_request(self, request):
        if type(request.data) is dict:
            return request.data
        return False
    
    def retrieve(self, request, pk):
        # posts = ClientPost.objects.filter(profile=request.user.user_profile)
        res = "Posts Not Found"
        stat = status.HTTP_404_NOT_FOUND
        # if len(posts):
        #     res = self.get_serializer(posts).data
        #     stat = status.HTTP_200_OK
        return Response(res, stat)
    
    def create(self, request, pk):
        data = request.data
        images = request.FILES.getlist("post_image")
        serializer = self.get_serializer(data=data, context={"images": images})
        if serializer.is_valid(raise_exception=True):
            print(serializer.data)
            data = serializer.data
            data["profile"] = request.user.user_profile
            print(data)
            serializer.create(data)
        return Response("Post Created")

    def update(self, request, pk):
        data = request.data
        serializer = self.get_serializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.update(instance=request.user, data=data)
        return Response("Your Account Detail Has Been Updated", status.HTTP_200_OK)


    def destroy(self, request, pk):
        data = request.data
        res = "Multiple Post Can Not Be Deleted"
        stat = status.HTTP_400_BAD_REQUEST
        if len(data)==1:
            res = "Post With This ID Can Be Found"
            stat = status.HTTP_404_NOT_FOUND
            # post = ClientPost.objects.filter(id=data.get("id"), profile=request.user.user_profile)
            # if len(post):
            #     res = "Post Deleted Successfully"
            #     post.delete()
        return Response(res, status=stat if stat else status.HTTP_200_OK)