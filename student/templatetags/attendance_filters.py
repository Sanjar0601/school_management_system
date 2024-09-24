from django import template

register = template.Library()

@register.filter
def check_attendance(attendance_records, args):
    student_id, date = args.split(',')
    record = attendance_records.filter(student_id=student_id, date=date).first()
    return record.status if record else '-'

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)