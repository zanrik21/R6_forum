from django import forms
from .models import Topic, Post


class TopicForm(forms.ModelForm):
    # текстове поле для назви категорії (юзер вводить руками)
    category_name = forms.CharField(
        label='Категорія',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Введи назву категорії...'})
    )

    class Meta:
        model = Topic
        fields = ['title', 'category_name']
        labels = {
            'title': 'Title',
        }


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']
        labels = {'content': 'Content'}
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5})
        }
