from flask import Flask, render_template, request, redirect, url_for, session
from boto3.dynamodb.conditions import Key, Attr
import boto3


app = Flask(__name__)
app.secret_key = "s3838330NikhilSecretKey"


def query_users(email, dynamodb=None):
    
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    table = dynamodb.Table('login')
    response = table.query(
        KeyConditionExpression=Key('email').eq(email)
    )
    return response['Items']

def query_add_user(email, userID, password, dynamodb=None):

    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    table = dynamodb.Table('login')
    response = table.put_item(
       Item={
            'email': email,
            'user_name': userID,
            'password': password
        }
    )
    return response

@app.route('/login', methods = ['GET','POST'])
def login():

    text=''
            
    if request.method == 'POST':

        email = request.form.get('emailId')
        password = request.form.get('psw')
        
        users = query_users(email,)

        isPasswordTrue = False

        if users:
            for user in users:
                
                if user['password'] == password:
                    
                    isPasswordTrue = True
                    
                    session["email"] = user["email"]
                    session["username"] = user["user_name"]

                    return redirect(url_for('homepage'))
        
        if isPasswordTrue == False:
                text = "Invalid ID or Password"
            
    return render_template("login.html", message = text)


@app.route('/signup', methods = ['GET','POST'])
def signup():
    
    text = ''

    if request.method == 'POST':

        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')

        user = query_users(email,)

        if (user):
            text = "The email already exists"

        else:
            res = query_add_user(email, username, password)
            return redirect(url_for('login'))
    
    return render_template("signup.html", message = text)


def search_music(title, artist, year, dynamodb=None):

    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.Table('music')

    response = None

    search_items = 0
    
    if title:
        search_items += 1
    elif artist:
        search_items += 1
    elif year:
        search_items += 1

    if search_items == 3:
        response = table.scan(
            FilterExpression=
                Attr('title').eq(title) &
                Attr('artist').eq(artist) &
                Attr('year').eq(year)
        )

    if search_items == 2 :
        if title and artist:
            response = table.scan(
            FilterExpression=
                Attr('title').eq(title) &
                Attr('artist').eq(artist)
        )


        elif(title and year):
            response = table.scan(
            FilterExpression=
                Attr('title').eq(title) &
                Attr('year').eq(year)
        )


        elif(artist and year):
            response = table.scan(
            FilterExpression=
                Attr('artist').eq(artist) &
                Attr('year').eq(year)
        )


    if(search_items == 1):
        if title:
            response = table.scan(
            FilterExpression=
                Attr('title').eq(title)
        )

        elif artist:
            response = table.scan(
            FilterExpression=
                Attr('artist').eq(artist)
        )

        elif year:
            response = table.scan(
            FilterExpression=
                Attr('year').eq(year)
        )


    return response['Items']

def get_subscriptions_list(email_id, dynamodb=None):
    
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    table = dynamodb.Table('subscriptions_table')

    response = table.scan(
            FilterExpression = Attr('email_id').eq(email_id))

    return response['Items']

@app.route('/homepage', methods = ['GET','POST'])
def homepage():

    if "username" in session:
        
        songs = ''
        text = ''

        #displaying the current subscriptions of the user
        sub_songs = get_subscriptions_list(session["email"],)

        #search query songs
        if request.method == 'POST' and 'showSongs' in request.form:

            #fetching entered search query
            title = request.form.get('title')
            artist = request.form.get('artist')
            year = request.form.get('year')

            songs = search_music(title,artist,year,)

            if songs:
                text = ''
                for song in songs:
                    image_url = "https://s3838330cloudassgn2-artists-images.s3.amazonaws.com/"
                    song['img_url'] = image_url+song['img_url'].split('/')[::-1][0]
            else:
                text = "*** No result is retrieved, Please query again. ***"

        #adding a subscription
        if request.method == 'POST' and 'addSubscription' in request.form:

            dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

            table = dynamodb.Table('subscriptions_table')
            response = table.put_item(
                Item={
                    'email_id': session["email"],
                    'sub_id': session["username"]+request.form['title']+request.form['artist'],
                    'user_name': session["username"],
                    'title': request.form['title'],
                    'artist': request.form['artist'],
                    'year': request.form['year'],
                    's3_url': request.form['img_url'] 
                    }
            )

            sub_songs = get_subscriptions_list(session["email"],)

            text = request.form['title'] + " by " + request.form['artist'] + " (" + request.form['year'] + "), Successfully Subscribed!"

        #removing a subscription
        if request.method == 'POST' and 'deleteSubscription' in request.form:
            
            dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

            table = dynamodb.Table('subscriptions_table')
            response = table.delete_item(
                Key={
                    'email_id': session["email"],
                    'sub_id': session["username"]+request.form['del_title']+request.form['del_artist']
                }
            )

            sub_songs = get_subscriptions_list(session["email"],)

            text = request.form['del_title'] + " by " + request.form['del_artist'] + " (" + request.form['del_year'] + "), Successfully Un-Subscribed!"

        return render_template("homepage.html", username = session["username"], sub_songs = sub_songs, songs = songs, text = text)

    else:
        return redirect(url_for('login'))

    return render_template("homepage.html")


@app.route('/logout', methods = ['GET','POST'])
def logout():

    session.pop("username", None)
    session.pop("email", None)
    
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)