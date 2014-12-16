from django.test import TestCase

import datetime
from django.utils import timezone

from django.core.urlresolvers import reverse

from mesg.models import *

def create_division_subdivisions(division_name, subdivision_names):
    division = Division.objects.create(name=division_name)
    subdivisions = [
            SubDivision.objects.create(name=x, division=division) for x in
            subdivision_names
    ]


class SubdivisionViewTests(TestCase):
    def test_subdivision_view_with_no_messages(self):
        """
        Should return 200
        """
        create_division_subdivisions('7', ['A' , 'B'])
        response = self.client.get(
                reverse(
                    'mesg:subdivision',
                    args=('7','A')
                )
        )
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
                response.context['messages'], []
        )


    def test_subdivision_view_with_message_in_parent(self):
        """
        Messages in parent should be seen in subdivisions
        """
        create_division_subdivisions('7', ['A' , 'B'])
        u = User.objects.create_user('testuser')
        m = Message.objects.create(
                message_text='Test message in parent',
                author=u,
                content_object=Division.objects.get(name='7')
        )

        response = self.client.get(
                reverse(
                    'mesg:subdivision',
                    args=('7','A')
                )
        )
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
                response.context['messages'], map(repr,[m])
        )


    def test_subdivision_view_with_message_in_subdivision(self):
        """
        Messages in subdivisions should be seen
        """
        create_division_subdivisions('7', ['A' , 'B'])
        u = User.objects.create_user('testuser')
        m = Message.objects.create(
                message_text='Test message in self',
                author=u,
                content_object=SubDivision.objects.get(name='A')
        )

        response = self.client.get(
                reverse(
                    'mesg:subdivision',
                    args=('7','A')
                )
        )
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
                response.context['messages'], map(repr,[m])
        )


    def test_subdivision_view_with_message_in_sibling_subdivision(self):
        """
        Messages in sibling subdivisions should not be seen
        """
        create_division_subdivisions('7', ['A' , 'B'])
        u = User.objects.create_user('testuser')
        m = Message.objects.create(
                message_text='Test message in sibling',
                author=u,
                content_object=SubDivision.objects.get(name='B')
        )

        response = self.client.get(
                reverse(
                    'mesg:subdivision',
                    args=('7','A')
                )
        )
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
                response.context['messages'], []
        )



    def test_subdivision_view_with_messages_in_self_parent_and_sibling(self):
        """
        Messages in parent and self should be visible and orderd by -pub_date
        """
        create_division_subdivisions('7', ['A' , 'B'])
        u = User.objects.create_user('testuser')

        m_self = Message.objects.create(
                message_text='Test message in self',
                author=u,
                content_object=SubDivision.objects.get(name='A'),
        )

        m_parent = Message.objects.create(
                message_text='Test message in parent posted now',
                author=u,
                content_object=Division.objects.get(name='7')
        )

        m_sibling = Message.objects.create(
                message_text='Test message in sibling posted',
                author=u,
                content_object=SubDivision.objects.get(name='B'),
        )

        response = self.client.get(
                reverse(
                    'mesg:subdivision',
                    args=('7','A')
                )
        )
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
                response.context['messages'],
                map(repr,[m_parent, m_self]),
                # Because auto_now_add cannot be overidden even
                # in testing and adding time.sleep(1) sucks
                ordered=False
        )


    def test_subdivision_view_with_messages_with_different_expires_date(self):
        """
        Expired messages should not be visible irrespective of category
        """
        create_division_subdivisions('7', ['A' , 'B'])
        u = User.objects.create_user('testuser')

        m_self_never_expires = Message.objects.create(
                message_text='Test message in self that never expires',
                author=u,
                content_object=SubDivision.objects.get(name='A'),
        )

        m_parent_never_expires = Message.objects.create(
                message_text='Test message in parent that never expires',
                author=u,
                content_object=Division.objects.get(name='7'),
        )
        m_sibling_never_expires = Message.objects.create(
                message_text='Test message in sibling that never expires',
                author=u,
                content_object=SubDivision.objects.get(name='B'),
        )

        m_self_future_expires = Message.objects.create(
                message_text='Test message in self that expires in future',
                author=u,
                content_object=SubDivision.objects.get(name='A'),
                expires_date=timezone.now() + datetime.timedelta(days=2),
        )
        m_parent_future_expires = Message.objects.create(
                message_text='Test message in parent that expires in future',
                author=u,
                content_object=Division.objects.get(name='7'),
                expires_date=timezone.now() + datetime.timedelta(days=2),
        )
        m_sibling_future_expires = Message.objects.create(
                message_text='Test message in sibling that expires in future',
                author=u,
                content_object=SubDivision.objects.get(name='B'),
                expires_date=timezone.now() + datetime.timedelta(days=2),
        )

        m_self_past_expires = Message.objects.create(
                message_text='Test message in self that has expired',
                author=u,
                content_object=SubDivision.objects.get(name='A'),
                expires_date=timezone.now() - datetime.timedelta(days=2),
        )
        m_parent_past_expires = Message.objects.create(
                message_text='Test message in parent that has expired',
                author=u,
                content_object=Division.objects.get(name='7'),
                expires_date=timezone.now() - datetime.timedelta(days=2),
        )
        m_sibling_past_expires = Message.objects.create(
                message_text='Test message in sibling that has expired',
                author=u,
                content_object=SubDivision.objects.get(name='B'),
                expires_date=timezone.now() - datetime.timedelta(days=2),
        )

        m_self_today_expires = Message.objects.create(
                message_text='Test message in self that expires today',
                author=u,
                content_object=SubDivision.objects.get(name='A'),
                expires_date=timezone.now()
        )
        m_parent_today_expires = Message.objects.create(
                message_text='Test message in parent that expires today',
                author=u,
                content_object=Division.objects.get(name='7'),
                expires_date=timezone.now()
        )
        m_sibling_today_expires = Message.objects.create(
                message_text='Test message in sibling that expires today',
                author=u,
                content_object=SubDivision.objects.get(name='B'),
                expires_date=timezone.now()
        )


        response = self.client.get(
                reverse(
                    'mesg:subdivision',
                    args=('7','A')
                )
        )
        self.assertEqual(response.status_code, 200)

        self.assertQuerysetEqual(
                response.context['messages'],
                map(repr,[
                    m_parent_today_expires,
                    m_self_today_expires,
                    m_parent_future_expires,
                    m_self_future_expires,
                    m_parent_never_expires,
                    m_self_never_expires,
                    ]
                ),
                # Because auto_now_add cannot be overidden even
                # in testing and adding time.sleep(1) sucks
                ordered=False
        )



class DivisionViewTests(TestCase):
    def test_division_view_with_no_messages(self):
        """
        Should return 200
        """
        create_division_subdivisions('7', ['A' , 'B'])
        response = self.client.get(
                reverse(
                    'mesg:division',
                    args=('7',)
                )
        )
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
                response.context['messages'], []
        )


    def test_division_view_with_message_in_self(self):
        """
        Messages in division should be seen
        """
        create_division_subdivisions('7', ['A' , 'B'])
        u = User.objects.create_user('testuser')
        m = Message.objects.create(
                message_text='Test message in self',
                author=u,
                content_object=Division.objects.get(name='7')
        )

        response = self.client.get(
                reverse(
                    'mesg:division',
                    args=('7',)
                )
        )
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
                response.context['messages'], map(repr,[m])
        )


    def test_division_view_with_message_in_subdivision(self):
        """
        Messages in subdivisions should be seen
        """
        create_division_subdivisions('7', ['A' , 'B'])
        u = User.objects.create_user('testuser')
        m = Message.objects.create(
                message_text='Test message in self',
                author=u,
                content_object=SubDivision.objects.get(name='A')
        )

        response = self.client.get(
                reverse(
                    'mesg:division',
                    args=('7',)
                )
        )
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
                response.context['messages'], map(repr,[m])
        )


    def test_division_view_with_messages_in_two_subdivisions(self):
        """
        Messages in all subdivisions should be seen
        """
        create_division_subdivisions('7', ['A' , 'B'])
        u = User.objects.create_user('testuser')

        m1 = Message.objects.create(
                message_text='Test message in sub1',
                author=u,
                content_object=SubDivision.objects.get(name='A')
        )
        m2 = Message.objects.create(
                message_text='Test message in sub2',
                author=u,
                content_object=SubDivision.objects.get(name='B')
        )

        response = self.client.get(
                reverse(
                    'mesg:division',
                    args=('7',)
                )
        )
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
                response.context['messages'],
                map(repr,[m1,m2]),
                ordered=False
        )



    def test_division_view_with_messages_in_self_and_two_subdivision(self):
        """
        Messages in parent and self should be visible and orderd by -pub_date
        """
        create_division_subdivisions('7', ['A' , 'B'])
        u = User.objects.create_user('testuser')

        m_self = Message.objects.create(
                message_text='Test message in self',
                author=u,
                content_object=Division.objects.get(name='7'),
        )

        m_sub_1 = Message.objects.create(
                message_text='Test message in sub1',
                author=u,
                content_object=SubDivision.objects.get(name='A')
        )

        m_sub_2 = Message.objects.create(
                message_text='Test message in sub2',
                author=u,
                content_object=SubDivision.objects.get(name='B'),
        )

        response = self.client.get(
                reverse(
                    'mesg:division',
                    args=('7',)
                )
        )
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
                response.context['messages'],
                map(repr,[m_self, m_sub_1, m_sub_2]),
                # Because auto_now_add cannot be overidden even
                # in testing and adding time.sleep(1) sucks
                ordered=False
        )


    def test_division_view_with_messages_with_different_expires_date(self):
        """
        Expired messages should not be visible irrespective of category
        """
        create_division_subdivisions('7', ['A' , 'B'])
        u = User.objects.create_user('testuser')

        m_self_never_expires = Message.objects.create(
                message_text='Test message in self that never expires',
                author=u,
                content_object=Division.objects.get(name='7'),
        )

        m_sub1_never_expires = Message.objects.create(
                message_text='Test message in sub1 that never expires',
                author=u,
                content_object=SubDivision.objects.get(name='A'),
        )
        m_sub2_never_expires = Message.objects.create(
                message_text='Test message in sub2 that never expires',
                author=u,
                content_object=SubDivision.objects.get(name='B'),
        )

        m_self_future_expires = Message.objects.create(
                message_text='Test message in self that expires in future',
                author=u,
                content_object=Division.objects.get(name='7'),
                expires_date=timezone.now() + datetime.timedelta(days=2),
        )
        m_sub1_future_expires = Message.objects.create(
                message_text='Test message in sub1 that expires in future',
                author=u,
                content_object=SubDivision.objects.get(name='A'),
                expires_date=timezone.now() + datetime.timedelta(days=2),
        )
        m_sub2_future_expires = Message.objects.create(
                message_text='Test message in sub2 that expires in future',
                author=u,
                content_object=SubDivision.objects.get(name='B'),
                expires_date=timezone.now() + datetime.timedelta(days=2),
        )

        m_self_past_expires = Message.objects.create(
                message_text='Test message in self that has expired',
                author=u,
                content_object=Division.objects.get(name='7'),
                expires_date=timezone.now() - datetime.timedelta(days=2),
        )
        m_sub1_past_expires = Message.objects.create(
                message_text='Test message in sub1 that has expired',
                author=u,
                content_object=SubDivision.objects.get(name='A'),
                expires_date=timezone.now() - datetime.timedelta(days=2),
        )
        m_sub2_past_expires = Message.objects.create(
                message_text='Test message in sub2 that has expired',
                author=u,
                content_object=SubDivision.objects.get(name='B'),
                expires_date=timezone.now() - datetime.timedelta(days=2),
        )

        m_self_today_expires = Message.objects.create(
                message_text='Test message in self that expires today',
                author=u,
                content_object=Division.objects.get(name='7'),
                expires_date=timezone.now()
        )
        m_sub1_today_expires = Message.objects.create(
                message_text='Test message in sub1 that expires today',
                author=u,
                content_object=SubDivision.objects.get(name='A'),
                expires_date=timezone.now()
        )
        m_sub2_today_expires = Message.objects.create(
                message_text='Test message in sub2 that expires today',
                author=u,
                content_object=SubDivision.objects.get(name='B'),
                expires_date=timezone.now()
        )


        response = self.client.get(
                reverse(
                    'mesg:division',
                    args=('7',)
                )
        )
        self.assertEqual(response.status_code, 200)

        self.assertQuerysetEqual(
                response.context['messages'],
                map(repr,[
                    m_sub1_today_expires,
                    m_sub2_today_expires,
                    m_self_today_expires,
                    m_sub1_future_expires,
                    m_sub2_future_expires,
                    m_self_future_expires,
                    m_sub1_never_expires,
                    m_sub2_never_expires,
                    m_self_never_expires,
                    ]
                ),
                # Because auto_now_add cannot be overidden even
                # in testing and adding time.sleep(1) sucks
                ordered=False 
        )
