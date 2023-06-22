from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin #Ограничение доступа к представлениям
from django.urls import reverse_lazy
from .models import Course



''' Миксины с методом get_queryset перепоределяем для того что б Устанавливается владелец этих курсов и Препод(владелец) мог использовать только свои Курсы и '''

''' Миксин OwnerMixin
Указанный примесный класс (Миксины оба и тот что ниже) будет переопределять этот метод get_queryset() с целью
фильтрации объектов по атрибуту owner, чтобы извлекать объекты, принадлежащие текущему пользователю (request.user).'''
class OwnerMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)

''' Миксин OwnerEditMixin'''
''' представлениями с формами или модельными формами, такими как CreateView и UpdateView. Метод form_valid() исполняется, когда
переданная на обработку форма является валидной '''
class OwnerEditMixin:
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

''' После OwnerMixin (установления владельца) выбирается курс и поля предмета курса, и ссылка успеха'''
''' LoginRequiredMixin,PermissionRequiredMixin  права/ограничения '''
class OwnerCourseMixin(OwnerMixin, LoginRequiredMixin,PermissionRequiredMixin):
    model = Course
    fields = ['subject', 'title', 'slug', 'overview']
    success_url = reverse_lazy('manage_course_list')

'''При создании или измения и  OwnerCourseMixin, OwnerEditMixin предоставляется шаблон для измениний'''
class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    template_name = 'courses/manage/course/form.html'

''' выводит список созданных пользователем курсов. Указанное представление наследует от OwnerCourseMixin и ListView
и определяет специальный атрибут template_name для шаблона, который будет выводить список курсов; '''
class ManageCourseListView(OwnerCourseMixin, ListView):
    model = Course
    template_name = 'courses/manage/course/list.html'
    permission_required = 'courses.view_course' #  права/ограничения
    def get_queryset(self):
        '''get_queryset() представления, чтобы извлекать только те курсы, которые были созданы текущим пользователем
        переопределим метод get_queryset() с использованием  примесей (примесные классы, или миксины)'''
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)

'''CourseCreateView: использует модельную форму для создания нового объекта Course. 
В указанном представлении используются поля, определенные в примесном классе OwnerCourseMixin, чтобы компоновать модельную форму; 
это представление также является подклассом класса CreateView. Оно использует шаблон, определенный в примесном классе OwnerCourseEditMixin '''
class CourseCreateView(OwnerCourseEditMixin, CreateView):
    permission_required = 'courses.add_course'  # права/ограничения


'''CourseUpdateView: обеспечивает возможность редактировать существующий объект Course. В указанном представлении используются поля,
определенные в примесном классе OwnerCourseMixin, чтобы компоновать модельную форму; это представление также является подклассом
класса UpdateView. '''
class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    permission_required = 'courses.change_course' #  права/ограничения

'''CourseDeleteView: наследует от OwnerCourseMixin и типового DeleteView.
В указанном представлении определяется специальный атрибут template_name для шаблона, который будет подтверждать удаление курса.'''
class CourseDeleteView(OwnerCourseMixin, DeleteView):
    template_name = 'courses/manage/course/delete.html'
    permission_required = 'courses.delete_course'  # права/ограничения