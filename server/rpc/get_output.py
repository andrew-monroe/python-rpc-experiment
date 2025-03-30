
from typing import TYPE_CHECKING
from msgspec import Struct
from rpc.structs.pre_input import PreInput

if TYPE_CHECKING:
    from utils.auth_context import AuthContext


class Input(PreInput):
    bar: str
    myOption: bool = False

class Output(Struct):
    hello: int
    world: str

async def get_output(auth: "AuthContext", input: Input) -> Output:
    print(auth.get_url())
    return Output(
        hello=input.foo,
        world=input.bar,
    )
