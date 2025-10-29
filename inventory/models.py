from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=200, unique=True)
    vat_id = models.CharField(max_length=32, blank=True)  # NIP opcjonalnie
    city = models.CharField(max_length=120, blank=True)
    address = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Firma"
        verbose_name_plural = "Firmy"

    def __str__(self):
        return self.name


class Employee(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="employees")
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    email = models.EmailField(blank=True)
    position = models.CharField(max_length=120, blank=True)
    phone_number = models.CharField(max_length=32, blank=True)  # <-- DODANE POLE

    class Meta:
        unique_together = ("company", "email")
        verbose_name = "Pracownik"
        verbose_name_plural = "Pracownicy"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Computer(models.Model):
    BRAND_CHOICES = [
        ("Dell", "Dell"), ("HP", "HP"), ("Lenovo", "Lenovo"),
        ("Apple", "Apple"), ("Acer", "Acer"), ("Asus", "Asus"),
        ("Other", "Other"),
    ]
    name = models.CharField(max_length=200)  # np. LAP-00123
    model = models.CharField(max_length=200)
    brand = models.CharField(max_length=50, choices=BRAND_CHOICES, default="Other")
    service_tag = models.CharField(max_length=120, unique=True)
    assigned_to = models.ForeignKey("Employee", on_delete=models.SET_NULL, null=True, blank=True, related_name="computers")
    purchase_date = models.DateField(null=True, blank=True)
    warranty_end = models.DateField(null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="computers", null=True, blank=True)
    assigned_to = models.ForeignKey("Employee", on_delete=models.SET_NULL, null=True, blank=True, related_name="computers")

    class Meta:
        verbose_name = "Komputer"
        verbose_name_plural = "Komputery"

    def __str__(self):
        return f"{self.name} / {self.service_tag}"


class ServiceAction(models.Model):
    computer = models.ForeignKey(Computer, on_delete=models.CASCADE, related_name="service_actions")
    title = models.CharField(max_length=200)  # np. Wymiana baterii
    description = models.TextField(blank=True)
    action_date = models.DateField()
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=50, choices=[("open","Otwarte"),("done","Zakończone")], default="open")

    class Meta:
        ordering = ["-action_date", "-id"]
        verbose_name = "Akcja serwisowa"
        verbose_name_plural = "Akcje serwisowe"

    def __str__(self):
        return f"{self.title} @ {self.computer}"

class ComputerReport(Computer):
    class Meta:
        proxy = True
        verbose_name = "Raport komputerów"
        verbose_name_plural = "Raporty komputerów"
