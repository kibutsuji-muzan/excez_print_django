from rest_framework.permissions import BasePermission

from accounts.models.UserModel import User

class IsSameUser(BasePermission):

    def permission(self, request):
        path = request.META.get('PATH_INFO').strip('/').split('/')
        user = []
        for pk in path:
            uu = User.object.filter(user=pk)
            if len(uu):
                user.append(uu[0])
        return ((True if user[0] == request.user else False) if len(user) else False)

    def has_permission(self, request, view):
        return self.permission(request)
    
    def has_object_permission(self, request, view, obj):
        return self.permission(request)

# class IsTutor(BasePermission):

#     def permission(self, request):
#         user = request.user
#         type = UserType.objects.get(name='Tutor')
#         if type in user.user_profile.type.all():
#             return True
#         return False

#     def has_permission(self, request, view):
#         return self.permission(request)
        
#     def has_object_permission(self, request, view, obj):
#         return self.permission(request)
