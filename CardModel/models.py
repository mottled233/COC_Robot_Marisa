from django.db import models


class Card(models.Model):
    card_id = models.CharField(primary_key=True, max_length=255)
    type = models.CharField(max_length=255, blank=False, default="默认")
    rare = models.CharField(max_length=255, blank=False, default="N")
    name = models.CharField(max_length=255)
    info = models.TextField(blank=True)
    chance = models.IntegerField(blank=False, default=0)
    description = models.TextField()


class UserCard(models.Model):
    user_id = models.CharField(max_length=255)
    card_id = models.CharField(max_length=255)
    count = models.IntegerField(default=1)

    class Meta:
        unique_together = ("user_id", "card_id")


class Probability(models.Model):
    type = models.CharField(max_length=255, blank=False)
    rare = models.CharField(max_length=255, blank=False)
    is_default = models.BooleanField(default=False, blank=False)
    prob = models.FloatField(blank=False)

    class Meta:
        unique_together = ("type", "rare")


class Chance(models.Model):
    user_id = models.CharField(primary_key=True, max_length=255)
    chance = models.IntegerField(default=0, blank=False)
    has_rolled = models.BooleanField(default=False, blank=False)


class SellPrice(models.Model):
    type = models.CharField(max_length=255, blank=False)
    rare = models.CharField(max_length=255, blank=False)
    price = models.FloatField(blank=False)

    class Meta:
        unique_together = ("type", "rare")



