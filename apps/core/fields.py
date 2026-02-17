from django.db import models
from ulid import ULID

class ULIDField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 26)
        kwargs.setdefault('primary_key', True)
        kwargs.setdefault('editable', False)
        super().__init__(*args, **kwargs)
    
    def pre_save(self, model_instance, add):
        if add and not getattr(model_instance, self.attname):
            value = str(ULID())
            setattr(model_instance, self.attname, value)
            return value
        return super().pre_save(model_instance, add)