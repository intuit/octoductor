import { join } from 'path';
import { Construct, Duration } from '@aws-cdk/core';
import { PythonFunction } from '@aws-cdk/aws-lambda-python'
import { SubnetType } from "@aws-cdk/aws-ec2";
import { ILambda } from "../model/i-lambda";
import { CommonInfra } from "../common-infra";

export class SlackConvo extends PythonFunction implements ILambda {
  endpointName: string = 'slackconvo';
  httpMethod: string = 'POST';

  constructor(scope: Construct, common: CommonInfra, memorySize: number = 128, duration: Duration = Duration.seconds(5)) {
    super(scope, 'slackconvo', {
      entry: join(__dirname, '..', '..', 'octoductor', 'slack', 'convo'),
      memorySize: memorySize,
      timeout: duration,
      vpc: common.params.vpc,
      environment: {
        SLACK_BOT_TOKEN_ARN: common.params.slackSecret.secretArn
      },
      vpcSubnets: { subnetType: SubnetType.PRIVATE },
      securityGroup: common.securityGroup
    });
    common.params.slackSecret.grantRead(this.role!)
  }
}
