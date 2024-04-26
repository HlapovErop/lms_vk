from django.urls import path
from .views import users
from .views import groups
from .views import courses
from .views.swagger import swagger

urlpatterns = [
    # Пользователи
    path(r'users/signup', users.createUser),                             # POST /users/signup - Регистрация пользователя
    path(r'users/login', users.login),                                   # POST /users/login - Вход пользователя
    path(r'users/update/<str:pk>', users.updateUser),                    # PUT /users/update/<id> - Обновление данных пользователя
    path(r'users/delete/<str:pk>', users.deleteUser),                    # DELETE /users/delete/<id> - Удаление пользователя
    path(r'users/<str:pk>', users.getUser),                              # GET /users/<id> - Получение информации о пользователе
    path(r'users', users.getUsers),                                      # GET /users - Получение списка пользователей

    # Группы
    path(r'groups/create', groups.createGroup),                          # POST /groups/create - Создание новой группы
    path(r'groups/update/<str:pk>', groups.updateGroup),                 # PUT /groups/update/<id> - Обновление данных группы
    path(r'groups/delete/<str:pk>', groups.deleteGroup),                 # DELETE /groups/delete/<id> - Удаление группы
    path(r'groups/<str:pk>/students/create', groups.addStudents),        # POST /groups/<id>/students/create - Добавление студентов в группу
    path(r'groups/<str:pk>/students/delete', groups.deleteStudents),     # DELETE /groups/<id>/students/delete - Удаление студентов из группы
    path(r'groups/<str:pk>/courses/create', groups.addCourses),          # POST /groups/<id>/courses/create - Добавление курсов в группу
    path(r'groups/<str:pk>/courses/delete', groups.deleteCourses),       # DELETE /groups/<id>/courses/delete - Удаление курсов из группы
    path(r'groups/<str:pk>', groups.getGroup),                           # GET /groups/<id> - Получение информации о группе
    path(r'groups', groups.getGroups),                                   # GET /groups - Получение списка групп
    
    # Курсы
    path('courses/create', courses.createCourse),                        # POST /courses/create - Создание нового курса
    path('courses/update/<str:pk>', courses.updateCourse),               # PUT /courses/update/<id> - Обновление данных курса
    path('courses/delete/<str:pk>', courses.deleteCourse),               # DELETE /courses/delete/<id> - Удаление курса
    path('courses/syllabus/<str:pk>', courses.syllabus),                 # POST /courses/syllabus/<id> - Подписаться на курс
    path('courses/my', courses.myCourses),                               # GET /courses/my - Получение списка курсов модератора или на которые подписан студент
    path('courses/<str:pk>', courses.getCourse),                         # GET /courses/<id> - Получение информации о курсе
    path('courses', courses.getCourses),                                 # GET /courses - Получение списка курсов

    # Swagger
    path('', swagger),                                                   # Корневой URL для Swagger-документации
]
