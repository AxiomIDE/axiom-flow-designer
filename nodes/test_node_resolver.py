from nodes.node_resolver import node_resolver


def test_node_resolver_imports():
    assert callable(node_resolver)
