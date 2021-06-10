import { expect as expectCDK, haveResource } from '@aws-cdk/assert';
import * as cdk from '@aws-cdk/core';
import { Vpc, SecurityGroup } from '@aws-cdk/aws-ec2';
import { HttpNamespace } from "@aws-cdk/aws-servicediscovery";
import { Onboarding } from "../../lib/onboarding/onboarding";

test('Onboarding', () => {
  const stack = new cdk.Stack()
  const vpc = new Vpc(stack, 'TheVPC')
  const securityGroup = SecurityGroup.fromSecurityGroupId(stack, 'SG', 'sg-12345');
  const namespace = new HttpNamespace(stack, 'Namespace', {
    name: 'octoductor-dev'
  });
  new Onboarding(stack, 'MyTestStack', namespace, vpc, securityGroup);
    // THEN
  expectCDK(stack).to(haveResource('AWS::Lambda::Function', {
    MemorySize: 128
  }));
});