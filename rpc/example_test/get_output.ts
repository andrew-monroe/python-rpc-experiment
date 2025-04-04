
import { getVar, testTest } from "asdf";


export function test(input: MyInput): Promise<MyOutput> {
  return fetch("/rpc/example-test/get-output", {
    method: "POST",
    body: JSON.stringify(input),
  }).then((res) => res.json());
}


export interface MyInterface {
  foo: bar;
  hello: world;
};
