from django.db import models
from django.conf import settings

class Company(models.Model):
    company_name = models.CharField(max_length=255,)
    symbol = models.CharField(max_length=20,unique=True,)
    scripcode = models.CharField(max_length=20,unique=True)
    class Meta:
        indexes = [
            models.Index(fields=['symbol']),                          
            models.Index(fields=['company_name']),                    
            models.Index(fields=['scripcode']),                       
        ]
    def __str__(self):
        return f"{self.symbol} — {self.company_name}"


class Watchlist(models.Model):
    user    = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,)
    company = models.ForeignKey(Company,on_delete=models.CASCADE,)
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'company') 
    def __str__(self):
        return f"{self.user.username} ↔ {self.company.symbol}"
