from blog import app
from flask import render_template

#出来页面404错误
@app.errorhandler(404)  
def page_not_found(e):
    # user = User.query.first()
    return render_template('errors/404.html'), 404
