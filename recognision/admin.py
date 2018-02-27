from django.contrib import admin

from .models import Algorithm, History

@admin.register(Algorithm)
class AlgorithmAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Algorithm._meta.fields]

    class Meta:
        model = Algorithm


@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in History._meta.fields]

    class Meta:
        model = History