# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
from flask_mail import Mail
from flask_moment import Moment
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from flask_ckeditor import CKEditor
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension


bootstrap = Bootstrap()
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
ckeditor = CKEditor()
mail = Mail()
moment = Moment()
toolbar = DebugToolbarExtension()
migrate = Migrate()

from bluelog.models import Admin


@login_manager.user_loader
def load_user(user_id: int) -> Admin:

    return Admin.query.get(int(user_id))


login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"
