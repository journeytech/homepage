'''
Created on Apr 25, 2014

@author: eastagile
'''
import factory
from django.contrib.auth.models import User


class UserFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = User
    username = factory.Sequence(lambda n: u'User{0}'.format(n))
    password = 'password'

    is_superuser = True
    is_staff = True
    is_active = True

    @classmethod
    def _prepare(cls, create, **kwargs):
        password = kwargs.pop('password', None)
        user = super(UserFactory, cls)._prepare(create, **kwargs)
        if password:
            user.raw_password = password
            user.set_password(password)
            if create:
                user.save()
        return user
