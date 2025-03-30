from __future__ import annotations

from pathlib import Path
from typing import Generic, Iterable, Protocol, Type, TypeVar

from msgspec import Struct
from msgspec.json import encode, decode
from msgspec.inspect import type_info, IntType, BoolType, StrType, StructType
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

from utils.auth_context import AuthContext
from utils.text_casing import to_kebab_case

class TypescriptImport(Struct):
    path: str
    symbols: list[str]

class TypescriptFetchMethod(Struct):
    input: str
    output: str
    route: str
    name: str

class TypescriptInterface(Struct):
    name: str
    attributes: list[tuple[str, str]]

class TypescriptFile(Struct):
    path: Path
    imports: list[TypescriptImport]
    fetch_methods: list[TypescriptFetchMethod]
    interfaces: list
    


InputStructType = TypeVar("InputStructType", bound=Struct, contravariant=True)
OutputStructType = TypeVar("OutputStructType", bound=Struct, covariant=True)

class RPC(Protocol, Generic[InputStructType, OutputStructType]):
    __name__: str
    async def __call__(self, auth: AuthContext, input: InputStructType) -> OutputStructType: ...

class RpcRouter:
    def __init__(self, app_name: str, routes: list[RPC]):
        assert app_name == to_kebab_case(app_name), f"'{app_name}' expected to be kebab-case ('{to_kebab_case(app_name)}')"
        self.app_name = app_name
        self.rpc_dict: dict[str, RPC] = {}
        for r in routes:
            self.rpc_dict[r.__name__] = r

    def get_path_name(self, func_name: str) -> str:
        return f"/rpc/{self.app_name}/{to_kebab_case(func_name)}"


    def get_handler(self, func_name: str):
        func = self.rpc_dict[func_name]

        async def wrapper(request: Request) -> Response:
            body = await request.body()
            if not body:
                return Response("Bad Request", 401)

            input_struct = func.__annotations__["input"]
            input = decode(body, type=input_struct)
            auth = AuthContext(request)
            output = await func(auth=auth, input=input)
            return Response(encode(output))

        return wrapper
    
    def get_routes(self) -> Iterable[Route]:
        for func_name in self.rpc_dict:
            yield Route(self.get_path_name(func_name), self.get_handler(func_name), methods=["POST"])

    def get_ts_file(self, func_name: str) -> TypescriptFile:
        project_root = Path(__file__).parent.parent.parent
        output_path = project_root / "rpc" / self.app_name / f"{func_name}.ts"
        return TypescriptFile(
            path=output_path,
            imports=[
                TypescriptImport(
                    path="asdf",
                    symbols=["getVar", "testTest"]
                )
            ],
            fetch_methods=[
                TypescriptFetchMethod(
                    input="MyInput",
                    output="MyOutput",
                    route="/rpc/app/test",
                    name="test",
                )
            ],
            interfaces=[
                TypescriptInterface(
                    name="MyInterface",
                    attributes=[
                        ("foo", "bar"),
                        ("hello", "world"),
                    ]
                )
            ],
        )

    def write(self):
        project_root = Path(__file__).parent.parent.parent
        output_path = project_root / "rpc"
        output_path.mkdir(exist_ok=True)

        for func_name in self.rpc_dict:
            ts_file = self.get_ts_file(func_name)
            ts_file.path.parent.mkdir(exist_ok=True)

            with open(ts_file.path, 'w') as f:
                # Write imports
                for impt in ts_file.imports:
                    f.write(self.get_ts_import_str(impt))

                f.write("\n")

                # Write fetch methods
                for fetcher in ts_file.fetch_methods:
                    f.write(self.get_ts_fetch_str(fetcher))

                f.write("\n")

                # Write interfaces
                for interface in ts_file.interfaces:
                    f.write(self.get_ts_interface_str(interface))

    def get_ts_import_str(self, importStmt: TypescriptImport) -> str:
        return f"""
import {{ {", ".join(importStmt.symbols)} }} from "{importStmt.path}";
"""
    
    def get_ts_fetch_str(self, fetcher: TypescriptFetchMethod) -> str:
        return f"""
export function {fetcher.name}(input: {fetcher.input}): Promise<{fetcher.output}> {{
  return fetch("{fetcher.route}", {{
    method: "POST",
    body: JSON.stringify(input),
  }}).then((res) => res.json());
}}
"""

    def get_ts_interface_str(self, interface: TypescriptInterface) -> str:
        return f"""
export interface {interface.name} {{
  {"\n  ".join([f"{x[0]}: {x[1]};" for x in interface.attributes])}
}};
"""

    
def convert_struct(struct: Type[Struct]) -> str:
    temp = []
    print(type_info(struct))
    struct_type_info: StructType = type_info(struct) # type: ignore
    for f in struct_type_info.fields:
        typeName = "unknown"
        print(f.type, f.type.__class__ is IntType)
        if f.type.__class__ is IntType:
            typeName = "number"
        elif f.type.__class__ is StrType:
            typeName = "string"
        elif f.type.__class__ is BoolType:
            typeName = "boolean"
        elif f.type.__class__ is StructType:
            typeName = f.type.cls.__name__

        temp.append(f"  {f.name}{"" if f.required else "?"}: {typeName};")
    temp.sort()
    print(temp)
    return "\n".join([
        f"interface {struct.__name__}" + " {",
        *temp,
    "};"])
