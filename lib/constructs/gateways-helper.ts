import { ILambda } from "../model/i-lambda";
import { StateMachine} from '@aws-cdk/aws-stepfunctions';
import { Role } from '@aws-cdk/aws-iam';
import { LambdaIntegration, RestApi, IRestApi, AwsIntegration, PassthroughBehavior, EmptyModel } from "@aws-cdk/aws-apigateway";

export function setLambdaEndpoints(api: IRestApi, integrations: ILambda[]) {

    integrations.forEach( (lambda: ILambda) => {
        const method = lambda.httpMethod
        const resource = api.root.addResource(lambda.endpointName);
        const integration = new LambdaIntegration(lambda, {
            requestTemplates: { "application/json": '{ "statusCode": "200" }' }
        });
        if (!(["POST", 'GET', 'DELETE', 'ANY'].includes(method))) {
            throw new Error('REST method provided for ' + lambda.functionName + ' is not POST, GET, DELETE, or ANY. Please check method provided.')
        }
        resource.addMethod(method, integration);
    });

}

export function setStepFunctionEndpoint(api: RestApi, stateMachine: StateMachine, endpointName: string, apiRole: Role) {    
    stateMachine.grantStartExecution(apiRole);
    
    const integration = new AwsIntegration({
        service: 'states',
        action: 'StartExecution',
        options: {
          credentialsRole: apiRole,
          requestTemplates: {
              'application/json': JSON.stringify({
                      stateMachineArn: stateMachine.stateMachineArn,
                      input: "$util.escapeJavaScript($input.json('$'))"
                  })
          },
          passthroughBehavior: PassthroughBehavior.NEVER,
          integrationResponses: [
            {
                selectionPattern: '200',
                statusCode: '200',
                // Consider hiding execution ARN for security reasons.
                responseTemplates: {
                  'application/json': JSON.stringify({
                    executionToken: "$util.parseJson($input.json('$')).executionArn.split(':')[7]"
                  })
                }
            }
          ]
        }
    });
    
    const res = api.root.addResource(endpointName);
    
    res.addMethod('POST', integration, {
        methodResponses: [
            {
                statusCode: '200',
                responseModels: {'application/json': new EmptyModel()}
            }]
    });
}