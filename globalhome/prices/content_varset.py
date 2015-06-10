# coding: utf-8
from content.TemplateVars import Variable, VarValue
from django.utils.translation import ugettext_lazy as _
import log
from prices.models import PricesGroup, Price

def GetVariables():

    class PriceVarValue(VarValue):
        def getValue(self):
            request = self.init_kwargs["request"]
            user = request.user
            price = self.kwargs["price"]
            is_user_price = self.kwargs["is_user_price"]
            
            if is_user_price:
                bac = user.get_profile().billing_account
                price = Price.objects.get(group = bac.prices_group, slug = price.slug)
            
            return price.value
    
    result = []
    for price in PricesGroup.objects.get(id = 1).price_set.all():
        result.append(
            Variable(
                "price_user_%s" % price.slug,
                u"Цена группы, которой принадлежит пользователь '%s'" % price,
                PriceVarValue(
                    price = price,
                    is_user_price = True,
                )
            ),
        )
    
    for pg in PricesGroup.objects.all():
        for price in pg.price_set.all():
            result.append(
                Variable(
                    "price_%s_%s" % (price.group.slug, price.slug),
                    u"'%s' в группе '%s'" % (price, price.group),
                    PriceVarValue(
                        price = price,
                        is_user_price = False,
                    )
                )
            )
            
    
    
    return result
