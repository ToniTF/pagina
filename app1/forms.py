from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import PasswordInput
from django.contrib.auth.models import User
from .models import Post, Comentario, Categoria

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Requerido. Introduce una dirección de correo válida.')
    
    password = forms.CharField(
        label="Contraseña", 
        strip=False,
        widget=PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=( 
            "<ul>"
            "<li>Su contraseña no puede ser demasiado similar a su otra información personal.</li>"
            "<li>Su contraseña debe contener al menos 8 caracteres.</li>"
            "<li>Su contraseña no puede ser una contraseña de uso común.</li>"
            "<li>Su contraseña no puede ser completamente numérica.</li>"
            "</ul>"
        ),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe una cuenta registrada con esta dirección de correo electrónico.")
        return email

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['titulo', 'contenido', 'extracto', 'categoria', 'imagen_destacada', 'publicado', 'destacado']
        widgets = {
            'extracto': forms.Textarea(attrs={'rows': 3}),
        }

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['contenido']
        widgets = {
            'contenido': forms.Textarea(attrs={
                'rows': 4, 
                'class': 'form-control'
            }),
        }
        labels = {
            'contenido': 'Tu comentario',
        }