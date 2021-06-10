import { join }  from 'path';
import {Construct, Duration} from '@aws-cdk/core';
import { PythonFunction } from '@aws-cdk/aws-lambda-python'
import {ISecurityGroup, IVpc, SubnetType} from "@aws-cdk/aws-ec2";
import { INamespace } from "@aws-cdk/aws-servicediscovery";
import { PolicyStatement } from "@aws-cdk/aws-iam";
import { CommonLayerSingleton } from '../common-layer'

export class Onboarding extends PythonFunction {
  constructor(scope: Construct, id: string,
    namespace: INamespace,
    vpc?: IVpc, securityGroup?: ISecurityGroup,
    memorySize: number = 128, duration: Duration = Duration.seconds(5)) {
    super(scope, id, {
      entry:  join(__dirname, '..', '..', 'octoductor', 'onboarding'),
      memorySize: memorySize,
      timeout: duration,
      vpc: vpc,
      environment: {
        NAMESPACE: namespace.namespaceName
      },
      vpcSubnets: { subnetType: SubnetType.PRIVATE },
      layers: [ CommonLayerSingleton.getInstance(scope).getLayer() ],
      securityGroup: securityGroup
    });
    this.role!.addToPrincipalPolicy(new PolicyStatement({
      actions: ['servicediscovery:DiscoverInstances'],
      resources: ['*']
    }));
  }
}
