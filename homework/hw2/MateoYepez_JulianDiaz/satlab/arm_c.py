"""Direct answer, with schema-only production detection."""
from .prompts import initial
from .arm_b import inspect_response


def run(public: dict, client, repeat: int, timeout: float) -> dict:
    return inspect_response(public,client.call(initial(public,'C'),public['id'],'C',repeat,0),timeout,direct=True)
