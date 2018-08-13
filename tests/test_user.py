def test_user(recorder, neuroscout):
    with recorder.use_cassette('user'):
        resp = neuroscout.user.get()
        assert resp.status_code == 200

        profile = resp.json()
        assert '@' in profile['email']
