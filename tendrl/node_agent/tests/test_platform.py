from tendrl.node_agent.persistence import platform


class TestPlatform(object):
    def test_platform(self):
        self.obj = platform.Platform(
            node_id="1234-123-12-12343",
            os="centos",
            os_version="7.0",
            kernel_version="1.1"
        )
        self.obj.render() == [
            {'dir': False,
             'value': '1.1',
             'name': 'kernel_version',
             'key': '/nodes/1234-123-12-12343/Platform//kernel_version'
             },
            {'dir': False,
             'value': '1234-123-12-12343',
             'name': 'node_id',
             'key': '/nodes/1234-123-12-12343/Platform//node_id'
             },
            {'dir': False,
             'value': 'centos',
             'name': 'os',
             'key': '/nodes/1234-123-12-12343/Platform//os'
             },
            {'dir': False,
             'value': '7.0',
             'name': 'os_version',
             'key': '/nodes/1234-123-12-12343/Platform//os_version'
             }]
