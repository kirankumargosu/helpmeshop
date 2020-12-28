"""
This is the people module and supports all the ReST actions for the
PEOPLE collection
"""

# System modules
from datetime import datetime as dt, date as d, timedelta as td
from InventoryPredictor.src.config import Config
import os
# 3rd party modules
from flask import make_response, abort
from Authenticator.src.decorator import login_required, is_valid_user
from InventoryPredictor.src.expenses import Expenses


def get_timestamp():
    return dt.now().strftime("%Y-%m-%d %H:%M:%S")


cfg = Config.get_instance()

htmlTemplate = '<!DOCTYPE html>' \
               '<html lang="en">' \
               '    <head>' \
               '        <title>Kiran Gosu</title>' \
               '        <meta charset="UTF-8">     ' \
               '        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1"> ' \
               '        <style>' \
               '            body, html {' \
               '               height: 100%;' \
               '                width: 100%;' \
               '                overflow-x: hidden;' \
               '                margin: 0;' \
               '                -webkit-perspective: 1000;' \
               '                font-family: "Poppins", sans-serif;' \
               '                background: #303030;' \
               '                -webkit-font-smoothing: antialiased;' \
               '            }' \
               '            .overlay {' \
               '                background: linear-gradient(to top right, #d2b48c, #000000);' \
               '                opacity: 0.9;' \
               '                position: absolute;' \
               '                top: 0;' \
               '                right: 0;' \
               '                bottom: 0;' \
               '                left: 0;' \
               '                width: 100%;' \
               '                height: 100%;' \
               '            }' \
               '            * {' \
               '                box-sizing: border-box;' \
               '                }' \
               '            .column {' \
               '                float: left;' \
               '                width: 20%;' \
               '                padding: 5px;' \
               '            }' \
               '            /* Clearfix (clear floats) */' \
               '            .row::after {' \
               '                content: "";' \
               '                clear: both;' \
               '                display: table;' \
               '            }' \
               '            h1 {' \
               '                font-weight: 300;' \
               '                line-height: inherit;' \
               '                color: #ffffff;' \
               '                font-size: 1.5em;' \
               '            }' \
               '            #home {' \
               '                display: -webkit-box;' \
               '                display: -webkit-flex;' \
               '                display: -ms-flexbox;' \
               '                display: flex;' \
               '                -webkit-box-align: center;' \
               '                -webkit-align-items: center;' \
               '                -ms-flex-align: center;' \
               '                align-items: center;' \
               '                text-align: center;' \
               '                position: relative;' \
               '            }' \
               '            .home-info {' \
               '                display: flex;' \
               '                flex-direction: column;' \
               '                justify-content: top;' \
               '                align-items: center;' \
               '                position: relative;' \
               '                z-index: 2;' \
               '                width: 100%;' \
               '                height: 100vh;' \
               '            }' \
               '            table {' \
               '                border-collapse: collapse;' \
               '                width: 95%;' \
               '                }' \
               '            th {' \
               '                text-align: left;' \
               '                padding: 3px;' \
               '                background-color:#333333;' \
               '                color:#ffffff' \
               '                }' \
               '            td {' \
               '                text-align: left;' \
               '                padding: 3px;' \
               '                color:#cccccc' \
               '               }' \
               '            table.center { ' \
               '                margin-left: auto; ' \
               '                margin-right: auto;' \
               '                }' \
               '            tr:nth-child(odd) {background-color: #595959; color:#cccccc}' \
               '        </style>' \
               '    </head>' \
               '    <body>' \
               '        <section id="home">' \
               '            <div class="overlay"></div>' \
               '            <div class="home-info">' \
               '                <h1> @@Header@@ </h1>' \
               '                @@Result@@' \
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
               '                        <a href = "/logout/">' \
               '                            <img src="/static/images/logout.png", height="50"/>' \
               '                        </a>' \
               '                    </div>' \
               '                </div>' \
               '            </div>' \
               '        </section>' \
               '    </body>' \
               '</html>'

# Data to serve with our API
PEOPLE = {
    "Farrell": {
        "fname": "Doug",
        "lname": "Farrell",
        "timestamp": get_timestamp(),
    },
    "Brockman": {
        "fname": "Kent",
        "lname": "Brockman",
        "timestamp": get_timestamp(),
    },
    "Easter": {
        "fname": "Bunny",
        "lname": "Easter",
        "timestamp": get_timestamp(),
    },
}


def curate_result(dataFrame, processType='usage', shop='', item=''):
    # print(dataFrame.columns)
    if processType == 'predict':
        dataFrame['DueDate'] = dataFrame.apply(lambda row: dt.strptime(row['DueDate'], '%Y%m%d').strftime('%d-%b-%Y'),
                                               axis=1)
    else:
        dataFrame['Date'] = dataFrame.apply(lambda row: dt.strptime(str(row['Date']), '%Y%m%d').strftime('%d-%b-%Y'),
                                            axis=1)
    if processType == 'predict':
        if shop == '' and item == '':
            header = 'Purchase due list'
        elif shop != '' and item == '':
            header = 'Purchase due list at ' + shop
        elif shop == '' and item != '':
            header = 'Purchase due for ' + item
        elif shop != '' and item != '':
            header = 'Purchase due for ' + item + ' at ' + shop
    elif processType == 'usage':
        if shop == '' and item == '':
            header = 'Items purchased'
        elif shop != '' and item == '':
            header = 'Items purchased at ' + shop
        elif shop == '' and item != '':
            header = item + '(s) purchased so far'
        elif shop != '' and item != '':
            header = item + ' (s) purchased at ' + shop

    result = dataFrame.to_html(index=False).replace('<th>1</th>', '') \
        .replace('<th></th>', '') \
        .replace(' border="1" class="dataframe"', ' class="center"') \
        .replace('Description', 'Item(s)') \
        .replace('DueDate', 'Purchase it by') \
        .replace(' style="text-align: right;"', '')
    # print(htmlTemplate.replace('@@Result@@', result))
    return htmlTemplate.replace('@@Result@@', result).replace('@@Header@@', header)


def filter_predict_window(dataFrame):
    dataFrame.dropna(inplace=True)
    # print(dataFrame[dataFrame['Description'] == 'Spinach'])
    predictWindowStart = cfg.predictWindowStart if os.environ.get('PREDICT_WINDOW_START') is None \
        else os.environ.get('PREDICT_WINDOW_START')
    predictWindowEnd = cfg.predictWindowEnd if os.environ.get('PREDICT_WINDOW_END') is None \
        else os.environ.get('PREDICT_WINDOW_END')
    vetoPredictionList = cfg.vetoPredictionList if os.environ.get('VETO_PREDICTION_LIST') is None \
        else os.environ.get('VETO_PREDICTION_LIST')
    vpl = [x.strip() for x in vetoPredictionList.lstrip(',').rstrip(',').split(',')]
    dataFrame = dataFrame[(dataFrame['DueDate'] <= (d.today() + td(days=predictWindowEnd)).strftime('%Y%m%d')) &
                          (dataFrame['DueDate'] >= (d.today() - td(days=predictWindowStart)).strftime('%Y%m%d')) &
                          (dataFrame['UsageIndex'] == -999)
                          ]
    dataFrame.sort_values(by=['DueDate'], inplace=True)
    # Remove Duplicates
    dataFrame.drop_duplicates(subset='Description', keep="first", inplace=True)

    # Remove the veto Prediction List from the dataFrame.
    dataFrame = dataFrame[~dataFrame.Description.isin(vpl)]

    return dataFrame


@login_required
@is_valid_user
def usage():
    expenses = Expenses.get_instance()
    # shopData.sort_values(by=['iDate'], ascending=False, inplace=True)
    result = expenses.data[['Date', 'Description', 'Category', 'Amount', 'Where']]
    return curate_result(result, processType='usage')


@login_required
@is_valid_user
def usage_shop(shop):
    expenses = Expenses.get_instance()
    shopData = expenses.data[expenses.data['Where'] == shop]
    # shopData.sort_values(by=['iDate'], ascending=False, inplace=True)
    result = shopData[['Date', 'Description', 'Category', 'Amount']]
    return curate_result(result, shop=shop, processType='usage')


@login_required
@is_valid_user
def usage_shop_item(shop, item):
    expenses = Expenses.get_instance()
    shopData = expenses.data[(expenses.data['Where'] == shop) & (expenses.data['Description'] == item)]
    # print(shopData)
    # shopData.sort_values(by=['iDate'], ascending=False, inplace=True)
    result = shopData[['Date', 'Description', 'Category', 'Amount']]
    return curate_result(result, shop=shop, item=item, processType='usage')


@login_required
@is_valid_user
def usage_item(item):
    expenses = Expenses.get_instance()
    shopData = expenses.data[(expenses.data['Description'] == item)]
    result = shopData[['Date', 'Description', 'Where', 'Category', 'Amount']]
    return curate_result(result, item=item, processType='usage')


@login_required
@is_valid_user
def predict():
    expenses = Expenses.get_instance()
    filteredData = filter_predict_window(expenses.data)
    result = filteredData[['Description', 'DueDate', 'Where']]
    return curate_result(result, processType='predict')


@login_required
@is_valid_user
def predict_shop(shop):
    expenses = Expenses.get_instance()
    shopData = expenses.data[(expenses.data['Where'] == shop)]
    filteredData = filter_predict_window(shopData)
    # print(filteredData)
    result = filteredData[['Description', 'DueDate']]
    return curate_result(result, shop=shop, processType='predict')


@login_required
@is_valid_user
def predict_shop_item(shop, item):
    expenses = Expenses.get_instance()
    shopData = expenses.data[(expenses.data['Where'] == shop) & (expenses.data['Description'] == item)]
    filteredData = filter_predict_window(shopData)
    result = filteredData[['Description', 'DueDate']]
    return curate_result(result, shop=shop, item=item, processType='predict')


@login_required
@is_valid_user
def predict_item(item):
    expenses = Expenses.get_instance()
    shopData = expenses.data[(expenses.data['Description'] == item)]
    filteredData = filter_predict_window(shopData)
    result = filteredData[['Description', 'DueDate']]
    return curate_result(result, item=item, processType='predict')


def matha():
    expenses = Expenses.get_instance()
    data = expenses.data
    return None


def read_all():
    """
    This function responds to a request for /api/people
    with the complete lists of people

    :return:        json string of list of people
    """
    # Create the list of people from our data
    return [PEOPLE[key] for key in sorted(PEOPLE.keys())]


def read_one(lname):
    """
    This function responds to a request for /api/people/{lname}
    with one matching person from people

    :param lname:   last name of person to find
    :return:        person matching last name
    """
    # Does the person exist in people?
    if lname in PEOPLE:
        person = PEOPLE.get(lname)

    # otherwise, nope, not found
    else:
        abort(
            404, "Person with last name {lname} not found".format(lname=lname)
        )

    return person


def create(person):
    """
    This function creates a new person in the people structure
    based on the passed in person data

    :param person:  person to create in people structure
    :return:        201 on success, 406 on person exists
    """
    lname = person.get("lname", None)
    fname = person.get("fname", None)

    # Does the person exist already?
    if lname not in PEOPLE and lname is not None:
        PEOPLE[lname] = {
            "lname": lname,
            "fname": fname,
            "timestamp": get_timestamp(),
        }
        return make_response(
            "{lname} successfully created".format(lname=lname), 201
        )

    # Otherwise, they exist, that's an error
    else:
        abort(
            406,
            "Person with last name {lname} already exists".format(lname=lname),
        )


def update(lname, person):
    """
    This function updates an existing person in the people structure

    :param lname:   last name of person to update in the people structure
    :param person:  person to update
    :return:        updated person structure
    """
    # Does the person exist in people?
    if lname in PEOPLE:
        PEOPLE[lname]["fname"] = person.get("fname")
        PEOPLE[lname]["timestamp"] = get_timestamp()

        return PEOPLE[lname]

    # otherwise, nope, that's an error
    else:
        abort(
            404, "Person with last name {lname} not found".format(lname=lname)
        )


def delete(lname):
    """
    This function deletes a person from the people structure

    :param lname:   last name of person to delete
    :return:        200 on successful delete, 404 if not found
    """
    # Does the person to delete exist?
    if lname in PEOPLE:
        del PEOPLE[lname]
        return make_response(
            "{lname} successfully deleted".format(lname=lname), 200
        )

    # Otherwise, nope, person to delete not found
    else:
        abort(
            404, "Person with last name {lname} not found".format(lname=lname)
        )