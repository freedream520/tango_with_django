import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tango_with_django_project.settings')

import django

django.setup()

from rango.models import Category, Page


def add_cat(name, views, likes):
    c = Category.objects.get_or_create(name=name, views=views, likes=likes)[0]
    # c.views = views
    # c.likes = likes
    return c


def add_page(cat, title, url, views=0):
    p = Page.objects.get_or_create(category=cat, title=title, url=url, views=views)[0]
    return p


def populate():
    python_cat = add_cat(name='Python', views=128, likes=64)
    add_page(cat=python_cat,
             title='Official Python Tutorial',
             url='http://docs.python.org/2/tutorial/',
             views=123)
    add_page(cat=python_cat,
             title='How to Think like a Computer Scientist',
             url='http://www.greenteapress.com/thinkpython/',
             views=1)
    add_page(cat=python_cat,
             title='Learn Python in 10 Minutes',
             url='http://www.korokithakis.net/tutorials/python',
             views=2)

    django_cat = add_cat(name='Django', views=64, likes=32)
    add_page(cat=django_cat,
             title="Official Django Tutorial",
             url="https://docs.djangoproject.com/en/1.5/intro/tutorial01/",
             views=12)
    add_page(cat=django_cat,
             title="Django Rocks",
             url="http://www.djangorocks.com/",
             views=34)
    add_page(cat=django_cat,
             title="How to Tango with Django",
             url="http://www.tangowithdjango.com/",
             views=56)

    frame_cat = add_cat(name="Other Frameworks", views=32, likes=16)
    add_page(cat=frame_cat,
             title="Bottle",
             url="http://bottlepy.org/docs/dev/",
             views=2)
    add_page(cat=frame_cat,
             title="Flask",
             url="http://flask.pocoo.org",
             views=1)


if __name__ == '__main__':
    print 'Starting Rango population script...'
    populate()
