# From
# https://realpython.com/flask-connexion-rest-api/
# https://realpython.com/flask-connexion-rest-api-part-2/
# https://realpython.com/flask-connexion-rest-api-part-3/
# https://www.sitepoint.com/hosted-postgresql-with-heroku/


from flask import render_template, redirect, url_for, session
import connexion
from authlib.integrations.flask_client import OAuth
import os
from datetime import timedelta
from dotenv import load_dotenv

# Create the application instance
app = connexion.FlaskApp(__name__, specification_dir='./')

# Read the swagger.yml file to configure the endpoints
app.add_api('swagger.yml')
# app.config.update('SESSION_COOKIE_NAME' = 'google-login-session')
# Session config
load_dotenv(dotenv_path='./config/.env')
app.app.secret_key = os.getenv('APP_SECRET_KEY')

app.app.config['SESSION_COOKIE_NAME'] = 'google-login-session'
app.app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
# print(os.getenv('GOOGLE_CLIENT_ID'))
# print(os.getenv('GOOGLE_CLIENT_SECRET'))
# print(os.getenv('APP_SECRET_KEY'))

# oAuth Setup
oauth = OAuth(app.app)
google = oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    # This is only needed if using openId to fetch user info
    client_kwargs={'scope': 'openid email profile'},
)


# predictor = Predictor.get_instance()
# predictor.read_data()


# wc.make_wordcloud()

# Create a URL route in our application for "/"
@app.route('/')
# @login_required
def home():
    """
    This function just responds to the browser ULR
    localhost:5000/
    :return:        the rendered template 'home.html'
    """
    # print(session)
    # print(len(session))
    # print(type(session))
    # print(dict(session).keys())
    # print(len(dict(session)))
    # print(type(dict(session)))
    f = open('./templates/home.html', 'r')
    html = f.read()
    if 'profile' in dict(session):
        email = dict(session)['profile']['email']
        name = dict(session)['profile']['given_name']
        # print(dict(session)['profile'])
        # print('home/ {}'.format(email))
        iconMsg = '<h1> Welcome, {}! </h1>' \
                  '<div class="row">' \
                  '<div class="column"><a href = "/wc/"><img src="./static/images/home.png", height="50"/>' \
                  '</a></div>' \
                  '    <div class="column"><a href = "/u/s/Tesco/"><img src="./static/images/usage.png", height="50"/>' \
                  '</a></div>' \
                  '<div class="column"><a href = "/p/s/Tesco/"><img src="./static/images/predict.png", height="50"/>' \
                  '</a></div>' \
                  '    <div class="column"><a href = "/r/"><img src="./static/images/settings.png", height="50"/>' \
                  '</a></div>' \
                  '    <div class="column"><a href = "/logout/"><img src="./static/images/logout.png", height="50"/>' \
                  '</a></div>' \
                  '</div>'.format(name)
        html = html.replace('@@header@@', iconMsg)
    else:
        # print('replacing @@header@@')
        # print(html)
        html = html.replace('@@header@@',
                            '<a href="/login"><img src = "./static/images/google_login_white.png" height = "70"> </a>')
        # print(html)
    # return render_template('home.html')
    return html


@app.route('/login/')
def login():
    google = oauth.create_client('google')  # create the google oauth client
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)


@app.route('/authorize/')
def authorize():
    google = oauth.create_client('google')  # create the google oauth client
    token = google.authorize_access_token()  # Access token from google (needed to get user info)
    resp = google.get('userinfo')  # userinfo contains stuff u specified in the scope
    user_info = resp.json()
    user = oauth.google.userinfo()  # uses openid endpoint to fetch user info
    # Here you use the profile/user data that you got and query your database find/register the user
    # and set ur own data in the session not the profile from google
    session['profile'] = user_info
    session.permanent = True  # make the session permanent so it keeps existing after browser gets closed

    return redirect('/wc/')


@app.route('/logout/')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')


# Option 1
# background process happening without any refreshing
@app.route('/background_process_test')
def background_process_test():
    print("Hello")
    return ("nothing")


# Option 2
@app.route("/forward/", methods=['POST'])
def move_forward():
    # Moving forward code
    forward_message = "Moving Forward..."
    return render_template('home.html', forward_message=forward_message);


# Option 3
@app.route('/SomeFunction')
def SomeFunction():
    print('In SomeFunction')
    return "Nothing"


# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
