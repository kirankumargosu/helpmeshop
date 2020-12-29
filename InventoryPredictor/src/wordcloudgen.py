from wordcloud import (WordCloud, get_single_color_func)
import matplotlib
import matplotlib.pyplot as plt
from InventoryPredictor.src.config import Config
from InventoryPredictor.src.predictor import Predictor
from InventoryPredictor.src.expenses import Expenses
from Authenticator.src.decorator import login_required, is_valid_user
import io
import os
import base64

cfg = Config.get_instance()
ex = Expenses.get_instance()
htmlTemplate = '<!DOCTYPE html>' \
               '<html lang="en">' \
               '    <head>' \
               '        <title>Help me Shop!</title>' \
               '        <meta charset="UTF-8">     ' \
               '        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1"> ' \
               '        <style>' \
               '        body, html {' \
               '            height: 100%;' \
               '            width: 100%;' \
               '            overflow-x: hidden;' \
               '            margin: 0;' \
               '            -webkit-perspective: 1000;' \
               '            font-family: "Poppins", sans-serif;' \
               '            background: #303030;' \
               '            -webkit-font-smoothing: antialiased;' \
               '        }' \
               '        .overlay {' \
               '            background: linear-gradient(to top right, #d2b48c, #000000);' \
               '            opacity: 0.9;' \
               '            position: absolute;' \
               '            top: 0;' \
               '            right: 0;' \
               '            bottom: 0;' \
               '            left: 0;' \
               '            width: 100%;' \
               '            height: 100%;' \
               '        }' \
               '            * {' \
               '                box-sizing: border-box;' \
               '                }' \
               '            .column {' \
               '                float: left;' \
               '                width: 16%;' \
               '                padding: 5px;' \
               '            }' \
               '            /* Clearfix (clear floats) */' \
               '            .row::after {' \
               '                content: "";' \
               '                clear: both;' \
               '                display: table;' \
               '            }' \
               '        h1 {' \
               '            font-weight: 300;' \
               '            line-height: inherit;' \
               '            color: #ffffff;' \
               '            font-size: 1.5em;' \
               '        }' \
               '        #home {' \
               '            display: -webkit-box;' \
               '            display: -webkit-flex;' \
               '            display: -ms-flexbox;' \
               '            display: flex;' \
               '            -webkit-box-align: center;' \
               '            -webkit-align-items: center;' \
               '            -ms-flex-align: center;' \
               '            align-items: center;' \
               '            text-align: center;' \
               '            position: relative;' \
               '        }' \
               '        .home-info {' \
               '            display: flex;' \
               '            flex-direction: column;' \
               '            justify-content: top;' \
               '            align-items: center;' \
               '            position: relative;' \
               '            z-index: 2;' \
               '            width: 100%;' \
               '            height: 100vh;' \
               '        }' \
               '        </style>' \
               '    </head>' \
               '    <body>' \
               '        <section id="home">' \
               '            <div class="overlay"></div>' \
               '            <div class="home-info">' \
               '                <h1> Glance </h1>' \
               '                <img src="data:image/png;base64, @@WordCloudImage@@" height="500">' \
               '                <div class="row">' \
               '                    <div class="column">' \
               '                        <a href = "/wc/">' \
               '                            <img src="/static/images/home.png", height="50"/>' \
               '                        </a>' \
               '                    </div>' \
               '                    <div class="column">' \
               '                        <a href = "/u/s/Tesco/">' \
               '                            <img src="/static/images/usage.png", height="50"/>' \
               '                        </a>' \
               '                    </div>' \
               '                    <div class="column">' \
               '                        <a href = "/p/s/Tesco/">' \
               '                            <img src="/static/images/predict.png", height="50"/>' \
               '                        </a>' \
               '                    </div>' \
               '                    <div class="column">' \
               '                        <a href = "/r/">' \
               '                            <img src="/static/images/settings.png", height="50"/>' \
               '                        </a>' \
               '                    </div>' \
               '                    <div class="column">' \
               '                        <a href = "https://github.com/kirankumargosu/helpmeshop/">' \
               '                            <img src="/static/images/forkme.png", height="50"/>' \
               '                        </a>' \
               '                    </div>' \
               '                    <div class="column">' \
               '                        <a href = "/logout/">' \
               '                            <img src="/static/images/logout.png", height="50"/>' \
               '                        </a>' \
               '                    </div>' \
               '                </div>' \
               '            </div>' \
               '        </section>' \
               '    </body>' \
               '</html>'


# '    <h3 align="center"; style="color:#cccccc"> @@Header@@ </h3>' \
# '        <img src="data:image/png;base64, @@WordCloudImage@@" height="550">' \


@login_required
@is_valid_user
def main():
    if ex.data is None:
        predictor = Predictor.get_instance()
        predictor.read_data()
    if ex.wordCloud is None:
        ex.wordCloud = make_wordcloud()
    return htmlTemplate \
        .replace('@@WordCloudImage@@', ex.wordCloud.decode('utf-8')) \
        .replace('@@Header@@', 'Glance')


class SimpleGroupedColorFunc(object):
    """Create a color function object which assigns EXACT colors
       to certain words based on the color to words mapping

       Parameters
       ----------
       color_to_words : dict(str -> list(str))
         A dictionary that maps a color to the list of words.

       default_color : str
         Color that will be assigned to a word that's not a member
         of any value from color_to_words.
    """

    def __init__(self, color_to_words, default_color):
        self.word_to_color = {word: color
                              for (color, words) in color_to_words.items()
                              for word in words}

        self.default_color = default_color

    def __call__(self, word, **kwargs):
        return self.word_to_color.get(word, self.default_color)


class GroupedColorFunc(object):
    """Create a color function object which assigns DIFFERENT SHADES of
       specified colors to certain words based on the color to words mapping.

       Uses wordcloud.get_single_color_func

       Parameters
       ----------
       color_to_words : dict(str -> list(str))
         A dictionary that maps a color to the list of words.

       default_color : str
         Color that will be assigned to a word that's not a member
         of any value from color_to_words.
    """

    def __init__(self, color_to_words, default_color):
        self.color_func_to_words = [
            (get_single_color_func(color), set(words))
            for (color, words) in color_to_words.items()]

        self.default_color_func = get_single_color_func(default_color)

    def get_color_func(self, word):
        """Returns a single_color_func associated with the word"""
        try:
            color_func = next(
                color_func for (color_func, words) in self.color_func_to_words
                if word in words)
        except StopIteration:
            color_func = self.default_color_func

        return color_func

    def __call__(self, word, **kwargs):
        return self.get_color_func(word)(word, **kwargs)


def fig_to_base64(fig):
    img = io.BytesIO()
    fig.savefig(img, format='png', bbox_inches='tight', pad_inches=0)
    img.seek(0)
    return base64.b64encode(img.getvalue())


def make_wordcloud():
    stopCategories = os.environ.get('STOP_CATEGORIES_FROM_CLOUD')
    if stopCategories is None:
        stopCategories = 'Utilities, Rent, Others'
    stopCategoriesList = [x.strip() for x in stopCategories.lstrip(',').rstrip(',').split(',')]
    description = ex.data[~ex.data['Category'].isin(stopCategoriesList)]['Description'].value_counts()
    text = '\t'.join([str(elem) for elem
                      in ex.data[~ex.data['Category'].isin(stopCategoriesList)]['Description'].to_list()])

    highest = 30 * description.max() / 100
    medium = 10 * description.min() / 100
    high = description.where(description >= highest).dropna().index.tolist()
    med = description.where((medium < description) & (description < highest)).dropna().index.tolist()
    low = description.where(description <= medium).dropna().index.tolist()
    high = [x.lower() for x in high]
    med = [x.lower() for x in med]
    low = [x.lower() for x in low]

    wc = WordCloud(background_color='black',
                   width=600,
                   height=1500,
                   collocations=True,
                   max_font_size=90).generate(text.lower())

    color_to_words = {'#FFFF00': high,
                      '#FF0000': med,
                      '#0000FF': low}
    default_color = '#00FF00'
    # Create a color function with single tone
    # grouped_color_func = SimpleGroupedColorFunc(color_to_words, default_color)

    # Create a color function with multiple tones
    grouped_color_func = GroupedColorFunc(color_to_words, default_color)
    # Apply our color function
    wc.recolor(color_func=grouped_color_func)
    # To stop Python Rocketship icon
    matplotlib.use('Agg')
    # Plot
    plt.figure(figsize=(10, 8))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis("off")
    encoded = fig_to_base64(plt)
    plt.close()
    return encoded
