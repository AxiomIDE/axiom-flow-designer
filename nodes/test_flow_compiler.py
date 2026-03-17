from nodes.flow_compiler import flow_compiler


def test_flow_compiler_imports():
    assert callable(flow_compiler)
