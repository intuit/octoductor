import { expect as expectCDK, haveResource } from '@aws-cdk/assert';
import * as cdk from '@aws-cdk/core';
import {ScoreGenerator} from "../../lib/evaluation/score-generator";
import {CommonInfra} from "../../lib/common-infra";
import {ConfigurationParameters} from "../../lib/configuration-parameters";

test('ScoreGenerator', () => {
  const stack = new cdk.Stack()
  const common = new CommonInfra(stack, new ConfigurationParameters(stack))
  new ScoreGenerator(stack, 'MyTestStack', common);
    // THEN
  expectCDK(stack).to(haveResource('AWS::Lambda::Function', {
    MemorySize: 512
  }));
});