# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
import os

from flask import (
    render_template,
    flash,
    redirect,
    url_for,
    request,
    current_app,
    Response,
    Blueprint,
    send_from_directory,
)
from flask_login import login_required, current_user
from flask_ckeditor import upload_success, upload_fail

from bluelog.extensions import db
from bluelog.models import Post, Category, Comment, Link
from bluelog.forms import SettingForm, PostForm, CategoryForm, LinkForm
from bluelog.utils import redirect_back, allowed_file, get_page, get_per_page


admin_bp = Blueprint("admin", __name__)


def _set_current_user_data_in_(form: SettingForm) -> None:
    form.name.data = current_user.name
    form.blog_title.data = current_user.blog_title
    form.blog_sub_title.data = current_user.blog_sub_title
    form.about.data = current_user.about


def _update_current_user_settings_with_data_from_(form: SettingForm) -> None:
    current_user.name = form.name.data
    current_user.blog_title = form.blog_title.data
    current_user.blog_sub_title = form.blog_sub_title.data
    current_user.about = form.about.data
    db.session.commit()


@admin_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings() -> str | Response:
    form = SettingForm()

    if form.validate_on_submit():
        _update_current_user_settings_with_data_from_(form)

        flash("Setting updated.", "success")
        return redirect(url_for("blog.index"))

    _set_current_user_data_in_(form)
    return render_template("admin/settings.html", form=form)


@admin_bp.route("/post/manage")
@login_required
def manage_post() -> str:
    page = get_page()
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, get_per_page()
    )
    return render_template(
        "admin/manage_post.html",
        page=page,
        pagination=pagination,
        posts=pagination.items,
    )


def _add_post_in_db_with_data_from_(form: PostForm) -> int:
    post = Post(
        title=form.title.data,
        body=form.body.data,
        category=Category.query.get(form.category.data),
    )
    db.session.add(post)
    db.session.commit()
    return post.id


@admin_bp.route("/post/new", methods=["GET", "POST"])
@login_required
def new_post() -> str | Response:
    form = PostForm()

    if form.validate_on_submit():
        flash("Post created.", "success")
        return redirect(
            url_for("blog.show_post", post_id=_add_post_in_db_with_data_from_(form))
        )
    return render_template("admin/new_post.html", form=form)


def _set_post_data_in_(form: PostForm, post: Post) -> None:
    form.title.data = post.title
    form.body.data = post.body
    form.category.data = post.category_id


def _update_post_with_data_from_(form: PostForm, post: Post) -> None:
    post.title = form.title.data
    post.body = form.body.data
    post.category = Category.query.get(form.category.data)
    db.session.commit()


@admin_bp.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit_post(post_id: int) -> str | Response:
    form = PostForm()
    post = Post.query.get_or_404(post_id)

    if form.validate_on_submit():
        _update_post_with_data_from_(form, post)
        flash("Post updated.", "success")
        return redirect(url_for("blog.show_post", post_id=post.id))

    _set_post_data_in_(form, post)
    return render_template("admin/edit_post.html", form=form)


@admin_bp.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id: int) -> Response:
    db.session.delete(Post.query.get_or_404(post_id))
    db.session.commit()

    flash("Post deleted.", "success")
    return redirect_back()


@admin_bp.route("/post/<int:post_id>/set-comment", methods=["POST"])
@login_required
def set_comment(post_id: int) -> Response:
    post = Post.query.get_or_404(post_id)
    post.can_comment, comment_status = (
        (False, "disabled") if post.can_comment else (True, "enabled")
    )
    db.session.commit()

    flash(f"Comment {comment_status}.", "success")
    return redirect_back()


@admin_bp.route("/comment/manage")
@login_required
def manage_comment() -> str:
    filter_rule = request.args.get("filter", "all")
    filtered_comments = {
        "unread": Comment.query.filter_by(reviewed=False),
        "admin": Comment.query.filter_by(from_admin=True),
    }.get(filter_rule, Comment.query)
    pagination = filtered_comments.order_by(Comment.timestamp.desc()).paginate(
        get_page(), get_per_page()
    )
    return render_template(
        "admin/manage_comment.html", comments=pagination.items, pagination=pagination
    )


@admin_bp.route("/comment/<int:comment_id>/approve", methods=["POST"])
@login_required
def approve_comment(comment_id: int) -> Response:
    comment = Comment.query.get_or_404(comment_id)
    comment.reviewed = True
    db.session.commit()

    flash("Comment published.", "success")
    return redirect_back()


@admin_bp.route("/comment/<int:comment_id>/delete", methods=["POST"])
@login_required
def delete_comment(comment_id: int) -> Response:
    db.session.delete(Comment.query.get_or_404(comment_id))
    db.session.commit()

    flash("Comment deleted.", "success")
    return redirect_back()


@admin_bp.route("/category/manage")
@login_required
def manage_category() -> str:
    return render_template("admin/manage_category.html")


@admin_bp.route("/category/new", methods=["GET", "POST"])
@login_required
def new_category() -> str | Response:
    form = CategoryForm()

    if form.validate_on_submit():
        db.session.add(Category(name=form.name.data))
        db.session.commit()

        flash("Category created.", "success")
        return redirect(url_for(".manage_category"))
    return render_template("admin/new_category.html", form=form)


@admin_bp.route("/category/<int:category_id>/edit", methods=["GET", "POST"])
@login_required
def edit_category(category_id: int) -> str | Response:
    form = CategoryForm()
    category = Category.query.get_or_404(category_id)

    if category.id == 1:
        flash("You can not edit the default category.", "warning")
        return redirect(url_for("blog.index"))

    if form.validate_on_submit():
        category.name = form.name.data
        db.session.commit()

        flash("Category updated.", "success")
        return redirect(url_for(".manage_category"))

    form.name.data = category.name
    return render_template("admin/edit_category.html", form=form)


@admin_bp.route("/category/<int:category_id>/delete", methods=["POST"])
@login_required
def delete_category(category_id: int) -> Response:
    category = Category.query.get_or_404(category_id)

    if category.id == 1:
        flash("You can not delete the default category.", "warning")
        return redirect(url_for("blog.index"))

    category.delete()

    flash("Category deleted.", "success")
    return redirect(url_for(".manage_category"))


@admin_bp.route("/link/manage")
@login_required
def manage_link() -> str:
    return render_template("admin/manage_link.html")


@admin_bp.route("/link/new", methods=["GET", "POST"])
@login_required
def new_link() -> str | Response:
    form = LinkForm()

    if form.validate_on_submit():
        db.session.add(Link(name=form.name.data, url=form.url.data))
        db.session.commit()

        flash("Link created.", "success")
        return redirect(url_for(".manage_link"))
    return render_template("admin/new_link.html", form=form)


def _set_link_data_in_(form: LinkForm, link: Link) -> None:
    form.name.data = link.name
    form.url.data = link.url


def _update_link_with_data_from_(form: LinkForm, link: Link) -> None:
    link.name = form.name.data
    link.url = form.url.data
    db.session.commit()


@admin_bp.route("/link/<int:link_id>/edit", methods=["GET", "POST"])
@login_required
def edit_link(link_id: int) -> str | Response:
    form = LinkForm()
    link = Link.query.get_or_404(link_id)

    if form.validate_on_submit():
        _update_link_with_data_from_(form, link)

        flash("Link updated.", "success")
        return redirect(url_for(".manage_link"))

    _set_link_data_in_(form, link)
    return render_template("admin/edit_link.html", form=form)


@admin_bp.route("/link/<int:link_id>/delete", methods=["POST"])
@login_required
def delete_link(link_id) -> Response:
    db.session.delete(Link.query.get_or_404(link_id))
    db.session.commit()

    flash("Link deleted.", "success")
    return redirect(url_for(".manage_link"))


@admin_bp.route("/uploads/<path:filename>")
def get_image(filename: str):
    return send_from_directory(current_app.config["BLUELOG_UPLOAD_PATH"], filename)


@admin_bp.route("/upload", methods=["POST"])
def upload_image():
    f = request.files.get("upload")

    if not allowed_file(f.filename):
        return upload_fail("Image only!")

    f.save(os.path.join(current_app.config["BLUELOG_UPLOAD_PATH"], f.filename))
    return upload_success(url_for(".get_image", filename=f.filename), f.filename)
