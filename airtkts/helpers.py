import collections


def has_model_permissions(entity, perms, instance):

    if not isinstance(perms, list):
        perms = [perms, ]

    if isinstance(instance, collections.Iterable):
        instances = instance
    else:
        instances = [instance, ]

    for perm in perms:
        for instance in instances:
            # Check if Model has permissions check
            if hasattr(instance, 'has_%s_permissions' % perm):
                # Check if the User can edit this item
                if getattr(instance, 'has_%s_permissions' % perm)(entity):
                    return True

    return False


def has_global_permissions(entity, model, perms, app):

    if not isinstance(perms, list):
        perms = [perms, ]

    for p in perms:
        if not entity.has_perm("%s.%s_%s" % (app, p, model.__name__.lower())):
            return False
        return True