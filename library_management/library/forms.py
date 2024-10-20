# library/forms.py
from django import forms
from .models import Book, Member, Transaction

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'authors', 'isbn', 'publisher', 'num_pages']

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['name', 'email', 'debt']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'style': 'font-size: 1.2rem; padding: 10px;'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'style': 'font-size: 1.2rem; padding: 10px;'}),
            'debt': forms.NumberInput(attrs={'class': 'form-control', 'style': 'font-size: 1.2rem; padding: 10px;'}),
        }
        
class IssueBookForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['book','member']
        
class ReturnBookForm(forms.ModelForm):
    return_date = forms.DateField(widget=forms.SelectDateWidget)

    class Meta:
        model = Transaction
        fields = ['return_date']  # Only select the return date

class ImportBooksForm(forms.Form):
    title = forms.CharField(
        max_length=255, 
        required=False, 
        label="Title (optional)",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',  # Adds Bootstrap and size class
            'placeholder': 'Enter book title'
        })
    )
    Author = forms.CharField(
        max_length=255, 
        required=False, 
        label="Author (optional)",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',  # Adds Bootstrap and size class
            'placeholder': 'Enter authors name'
        })
    )
    publisher = forms.CharField(
        max_length=255, 
        required=False, 
        label="Publisher (optional)",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',  # Adds Bootstrap and size class
            'placeholder': 'Enter Publisher'
        })
    )
    num_page = forms.IntegerField(
        max_value=20, 
        required=True, 
        label="No. of books",
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg',  # Adds Bootstrap and size class
            'placeholder': 'Enter number of books'
        })
    )

    
