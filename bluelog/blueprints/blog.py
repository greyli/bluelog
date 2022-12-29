# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
from flask import (
    Blueprint,
    abort,
    flash,
    url_for,
    request,
    redirect,
    current_app,
    make_response,
    render_template,
)
from flask_login import current_user

from bluelog.extensions import db
from bluelog.models import Post, Category, Comment
from bluelog.forms import CommentForm, AdminCommentForm
from bluelog.utils import redirect_back, get_page, get_per_page
from bluelog.emails import send_new_comment_email, send_new_reply_email


blog_bp = Blueprint("blog", __name__)


@blog_bp.route("/")
def index():
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        get_page(), get_per_page()
    )
    return render_template(
        "blog/index.html", pagination=pagination, posts=pagination.items
    )


@blog_bp.route("/about")
def about():
    return render_template("blog/about.html")


def _get_pagination_by_(category):
    return (
        Post.query.with_parent(category)
        .order_by(Post.timestamp.desc())
        .paginate(get_page(), get_per_page())
    )


@blog_bp.route("/category/<int:category_id>")
def show_category(category_id):
    category = Category.query.get_or_404(category_id)
    pagination = _get_pagination_by_(category)
    return render_template(
        "blog/category.html",
        category=category,
        pagination=pagination,
        posts=pagination.items,
    )


def _get_form_for_comment():
    if current_user.is_authenticated:
        form = AdminCommentForm()
        form.author.data = current_user.name
        form.email.data = current_app.config["BLUELOG_EMAIL"]
        form.site.data = url_for(".index")
    else:
        form = CommentForm()

    return form


def _get_comment_with_data_from_(form, post):
    from_admin, reviewed = (
        (False, False) if isinstance(form, CommentForm) else (True, True)
    )
    comment = Comment(
        post=post,
        reviewed=reviewed,
        body=form.body.data,
        site=form.site.data,
        email=form.email.data,
        from_admin=from_admin,
        author=form.author.data,
    )
    replied_id = request.args.get("reply")
    if replied_id:
        replied_comment = Comment.query.get_or_404(replied_id)
        comment.replied = replied_comment
        send_new_reply_email(replied_comment)

    return comment


def _add_comment_with_data_from_(form, post):
    db.session.add(_get_comment_with_data_from_(form, post))
    db.session.commit()

    if current_user.is_authenticated:  # send message based on authentication status
        flash("Comment published.", "success")
    else:
        flash("Thanks, your comment will be published after reviewed.", "info")
        send_new_comment_email(post)  # send notification email to admin


@blog_bp.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    pagination = (
        Comment.query.with_parent(post)
        .filter_by(reviewed=True)
        .order_by(Comment.timestamp.asc())
        .paginate(get_page(), get_per_page())
    )
    form = _get_form_for_comment()

    if form.validate_on_submit():
        _add_comment_with_data_from_(form)
        return redirect(url_for(".show_post", post_id=post_id))
    return render_template(
        "blog/post.html",
        form=form,
        post=post,
        pagination=pagination,
        comments=pagination.items,
    )


@blog_bp.route("/reply/comment/<int:comment_id>")
def reply_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    if not comment.post.can_comment:
        flash("Comment is disabled.", "warning")
        return redirect(url_for(".show_post", post_id=comment.post.id))

    return redirect(
        url_for(
            ".show_post",
            reply=comment_id,
            author=comment.author,
            post_id=comment.post_id,
        )
        + "#comment-form"
    )


@blog_bp.route("/change-theme/<theme_name>")
def change_theme(theme_name):
    if theme_name not in current_app.config["BLUELOG_THEMES"].keys():
        abort(404)

    response = make_response(redirect_back())
    response.set_cookie("theme", theme_name, max_age=30 * 24 * 60 * 60)
    return response
