def test_flow_compiler_imports():
    import nodes.flow_compiler as m
    assert hasattr(m, "handle")
