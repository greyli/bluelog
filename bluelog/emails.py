# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
from threading import Thread

from flask_mail import Message
from flask import url_for, current_app

from bluelog.extensions import mail
from bluelog.models import Post, Comment


def _send_async_mail(app: current_app, message: Message) -> None:
    with app.app_context():
        mail.send(message)


def send_mail(subject: str, to: str, html: str) -> Thread:
    thr = Thread(
        target=_send_async_mail,
        args=[
            current_app._get_current_object(),
            Message(subject, recipients=[to], html=html),
        ],
    )
    thr.start()
    return thr


def send_new_comment_email(post: Post) -> None:
    post_url = url_for("blog.show_post", post_id=post.id, _external=True) + "#comments"
    send_mail(
        subject="New comment",
        to=current_app.config["BLUELOG_EMAIL"],
        html="<p>New comment in post <i>%s</i>, click the link below to check:</p>"
        '<p><a href="%s">%s</a></P>'
        '<p><small style="color: #868e96">Do not reply this email.</small></p>'
        % (post.title, post_url, post_url),
    )


def send_new_reply_email(comment: Comment) -> None:
    post_url = (
        url_for("blog.show_post", post_id=comment.post_id, _external=True) + "#comments"
    )
    send_mail(
        subject="New reply",
        to=comment.email,
        html="<p>New reply for the comment you left in post <i>%s</i>, click the link below to check: </p>"
        '<p><a href="%s">%s</a></p>'
        '<p><small style="color: #868e96">Do not reply this email.</small></p>'
        % (comment.post.title, post_url, post_url),
    )
