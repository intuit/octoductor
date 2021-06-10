import { expect as expectCDK, haveResource } from '@aws-cdk/assert';
import * as cdk from '@aws-cdk/core';
import {Notifier} from "../../lib/evaluation/notifier";
import {CommonInfra} from "../../lib/common-infra";
import {ConfigurationParameters} from "../../lib/configuration-parameters";

test('Notifier', () => {
  const stack = new cdk.Stack()
  const common = new CommonInfra(stack, new ConfigurationParameters(stack))
  new Notifier(stack, 'MyTestStack', common);
    // THEN
  expectCDK(stack).to(haveResource('AWS::Lambda::Function', {
    MemorySize: 128
  }));
});