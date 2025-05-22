from django.db import models
from django.conf import settings

class Company(models.Model):
    company_name = models.CharField(max_length=255,)
    symbol = models.CharField(max_length=20,null=True)
    scripcode = models.CharField(max_length=20,null=True)
    co_code = models.IntegerField( primary_key=True)
    class Meta:
        indexes = [
            models.Index(fields=['symbol']),                          
            models.Index(fields=['company_name']),                    
            models.Index(fields=['scripcode']),
        ]
    def __str__(self):
        return f"{self.symbol} — {self.company_name}"

class finalcial(models.Model):
    id = models.IntegerField(primary_key=True)
    ttm_ason = models.IntegerField()
    pe = models.FloatField()
    roe_ttm = models.FloatField()   
    company_id = models.ForeignKey(Company,to_field='co_code',on_delete=models.CASCADE)


class Watchlist(models.Model):
    user    = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,)
    company = models.ForeignKey(Company,on_delete=models.CASCADE,)
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'company') 
    def __str__(self):
        return f"{self.user.username} ↔ {self.company.symbol}"
