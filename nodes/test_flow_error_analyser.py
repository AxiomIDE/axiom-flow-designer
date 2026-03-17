def test_flow_error_analyser_imports():
    import nodes.flow_error_analyser as m
    assert hasattr(m, "handle")
