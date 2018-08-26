# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
from flask import url_for

from bluelog.models import Post, Category, Link, Comment
from bluelog.extensions import db

from tests.base import BaseTestCase


class BlogTestCase(BaseTestCase):

    def setUp(self):
        super(BlogTestCase, self).setUp()
        self.login()

        category = Category(name='Default')
        post = Post(title='Hello Post', category=category, body='Blah...')
        comment = Comment(body='A comment', post=post, from_admin=True, reviewed=True)
        link = Link(name='GitHub', url='https://github.com/greyli')

        db.session.add_all([category, post, comment, link])
        db.session.commit()

    def test_index_page(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertIn('Home', data)
        self.assertIn('Testlog', data)
        self.assertIn('a test', data)
        self.assertIn('Hello Post', data)
        self.assertIn('GitHub', data)

    def test_post_page(self):
        response = self.client.get(url_for('blog.show_post', post_id=1))
        data = response.get_data(as_text=True)
        self.assertIn('Hello Post', data)
        self.assertIn('A comment', data)

    def test_change_theme(self):
        response = self.client.get(url_for('blog.change_theme', theme_name='perfect_blue'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('css/perfect_blue.min.css', data)
        self.assertNotIn('css/black_swan.min.css', data)

        response = self.client.get(url_for('blog.change_theme', theme_name='black_swan'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('css/black_swan.min.css', data)
        self.assertNotIn('css/perfect_blue.min.css', data)

    def test_about_page(self):
        response = self.client.get(url_for('blog.about'))
        data = response.get_data(as_text=True)
        self.assertIn('I am test', data)
        self.assertIn('About', data)

    def test_category_page(self):
        response = self.client.get(url_for('blog.show_category', category_id=1))
        data = response.get_data(as_text=True)
        self.assertIn('Category: Default', data)
        self.assertIn('Hello Post', data)

    def test_new_admin_comment(self):
        response = self.client.post(url_for('blog.show_post', post_id=1), data=dict(
            body='I am an admin comment.',
            post=Post.query.get(1),
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Comment published.', data)
        self.assertIn('I am an admin comment.', data)

    def test_new_guest_comment(self):
        self.logout()
        response = self.client.post(url_for('blog.show_post', post_id=1), data=dict(
            author='Guest',
            email='a@b.com',
            site='http://greyli.com',
            body='I am a guest comment.',
            post=Post.query.get(1),
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Thanks, your comment will be published after reviewed.', data)
        self.assertNotIn('I am a guest comment.', data)

    def test_reply_status(self):
        response = self.client.get(url_for('blog.reply_comment', comment_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Reply to', data)
        self.assertIn('Cancel', data)

        post = Post.query.get(1)
        post.can_comment = False
        db.session.commit()

        response = self.client.get(url_for('blog.reply_comment', comment_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Comment is disabled.', data)
        self.assertNotIn('Reply to', data)
        self.assertNotIn('Cancel', data)

    def test_new_admin_reply(self):
        response = self.client.post(url_for('blog.show_post', post_id=1) + '?reply=1', data=dict(
            body='I am an admin reply comment.',
            post=Post.query.get(1),
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Comment published.', data)
        self.assertIn('I am an admin reply comment.', data)
        self.assertIn('Reply', data)

    def test_new_guest_reply(self):
        self.logout()
        response = self.client.post(url_for('blog.show_post', post_id=1) + '?reply=1', data=dict(
            author='Guest',
            email='a@b.com',
            site='http://greyli.com',
            body='I am a guest comment.',
            post=Post.query.get(1),
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Thanks, your comment will be published after reviewed.', data)
        self.assertNotIn('I am a guest comment.', data)
