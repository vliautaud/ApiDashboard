from django import template
import datetime
register = template.Library()

@register.simple_tag
def ecart_date(ddeb,dfin):
    if ddeb==None or dfin==None :
        return "S/O"
    else :
        ecart_date=dfin-ddeb
        return str(round(ecart_date.total_seconds(),2)) + " secs"
