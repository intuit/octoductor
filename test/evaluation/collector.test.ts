import { expect as expectCDK, haveResource } from '@aws-cdk/assert';
import * as cdk from '@aws-cdk/core';
import {CollectorFunction} from "../../lib/evaluation/collector";
import {CommonInfra} from "../../lib/common-infra";
import {ConfigurationParameters} from "../../lib/configuration-parameters";

test('CollectorFunction', () => {
  const stack = new cdk.Stack()
  const common = new CommonInfra(stack, new ConfigurationParameters(stack))
  new CollectorFunction(stack, 'MyTestStack', common);
    // THEN
  expectCDK(stack).to(haveResource('AWS::Lambda::Function', {
    MemorySize: 512
  }));
});