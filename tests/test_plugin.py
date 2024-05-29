import subprocess

from pytest_kind.cluster import _DEFAULT_KUBECTL_VERSION


def test_kind_cluster(testdir):
    k8s_version_tuple = ("1", "30")
    testdir.makepyfile(
        f"""
    import socket

    def test_cluster_api(kind_cluster):
        assert kind_cluster.api.version == {k8s_version_tuple!r}

    def test_kubectl_version(kind_cluster):
        assert "{_DEFAULT_KUBECTL_VERSION}" in kind_cluster.kubectl("version")

    def test_load_docker_image(kind_cluster):
        kind_cluster.load_docker_image("busybox")

    def test_port_forward(kind_cluster):
        kind_cluster.kubectl("rollout", "status", "deploy/coredns", "-n", "kube-system")

        # high number of retries as pod is pending for a while..
        with kind_cluster.port_forward("service/kube-dns", 53, "-n", "kube-system", retries=20) as port:
            assert port >= 1024
            s = socket.socket()
            try:
                s.connect(('127.0.0.1', port))
            finally:
                s.close()
    """
    )

    subprocess.run(["docker", "pull", "busybox"], check=True)

    result = testdir.runpytest("--cluster-name", "pytest-kind-test-plugin")
    result.assert_outcomes(passed=4)
