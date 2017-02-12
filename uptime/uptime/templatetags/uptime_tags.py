from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """ Retorna un atributo de un diccionario.
        Permite usar variables como nombres de atributo
    """

    return dictionary.get(key)
