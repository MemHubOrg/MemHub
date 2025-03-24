from django import forms
import re

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