from django.utils.deprecation import MiddlewareMixin
from captcha.image import ImageCaptcha
import random
import base64
from django.http import HttpResponse
from django.shortcuts import render
from allauth.account.forms import LoginForm, SignupForm


class GlobalRequestMiddleware(MiddlewareMixin):

    __instance = None

    # def __new__(cls, *args, **kwargs):
    #     if not cls.__instance:
    #         cls.__instance = object.__new__(cls)
    #     return cls.__instance

    def process_request(self, request):
        GlobalRequestMiddleware.__instance = request

    @classmethod
    def getRequest(cls):
        return cls.__instance


class AddCaptchaAndVerify(MiddlewareMixin):

    def process_request(self, request):
        if request.path_info in ['/accounts/login/', '/accounts/signup/']:
            if request.GET.get('update_captcha'):
                ic = ImageCaptcha()
                nums = ''.join(random.sample('0123456789', 4))
                request.session['captcha'] = nums
                img = ic.generate(nums)
                request.session['captcha_img'] = 'data:image/jpg;base64,' + base64.b64encode(
                    img.getvalue()).decode()
                return HttpResponse(request.session['captcha_img'])
            if request.method == 'GET':
                ic = ImageCaptcha()
                nums = ''.join(random.sample('0123456789', 4))
                request.session['captcha'] = nums
                img = ic.generate(nums)
                request.session['captcha_img'] = 'data:image/jpg;base64,' + base64.b64encode(img.getvalue()).decode()
            elif request.method == 'POST':
                if request.POST.get('captcha') != request.session['captcha']:
                    if request.path_info == '/accounts/login/':
                        form = LoginForm(request.POST)
                        form.non_field_errors = ['验证码错误。']
                        return render(request, 'account/login.html', dict(form=form))
                    elif request.path_info == '/accounts/signup/':
                        form = SignupForm(request.POST)
                        form.non_field_errors = ['验证码错误。']
                        return render(request, 'account/signup.html', dict(form=form))