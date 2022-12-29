# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
import random

from faker import Faker
from sqlalchemy.exc import IntegrityError

from bluelog.extensions import db
from bluelog.models import Admin, Category, Post, Comment, Link


fake = Faker()


def fake_admin():
    admin = Admin(
        username="admin",
        blog_title="Bluelog",
        blog_sub_title="No, I'm the real thing.",
        name="Mima Kirigoe",
        about="Um, l, Mima Kirigoe, had a fun time as a member of CHAM...",
    )
    admin.set_password("helloflask")
    db.session.add(admin)
    db.session.commit()


def fake_categories(count=10):
    db.session.add(Category(name="Default"))

    for _ in range(count):
        db.session.add(Category(name=fake.word()))
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def fake_posts(count=50):
    for _ in range(count):
        db.session.add(
            Post(
                title=fake.sentence(),
                body=fake.text(2000),
                category=Category.query.get(random.randint(1, Category.query.count())),
                timestamp=fake.date_time_this_year(),
            )
        )
    db.session.commit()


def _get_comment_with_fake_data_and_(reviewed, replied=None):
    comment = Comment(
        author=fake.name(),
        email=fake.email(),
        site=fake.url(),
        body=fake.sentence(),
        timestamp=fake.date_time_this_year(),
        reviewed=reviewed,
        post=Post.query.get(random.randint(1, Post.query.count())),
    )
    if replied:
        comment.replied = replied
    return comment


def _get_comment_from_admin():
    return Comment(
        author="Mima Kirigoe",
        email="mima@example.com",
        site="example.com",
        body=fake.sentence(),
        timestamp=fake.date_time_this_year(),
        from_admin=True,
        reviewed=True,
        post=Post.query.get(random.randint(1, Post.query.count())),
    )


def fake_comments(count=500):
    for _ in range(count):
        db.session.add(_get_comment_with_fake_data_and_(reviewed=True))

    salt = int(count * 0.1)

    for _ in range(salt):
        # not reviewed comments
        db.session.add(_get_comment_with_fake_data_and_(reviewed=False))
        # from admin
        db.session.add(_get_comment_from_admin())
    db.session.commit()

    # replies
    for _ in range(salt):
        db.session.add(
            _get_comment_with_fake_data_and_(
                reviewed=True,
                replied=Comment.query.get(random.randint(1, Comment.query.count())),
            )
        )
    db.session.commit()


def fake_links():
    db.session.add_all(
        [
            Link(name="Twitter", url="#"),
            Link(name="Facebook", url="#"),
            Link(name="LinkedIn", url="#"),
            Link(name="Google+", url="#"),
        ]
    )
    db.session.commit()
