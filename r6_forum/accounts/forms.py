from django import forms
from .models import Profile


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'bio', 'rank', 'show_admin_status']
        labels = {
            'avatar': 'Аватар',
            'bio': 'Bio',
            'rank': 'Ранг',
            'show_admin_status': 'Показувати, що я адмін / модератор',
        }
