from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.conf import settings

class CustomUser(AbstractUser):
    pass

    def __str__(self):  
        return self.username

User = get_user_model()

class Blog(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200, blank=True)
    excerpt = models.TextField(max_length=300, help_text="Short preview for dashboard")
    content = models.TextField(help_text="Full blog content")
    published_date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-published_date']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Category(models.Model):
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=10, choices=[('Income', 'Income'), ('Expense', 'Expense')])

    def __str__(self):
        return f"{self.name} ({self.type})"

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('Income', 'Income'),
        ('Expense', 'Expense'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    category = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.type} - {self.category} ({self.amount})"

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=100)
    limit = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def spent(self):
        transactions = Transaction.objects.filter(user=self.user, category=self.category, type__iexact='Expense')
        return sum(t.amount for t in transactions)

    @property
    def percent(self):
        if self.limit == 0:
            return 0
        return min(int((self.spent / self.limit) * 100), 100)

    @property
    def exceeded(self):
        return self.spent_amount > self.limit

    def __str__(self):
        return f"{self.category} - {self.limit}"

class Investment(models.Model):
    INVESTMENT_TYPES = [
        ('Stock', 'Stock'),
        ('Mutual Fund', 'Mutual Fund'),
        ('Crypto', 'Crypto'),
        ('Other', 'Other'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    type = models.CharField(max_length=20, choices=INVESTMENT_TYPES)
    quantity = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    purchase_price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    current_price = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    @property
    def current_value(self):
        return self.quantity * self.current_price

    @property
    def profit_percentage(self):
        if self.purchase_price == 0:
            return 0
        return float((self.current_value - (self.purchase_price * self.quantity)) / (self.purchase_price * self.quantity) * 100)

    @property
    def gain_loss(self):
        return self.current_value - (self.purchase_price * self.quantity)

    def __str__(self):
        return f"{self.name} ({self.type})"

class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    saved_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def progress(self):
        if self.target_amount == 0:
            return 0
        return min(int((self.saved_amount / self.target_amount) * 100), 100)

    def __str__(self):
        return f"{self.name} - ₹{self.saved_amount}/₹{self.target_amount}"
