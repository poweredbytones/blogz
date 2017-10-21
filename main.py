from flask import Flask, request, redirect, render_template, flash, session, make_response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


#############################################################################################
#
# TODOS:
#    
#
#
#

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:123456@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True  
db = SQLAlchemy(app)
app.secret_key = "muchSecrets"


class Blogz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.String(1500))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    pubdate = db.Column(db.DateTime)
    username = db.Column(db.String(15))
    

    def __init__(self, title, content, author_id, username, pubdate = None):
        self.title = title
        self.content = content
        self.author_id = author_id
        if pubdate is None:
            pubdate = datetime.utcnow()
        self.username = username
        self.pubdate = pubdate

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    password = db.Column(db.String(20))
    blogs = db.relationship('Blogz', backref='user')

    def __init__(self, username, password):
        self.username = username
        self.password = password

def isLoggedIn():
    logged_in = None
    logged_in = request.cookies.get('logged_in_token')
    if logged_in == None:
        result_log = False
    else:
        result_log = True
    print("*********************************************")
    print("Checking for log in status =>",result_log)
    print("*********************************************")
    return result_log
        


@app.before_request
def req_login():
    isLoggedIn()
    allowed_routes = ['login', 'signup', 'index', 'blog']
    if request.endpoint not in allowed_routes and (not isLoggedIn()):
        return redirect('/login')

@app.route('/logout')
def logout():
    isLoggedIn()
    resp = make_response(render_template('/blog.html'))
    resp.set_cookie('logged_in_token', expires=0)

    return resp

@app.route('/signup', methods=['POST','GET'])
def signup():
    isLoggedIn()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify_pw = request.form['verify_pw']
        user = User.query.filter_by(username=username).first()

        username_error=''
        password_error=''
        verify_pw_error=''


        if user:
            username_error = False
            username = ''
            flash('The username your are trying to use it already taken - Please try again.')
            return render_template("/signup.html")

        #add new user to database
        if not user and len(password) > 3 and password == verify_pw:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')

        if not user and (len(password) < 3 or len(verify_pw) < 3 ):
            flash ('Your Password is invalid')
            return render_template("/signup.html") 
        
        if not user and (len(username) < 3):
            flash ('Your username is invalid')
            return render_template("/signup.html")   

        #verify username
        if username == '' or password == '' or verify_pw == '':
            flash ('Your Username and/or Password is invalid')
            username_error = False
            password_error = False
            verify_pw_error = False

        if username == '':
            username_error = False
            username = ''
            flash('Your username should be between 5 and 20 characters.')

        elif len(username) < 3:
            username_error = False
            username = ''
            flash('Your username should be between 5 and 20 characters.')


        #verify Passwords
        if password == '':
            password_error = False
            password = ''
            flash('Please enter password')

        elif len(password) < 5:
            password_error = False
            password = ''
            flash('Your password should be between 5 and 20 characters.')

        elif password != verify_pw:
            password_error = False
            password = ''
            flash('Your passwords do not match - Please try again.')
    return render_template("/signup.html")



@app.route('/login', methods=['POST', 'GET'])
def login():
    if isLoggedIn():
        return render_template("already_logged.html")
    print(request.method)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        username_error = ""
        password_error = ""

        if user and user.password == password:
            session['username'] = username
            flash('You are logged in!')
            url ='/newpost'
            response = make_response(redirect(url))
            response.set_cookie('logged_in_token', username, max_age=60)
            return response

        elif user == '':
            username_error = False
            username = ''
            flash('Username is not filled - Try again.')


        elif not user:
            username_error = True
            username = ''
            flash ('Username does not exist')


        if password == "":
            password_error = False
            password = ''
            flash('Your password must not be left blank')

        elif user and user.password != password:
            flash('Incorrect user name or password!')
            

        return render_template("login.html", username=username, username_error=username_error, password_error=password_error)

    return render_template("login.html")


@app.route('/', methods=['POST', 'GET'])
def index():
    isLoggedIn()
    users = User.query.all()
    print(users)
    return render_template('index.html', userList=users)




# this lists blogs... it an show one users, or all blogs.
@app.route('/blog', methods=['GET'])
def blog():
    isLoggedIn()
    blogs = Blogz.query.all()
    userList = User.query.all()
    for item in userList:
        print(item.__dict__)
    print(request.args.get('user'))
    if request.args.get('user') == None:
        blogs_to_see = Blogz.query.all()
        print("blogs_to_see",blogs_to_see)
        return render_template('blog.html', title='Your Blog', blogsbyuser=blogs_to_see)
    else:
        blog_id = request.args.get('user')
        blog_post = Blogz.query.filter_by(author_id=blog_id).first()
        author_id = blog_post.author_id
        user = User.query.get(author_id)
        blogs_to_see = Blogz.query.filter_by(author_id=blog_id).all()
        return render_template('singleUser.html', title='Your Blog', blogsbyuser=blogs_to_see, user=user)

# TODO: query all blogs and return/gets the selected blog
@app.route('/selected_blog', methods=['GET'])
def selected_blog():
    isLoggedIn()
    blog_id = request.args.get('id')
    blog_post = Blogz.query.get(blog_id)
    author_id = blog_post.author_id
    user = User.query.get(author_id)

    return render_template('selected_blog.html', user_id=blog_id, blog=blog_post, user=author_id, username=user.username)



# TODO: new post and check for errors
@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    isLoggedIn()
    title_error = ''
    content_error = ''
    error_check = False

    if request.method == 'GET':
        return render_template('newpost.html', title="Add a Blog Entry")

    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_content = request.form['blog_content']
        blog_pubdate = datetime.now()
        author_id = User.query.filter_by(username=session['username']).first().id

        
        if not blog_title:
            title_error = 'No Title Writen'
            error_check = True

        
        if not blog_content:
            content_error = 'Blog content is empty!'
            error_check = True

        
        if error_check:
            return render_template('newpost.html', title_error=title_error, content_error=content_error,blog_title=blog_title, blog_content=blog_content)

        if (not title_error and not content_error):
            new_blog = Blogz(blog_title, blog_content, author_id, session['username'])
            db.session.add(new_blog)
            db.session.commit()
            blog_id = str(new_blog.id)
            return redirect('/selected_blog?id='+ blog_id)

    return render_template('newpost.html', title='New Post')


if __name__ == '__main__':
    app.run()
