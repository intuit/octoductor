import {
  expect as expectCDK,
  matchTemplate,
  haveResource,
  MatchStyle,
} from "@aws-cdk/assert";
import * as CdkAgi from "../lib/deployment/cdk-stack";

test("Empty Stack", () => {

  // // WHEN
  // const stack = new CdkAgi.OctoductorStack();
  // // THEN

  // expectCDK(stack).to(haveResource('AWS::Lambda::Function', {
  //   MemorySize: 128
  // }));

  // expectCDK(stack).to(
  //   matchTemplate(
  //     {
  //       Resources: {},
  //     },
  //     MatchStyle.EXACT
  //   )
  // );
});
