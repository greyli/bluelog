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


class AdminTestCase(BaseTestCase):

    def setUp(self):
        super(AdminTestCase, self).setUp()
        self.login()

        category = Category(name='Default')
        post = Post(title='Hello', category=category, body='Blah...')
        comment = Comment(body='A comment', post=post, from_admin=True)
        link = Link(name='GitHub', url='https://github.com/greyli')
        db.session.add_all([category, post, comment, link])
        db.session.commit()

    def test_new_post(self):
        response = self.client.get(url_for('admin.new_post'))
        data = response.get_data(as_text=True)
        self.assertIn('New Post', data)

        response = self.client.post(url_for('admin.new_post'), data=dict(
            title='Something',
            category=1,
            body='Hello, world.'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Post created.', data)
        self.assertIn('Something', data)
        self.assertIn('Hello, world.', data)

    def test_edit_post(self):
        response = self.client.get(url_for('admin.edit_post', post_id=1))
        data = response.get_data(as_text=True)
        self.assertIn('Edit Post', data)
        self.assertIn('Hello', data)
        self.assertIn('Blah...', data)

        response = self.client.post(url_for('admin.edit_post', post_id=1), data=dict(
            title='Something Edited',
            category=1,
            body='New post body.'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Post updated.', data)
        self.assertIn('New post body.', data)
        self.assertNotIn('Blah...', data)

    def test_delete_post(self):
        response = self.client.get(url_for('admin.delete_post', post_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Post deleted.', data)
        self.assertIn('405 Method Not Allowed', data)

        response = self.client.post(url_for('admin.delete_post', post_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Post deleted.', data)

    def test_delete_comment(self):
        response = self.client.get(url_for('admin.delete_comment', comment_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Comment deleted.', data)
        self.assertIn('405 Method Not Allowed', data)

        response = self.client.post(url_for('admin.delete_comment', comment_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Comment deleted.', data)
        self.assertNotIn('A comment', data)

    def test_enable_comment(self):
        post = Post.query.get(1)
        post.can_comment = False
        db.session.commit()

        response = self.client.post(url_for('admin.set_comment', post_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Comment enabled.', data)

        response = self.client.post(url_for('blog.show_post', post_id=1))
        data = response.get_data(as_text=True)
        self.assertIn('<div id="comment-form">', data)

    def test_disable_comment(self):
        response = self.client.post(url_for('admin.set_comment', post_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Comment disabled.', data)

        response = self.client.post(url_for('blog.show_post', post_id=1))
        data = response.get_data(as_text=True)
        self.assertNotIn('<div id="comment-form">', data)

    def test_approve_comment(self):
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

        self.login()
        response = self.client.post(url_for('admin.approve_comment', comment_id=2), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Comment published.', data)

        response = self.client.post(url_for('blog.show_post', post_id=1))
        data = response.get_data(as_text=True)
        self.assertIn('I am a guest comment.', data)

    def test_new_category(self):
        response = self.client.get(url_for('admin.new_category'))
        data = response.get_data(as_text=True)
        self.assertIn('New Category', data)

        response = self.client.post(url_for('admin.new_category'), data=dict(name='Tech'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Category created.', data)
        self.assertIn('Tech', data)

        response = self.client.post(url_for('admin.new_category'), data=dict(name='Tech'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Name already in use.', data)

        category = Category.query.get(1)
        post = Post(title='Post Title', category=category)
        db.session.add(post)
        db.session.commit()
        response = self.client.get(url_for('blog.show_category', category_id=1))
        data = response.get_data(as_text=True)
        self.assertIn('Post Title', data)

    def test_edit_category(self):
        response = self.client.post(url_for('admin.edit_category', category_id=1),
                                    data=dict(name='Default edited'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Category updated.', data)
        self.assertIn('Default', data)
        self.assertNotIn('Default edited', data)
        self.assertIn('You can not edit the default category', data)

        response = self.client.post(url_for('admin.new_category'), data=dict(name='Tech'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Category created.', data)
        self.assertIn('Tech', data)

        response = self.client.get(url_for('admin.edit_category', category_id=2))
        data = response.get_data(as_text=True)
        self.assertIn('Edit Category', data)
        self.assertIn('Tech', data)

        response = self.client.post(url_for('admin.edit_category', category_id=2),
                                    data=dict(name='Life'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Category updated.', data)
        self.assertIn('Life', data)
        self.assertNotIn('Tech', data)

    def test_delete_category(self):
        category = Category(name='Tech')
        post = Post(title='test', category=category)
        db.session.add(category)
        db.session.add(post)
        db.session.commit()

        response = self.client.get(url_for('admin.delete_category', category_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Category deleted.', data)
        self.assertIn('405 Method Not Allowed', data)

        response = self.client.post(url_for('admin.delete_category', category_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('You can not delete the default category.', data)
        self.assertNotIn('Category deleted.', data)
        self.assertIn('Default', data)

        response = self.client.post(url_for('admin.delete_category', category_id=2), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Category deleted.', data)
        self.assertIn('Default', data)
        self.assertNotIn('Tech', data)

    def test_new_link(self):
        response = self.client.get(url_for('admin.new_link'))
        data = response.get_data(as_text=True)
        self.assertIn('New Link', data)

        response = self.client.post(url_for('admin.new_link'), data=dict(
            name='HelloFlask',
            url='http://helloflask.com'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Link created.', data)
        self.assertIn('HelloFlask', data)

    def test_edit_link(self):
        response = self.client.get(url_for('admin.edit_link', link_id=1))
        data = response.get_data(as_text=True)
        self.assertIn('Edit Link', data)
        self.assertIn('GitHub', data)
        self.assertIn('https://github.com/greyli', data)

        response = self.client.post(url_for('admin.edit_link', link_id=1), data=dict(
            name='Github',
            url='https://github.com/helloflask'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Link updated.', data)
        self.assertIn('https://github.com/helloflask', data)

    def test_delete_link(self):
        response = self.client.get(url_for('admin.delete_link', link_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Link deleted.', data)
        self.assertIn('405 Method Not Allowed', data)

        response = self.client.post(url_for('admin.delete_link', link_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Link deleted.', data)

    def test_manage_post_page(self):
        response = self.client.get(url_for('admin.manage_post'))
        data = response.get_data(as_text=True)
        self.assertIn('Manage Posts', data)

    def test_manage_comment_page(self):
        response = self.client.get(url_for('admin.manage_comment'))
        data = response.get_data(as_text=True)
        self.assertIn('Manage Comments', data)

    def test_manage_category_page(self):
        response = self.client.get(url_for('admin.manage_category'))
        data = response.get_data(as_text=True)
        self.assertIn('Manage Categories', data)

    def test_manage_link_page(self):
        response = self.client.get(url_for('admin.manage_link'))
        data = response.get_data(as_text=True)
        self.assertIn('Manage Links', data)

    def test_blog_setting(self):
        response = self.client.post(url_for('admin.settings'), data=dict(
            name='Grey Li',
            blog_title='My Blog',
            blog_sub_title='Just some raw ideas.',
            bio='I am ...',
            about='Example about page',
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Setting updated.', data)
        self.assertIn('My Blog', data)

        response = self.client.get(url_for('admin.settings'))
        data = response.get_data(as_text=True)
        self.assertIn('Grey Li', data)
        self.assertIn('My Blog', data)

        response = self.client.get(url_for('blog.about'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Example about page', data)
