from functools import wraps
from django.http import HttpResponseForbidden
from djangoapp.models.user import UserRoleEnum


def role_required(required_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.role not in required_roles:
                return HttpResponseForbidden({'error': 'You do not have permission to perform this action.'})
            return view_func(request, *args, **kwargs)
        return wrapper

    return decorator


# Декораторы для разных ролей
admin_required = role_required([UserRoleEnum.ADMIN])
methodologist_required = role_required([UserRoleEnum.METHODOLOGIST])
student_required = role_required([UserRoleEnum.STUDENT])
teacher_required = role_required([UserRoleEnum.TEACHER])
methodologist_or_admin_required = role_required([UserRoleEnum.METHODOLOGIST, UserRoleEnum.ADMIN])
teacher_or_admin_required = role_required([UserRoleEnum.TEACHER, UserRoleEnum.ADMIN])
