# One place to render HTMLs
import pandas as pd
import numpy as np


class HtmlHelper:
    __instance = None
    __htmlTemplate = None

    __homeImage = '/static/images/home.png'
    __usageImage = '/static/images/usage.png'
    __predictImage = '/static/images/predict.png'
    __settingsImage = '/static/images/settings.png'
    __logoutImage = '/static/images/logout.png'
    __githubImage = '/static/images/forkme.png'

    __homeDefaultEndPoint = '/wc/'
    __usageDefaultEndPoint = '/u/s/Tesco/'
    __predictDefaultEndPoint = '/p/s/Tesco/'
    __settingsDefaultEndPoint = '/r/'
    __githubUrl = 'https://github.com/kirankumargosu/helpmeshop/'
    __logoutDefaultEndPoint = '/logout/'

    __icons = pd.DataFrame(data={
        'EndPoint': [__homeDefaultEndPoint,
                     __usageDefaultEndPoint,
                     __predictDefaultEndPoint,
                     __settingsDefaultEndPoint,
                     __githubUrl,
                     __logoutDefaultEndPoint],
        'IconPath': [__homeImage,
                     __usageImage,
                     __predictImage,
                     __settingsImage,
                     __githubImage,
                     __logoutImage],
        'Inactive': [0, 0, 0, 0, 1, 1]
    },
        columns=['EndPoint', 'IconPath', 'Inactive']
    )

    endPoint = {'/wc/', __homeImage,
                '/u/s/Tesco/', __usageImage,
                '/p/s/Tesco', __predictImage,
                '/r/', __settingsImage,
                '/logout', __logoutImage}

    def __init__(self):
        if HtmlHelper.__instance is not None:
            raise Exception("I'm Singleton")
        else:
            HtmlHelper.__instance = self
            self.__cfg = HtmlHelper.get_instance()
            f = open('./templates/home.html', 'r')
            self.__htmlTemplate = f.read()

    @staticmethod
    def get_instance():
        if HtmlHelper.__instance is None:
            HtmlHelper.__instance = HtmlHelper()
        return HtmlHelper.__instance

    def get_html(self, page, userName, isActiveUser=True):
        iconHtml = '<div class="row">'
        for i in self.__icons.index:
            if self.__icons['Inactive'][i] == 1 or isActiveUser:
                iconHtml += '<div class="column"><a href="{}"><img src="{}", height="50"/></a></div>'.format(
                    self.__icons['EndPoint'][i], self.__icons['IconPath'][i])
        iconHtml += '</div>'

        if page == 'home':
            if userName is not None:
                if isActiveUser:
                    return self.__htmlTemplate \
                        .replace('@@iconPercentage@@', '16%') \
                        .replace('@@header@@', '<h1> Welcome, {}! </h1> {}'.format(userName, iconHtml))
                else:
                    return self.__htmlTemplate \
                        .replace('@@iconPercentage@@', '50%') \
                        .replace('@@header@@', '<h1> Welcome, {}! </h1> {}'.format(userName, iconHtml))
            else:
                return self.__htmlTemplate \
                    .replace('@@header@@',
                             '<a href="/login"><img src = "/static/images/google_login_white.png" height = "70"> </a>')
