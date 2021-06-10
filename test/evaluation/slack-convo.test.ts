import { expect as expectCDK, haveResource } from '@aws-cdk/assert';
import * as cdk from '@aws-cdk/core';
import {SlackConvo} from "../../lib/evaluation/slack-convo";
import {CommonInfra} from "../../lib/common-infra";
import {ConfigurationParameters} from "../../lib/configuration-parameters";

test('SlackConvo', () => {
  const stack = new cdk.Stack()
  const common = new CommonInfra(stack, new ConfigurationParameters(stack))
  new SlackConvo(stack, common);
    // THEN
  expectCDK(stack).to(haveResource('AWS::Lambda::Function', {
    MemorySize: 128
  }));
});