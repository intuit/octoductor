import { expect as expectCDK, haveResource } from '@aws-cdk/assert';
import * as cdk from '@aws-cdk/core';
import {Badge} from "../../lib/evaluation/badge";
import {CommonInfra} from "../../lib/common-infra";
import {ConfigurationParameters} from "../../lib/configuration-parameters";

test('Badge', () => {
  const stack = new cdk.Stack()
  const common = new CommonInfra(stack, new ConfigurationParameters(stack))
  new Badge(stack, 'MyTestStack', common);
    // THEN
  expectCDK(stack).to(haveResource('AWS::Lambda::Function', {
    MemorySize: 512
  }));
});