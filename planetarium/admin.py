from django.contrib import admin

from planetarium.models import (
    AstronomyShow,
    ShowTheme,
    PlanetariumDome,
    ShowSession,
    Reservation,
    Ticket,
    Presenter
)

admin.site.register(AstronomyShow)
admin.site.register(ShowTheme)
admin.site.register(PlanetariumDome)
admin.site.register(ShowSession)
admin.site.register(Reservation)
admin.site.register(Ticket)
admin.site.register(Presenter)
