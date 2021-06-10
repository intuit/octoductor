import { join }  from 'path';
import { Construct, Duration} from '@aws-cdk/core';
import { PythonFunction } from '@aws-cdk/aws-lambda-python'
import { SubnetType } from "@aws-cdk/aws-ec2";
import * as iam from '@aws-cdk/aws-iam';
import { CommonLayerSingleton } from "../common-layer";
import { CommonInfra } from "../common-infra";

export class Notifier extends PythonFunction {

  constructor(scope: Construct, id: string, common: CommonInfra, memorySize: number = 128, duration: Duration = Duration.seconds(300)) {
    super(scope, id, {
      entry:  join(__dirname, '..', '..', 'octoductor', 'scoring', 'notifier'),
      memorySize: memorySize,
      timeout: duration,
      vpc: common.params.vpc,
      layers: [CommonLayerSingleton.getInstance(scope).getLayer()],
      vpcSubnets: { subnetType: SubnetType.PRIVATE },
      securityGroup: common.securityGroup,
      environment: {
        NAMESPACE: common.namespace.namespaceName
      }
    });

    this.role!.addToPrincipalPolicy(new iam.PolicyStatement({
      actions: ['servicediscovery:DiscoverInstances'],
      resources: ['*']
    }));
  }
}
