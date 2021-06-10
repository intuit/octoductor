import { expect as expectCDK, haveResource } from '@aws-cdk/assert';
import * as cdk from '@aws-cdk/core';
import { Vpc, SecurityGroup } from '@aws-cdk/aws-ec2';
import { LogGroup, RetentionDays } from "@aws-cdk/aws-logs";
import { Pass } from "@aws-cdk/aws-stepfunctions";
import { OnboardingStateMachine } from '../../lib/onboarding/onboarding-workflow';

test('OnboardingWorkflow', () => {
  const stack = new cdk.Stack()
  const vpc = new Vpc(stack, 'TheVPC')
  const logGroup = new LogGroup(stack, "OctoLogGroup", {
    logGroupName: '/test'
  });
  const pass1 = new Pass(stack, 'pass1');
  const pass2 = new Pass(stack, 'pass2');
  const def = pass1.next(pass2)

  new OnboardingStateMachine(stack, logGroup, 'test', def);
    // THEN
  expectCDK(stack).to(haveResource('AWS::StepFunctions::StateMachine'));
});