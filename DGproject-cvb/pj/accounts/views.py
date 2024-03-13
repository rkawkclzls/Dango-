from django.shortcuts import render, redirect
from django.views import View
from .models import User
from django.contrib.auth.hashers import make_password, check_password
from .forms import LoginForm
from django.contrib import messages
import jwt
from django.conf import settings

# HomeView는 home.html 템플릿을 렌더링합니다.
class HomeView(View):
    def get(self, request):
        return render(request, 'accounts/home.html')


# 사용자 등록을 처리합니다.
class RegisterView(View):
    def get(self, request):
        return render(request, 'accounts/register.html')

    def post(self, request):
        # POST 요청에서 폼 데이터 가져오기
        username = request.POST.get('username', None)
        useremail = request.POST.get('useremail', None)
        password = request.POST.get('password', None)
        re_password = request.POST.get('re_password', None)

        err_data = {}
        if not (username and useremail and password and re_password):
            err_data['error'] = '모든 값을 입력해주세요.'  # 필드가 누락된 경우 오류 메시지
        elif password != re_password:
            err_data['error'] = '비밀번호가 일치하지 않습니다.'  # 비밀번호가 일치하지 않는 경우 오류 메시지
        else:
            # 중복 확인
            if User.objects.filter(username=username).exists():
                err_data['error'] = '이미 사용 중인 사용자 이름입니다.'  # 사용자 이름이 이미 사용 중인 경우 오류 메시지
            elif User.objects.filter(useremail=useremail).exists():
                err_data['error'] = '이미 사용 중인 이메일입니다.'  # 이메일이 이미 사용 중인 경우 오류 메시지
            else:
                # 새로운 User 객체를 생성하고 데이터베이스에 저장합니다.
                user = User(
                    username=username,
                    useremail=useremail,
                    password=make_password(password),
                )
                user.save()
                messages.success(request, '등록이 성공적으로 완료되었습니다! 로그인 페이지로 이동합니다.')  # 성공 메시지
                return redirect('/accounts/login/')

        return render(request, 'accounts/register.html', err_data)


# 사용자 로그인을 처리합니다.
class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'accounts/login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:
                user = User.objects.get(username=username)
                if check_password(password, user.password):
                    # JWT 토큰 생성
                    payload = {'user_id': user.id}
                    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')
                    # 세션에 토큰 저장
                    request.session['token'] = token
                    return redirect('/')
                else:
                    form.add_error('password', '잘못된 비밀번호입니다.')
            except User.DoesNotExist:
                form.add_error('username', '사용자가 존재하지 않습니다.')
        return render(request, 'accounts/login.html', {'form': form})


# 사용자 로그아웃을 처리합니다.
class LogoutView(View):
    def get(self, request):
        return self.logout(request)

    def post(self, request):
        return self.logout(request)

    def logout(self, request):
        if request.session.get('token'):
            del request.session['token']
        return redirect('/')
