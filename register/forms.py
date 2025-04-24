from django import forms
import re

from captcha.fields import CaptchaField
from django.shortcuts import render


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=32,
        min_length=5,
        required=True,
        label='Логин',
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'placeholder': 'Введите логин Telegram'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control',
                                          'placeholder': 'Введите пароль'}),
        max_length=12,
        min_length=8,
        required=True,
        label='Пароль'
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if len(username) < 5 or len(username) > 31:
            raise forms.ValidationError("Ник должен содержать не менее 5 символов!")
        elif not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise forms.ValidationError("Неверный формат никнейма: допустимы символы a-z, 0-9 и подчёркивание!")
        return username

class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите старый пароль',
            'id': 'id_old_password'
        }),
        max_length=12,
        min_length=8,
        required=True,
        label='Старый пароль'
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите новый пароль',
            'id': 'id_new_password1'
        }),
        max_length=12,
        min_length=8,
        required=True,
        label='Новый пароль'
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Подтвердите новый пароль',
            'id': 'id_new_password2'
        }),
        max_length=12,
        min_length=8,
        required=True,
        label='Подтвердите новый пароль'
    )


    def change_password(request):
        if request.method == 'POST':
            form = PasswordChangeForm(user=request.user, data=request.POST)
            if form.is_valid():
                form.save()
                #TODO логика редиректа и сообщения
        else:
            form = PasswordChangeForm(user=request.user)

        return render(request, 'users/change_password.html', {'form': form})

class TelegramCodeForm(forms.Form):
    telegram_code = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control',
                                          'placeholder': 'Введите код подтверждения из Telegram'}),
        min_length=6,
        max_length=6,
        required=True,
        label='Телеграм код'
    )
    username = forms.CharField(
        max_length=32,
        min_length=5,
        required=True,
        label='Логин',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    def clean_telegram_code(self):
        telegram_code = self.cleaned_data["telegram_code"]
        if len(telegram_code) != 6:
            raise forms.ValidationError("Телеграм код должен состоять из 6 символов!")
        elif not telegram_code.isdigit():
            raise forms.ValidationError('Код может содержать только цифры!')
        else:
            return telegram_code

class RegisterForm(forms.Form):
    username = forms.CharField(
        max_length=32,
        min_length=5,
        required=True,
        label='Логин',
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'placeholder': 'Введите ник из Telegram'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control',
                                          'placeholder': 'Введите пароль'}),
        max_length=12,
        min_length=8,
        required=True,
        label='Пароль'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control',
                                          'placeholder': 'Подтвердите пароль'}),
        max_length=12,
        min_length=8,
        required=True,
        label='Подтверждение пароля'
    )

    captcha = CaptchaField()

    def clean_username(self):
        username = self.cleaned_data['username']
        if len(username) < 5 or len(username) > 31:
            raise forms.ValidationError("Ник должен содержать не менее 5 символов!")
        elif not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise forms.ValidationError("Неверный формат никнейма: допустимы символы a-z, 0-9 и подчёркивание!")
        return username

    def clean_password(self):
        password = self.cleaned_data['password']
        if not re.match(r'^[a-zA-Z0-9!@#$%^&*()_+={}[\]|:;<>,.?/`~"-]+$', password):
            raise forms.ValidationError('Пароль содержит недопустимые символы!')
        elif not re.search(r'\d', password):
            raise forms.ValidationError('Слабый пароль! Пароль должен содержать минимум одну цифру.')
        return password

    def clean_confirm_password(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError('Введённые пароли не совпадают!')
        return password