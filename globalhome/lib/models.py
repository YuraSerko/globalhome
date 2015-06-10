# coding: utf-8
from django.db import models
from django.core.exceptions import ValidationError
import cPickle as pickle

class ListModelsField(models.TextField):
    "Позволяет хранить список id-ов объектов указанной модели и прозрачно получать к ним доступ"
    __metaclass__ = models.SubfieldBase

    def __init__(self, modelClass, *args, **kwargs):
        "Первым параметром нужно передать класс модели, id которых будут хранится в этом поле"
        self.modelClass = modelClass
        if not modelClass:
            raise AttributeError(_(u"First argument must be a model class!"))
        self._comma = kwargs.get("comma", ",")
        kwargs.setdefault('null', True)
        super(ListModelsField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        "Вызывается при присваивании полю какого-то значения и при первом получении данных из базы"
        if issubclass(type(value), basestring):
            if value:
                try:
                    ids = [int(id) for id in value.split(self._comma)]
                    data = self.modelClass.objects.filter(id__in = ids)
                    result = []
                    for id in ids:
                        result.append(data.get(id = id))
                    return result
                except Exception, e:
                    raise ValidationError("Some exception in field.to_python: '%s'" % e)
            else:
                return []
        for i, val in enumerate(value):
            if not issubclass(type(val), self.modelClass):
                raise ValidationError("Item on index %s is not a subclass of %s!" % (i, self.modelClass))
        return value

    def get_db_prep_value(self, value):
        "Вызывается перед сохранением данных в базу"
        ids = ""
        for i, val in enumerate(value):
            if issubclass(type(val), self.modelClass):
                if ids:
                    ids += self._comma
                ids += str(val.id)
            else:
                raise ValidationError("Item on index %s is not a subclass of %s!" % (i, self.modelClass))
        return ids

    def get_internal_type(self):
        return "TextField"


class ParamsModel(models.Model):
    "Базовый класс для всех моделей, способных хранить в себе параметры"
    params_data = models.TextField(blank = True, null = True)

    def unpickle_params(self):
        if self.params_data:
            return pickle.loads(str(self.params_data))
        else:
            return {}

    def pickle_params(self, dict = {}):
        self.params_data = pickle.dumps(dict)

    class Meta:
        managed = False
        abstract = True



