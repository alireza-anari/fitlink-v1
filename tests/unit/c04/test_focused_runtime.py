import importlib
import importlib.util


def test_focused_runtime_never_exports_unrestricted_child_output():
    name = "docker.c04_task07_focused"
    assert importlib.util.find_spec(name), "Missing real focused storage harness"
    module = importlib.import_module(name)
    value = module.sanitized_results(
        'private-sentinel\nC04_REQUIRED_COUNTS {"counts":{"passed":1,"failed":0,'
        '"error":0,"skipped":0,"xfailed":0,"xpassed":0,"deselected":0},"exit_code":0}\n'
    )
    assert "private-sentinel" not in value
    assert "C04_REQUIRED_COUNTS" in value


def test_focused_runtime_rejects_forged_metadata_payload():
    name = "docker.c04_task07_focused"
    assert importlib.util.find_spec(name), "Missing real focused storage harness"
    module = importlib.import_module(name)
    assert "private-sentinel" not in module.sanitized_results(
        'C04_REQUIRED_COUNTS {"secret":"private-sentinel"}\n'
    )
