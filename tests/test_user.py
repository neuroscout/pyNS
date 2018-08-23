def test_user(recorder, neuroscout):
    with recorder.use_cassette('user'):
        resp = neuroscout.user.get()

        assert '@' in resp['email']
