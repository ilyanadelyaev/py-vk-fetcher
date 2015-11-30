import datetime


def create_tables(cur):
    cur.execute("""CREATE TABLE IF NOT EXISTS person
    -- base information
    (
        id int primary key,  -- vk idNNN
        login char(50),  -- login if presents

        name char(120),  -- full name
        first_name char(60),
        second_name char(60),
        nick char(60),

        gender char(1),  -- m - male / f - female
        family_status char(4),

        birth_day char(5),  -- MM-DD
        birth_date char(10),  -- YYYY-MM-DD

        current_city char(30),

        subscribers_count int,
        friends_count int,
        subscribed_to_count int
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS birthday_place
    -- birthday plases. "Moscow, Russia" for example are 2 records in table
    (
        -- why not forein key?
        person_id int,  -- vk idNNN
        place char(30)  -- city or country or something
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS account
    -- account tech information
    (
        person_id int,  -- vk idNNN
        public_access char(3),  -- allowed / disallowed
        profile_state char(3), -- verified / active / deactivated / deleted / banned
        created char(40),  -- ISO8601 datetime
        last_logged_id char(40),  -- ISO8601 datetime
        modified char(40),  -- ISO8601 datetime
        fetched char(40)  -- ISO8601 datetime
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS contact
    -- urls, phones and other contacts
    -- sometimes "web" is garbage
    (
        person_id int,  -- vk idNNN
        type char(4),  -- phone / skype / web-page / profile
        data char(50),
        valid bool  -- valid / invalid or null
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS education
    (
        person_id int,  -- vk idNNN

        type char(3), -- school / university

        start_date char(7),  -- YYYY-MM
        end_date char(7),  -- YYYY-MM

        place_city char(30),
        place_county char(30),

        title char(50),
        caption char(50),
        short_caption char(50),
        sub_caption char(50),
        form char(50),
        status char(50)
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS career
    (
        person_id int,  -- vk idNNN

        type char(3), -- job / military

        start_date char(4),  -- YYYY
        end_date char(4),  -- YYYY

        place_city char(30),
        place_county char(30),

        title char(50),
        position char(50)
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS misc
    -- some unsorted information
    (
        person_id int,  -- vk idNNN
        data text  -- some non-sorted information. bio, interests, mood message or something
    )""")


def add_record(cur, obj):
    obj = obj['Person']
    if 'URI' not in obj:
        return
    id = _add_person(cur, obj)
    _add_birthday_places(cur, id, obj)
    _add_account(cur, id, obj)
    _add_contacts(cur, id, obj)
    _add_education(cur, id, obj)
    _add_career(cur, id, obj)
    _add_misc(cur, id, obj)


def _add_person(cur, obj):
    id = None
    login = None
    for u in obj['URI']:
        if u.get('primary') == 'yes':
            id = int(u['resource'].split('/')[-1][2:])
        else:
            login = u['resource'].split('/')[-1]

    gender = obj.get('gender', '')[:1] or None
    family_status = obj.get('familyStatus', '')[:4] or None

    cur.execute(u"""INSERT INTO person VALUES (
        ?, ?,
        ?, ?, ?, ?,
        ?, ?,
        ?, ?,
        ?,
        ?, ?, ?
    )""", (
        id, login,
        obj.get('name'), obj.get('firstName'), obj.get('secondName'), obj.get('nick'),
        gender, family_status,
        obj.get('birthday'), obj.get('dateOfBirth'),
        obj.get('location', {}).get('city'),
        obj.get('subscribersCount'),
        obj.get('friendsCount'),
        obj.get('subscribedToCount'),
    ))

    return id


def _add_birthday_places(cur, id, obj):
    for p in obj.get('locationOfBirth', []):
        if p.get('city'):
            cur.execute(u"""INSERT INTO birthday_place VALUES (
                ?,
                ?
            )""", (
                id,
                p.get('city'),
            ))


def _add_account(cur, id, obj):
    public_access = obj.get('publicAccess', '')[:3] or None
    profile_state = obj.get('profileState', '')[:3] or None
    cur.execute(u"""INSERT INTO account VALUES (
        ?,
        ?, ?,
        ?, ?, ?,
        ?
    )""", (
        id,
        public_access, profile_state,
        obj.get('created', {}).get('date'),
        obj.get('lastLoggedIn', {}).get('date'),
        obj.get('modified', {}).get('date'),
        str(datetime.datetime.now()),
    ))


def _add_contacts(cur, id, obj):
    for p in obj.get('externalProfile', []):
        cur.execute(u"""INSERT INTO contact VALUES (
            ?,
            ?,
            ?,
            ?
        )""", (
            id,
            'prof',
            p.get('resource'),
            p.get('status') == 'validated',
        ))
    if obj.get('skypeID'):
        cur.execute(u"""INSERT INTO contact VALUES (
            ?,
            ?,
            ?,
            ?
        )""", (
            id,
            'skyp',
            obj.get('skypeID'),
            None,
        ))
    for p in obj.get('phone', []):
        cur.execute(u"""INSERT INTO contact VALUES (
            ?,
            ?,
            ?,
            ?
        )""", (
            id,
            'phon',
            p.get('___text___'),
            None,
        ))

    if obj.get('homepage'):
        cur.execute(u"""INSERT INTO contact VALUES (
            ?,
            ?,
            ?,
            ?
        )""", (
            id,
            'web',
            obj.get('homepage'),
            None,
        ))


def _add_education(cur, id, obj):
    if not obj.get('edu'):
        return
    for k, v in obj.get('edu').iteritems():
        k = k[:3]
        for vv in v:
            cur.execute(u"""INSERT INTO education VALUES (
                ?,
                ?,
                ?, ?,
                ?, ?,
                ?,
                ?, ?, ?,
                ?, ?
            )""", (
                id,
                k,
                vv.get('dateStart'), vv.get('dateFinish'),
                vv.get('location', {}).get('city'), vv.get('location', {}).get('country'),
                vv.get('title'),
                vv.get('caption'), vv.get('shortCaption'), vv.get('subCaption'),
                vv.get('form'),
                vv.get('status'),
            ))


def _add_career(cur, id, obj):
    if not obj.get('job'):
        return
    for k, v in obj.get('job').iteritems():
        if k == 'workPlace':
            k = 'job'
        k = k[:3]
        for vv in v:
            cur.execute(u"""INSERT INTO career VALUES (
                ?,
                ?,
                ?, ?,
                ?, ?,
                ?, ?
            )""", (
                id,
                k,
                vv.get('dateStart'), vv.get('dateFinish'),
                vv.get('location', {}).get('city'), vv.get('location', {}).get('country'),
                vv.get('title'), vv.get('position'),
            ))


def _add_misc(cur, id, obj):
    if obj.get('interest'):
        cur.execute(u"""INSERT INTO misc VALUES (
            ?,
            ?
        )""", (
            id,
            obj.get('interest'),
        ))
    if obj.get('weblog'):
        cur.execute(u"""INSERT INTO misc VALUES (
            ?,
            ?
        )""", (
            id,
            obj.get('weblog', {}).get('title'),
        ))
    if obj.get('bio'):
        cur.execute(u"""INSERT INTO misc VALUES (
            ?,
            ?
        )""", (
            id,
            obj.get('bio'),
        ))
