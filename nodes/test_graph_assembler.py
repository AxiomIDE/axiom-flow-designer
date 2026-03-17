from nodes.graph_assembler import graph_assembler


def test_graph_assembler_imports():
    assert callable(graph_assembler)
