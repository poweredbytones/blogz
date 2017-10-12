from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:123456@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True

app.secret_key = 'muchSecrets'

db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(256))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/')
def index():
    return render_template('blog.html')

@app.route('/blog', methods=['GET'])
def blog():

  if request.args:
    id = request.args.get("id")
    blog = Blog.query.get(id)

    return render_template('blog-entry.html', title="Build A Blog", blog=blog)

  else:
    blogs = Blog.query.all()

    return render_template('blog.html', blogs=blogs)

    
@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    print("XX")
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        
        print(title," ",body)

        if not title or not body:
            flash("Please fill out all fields.")
            return redirect('/newpost')
        

        else:
             blog = Blog(title, body) 
             db.session.add(blog)
             db.session.commit()
             return redirect('/blog?id='+str(blog.id))

    return render_template('newpost.html')



if __name__ == '__main__':
    app.run()