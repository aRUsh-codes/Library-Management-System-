# library/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Book, Member, Transaction
from .forms import BookForm, MemberForm, IssueBookForm, ImportBooksForm, ReturnBookForm
import requests
from django.utils import timezone
from django.contrib import messages

# -------------- HOME ------------
def home(request):
    return render(request,'index.html')

# ------------------- Book CRUD -------------------
def book_list(request):
    books = Book.objects.all()
    return render(request, 'book_list.html', {'books': books})


def update_book(request, isbn):
    # Fetch the book by isbn
    book = get_object_or_404(Book, isbn=isbn)

    # If the request is a POST, we need to save the form data
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()  # Save changes to the book
            return redirect('book_list')  # Redirect to the book list after updating
    else:
        # Otherwise, just display the form with pre-filled data
        form = BookForm(instance=book)

    return render(request, 'update_book.html', {'form': form, 'book': book})
    
def import_books(request):
    if request.method == 'POST':
        form = ImportBooksForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data.get('title', '')  # This should be fine
            title = title.replace(' ', '+')  # Replace spaces with '+'
            author = form.cleaned_data.get('authors', '')
            publisher = form.cleaned_data.get('publisher', '')
            num_page = form.cleaned_data['num_page']  # Access number of pages
            # Construct the API URL
            api_url = f"https://frappe.io/api/method/frappe-library?page={1}&title={title}&author={author}&publisher={publisher}"
            print(api_url)
            try:
                response = requests.get(api_url)
                if response.status_code == 200:
                    api_books = response.json().get('message', [])
                    # Loop through the books and save them to the database
                    i=0
                    if len(api_books) >= num_page :
                        for i in range(num_page):
                            api_book = api_books[i]
                            print(api_book)
                            isbn=api_book.get('isbn', '')
                            if isbn:
                                book, created = Book.objects.get_or_create(
                                    isbn = isbn,
                                    defaults={
                                    'title' : api_book['title'],
                                    'authors' : api_book['authors'],
                                    'isbn' : api_book.get('isbn', ''),
                                    'publisher' : api_book.get('publisher', ''),
                                    'num_pages' : api_book["  num_pages"],
                                    'stock' :  1
                                            })
                                print("...")
                                if not created:
                                    book.stock += 1
                                    book.save()
                                    print(f"Added new book: {book.title}")  # Optional logging for debugging
                                

                        # Redirect to the book_list view after successful import
                        return redirect('book_list')  # Ensure that 'book_list' is the correct URL name for your book list view
                    else:
                        messages.error(request, "Oops, not enough books available. Please try another one")
                        return redirect('import_books')
                else:
                    error_message = f"Error: Unable to fetch data (Status Code {response.status_code})"
            except requests.exceptions.RequestException as e:
                error_message = f"Error: {str(e)}"
    else:
        form = ImportBooksForm()

    return render(request, 'import_books.html', {
        'form': form,
        'error_message': error_message if 'error_message' in locals() else None
    })


def delete_book(request, isbn):
    # Get the book with the given isbn
    book = get_object_or_404(Book, isbn=isbn)
    
    # Delete the book from the database
    book.delete()
    
    # Redirect back to the book list after deletion
    return redirect('book_list')



# ------------- MEMBERS CRUD --------------


# List all members
def member_list(request):
    members = Member.objects.all()
    return render(request, 'member_list.html', {'members': members})

# Add a new member
def add_member(request):
    if request.method == 'POST':
        form = MemberForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('member_list')
    else:
        form = MemberForm()
    return render(request, 'add_member.html', {'form': form})

# Update an existing member
def update_member(request, id):
    member = get_object_or_404(Member, id=id)
    if request.method == 'POST':
        form = MemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            return redirect('member_list')
    else:
        form = MemberForm(instance=member)
    return render(request, 'update_member.html', {'form': form, 'member': member})

# Delete a member
def delete_member(request, id):
    member = get_object_or_404(Member, id=id)
    if request.method == 'POST':
        member.delete()
        return redirect('member_list')
    return render(request, 'delete_member.html', {'member': member})



# --------------- TRANSACTION CRUD -----------------

# View the transaction log
def transaction_list(request):
    transactions = Transaction.objects.all().order_by('-issued_date')
    return render(request, 'transaction_list.html', {'transactions': transactions})

def issue_book(request):
    if request.method == 'POST':
        book_id = request.POST.get('book')
        member_id = request.POST.get('member')
        
        book = get_object_or_404(Book, id=book_id)
        member = get_object_or_404(Member, id=member_id)
        
        # Check if the book is already issued and not yet returned
        if Transaction.objects.filter(book=book, return_date__isnull=True).exists() and book.stock <= 0:
            messages.error(request, 'This book is currently issued to another member or out of stock.')
            return redirect('issue_book')

        # Check if the book has stock available
        if book.stock <= 0:
            messages.error(request, 'This book is out of stock.')
            return redirect('issue_book')
        
        # Check if the member can borrow
        if not member.can_borrow():
            messages.error(request, 'This member has exceeded the allowable debt limit.')
            return redirect('issue_book')

        # Create the transaction for issuing the book
        transaction = Transaction.objects.create(
            book=book,
            member=member,
            issued_date=timezone.now(),
        )
        
        # Reduce the stock by 1
        book.stock -= 1
        book.save()
        
        transaction.save()
        messages.success(request, f'Book "{book.title}" issued to {member.name}.')
        return redirect('transaction_list')

    # Only pass books that are not currently issued
    available_books = Book.objects.filter(transaction__return_date__isnull=False) | Book.objects.filter(transaction__isnull=True)

    context = {
        'books': available_books,
        'members': Member.objects.all(),
    }
    return render(request, 'issue_book.html', context)


# Return a book from a member
def return_book(request, id):
    transaction = get_object_or_404(Transaction, id=id)
    if request.method == 'POST':
        form = ReturnBookForm(request.POST, instance=transaction)
        if form.is_valid():
            return_date = form.cleaned_data['return_date']
            transaction.return_date = return_date
            # Calculate the rent fee (basic example)
            days_issued = (return_date - transaction.issued_date).days
            transaction.rent_fee = days_issued * 10  # Rs.10 per day rent fee
            transaction.save()

            # Add the rent fee to member's debt
            transaction.member.debt += transaction.rent_fee
            transaction.member.save()

            return redirect('transaction_list')
    else:
        form = ReturnBookForm(instance=transaction)
    return render(request, 'return_book.html', {'form': form, 'transaction': transaction})