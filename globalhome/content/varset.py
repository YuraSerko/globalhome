# coding: utf-8
from content.TemplateVars import Variable, VarValue
from content.views import  pannel_construct
from account.content_varset import GetVariables as gv


def GetVariables():

    class ContentVarValue(VarValue):
       
        def getValue(self):
            option = self.kwargs.get("option")
            request = self.init_kwargs["request"]
            if   option == "buttons_panel_description":
                pannel = pannel_construct(request) 
                return pannel
                            
    result = [
       
        Variable(
            "buttons_panel_description",
            u"набор кнопок страницы Описание",
            ContentVarValue(option = "buttons_panel_description")
        ),
       ]

    return result




