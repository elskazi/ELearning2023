from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin #Ограничение доступа к представлениям
from django.urls import reverse_lazy
from .models import Course

#Использование наборов форм для модулей курса
from django.shortcuts import redirect, get_object_or_404
from django.views.generic.base import TemplateResponseMixin, View
from .forms import ModuleFormSet

#Добавление содержимого в модули курса
from django.forms.models import modelform_factory
from django.apps import apps
from .models import Module, Content

#Использование примесей из модуля django-braces
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin

# Отображение курсов
from django.db.models import Count
from .models import Subject
from django.views.generic.detail import DetailView

#  зачисляемых на курсы студентов
from students.forms import CourseEnrollForm

# кеш
from django.core.cache import cache

# Отображение курсов
class CourseListView(TemplateResponseMixin, View):
    model = Course
    template_name = 'courses/course/list.html'
    def get(self, request, subject=None):
        subjects = cache.get('all_subjects')
        if not subjects:
            subjects = Subject.objects.annotate(total_courses=Count('courses'))
            cache.set('all_subjects', subjects)
        all_courses = Course.objects.annotate(total_modules=Count('modules'))
        if subject:
            subject = get_object_or_404(Subject, slug=subject)
            key = f'subject_{subject.id}_courses'
            courses = cache.get(key)
            if not courses:
                courses = all_courses.filter(subject=subject)
                cache.set(key, courses)
        else:
            courses = cache.get('all_courses')
            if not courses:
                courses = all_courses
                cache.set('all_courses', courses)
        return self.render_to_response({'subjects': subjects,'subject': subject,'courses': courses})




class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enroll_form'] = CourseEnrollForm(initial={'course': self.object})
        return context



#Использование примесей из модуля django-braces
class ModuleOrderView(CsrfExemptMixin,JsonRequestResponseMixin,View):
    def post(self, request):
        for id, order in self.request_json.items():
            Module.objects.filter(id=id,course__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})

class ContentOrderView(CsrfExemptMixin,JsonRequestResponseMixin,View):
    def post(self, request):
        for id, order in self.request_json.items():
            Content.objects.filter(id=id,module__course__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})

# Управление модулями и их содержимым
class ModuleContentListView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/content_list.html'
    def get(self, request, module_id):
        module = get_object_or_404(Module,id=module_id,course__owner=request.user)
        return self.render_to_response({'module': module})
# Конец Управление модулями и их содержимым

#Добавление содержимого в модули курса
class ContentCreateUpdateView(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    template_name = 'courses/manage/content/form.html'
    def get_model(self, model_name):
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(app_label='courses',model_name=model_name)
        return None
    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(model, exclude=['owner','order','created','updated'])
        return Form(*args, **kwargs)
    def dispatch(self, request, module_id, model_name, id=None):
        self.module = get_object_or_404(Module,id=module_id,course__owner=request.user)
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model,id=id,owner=request.user)
        return super().dispatch(request, module_id, model_name, id)

    def get(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form,'object': self.obj})

    def post(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model,
                             instance=self.obj,
                             data=request.POST,
                             files=request.FILES)

        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                # new content
                Content.objects.create(module=self.module, item=obj)
            return redirect('module_content_list', self.module.id)
        return self.render_to_response({'form': form,'object': self.obj})

class ContentDeleteView(View):
    def post(self, request, id):
        content = get_object_or_404(Content,id=id,module__course__owner=request.user)
        module = content.module
        content.item.delete()
        content.delete()
        return redirect('module_content_list', module.id)
# Конец Добавление содержимого в модули курса


#Использование наборов форм для модулей курса
class CourseModuleUpdateView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/formset.html'
    course = None

    def get_formset(self, data=None):
        return ModuleFormSet(instance=self.course,data=data)

    def dispatch(self, request, pk):
        self.course = get_object_or_404(Course,id=pk,owner=request.user)
        return super().dispatch(request, pk)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({'course': self.course,'formset': formset})

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('manage_course_list')
        return self.render_to_response({'course': self.course,'formset': formset})
# КОНЕЦ  Использование наборов форм для модулей курса



# Создание курса Юзером, изменеие, удаление, доступ к управлению курса толькко Юзером тек что создал
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