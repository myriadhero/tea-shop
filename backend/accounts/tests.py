from django.contrib.auth import get_user_model
from django.test import TestCase


class CustomUserTests(TestCase):
    def test_create_user(self):
        uname = "Doggo69"
        email = "doggersondog@alldoggos.com"
        pword = "tEstpasword123!"

        User = get_user_model()
        user = User.objects.create_user(username=uname, email=email, password=pword)

        self.assertEqual(user.username, uname)
        self.assertEqual(user.email, email)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        uname = "superDoggo69"
        email = "doggersonsuperdog@alldoggos.com"
        pword = "tEstpasword1234!"

        User = get_user_model()
        user = User.objects.create_superuser(
            username=uname, email=email, password=pword
        )

        self.assertEqual(user.username, uname)
        self.assertEqual(user.email, email)
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
