# coding: utf-8

import json
import mimetypes
from base.tests.helpers.testing import TestBase
from base.application.lookup import responses as rmsgs


class TestBlogBase(TestBase):

    def reg(self, username, password, data):

        self.token = None
        self.get_user(username, password, data)
        self.assertIsNotNone(self.token)

        return self._user.id, self.token

    def api(self, token, method, address, body=None, expected_status_code=None, expected_result=None):

        bdy = json.dumps(body) if body else None

        if method in ('PUT'):
            if not bdy:
                bdy = '{}'

        res = self.fetch(address, method=method, body=bdy, headers={"Authorization": token} if token else {})
        if expected_status_code:
            self.assertEqual(res.code, expected_status_code)

        if not res.body:
            return None

        jres = json.loads(res.body.decode('utf-8'))

        if expected_result:
            self.assertEqual(jres, expected_result)

        return jres


class TestPostTags(TestBlogBase):

    def test_add_post_with_the_same_parent_and_different_language(self):
        id_user, token_user = self.reg('test@knowledge-base.com', '123', {'first_name': 'test',
                                                                          'last_name': 'user',
                                                                          'data': '{}',
                                                                          'role_flags': 1})

        r = self.api(token_user, 'PUT', '/api/wiki/posts', body={'title': 'neki tamo naslov',
                                                                 'body': '<p>tekst</p>',
                                                                 'tags': ['telmekom', 'test', 'showTag', 'abc', 'Abc',
                                                                          'ABc'],
                                                                 }, expected_status_code=200)
        self.assertIn('id', r)
        _id_group = r['id']

        r = self.api(token_user, 'PUT', '/api/wiki/posts', body={'title': 'neki tamo naslov',
                                                                 'body': '<p>tekst</p>',
                                                                 'tags': ['telmekom', 'test', 'showTag', 'abc', 'Abc',
                                                                          'ABc'],
                                                                 'language': 'rs',
                                                                 'id_group': _id_group
                                                                 }, expected_status_code=200)
        self.assertIn('id', r)
        _id_group = r['id']

        r = self.api(token_user, 'GET', '/api/wiki/tags', expected_status_code=200)
        self.assertIn('tags', r)
        self.assertEqual(len(r['tags']), 8)

        r = self.api(token_user, 'GET', '/api/wiki/show-tags', expected_status_code=200)
        self.assertIn('show_tags', r)
        self.assertEqual(len(r['show_tags']), 8)


class TestPostGroups(TestBlogBase):

    def test_add_post_with_the_same_parent_and_different_language(self):
        id_user, token_user = self.reg('test@knowledge-base.com', '123', {'first_name': 'test',
                                                                          'last_name': 'user',
                                                                          'data': '{}',
                                                                          'role_flags': 1})

        r = self.api(token_user, 'PUT', '/api/wiki/posts', body={'title': 'neki tamo naslov',
                                                                 'body': '<p>tekst</p>',
                                                                 'tags': ['telmekom', 'test', 'showTag', 'abc', 'Abc',
                                                                          'ABc'],
                                                                 }, expected_status_code=200)
        self.assertIn('id', r)
        _id_group = r['id']

        r = self.api(token_user, 'PUT', '/api/wiki/posts', body={'title': 'neki tamo naslov',
                                                                 'body': '<p>tekst</p>',
                                                                 'tags': ['telmekom', 'test', 'showTag', 'abc', 'Abc',
                                                                          'ABc'],
                                                                 'language': 'rs',
                                                                 'id_group': _id_group
                                                                 }, expected_status_code=200)
        self.assertIn('id', r)
        _id_group = r['id']

    def test_add_post_with_the_same_parent_and_language(self):
        id_user, token_user = self.reg('test@knowledge-base.com', '123', {'first_name': 'test',
                                                                          'last_name': 'user',
                                                                          'data': '{}',
                                                                          'role_flags': 1})

        r = self.api(token_user, 'PUT', '/api/wiki/posts', body={'title': 'neki tamo naslov',
                                                                 'body': '<p>tekst</p>',
                                                                 'tags': ['telmekom', 'test', 'showTag', 'abc', 'Abc',
                                                                          'ABc'],
                                                                 'language': 'en',
                                                                 }, expected_status_code=200)
        self.assertIn('id', r)
        _id_group = r['id']

        r = self.api(token_user, 'PUT', '/api/wiki/posts', body={'title': 'neki tamo naslov',
                                                                 'body': '<p>tekst</p>',
                                                                 'tags': ['telmekom', 'test', 'showTag', 'abc', 'Abc',
                                                                          'ABc'],
                                                                 'language': 'en',
                                                                 'id_group': _id_group
                                                                 }, expected_status_code=400)
        self.assertIn('message', r)
        self.assertEqual(r['message'], 'Can not add post with the same group and language')

    def test_add_two_posts_without_language(self):
        id_user, token_user = self.reg('test@knowledge-base.com', '123', {'first_name': 'test',
                                                                          'last_name': 'user',
                                                                          'data': '{}',
                                                                          'role_flags': 1})

        r = self.api(token_user, 'PUT', '/api/wiki/posts', body={'title': 'neki tamo naslov',
                                                                 'body': '<p>tekst</p>',
                                                                 'tags': ['telmekom', 'test', 'showTag', 'abc', 'Abc',
                                                                          'ABc']
                                                                 }, expected_status_code=200)
        self.assertIn('id', r)
        _id_group = r['id']

        r = self.api(token_user, 'PUT', '/api/wiki/posts', body={'title': 'neki tamo naslov',
                                                                 'body': '<p>tekst</p>',
                                                                 'tags': ['telmekom', 'test', 'showTag', 'abc', 'Abc',
                                                                          'ABc'],
                                                                 'id_group': _id_group
                                                                 }, expected_status_code=400)
        self.assertIn('message', r)
        self.assertEqual(r['message'], 'Can not add post with the same group and language')

    def test_add_post_without_language_code(self):
        id_user, token_user = self.reg('test@knowledge-base.com', '123', {'first_name': 'test',
                                                                          'last_name': 'user',
                                                                          'data': '{}',
                                                                          'role_flags': 1})

        r = self.api(token_user, 'PUT', '/api/wiki/posts', body={'title': 'neki tamo naslov',
                                                                 'body': '<p>tekst</p>',
                                                                 'tags': ['telmekom', 'test', 'showTag', 'abc', 'Abc',
                                                                          'ABc']
                                                                 }, expected_status_code=200)
        self.assertIn('id', r)

    def test_add_post_with_language_code_uppercase(self):
        id_user, token_user = self.reg('test@knowledge-base.com', '123',
                                       {'first_name': 'test', 'last_name': 'user', 'data': '{}', 'role_flags': 1})

        r = self.api(token_user, 'PUT', '/api/wiki/posts',
                     body={'title': 'neki tamo naslov', 'body': '<p>tekst</p>', 'tags':
                         ['telmekom', 'test', 'showTag', 'abc', 'Abc', 'ABc'], 'language': 'EN'},
                     expected_status_code=200)

        self.assertIn('id', r)

    def test_add_post_with_wrong_language_code(self):
        id_user, token_user = self.reg('test@knowledge-base.com', '123', {'first_name': 'test',
                                                                          'last_name': 'user',
                                                                          'data': '{}',
                                                                          'role_flags': 1})

        r = self.api(token_user, 'PUT', '/api/wiki/posts', body={'title': 'neki tamo naslov',
                                                                 'body': '<p>tekst</p>',
                                                                 'tags': ['telmekom', 'test', 'showTag', 'abc', 'Abc',
                                                                          'ABc'],
                                                                 'language': 'ENS'
                                                                 }, expected_status_code=400)
        self.assertIn('message', r)
        self.assertEqual(r['message'], rmsgs.lmap[rmsgs.ARGUMENT_HIGHER_THEN_MAXIMUM])

        r = self.api(token_user, 'PUT', '/api/wiki/posts', body={'title': 'neki tamo naslov',
                                                                 'body': '<p>tekst</p>',
                                                                 'tags': ['telmekom', 'test', 'showTag', 'abc', 'Abc',
                                                                          'ABc'],
                                                                 'language': 'E'
                                                                 }, expected_status_code=400)
        self.assertIn('message', r)
        self.assertEqual(r['message'], rmsgs.lmap[rmsgs.ARGUMENT_LOWER_THEN_MINIMUM])

    def test_get_posts_by_group_id_when_group_not_exists(self):
        id_user, token_user = self.reg('test@knowledge-base.com', '123', {'first_name': 'test',
                                                                          'last_name': 'user',
                                                                          'data': '{}',
                                                                          'role_flags': 1})

        r = self.api(token_user, 'PUT', '/api/wiki/posts', body={'title': 'neki tamo naslov',
                                                                 'body': '<p>tekst</p>',
                                                                 'tags': ['telmekom', 'test', 'showTag', 'abc', 'Abc',
                                                                          'ABc']
                                                                 }, expected_status_code=200)
        self.assertIn('id', r)

        r1 = self.api(token_user, 'PUT', '/api/wiki/posts', body={'title': 'neki tamo naslov',
                                                                  'body': '<p>tekst</p>',
                                                                  'tags': ['telmekom', 'test', 'showTag', 'abc', 'Abc',
                                                                           'ABc']
                                                                  }, expected_status_code=200)
        self.assertIn('id', r1)

        _id_group = 4
        self.assertNotEqual(r['id'], _id_group)
        self.assertNotEqual(r1['id'], _id_group)
        r = self.api(token_user, 'GET', '/api/wiki/posts/group/{}'.format(_id_group), expected_status_code=200)
        self.assertIn('posts', r)
        self.assertEqual(len(r['posts']), 0)

    def test_get_posts_by_group_id(self):
        id_user, token_user = self.reg('test@knowledge-base.com', '123', {'first_name': 'test',
                                                                          'last_name': 'user',
                                                                          'data': '{}',
                                                                          'role_flags': 1})

        r = self.api(token_user, 'PUT', '/api/wiki/posts', body={'title': 'neki tamo naslov',
                                                                 'body': '<p>tekst</p>',
                                                                 'tags': ['telmekom', 'test', 'showTag', 'abc', 'Abc',
                                                                          'ABc']
                                                                 }, expected_status_code=200)
        self.assertIn('id', r)
        _id_post1 = r['id']

        r = self.api(token_user, 'PUT', '/api/wiki/posts', body={'title': 'neki tamo naslov',
                                                                 'body': '<p>tekst</p>',
                                                                 'tags': ['telmekom', 'test', 'showTag', 'abc', 'Abc',
                                                                          'ABc']
                                                                 }, expected_status_code=200)
        self.assertIn('id', r)
        _id_post2 = r['id']

        _id_group = 4
        self.assertNotEqual(_id_post1, _id_group)
        self.assertNotEqual(_id_post2, _id_group)
        r = self.api(token_user, 'GET', '/api/wiki/posts/group/{}'.format(_id_group), expected_status_code=200)
        self.assertIn('posts', r)
        self.assertEqual(len(r['posts']), 0)

        r = self.api(token_user, 'PUT', '/api/wiki/posts', body={'title': 'neki tamo naslov',
                                                                 'body': '<p>tekst</p>',
                                                                 'tags': ['telmekom', 'test', 'showTag', 'abc', 'Abc',
                                                                          'ABc'],
                                                                 'language': 'rs',
                                                                 'id_group': _id_post1
                                                                 }, expected_status_code=200)
        self.assertIn('id', r)

        r = self.api(token_user, 'PUT', '/api/wiki/posts', body={'title': 'neki tamo naslov',
                                                                 'body': '<p>tekst</p>',
                                                                 'tags': ['telmekom', 'test', 'showTag', 'abc', 'Abc',
                                                                          'ABc'],
                                                                 'language': 'de',
                                                                 'id_group': _id_post1
                                                                 }, expected_status_code=200)
        self.assertIn('id', r)

        r = self.api(token_user, 'PUT', '/api/wiki/posts', body={'title': 'neki tamo naslov',
                                                                 'body': '<p>tekst</p>',
                                                                 'tags': ['telmekom', 'test', 'showTag', 'abc', 'Abc',
                                                                          'ABc'],
                                                                 'language': 'de',
                                                                 'id_group': _id_post2
                                                                 }, expected_status_code=200)
        self.assertIn('id', r)

        r = self.api(token_user, 'GET', '/api/wiki/posts/group/{}'.format(_id_post1), expected_status_code=200)
        self.assertIn('posts', r)
        self.assertEqual(len(r['posts']), 3)

        r = self.api(token_user, 'GET', '/api/wiki/posts/group/{}'.format(_id_post2), expected_status_code=200)
        self.assertIn('posts', r)
        self.assertEqual(len(r['posts']), 2)


class TestBlog(TestBlogBase):

    def test_0(self):
        id_user, token_user = self.reg('test@knowledge-base.com', '123', {'first_name': 'test',
                                                                          'last_name': 'user',
                                                                          'data': '{}',
                                                                          'role_flags': 1})

        r = self.api(token_user, 'PUT', '/api/wiki/posts', body={'title': 'neki tamo naslov',
                                                                 'body': '<p>tekst</p>',
                                                                 'tags': ['telmekom', 'test', 'showTag', 'abc', 'Abc',
                                                                          'ABc']
                                                                 }, expected_status_code=200)
        self.assertTrue('id' in r)
        _id = r['id']

        r = self.api(token_user, 'PUT', '/api/wiki/posts/{}/files'.format(_id),
                     body={'filename': 'doc.doc', 'local_name': '3fd75bac-62a9-4eaa-b087-06a5e1ca096c.doc'},
                     expected_status_code=200)
        self.api(token_user, 'PUT', '/api/wiki/posts/{}/files'.format(_id),
                 body={'filename': 'pera.xls', 'local_name': '3fd75bac-62a9-4eaa-b087-06a5e1ca096c.xls'},
                 expected_status_code=200)
        self.api(token_user, 'PUT', '/api/wiki/posts/{}/files'.format(_id),
                 body={'filename': 'zika.doc', 'local_name': '3fd75bac-62a9-4eaa-b087-06a5e1ca096c.doc'},
                 expected_status_code=200)
        self.api(token_user, 'PUT', '/api/wiki/posts/{}/files'.format(_id),
                 body={'filename': 'arhiva.zip', 'local_name': '3fd75bac-62a9-4eaa-b087-06a5e1ca096c.zip'},
                 expected_status_code=200)

        r = self.api(token_user, 'PATCH', '/api/wiki/posts/{}'.format(_id),
                     body={'title': 'Izmenjen naslov',
                           'body': '<p>izmenjen tekst</p>',
                           },
                     expected_status_code=200)
        self.assertTrue('changed' in r and ['title', 'body'] == r['changed'])

        r = self.api(token_user, 'PATCH', '/api/wiki/posts/{}'.format(_id),
                     body={'title': 'Finalni naslov',
                           'body': '<p>tekst finalnog naslova</p>',
                           'tags': ['novi', 'tag']
                           }, expected_status_code=200)
        self.assertTrue('changed' in r and ['title', 'body', 'tags'] == r['changed'])

        r = self.api(token_user, 'GET', '/api/wiki/posts/{}'.format(_id), expected_status_code=200)
        self.assertTrue('title' in r and r['title'] == 'Finalni naslov')

        r = self.api(token_user, 'GET', '/api/wiki/posts/tagged_with/{}'.format('showTag'), expected_status_code=200)
        self.assertTrue('posts' in r and r['posts'] == [])

        r = self.api(token_user, 'GET', '/api/wiki/posts/tagged_with/{}'.format('novi'), expected_status_code=200)
        self.assertTrue('posts' in r and r['posts'] != [] and len(r['posts']) == 1)

        r = self.api(token_user, 'GET', '/api/wiki/posts/{}/files'.format(_id), expected_status_code=200)
        self.assertTrue('files' in r and r['files'] != [] and len(r['files']) == 4)

        self.api(token_user, 'PATCH', '/api/wiki/posts/{}/files'.format(_id), body={
            'file_names':
                [{'filename': 'arhiva2.zip', 'local_name': '3fd75bac-62a9-4eaa-b087-06a5e1ca096c.zip'},
                 {'filename': 'pera2.xls', 'local_name': '3fd75bac-62a9-4eaa-b087-06a5e1ca096c.zip'},
                 {'filename': 'arhiva2.zip', 'local_name': '3fd75bac-62a9-4eaa-b087-06a5e1ca096c.zip'},
                 {'filename': 'zika2.doc', 'local_name': '3fd75bac-62a9-4eaa-b087-06a5e1ca096c.zip'}]

        }, expected_status_code=200)
        r = self.api(token_user, 'GET', '/api/wiki/posts/{}/files'.format(_id), expected_status_code=200)
        self.assertTrue('files' in r and r['files'] != [] and len(r['files']) == 8)

        r = self.api(token_user, 'PUT', '/api/wiki/posts/{}/authorized/comments'.format(_id),
                     body={
                         'text': 'my comment'
                     }, expected_status_code=200)

        id_comment = r['id']

        for i in range(1, 5):
            r = self.api(token_user, 'PUT', '/api/wiki/posts/{}/authorized/comments'.format(_id),
                         body={
                             'text': 'reply to my comment ({})'.format(i),
                             'id_parent_comment': id_comment
                         }, expected_status_code=200)

        id_comment = r['id']

        r = self.api(token_user, 'PUT', '/api/wiki/posts/{}/authorized/comments'.format(_id),
                     body={
                         'text': 'reply re to my comment',
                         'id_parent_comment': id_comment
                     }, expected_status_code=200)

        r = self.api(None, 'PUT', '/api/wiki/posts/{}/comments'.format(_id),
                     body={
                         'text': 'unauthorized comment'
                     }, expected_status_code=200)

        id_comment = r['id']

        for i in range(1, 4):
            r = self.api(None, 'PUT', '/api/wiki/posts/{}/comments'.format(_id),
                         body={
                             'text': 're unauthorized comment ({})'.format(i),
                             'email': 'igor@digitalcube.rs',
                             'id_parent_comment': id_comment
                         }, expected_status_code=200)
            id_comment = r['id']

        r = self.api(None, 'GET', '/api/wiki/posts/{}/comments?canonical=false'.format(_id), expected_status_code=200)

        # print(json.dumps(r,indent=4))

        r = self.api(None, 'GET', '/api/wiki/posts/{}/comments?canonical=true'.format(_id), expected_status_code=200)

        # print(json.dumps(r,indent=4))

        self.api(token_user, 'PUT', '/api/wiki/posts',
                 body=
                 {'title': 'Take a look at the production version of the PAL-V Liberty flying car',
                  'body': '''<p>Flying cars aren’t as out of reach as you might think – the PAL-V Liberty, for instance, is a real physical thing you can see and touch at the Geneva Motor Show in Switzerland. The production version of the aerocar is on display for the first time ever at the show, and we got a chance to take a look.</p><p>The PAL-V Liberty looks like more car than aircraft, though it feels like something that you might expect to find at a super specialist racing circuit, rather than on the road. The narrow body features two side-by-side seats up front, a tricycle design and a rotor which unfolds mounted on top for the flying bit of the equation.</p><p>The car features a dual engine design, using one for road and one for doing through the air, and it’s actually based on a classic style of aircraft design, called a ‘gyroplane’ which is a proven way of navigating the skies. The PAL-V Liberty is also actually certified to fly under the rules of both the EASA in Europe and the FAA in the U.S., and complies with road safety regulations, too.</p><p>You’ll still need a pilot’s license to fly the PAL-V Liberty, and it needs a small airfield or airstrip to take off and land. It converts from flying to driving mode and vice versa in between five to 10 minutes, however, so as long as you have the room it won’t take you long to go between modes.</p><p>Pricing for the PAL-V starts at $400,000, so aside from being qualified you’ll also need considerable bank to participate. The company hopes to e able to begin handing over keys to its first pre-order customers in 2019, once all its certifications are complete.</p>''',
                  'datetime': '2017-01-15 10:00:00',
                  'source': 'https://techcrunch.com/2018/03/06/honda-intends-to-actually-put-its-retro-urban-ev-concept-on-sale-in-2019/',
                  'tags': ['flying car', 'flying', 'car', 'future', 'blog']
                  },
                 expected_status_code=200)

        self.api(token_user, 'PUT', '/api/wiki/posts',
                 body=
                 {'title': '''Volkswagen's I.D. Vizzion electric sedan aims for 2022 production''',
                  'subtitle': '''Test subtitle ''',
                  'body': '''<p>Honda’s adorable little Urban EV Concept stole hearts at last year’s Frankfurt Motor Show, and at the Geneva Motor Show this week, the automaker confirmed that it’s making a production version of the car, with a target street date of late 2019 for the cute little guy, though it’ll be a European exclusive at first.<p>The Honda Urban EV concept features a two-door, four-seat design, and a look that evokes virtual pets more than maybe automobiles. It’s a natural fit for the European market, where its quirky styling and maximum use of minimum space are a good fit for street conditions and use cases.<p>We still don’t know the target range fo the vehicle or its final design, but hopefully Honda doesn’t stray far from the concept when it comes time to produce the car. Why mess with perfection?''',
                  'slug': 'honda-intends-to-actually-put-its-retro-urban-ev-concept-on-sale-in-2019',
                  'datetime': '2017-03-02 11:00:00',
                  'source': 'https://techcrunch.com/2018/03/06/volkswagens-i-d-vizzion-electric-sedan-aims-for-2022-production/',
                  'tags': ['car', 'Volkswagen', 'electric', 'sedan', '2022']
                  },
                 expected_status_code=200)

        self.api(token_user, 'PUT', '/api/wiki/posts',
                 body=
                 {'title': '''Honda intends to actually put its retro Urban EV concept on sale in 2019''',
                  'body': '''<p>Volkswagen’s big centerpiece for this year’s Geneva Motor Show is the I.D. Vizzion, the latest in its I.D. EV lineup and the car that’s designed to lead the pack as a premium offering. Volkswagen talked a lot about the Vizzion’s future-focused design and features yesterday during a special pre-show press unveiling, but on Tuesday it also detailed some more realistic near-term goals for the Vizzion, including a target 2022 production date.</p><p>The sedan, which combines ample interior space with a Passat-style exterior footprint, will eventually come in a version without any physical steering wheel or pedals, according to Volkswagen, but the 2022 version will feature a more traditional cockpit since Level 5 autonomy in the way envisioned by VW in its concept video for this car likely isn’t feasible until at least 2030.</p><p>The Vizzion is a very attractive and contemporary sedan in terms of design, however, so it makes sense that the company would be looking to put it on the street before full autonomy and a fully control-free cockpit is a practical reality. The car just plain looks like something you want to drive now, and something to draw the eye of any potential Tesla Model X buyers.</p><p>It’s based on Volkswagen’s modular MEB platform, which will provide the baes for all of its I.D. lineup, including the Crozz and the Buzz microbus. The MEB is also the future of electric cars from other brands in the Volkswagen Group, like Skokda, which is also showing off some of its future EV designs at Geneva. Central to the MEB is the flat, under floor ‘skateboard deck’-style battery, which can be paired up with a variety of drive options.</p><p>In the case of the Vizzion, the MEB features a dual motor design with a 200 HP equivalent one on the rear axle and a 100 HP version on the front for over 300 HP combined. It’s definitely a car that seems like it would appeal to drivers in the family way who also want to have a good time when on the road.</p>''',
                  'slug': 'volkswagens-i-d-vizzion-electric-sedan-aims-for-2022-production',
                  'datetime': '2017-03-02 12:00:00',
                  'source': 'https://techcrunch.com/2018/03/06/volkswagens-i-d-vizzion-electric-sedan-aims-for-2022-production/',
                  'tags': ['car', 'Honda', 'Geneva', '2019'],
                  'category': 'Bussines Blog',

                  },
                 expected_status_code=200)

        self.api(token_user, 'PUT', '/api/wiki/posts',
                 body=
                 {
                     'title': '''UiPath confirms $153M at $1.1B valuation from Accel, CapitalG and KP for its “software robots”''',
                     'body': '''<p>Last week, we reported that UiPath, a startup out of Romania building AI-based services for enterprises in the area of robotic process automation (RPA) — helping businesses automate mundane tasks in back-office IT systems — was about to close a big round, upwards of $120 million at a $1 billion-plus valuation.<p>Today, the company is making it official (and officially bigger): UiPath has raised $153 million in a Series B round that values the company at $1.1 billion — more than ten-fold the company’s valuation when it last raised funding, in April of last year.<p>This latest round was led by previous backer Accel, along with participation from new investors CapitalG (one if Google’s investment vehicles) and Kleiner Perkins Caulfield & Byers, as well as previous investors Earlybird, Credo Ventures and Seedcamp.<p>“We’re putting our money where our mouth is,” Accel partner Rich Wong, who is joining the board, said in an interview. “We wouldn’t have led the Series B after leading the Series A if it wasn’t for that momentum.” He compared the kind of growth that he’s seen at UiPath to that of other successful enterprise startups Accel has backed such as Atlassian, Slack and Qualtrics. “We think UiPath has all the evidence of progress.”<p>UiPath’s valuation isn’t the only thing that has been growing fast. Following a large wave of interest in RPA from the world of enterprise IT, the company has, too.<p>Today, UiPath has over 700 paying enterprise customers, including BMW Group, CenturyLink, Dentsu Inc. and Huawei. That customer list represents a seven-fold increase over last year, and UiPath said that its annual recurring revenues are up eightfold in the same period.<p>Although the startup itself cash-flow positive, the reason for raising more money was to seize the RPA opportunity, and essentially to upsize its startup infrastructure, to offer the kinds of services that enterprises need when they work with companies.<p>“Every large enterprise is doing something with RPA,” said co-founder and CEO Daniel Dines in an interview. “We need to be close to them and building with our customers. But it’s a delicate time. When a lot of programs are starting up, there is a lot of confusion in the market. So we want to build a great presence next to them, with strong customer success teams and account management teams.”<p>RPA taps an interesting moment in the state of enterprise IT today: there is a lot of legacy and new software that requires multiple steps to work both on its own and with other software. Solutions such as those being built by UiPath addresses that issue: it creates AI-based systems — “robots” — that do the busywork of those tasks, freeing up employees’ time to focus on work that AI systems and software cannot do: for example give reasoned assessments of invoices and other forms before they are processed.<p>There are obvious questions you can ask about this field: will RPA become so advanced at some point that the humans will not be needed? Will software become AI-savvy enough that RPA will not be needed? These are issues for the future, but in UiPath’s view, not questions that will have solutions any time soon.<p>Funding, Dines added, will also be used to continue building its products. UiPath’s roadmap already includes a lot of AI and cognitive developments that it plans to roll out as fast as it can. Up to now, the company has been working on a two-month release cycle. “This year we will bring innovations faster than in the past,” he said.<p>On top of this, expect to see more solutions from UiPath that gradually bring in front-office tasks, too. Some of that has already been in evidence: last week, the company released its first solutions for customer care agents.<p>“One of our strengths is the combination of assisted and unassisted,” Dines said. “Our idea is to have a robot for every employee, working side by side on the same computer in assisted automation. We see this as a compelling proposition to many of our customers, having both back office and front office.” He said that the company plans to announce “in the next couple of weeks” a “really huge implementation” at a US business that will specifically be solving both.''',
                     'slug': 'uipath-confirms-153m-at-1-1b-valuation-from-accel-capitalg-and-kp-for-its-software-robots',
                     'datetime': '2017-03-02 13:00:00',
                     'source': 'https://techcrunch.com/2018/03/06/uipath-confirms-153m-at-1-1b-valuation-from-accel-capitalg-and-kp-for-its-software-robots/',
                     'tags': ['Romania', 'Accell', 'CapitalG', 'robots'],
                     'category': 'Bussines Blog',
                 },
                 expected_status_code=200)

        self.api(token_user, 'PUT', '/api/wiki/posts',
                 body=
                 {
                     'title': '''Blockchain company Centrifuge wants every business to get paid on time''',
                     'body': '''<p>The co-founders behind Centrifuge have previously created an essential company with Taulia. Now, they want to do it again, but on the blockchain.<p>Taulia is a supply-chain financing company. It has raised over $150 million and moves billions of dollars per day. 97 out of the Fortune 100 companies use it to improve liquidity when it comes to accounts payable.<p>Let’s say you’re a big industrial company and you have a client that represents 50 percent of your revenue. If you want to meet your client’s deadline and manufacture everything on time, you need to start producing right now.<p>But chances are this client is going to pay your invoice in 30 or 60 days. If you want to get the money now, you currently use Taulia to finance your production. Of course, you’ll end up paying interests, but you can buy supplies right now.<p>Centrifuge wants to take this one step further using blockchain technologies. The company plans to build an open-source protocol that uses the Ethereum blockchain as well as private sidechains, a marketplace of products and its own apps.<p>The company raised $3.8 million led by Mosaic Ventures and BlueYard Capital. “We anticipate to release the first version of the protocol in about four months,” co-founder Maex Ament told me.<p>Shortly after that, Centrifuge will release its first app based on its protocol. And the first one will be a decentralized funding marketplace. Companies can automatically push out their their unpaid invoices to Centrifuge. Banks or alternative lenders can provide liquidity to those companies using Centrifuge.<p>Building this on a blockchain makes a ton of sense because everybody can check transactions on a blockchain. It’s an open protocol with smart contracts to trigger transactions.<p>Eventually, you can imagine other services that leverage the Centrifuge graph. Companies could provide credit insurance, currency exchange and more on top of the Centrifuge protocol.''',
                     'slug': 'blockchain-company-centrifuge-wants-every-business-to-get-paid-on-time',
                     'datetime': '2017-12-01 11:00:00',
                     'source': 'https://techcrunch.com/2018/03/06/blockchain-company-centrifuge-wants-every-business-to-get-paid-on-time/',
                     'tags': ['Blockchain', 'Software', 'Bussines'],
                     'category': 'Private Blog',
                 },
                 expected_status_code=200)

        tags = self.api(token_user, 'GET', '/api/wiki/tags', expected_status_code=200)
        self.assertEqual(len(tags['tags']), 25)

        categories = self.api(token_user, 'GET', '/api/wiki/categories', expected_status_code=200)
        self.assertEqual(len(categories['categories']), 2)


class TestFilesUpload(TestBlogBase):

    def test_upload_file(self):
        self._register('test@knowledge-base.com', '123', {'first_name': 'test',
                                                          'last_name': 'user',
                                                          'data': '{}',
                                                          'role_flags': 1})

        r = self.api(self.token, 'PUT', '/api/wiki/posts', body={'title': 'neki tamo naslov',
                                                                 'body': '<p>tekst</p>',
                                                                 'tags': ['telmekom', 'test', 'showTag', 'abc', 'Abc',
                                                                          'ABc']
                                                                 }, expected_status_code=200)
        self.assertTrue('id' in r)
        _id = r['id']

        # create a boundary
        boundary = 'SomeRandomBoundary'
        boundary_enc = 'SomeRandomBoundary'.encode()

        # set the Content-Type header
        headers = {
            'Authorization': self.token,
            'Content-Type': 'multipart/form-data; boundary=%s' % boundary
        }

        # create the body

        # opening boundary
        body = b'--%s\r\n' % boundary_enc

        # data for field1
        body += b'Content-Disposition: form-data; name="id_post"\r\n'
        body += b'\r\n'  # blank line
        body += b'%s\r\n' % str(_id).encode()

        # separator boundary
        body += b'--%s\r\n' % boundary_enc

        # data for field2
        body += b'Content-Disposition: form-data; name="files[]"; filename="test_file.png"\r\n'
        mtype = mimetypes.guess_type('test_file.png')[0] or 'application/octet-stream'
        body += b'Content-Type: form-data; %s\r\n' % mtype.encode()
        body += b'\r\n'  # blank line

        with open('tests/test_file.png', 'rb') as f:
            body += f.read()

        body += b'\r\n'  # blank line

        # the closing boundary
        body += b"--%s--\r\n" % boundary_enc

        # make a request
        res = self.fetch('/api/posts/files', method='POST', headers=headers, body=body)
        self.assertEqual(res.code, 200)
        r = json.loads(str(res.body, 'utf-8'))

        self.assertIn('result', r)
        self.assertEqual(type(r['result']), list)
        self.assertEqual(len(r['result']), 1)

    def test_upload_few_files(self):
        self._register('test@knowledge-base.com', '123', {'first_name': 'test',
                                                          'last_name': 'user',
                                                          'data': '{}',
                                                          'role_flags': 1})

        r = self.api(self.token, 'PUT', '/api/wiki/posts', body={'title': 'neki tamo naslov',
                                                                 'body': '<p>tekst</p>',
                                                                 'tags': ['telmekom', 'test', 'showTag', 'abc', 'Abc',
                                                                          'ABc']
                                                                 }, expected_status_code=200)
        self.assertTrue('id' in r)
        _id = r['id']

        # create a boundary
        boundary = 'SomeRandomBoundary'
        boundary_enc = 'SomeRandomBoundary'.encode()

        # set the Content-Type header
        headers = {
            'Authorization': self.token,
            'Content-Type': 'multipart/form-data; boundary=%s' % boundary
        }

        # create the body

        # opening boundary
        body = b'--%s\r\n' % boundary_enc

        # data for field1
        body += b'Content-Disposition: form-data; name="id_post"\r\n'
        body += b'\r\n'  # blank line
        body += b'%s\r\n' % str(_id).encode()

        for file in ['test_file.png', 'test_file2.pdf', 'test_file3.txt']:
            # separator boundary
            body += b'--%s\r\n' % boundary_enc

            # data for field2
            body += b'Content-Disposition: form-data; name="files[]"; filename="%s"\r\n' % file.encode()
            mtype = mimetypes.guess_type(file)[0] or 'application/octet-stream'
            body += b'Content-Type: form-data; %s\r\n' % mtype.encode()
            body += b'\r\n'  # blank line

            with open('tests/{}'.format(file), 'rb') as f:
                body += f.read()

            body += b'\r\n'  # blank line

        # the closing boundary
        body += b"--%s--\r\n" % boundary_enc

        # make a request
        res = self.fetch('/api/posts/files', method='POST', headers=headers, body=body)
        self.assertEqual(res.code, 200)
        r = json.loads(str(res.body, 'utf-8'))

        self.assertIn('result', r)
        self.assertEqual(type(r['result']), list)
        self.assertEqual(len(r['result']), 3)


class TestUserGetPosts(TestBlogBase):

    def test_user_get_posts(self):
        self._register('test@knowledge-base.com', '123', {'first_name': 'test',
                                                          'last_name': 'user',
                                                          'data': '{}',
                                                          'role_flags': 1})

        r = self.api(self.token, 'GET', '/api/wiki/posts', expected_status_code=200)
        self.assertIn('posts', r)
        self.assertEqual(len(r['posts']), 0)

        r = self.api(self.token, 'PUT', '/api/wiki/posts', body={'title': 'neki tamo naslov',
                                                                 'body': '<p>tekst</p>',
                                                                 'tags': ['telmekom', 'test', 'showTag', 'abc', 'Abc',
                                                                          'ABc']
                                                                 }, expected_status_code=200)
        self.assertTrue('id' in r)

        r = self.api(self.token, 'GET', '/api/wiki/posts', expected_status_code=200)
        self.assertIn('posts', r)
        self.assertEqual(len(r['posts']), 1)

        for x in range(3):
            r = self.api(self.token, 'PUT', '/api/wiki/posts', body={'title': 'neki tamo naslov',
                                                                     'body': '<p>tekst</p>',
                                                                     'tags': ['telmekom', 'test', 'showTag', 'abc',
                                                                              'Abc', 'ABc']
                                                                     }, expected_status_code=200)
            self.assertTrue('id' in r)

        r = self.api(self.token, 'GET', '/api/wiki/posts', expected_status_code=200)
        self.assertIn('posts', r)
        self.assertEqual(len(r['posts']), 4)


class TestPostMeta(TestBlogBase):

    def test_add_post_with_damaged_meta_html(self):
        id_user, token_user = self.reg('test@knowledge-base.com', '123', {'first_name': 'test',
                                                                          'last_name': 'user',
                                                                          'data': '{}',
                                                                          'role_flags': 1})

        r = self.api(token_user, 'PUT', '/api/wiki/posts', body={'title': 'neki tamo naslov',
                                                                 'body': '<p>tekst</p>',
                                                                 'tags': ['telmekom', 'test', 'showTag', 'abc', 'Abc',
                                                                          'ABc'],
                                                                 'html_meta': 'dummy'
                                                                 }, expected_status_code=400)
        self.assertIn('message', r)
        self.assertEqual(r['message'], rmsgs.lmap[rmsgs.INVALID_REQUEST_ARGUMENT])

    def test_add_post_with_meta_html(self):
        id_user, token_user = self.reg('test@knowledge-base.com', '123', {'first_name': 'test',
                                                                          'last_name': 'user',
                                                                          'data': '{}',
                                                                          'role_flags': 1})

        r = self.api(token_user, 'PUT', '/api/wiki/posts', body={'title': 'neki tamo naslov',
                                                                 'body': '<p>tekst</p>',
                                                                 'tags': ['telmekom', 'test', 'showTag', 'abc', 'Abc',
                                                                          'ABc'],
                                                                 'html_meta': json.dumps('<h1>test html</h1>')
                                                                 }, expected_status_code=200)
        self.assertIn('id', r)
        _id = r['id']

        r = self.api(token_user, 'GET', '/api/wiki/posts/{}'.format(_id), expected_status_code=200)
        self.assertIn('html_meta', r)
        self.assertNotEqual(r['html_meta'], '')
        self.assertEqual(json.loads(r['html_meta']), '<h1>test html</h1>')

