def custom_change_delete_permission(user, obj):
    return obj is None or (obj.publish_time is None and (
            user.is_superuser or user.id in obj.pages.all().values_list('admins', flat=True)
    )) and not obj.is_crontab


def custom_view_permission(user, obj):
    return obj is None or user.is_superuser or user.id in obj.pages.all().values_list('admins', flat=True)
