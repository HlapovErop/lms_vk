from .views import users
from .views import groups
from .views import courses
from .views import lessons
from .views import notifications
from django.urls import path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.inspectors import SwaggerAutoSchema

from rest_framework.permissions import AllowAny
from rest_framework.authentication import BasicAuthentication


class CustomOpenAPISchemaGenerator(OpenAPISchemaGenerator):
    def get_security_definitions(self):
        return {
            "ApiKeyAuth": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header"
            }
        }


schema_view = get_schema_view(
    openapi.Info(
        title="Your API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@yourapi.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(AllowAny,),
    authentication_classes=(BasicAuthentication,),
    generator_class=CustomOpenAPISchemaGenerator
)

urlpatterns = [
    # Пользователи
    path(r'users/signup', users.createUser),  # POST /users/signup - Регистрация пользователя
    path(r'users/login', users.login),  # POST /users/login - Вход пользователя
    path(r'users/profile', users.login),  # GET /users/profile - Получение данных для пользователя
    path(r'users/update/<str:pk>', users.updateUser),  # PUT /users/update/<id> - Обновление данных пользователя
    path(r'users/delete/<str:pk>', users.deleteUser),  # DELETE /users/delete/<id> - Удаление пользователя
    path(r'users/<str:pk>', users.getUser),  # GET /users/<id> - Получение информации о пользователе
    path(r'users', users.getUsers),  # GET /users - Получение списка пользователей

    # Группы
    path(r'groups/create', groups.createGroup),  # POST /groups/create - Создание новой группы
    path(r'groups/update/<str:pk>', groups.updateGroup),  # PUT /groups/update/<id> - Обновление данных группы
    path(r'groups/delete/<str:pk>', groups.deleteGroup),  # DELETE /groups/delete/<id> - Удаление группы
    path(r'groups/<str:pk>/students/create', groups.addStudents),
    # POST /groups/<id>/students/create - Добавление студентов в группу
    path(r'groups/<str:pk>/students/delete', groups.deleteStudents),
    # DELETE /groups/<id>/students/delete - Удаление студентов из группы
    path(r'groups/<str:pk>/courses/create', groups.addCourses),
    # POST /groups/<id>/courses/create - Добавление курсов в группу
    path(r'groups/<str:pk>/courses/delete', groups.deleteCourses),
    # DELETE /groups/<id>/courses/delete - Удаление курсов из группы
    path(r'groups/<str:pk>', groups.getGroup),  # GET /groups/<id> - Получение информации о группе
    path(r'groups', groups.getGroups),  # GET /groups - Получение списка групп

    # Курсы
    path('courses/create', courses.createCourse),  # POST /courses/create - Создание нового курса
    path('courses/<str:pk>/update', courses.updateCourse),  # PUT /courses/update/<id> - Обновление данных курса
    path('courses/<str:pk>/delete', courses.deleteCourse),  # DELETE /courses/delete/<id> - Удаление курса
    path('courses/<str:pk>/syllabus', courses.syllabus),  # POST /courses/syllabus/<id> - Подписаться на курс
    path('courses/<str:pk>/add_lesson', courses.addLesson),  # POST /courses/syllabus/<id> - Добавить урок в курс
    path('courses/my', courses.myCourses),
    # GET /courses/my - Получение списка курсов модератора или на которые подписан студент
    path('courses/<str:pk>', courses.getCourse),  # GET /courses/<id> - Получение информации о курсе
    path('courses', courses.getCourses),  # GET /courses - Получение списка курсов

    # Уроки
    path('lessons/solve', lessons.solve), # POST /lessons/solve - Отправить решение курса
    path('lessons/<str:pk>', lessons.getLesson),  # GET /lessons/<id> - Получение информации об уроке

    # Уведомления
    path('notifications/create', notifications.createNotification),
    # POST /notifications/create - Создание нового уведомления
    path('notifications/my', notifications.getNotifications),
    # GET /notifications/my - Уведомления, адресованные пользователю
    path('notifications/read', notifications.readNotifications),
    # DELETE /notifications/read - "Просмотр" и удаление уведомлений

    # Swagger
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

]
