def test_flow_test_invoker_imports():
    import nodes.flow_test_invoker as m
    assert hasattr(m, "handle")
