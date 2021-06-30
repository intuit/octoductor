import { join }  from 'path';
import { Construct, Duration } from '@aws-cdk/core';
import { PythonFunction } from '@aws-cdk/aws-lambda-python'
import { SubnetType } from "@aws-cdk/aws-ec2";
import { CommonInfra } from "../common-infra";
import {CommonLayerSingleton} from "../common-layer";

export class Badge extends PythonFunction {

  constructor(scope: Construct, id: string, common: CommonInfra, memorySize: number = 512, duration: Duration = Duration.seconds(600)) {
    super(scope, id, {
      entry:  join(__dirname, '..', '..', 'octoductor', 'scoring', 'badge_generator'),
      memorySize: memorySize,
      timeout: duration,
      vpc: common.params.vpc,
      layers: [CommonLayerSingleton.getInstance(scope).getLayer()],
      vpcSubnets: { subnetType: SubnetType.PRIVATE },
      securityGroup: common.securityGroup,
      environment: {
        BUCKET: common.octoductorBucket.bucketName
      }
    });
    common.octoductorBucket.grantPut(this);
    common.octoductorBucket.grantWrite(this);
  }
}
