import { expect as expectCDK, haveResource, MatchStyle } from '@aws-cdk/assert';
import * as cdk from '@aws-cdk/core';
import { Data } from '../../lib/data/data';

test('Data API', () => {
  // WHEN
  const stack = new cdk.Stack()
  // const lambda = new Data(stack, 'MyTestStack');
  // THEN
  // expectCDK(stack).to(
  //   haveResource("AWS::IAM::Role")
  //     .and(haveResource("AWS::Lambda::Function")))
});
