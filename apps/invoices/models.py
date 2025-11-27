import uuid
from django.db import models
from core.models import Organization, TimeStampedModel
from chartofaccounts.models import Account
from core.models import User

class Customer(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="customers")
    name = models.CharField(max_length=255)
    contact = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    
    class Meta:
        verbose_name = "مشتری"
        verbose_name_plural = "مشتریان"
        ordering = ("name",)

    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="products")
    sku = models.CharField(max_length=50, blank=True, null=True)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=18, decimal_places=2)
    track_inventory = models.BooleanField(default=False)

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"
        ordering = ("name",)

    def __str__(self):
        return f"{self.name} ({self.sku})" if self.sku else self.name


class Invoice(TimeStampedModel):
    STATUS_CHOICES = [
        ("draft", "پیش‌نویس"),
        ("sent", "ارسال شده"),
        ("paid", "پرداخت شده"),
        ("overdue", "معوق"),
        ("cancelled", "لغو شده"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="invoices")
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, related_name="invoices")
    invoice_number = models.CharField(max_length=50, unique=True)
    issue_date = models.DateField()
    due_date = models.DateField()
    subtotal = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "فاکتور"
        verbose_name_plural = "فاکتورها"
        ordering = ("-issue_date",)

    def __str__(self):
        return f"{self.invoice_number} - {self.customer}"


class InvoiceLine(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="lines")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name="invoice_lines")
    description = models.CharField(max_length=255, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=18, decimal_places=2)
    line_total = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    class Meta:
        verbose_name = "خط فاکتور"
        verbose_name_plural = "خطوط فاکتور"
        ordering = ("invoice",)

    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.product or self.description}"

    def save(self, *args, **kwargs):
        # محاسبه خودکار line_total
        self.line_total = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        # بروزرسانی subtotal و total فاکتور
        invoice = self.invoice
        invoice.subtotal = sum(line.line_total for line in invoice.lines.all())
        invoice.total = invoice.subtotal + invoice.tax
        invoice.save()
