# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
from flask import render_template, flash, redirect, url_for, Blueprint, Response
from flask_login import login_user, logout_user, login_required, current_user

from bluelog.models import Admin
from bluelog.forms import LoginForm
from bluelog.utils import redirect_back


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login() -> str | Response:
    if current_user.is_authenticated:
        return redirect(url_for("blog.index"))

    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.first()
        if admin:
            if form.username.data == admin.username and admin.validate_password(
                form.password.data
            ):
                login_user(admin, form.remember.data)
                flash("Welcome back.", "info")
                return redirect_back()
            flash("Invalid username or password.", "warning")
        else:
            flash("No account.", "warning")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout() -> Response:
    logout_user()

    flash("Logout success.", "info")
    return redirect_back()
