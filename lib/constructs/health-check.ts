import { Construct } from '@aws-cdk/core';
import { ISecurityGroup, IVpc, SubnetType } from "@aws-cdk/aws-ec2";
import { Function, Code, Runtime } from '@aws-cdk/aws-lambda';
import { LambdaIntegration, IResource} from "@aws-cdk/aws-apigateway";

export class HealthCheck extends Function {

  constructor(scope: Construct, id: string, vpc?: IVpc, securityGroup?: ISecurityGroup) {
    super(scope, id, {
      code: Code.fromInline(`
import json
def handler(event, context):
    print("Event: %s" % json.dumps(event))
    context_serializable = {k:v for k, v in context.__dict__.items() if type(v) in [int, float, bool, str, list, dict]}
    body = {
        "context": context_serializable,
        "input": event
    };
    
    response = {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": json.dumps(body, indent=4),
    }
    return response;      
      `),
      vpc: vpc,
      vpcSubnets: { subnetType: SubnetType.PRIVATE },
      securityGroup: securityGroup,
      runtime: Runtime.PYTHON_3_7,
      handler: 'index.handler'
    });
  }

  public register(root: IResource): IResource {
    const resource = root.addResource('health');
    const integration = new LambdaIntegration(this, {
        requestTemplates: { "application/json": '{ "statusCode": "200" }' }
    });
    resource.addMethod('GET', integration);
    return resource;
  }
}
