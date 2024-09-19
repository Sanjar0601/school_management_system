from django import template

register = template.Library()

@register.simple_tag
def get_attendance(attendance, date):
    return attendance.get(date, '')