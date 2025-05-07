from django import forms

class AdminLoginForm(forms.Form):
    login = forms.CharField(
        max_length=100,
        required=True,
        label='Логин',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите логин администратора'
        })
    )

    password = forms.CharField(
        max_length=128,
        required=True,
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )
