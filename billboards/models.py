from django.db import models

class Billboard(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='billboards/')
    sqft = models.IntegerField(help_text="Total Square Feet")
    size = models.CharField(max_length=50, help_text="Dimensions (e.g., 20x10)")
    description = models.TextField(blank=True, help_text="Detailed description of the billboard location and advantages")
    location = models.CharField(max_length=200)
    map_url = models.URLField(max_length=500, blank=True, help_text="Google Maps Embed Link or URL")
    is_available = models.BooleanField(default=True)
    price_per_month = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.title} - {self.location}"

class Booking(models.Model):
    billboard = models.ForeignKey(Billboard, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20)
    start_date = models.DateField()
    duration_months = models.IntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Booking #{self.id} - {self.customer_name}"
