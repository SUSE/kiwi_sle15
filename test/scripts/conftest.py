from pytest_container import auto_container_parametrize, DerivedContainer


FUNCTIONS_COPY_CONTAINERFILE = """COPY kiwi/config/functions.sh /bin/functions.sh
"""


CONTAINERS = [
    DerivedContainer(base=url, containerfile=FUNCTIONS_COPY_CONTAINERFILE)
    for url in [
        "registry.opensuse.org/opensuse/leap:15.3",
        "registry.opensuse.org/opensuse/leap:15.2",
        "registry.opensuse.org/opensuse/tumbleweed:latest",
        "registry.suse.com/suse/sle15:15.3",
        "registry.suse.com/suse/sle15:15.2",
        "registry.suse.com/suse/sle15:15.1",
        "registry.suse.com/suse/sles12sp5:latest",
        "quay.io/centos/centos:stream8",
    ]
]

(
    LEAP_15_3,
    LEAP_15_2,
    TUMBLEWEED,
    SLE_15_SP3,
    SLE_15_SP2,
    SLE_15_SP1,
    SLE_12_SP5,
    CENTOS_STREAM_8,
) = CONTAINERS


def pytest_generate_tests(metafunc):
    auto_container_parametrize(metafunc)
