from django.db import models

class Match(models.Model):
    date = models.DateField()
    home_team = models.CharField(max_length=100)
    away_team = models.CharField(max_length=100)
    home_score = models.IntegerField()
    away_score = models.IntegerField()
    round_name = models.CharField(max_length=100)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.home_team} {self.home_score}-{self.away_score} {self.away_team} ({self.date})"
