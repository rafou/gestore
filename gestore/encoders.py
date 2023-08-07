from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.fields.files import FieldFile


class GestoreEncoder(DjangoJSONEncoder):
    """
    A custom encoder that allows us to serialize unserializable fields
    like `FieldFile` and `Country` objects.

    For each field you are trying to encode, make sure the return value is
    appropriate to be imported back again.
    """
    def default(self, o, *args, **kwargs):
        if isinstance(o, FieldFile):
            return o.name

        try:
            from django_countries.fields import Country
            if isinstance(o, Country):
                return o.code
        except ImportError:
            pass

        return super(GestoreEncoder, self).default(o)
