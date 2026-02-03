from django import template

register = template.Library()


@register.filter(name='has_all_groups')
def has_all_groups(user, group_names):
    groups = [g.strip() for g in group_names.split(',')]
    return all(user.groups.filter(name=g).exists() for g in groups)


@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


@register.filter(name='has_any_group')
def has_any_group(user, group_names):
    groups = [g.strip() for g in group_names.split(',')]
    return user.groups.filter(name__in=groups).exists()
