from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.http import JsonResponse
from .forms import CustomUserCreationForm, ForgotPasswordForm, CustomAuthenticationForm, TransactionForm
from .models import Transaction, Budget, Goal, Investment, Blog
from django.http import JsonResponse
from decimal import Decimal
import json, random
from django.db.models import Sum

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')

User = get_user_model()

def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            new_password = form.cleaned_data['new_password']

            try:
                user = User.objects.get(username=username)
                user.set_password(new_password)
                user.save()
                messages.success(request, "Password reset successful! Please log in with your new password.")
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, "User not found.")
    else:
        form = ForgotPasswordForm()
    return render(request, 'forgot_password.html', {'form': form})

def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug)
    return render(request, "blog_detail.html", {"blog": blog})

@login_required
def dashboard(request):
    user = request.user

    # --- Profile Image ---
    if 'profile_image' not in request.session:
        image_choices = [
            "pic1.webp", "pic2.jpeg", "pic3.jpeg", "pic4.webp", "pic5.jpg",
            "pic6.jpeg", "pic7.webp", "pic8.jpg", "pic9.jpg", "pic10.jpg"
        ]
        selected_pic = random.choice(image_choices)
        request.session['profile_image'] = selected_pic
    else:
        selected_pic = request.session['profile_image']

    # --- Transactions ---
    transactions = Transaction.objects.filter(user=user)
    total_income = sum(t.amount for t in transactions if t.type.lower() == 'income')
    total_expense = sum(t.amount for t in transactions if t.type.lower() == 'expense')
    balance = total_income - total_expense

    # --- Investments ---
    investments = Investment.objects.filter(user=user)
    total_invested = sum(inv.quantity * inv.purchase_price for inv in investments)
    total_current = sum(inv.current_value for inv in investments)
    net_gain_loss = total_current - total_invested

    investment_chart_data = json.dumps([
        {"name": inv.name, "value": float(inv.current_value)}
        for inv in investments
    ])

    # --- Goals ---
    goals_data = []
    for g in Goal.objects.filter(user=user):
        progress = round((g.saved_amount / g.target_amount) * 100, 2) if g.target_amount else 0
        goals_data.append({
            "name": g.name,
            "saved_amount": float(g.saved_amount),
            "target_amount": float(g.target_amount),
            "progress": progress
        })

    # --- Budgets ---
    budgets_data = []
    for b in Budget.objects.filter(user=user):
        spent = sum(
            t.amount for t in Transaction.objects.filter(
                user=user, category=b.category, type__iexact="Expense"
            )
        )
        percent = round((spent / b.limit) * 100, 2) if b.limit else 0
        exceeded = spent > b.limit if b.limit else False
        budgets_data.append({
            "category": b.category,
            "limit": float(b.limit),
            "spent": float(spent),
            "percent": percent,
            "exceeded": exceeded
        })

    # --- Blogs (Latest 2) ---
    blogs = Blog.objects.all()[:2]

    context = {
        "user": user,
        "transactions": transactions,
        "balance": balance,
        "total_income": total_income,
        "total_expense": total_expense,
        "investments": investments,
        "total_invested": total_invested,
        "total_current": total_current,
        "net_gain_loss": net_gain_loss,
        "investment_chart_data": investment_chart_data,
        "goals": goals_data,
        "budgets": budgets_data,
        "selected_pic": selected_pic,
        "blogs": blogs,
    }

    return render(request, "dashboard.html", context)

@login_required
@require_GET
def dashboard_data(request):
    transactions = Transaction.objects.filter(user=request.user)
    total_income = sum(t.amount for t in transactions if t.type.lower() == 'income')
    total_expense = sum(t.amount for t in transactions if t.type.lower() == 'expense')
    balance = total_income - total_expense

    latest_transactions = list(
        transactions.order_by('-date')[:5].values('date', 'type', 'category', 'amount', 'description')
    )

    return JsonResponse({
        'balance': float(balance),
        'total_income': float(total_income),
        'total_expense': float(total_expense),
        'transactions': latest_transactions
    })

@login_required
def transactions_view(request):
    import json
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    form = TransactionForm()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.content_type == 'application/json':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)

        if data.get('action') == 'delete':
            delete_id = data.get('delete_id')
            transaction = get_object_or_404(Transaction, id=delete_id, user=request.user)
            transaction.delete()

            transactions = Transaction.objects.filter(user=request.user)
            total_income = sum(t.amount for t in transactions.filter(type__iexact='Income'))
            total_expense = sum(t.amount for t in transactions.filter(type__iexact='Expense'))
            balance = total_income - total_expense

            return JsonResponse({
                'status': 'deleted',
                'message': 'Transaction deleted successfully!',
                'balance': float(balance),
                'income': float(total_income),
                'expense': float(total_expense),
            })

    if request.method == 'POST':
        transaction_id = request.POST.get('transaction_id')
        if transaction_id:
            transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
            form = TransactionForm(request.POST, instance=transaction)
        else:
            form = TransactionForm(request.POST)

        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()

            transactions = Transaction.objects.filter(user=request.user)
            total_income = sum(t.amount for t in transactions.filter(type__iexact='Income'))
            total_expense = sum(t.amount for t in transactions.filter(type__iexact='Expense'))
            balance = total_income - total_expense

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Transaction saved successfully!',
                    'balance': float(balance),
                    'income': float(total_income),
                    'expense': float(total_expense),
                })

            return redirect('transactions')

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

    return render(request, 'transactions.html', {
        'transactions': transactions,
        'form': form
    })

@login_required
def budget(request):
    user = request.user

    if request.method == "POST" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = json.loads(request.body)
        action = data.get('action')

        if action == 'add':
            category = data.get('category')
            limit = data.get('limit')
            if category and limit:
                Budget.objects.create(user=user, category=category, limit=Decimal(limit))
                return JsonResponse({'status': 'success'})
            return JsonResponse({'status': 'error', 'message': 'Invalid data'})

        if action == 'delete':
            bid = data.get('id')
            try:
                budget_obj = Budget.objects.get(id=bid, user=user)
                budget_obj.delete()
                return JsonResponse({'status': 'deleted'})
            except Budget.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Budget not found'})

        if action == 'update':
            bid = data.get('id')
            add_amount = data.get('spent_amount')
            if add_amount:
                try:
                    budget_obj = Budget.objects.get(id=bid, user=user)
                    Transaction.objects.create(
                        user=user,
                        category=budget_obj.category,
                        type='Expense',
                        amount=Decimal(add_amount),
                        date='2025-10-23'  
                    )
                    return JsonResponse({'status': 'updated'})
                except Budget.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': 'Budget not found'})

        return JsonResponse({'status': 'error', 'message': 'Unknown action'})

    budgets_list = []
    for b in Budget.objects.filter(user=user):
        spent = b.spent  
        budgets_list.append({
            'id': b.id,
            'category': b.category,
            'limit': b.limit,
            'spent': spent,
            'percent': b.percent,
            'exceeded': spent > b.limit,
        })

    return render(request, 'budget.html', {'budgets': budgets_list})

def investments(request):
    user = request.user

    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        data = json.loads(request.body)
        action = data.get("action")

        if action == "add":
            name = data.get("name")
            type_ = data.get("type")
            quantity = float(data.get("quantity", 0))
            purchase_price = float(data.get("purchase_price", 0))
            current_price = float(data.get("current_price", 0))
            Investment.objects.create(
                user=user,
                name=name,
                type=type_,
                quantity=quantity,
                purchase_price=purchase_price,
                current_price=current_price
            )
            return JsonResponse({"status": "success"})

        if action == "update":
            inv_id = data.get("id")
            current_price = float(data.get("current_price", 0))
            inv = Investment.objects.get(id=inv_id, user=user)
            inv.current_price = current_price
            inv.save()
            return JsonResponse({"status": "updated"})

        if action == "delete":
            inv_id = data.get("id")
            Investment.objects.filter(id=inv_id, user=user).delete()
            return JsonResponse({"status": "deleted"})

    investments_list = Investment.objects.filter(user=user)
    chart_data = [
        {"name": inv.name, "profit_percentage": inv.profit_percentage}
        for inv in investments_list
    ]

    return render(request, "investments.html", {
        "investments": investments_list,
        "chart_data": json.dumps(chart_data)
    })

@login_required
def goals(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = json.loads(request.body)
        action = data.get('action')

        if action == 'add':
            name = data.get('name')
            target_amount = Decimal(data.get('target_amount', 0))
            saved_amount = Decimal(data.get('saved_amount', 0))
            Goal.objects.create(user=request.user, name=name, target_amount=target_amount, saved_amount=saved_amount)
            return JsonResponse({'status': 'success'})

        elif action == 'delete':
            goal_id = data.get('id')
            goal = get_object_or_404(Goal, id=goal_id, user=request.user)
            goal.delete()
            return JsonResponse({'status': 'deleted'})

        elif action == 'update':
            goal_id = data.get('id')
            try:
                added_amount = Decimal(data.get('added_amount', 0))
            except:
                added_amount = Decimal(0)

            if added_amount <= 0:
                return JsonResponse({'status': 'error', 'message': 'Invalid amount'}, status=400)

            goal = get_object_or_404(Goal, id=goal_id, user=request.user)
            goal.saved_amount += added_amount
            goal.save()
            return JsonResponse({'status': 'updated', 'saved_amount': float(goal.saved_amount)})

    goals_list = Goal.objects.filter(user=request.user)
    goals_data = []
    for g in goals_list:
        progress = 0
        if g.target_amount > 0:
            progress = min(int((g.saved_amount / g.target_amount) * 100), 100)
        goals_data.append({
            'id': g.id,
            'name': g.name,
            'saved_amount': float(g.saved_amount),
            'target_amount': float(g.target_amount),
            'progress': progress
        })

    return render(request, 'goals.html', {'goals': goals_data})

@login_required
def reports(request):
    user = request.user

    category_data = (
        Transaction.objects
        .filter(user=user, type='Expense')
        .values('category')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )
    category_chart = [
        {"category": c["category"], "total": float(c["total"])}
        for c in category_data
    ]

    month_data = (
        Transaction.objects
        .filter(user=user)
        .extra(select={'month': "strftime('%%Y-%%m', date)"})
        .values('month', 'type')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    monthly_chart = {}
    for entry in month_data:
        month = entry['month']
        typ = entry['type']
        if month not in monthly_chart:
            monthly_chart[month] = {'Income': 0, 'Expense': 0}
        monthly_chart[month][typ] = float(entry['total'])

    months = list(monthly_chart.keys())
    income_values = [monthly_chart[m]['Income'] for m in months]
    expense_values = [monthly_chart[m]['Expense'] for m in months]

    context = {
        'category_chart': json.dumps(category_chart),
        'months': json.dumps(months),
        'income_values': json.dumps(income_values),
        'expense_values': json.dumps(expense_values),
    }

    return render(request, "reports.html", context)

@login_required
def add_expense(request):
    return redirect('transactions')
