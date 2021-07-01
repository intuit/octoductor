import { Stack, Construct, StackProps } from "@aws-cdk/core";
import { LambdaIntegration } from "@aws-cdk/aws-apigateway";
import { Role, ServicePrincipal } from '@aws-cdk/aws-iam';
import { BucketDeployment, Source } from '@aws-cdk/aws-s3-deployment'
import { LambdaInvoke } from '@aws-cdk/aws-stepfunctions-tasks';

import { join } from 'path';
import { CommonInfra } from "../common-infra";
import { HealthCheck } from "../constructs/health-check";
import { PublicGateway } from "../constructs/public-gateway";
import { setStepFunctionEndpoint } from "../constructs/gateways-helper";
import { ConfigurationParameters } from "../configuration-parameters";
import { GitHub } from "../onboarding/github";
import { Onboarding } from "../onboarding/onboarding";
import { OnboardingStateMachine } from "../onboarding/onboarding-workflow";
import { EvaluationFlow, PythonEvaluatorGenerator } from "../evaluation/evaluation-flow";
import { SlackConvo } from "../evaluation/slack-convo";

export class OctoductorStack extends Stack {
  constructor(scope?: Construct, id?: string, props?: StackProps) {
    super(scope, id, props);
    const common = new CommonInfra(this, new ConfigurationParameters(this))

    const slackConvo = new SlackConvo(this, common);
    const onboarding = new Onboarding(this, 'onboarding', common.namespace, common.params.vpc, common.securityGroup);
    const health = new HealthCheck(this, 'health', common.params.vpc, common.securityGroup);
    // Gateways and Lambda integrations

    const publicGW = new PublicGateway(this, 'public-api', [], common.params.env, common.params.domain, common.params.hostedZone, common.logGroup);
    health.register(publicGW.root);

    const github = new GitHub(this, 'github', common.namespace, common.params.githubSecret, common.params.vpc, common.securityGroup)
    publicGW.root.addResource("github").addProxy({
      defaultIntegration: new LambdaIntegration(github),
      anyMethod: true
    });

    // Step function workflows
    // TODO: add resultPath: JsonPath.DISCARD to pass input payload through to next step in workflow
    const pushToDataApi = new LambdaInvoke(this, 'push-to-data-api', {
      lambdaFunction: onboarding
    });

    const confirm = new LambdaInvoke(this, 'slack-message', {
      inputPath: "$.Payload",
      lambdaFunction: slackConvo
    });

    const onboardingWorkflow = pushToDataApi.next(confirm);
    const onboardingStateMachine = new OnboardingStateMachine(this, common.logGroup, common.params.env, onboardingWorkflow);

    const apiRole = new Role(this, 'GatewayRole', {
      roleName: 'GatewayStartExecutionRole-' + common.params.env,
      assumedBy: new ServicePrincipal('apigateway.amazonaws.com')
    });
    setStepFunctionEndpoint(publicGW, onboardingStateMachine, 'onboarding-workflow', apiRole);


    const generator = new PythonEvaluatorGenerator(this, common.params, common.namespace, common.octoductorBucket);

    
    setStepFunctionEndpoint(publicGW, new EvaluationFlow(this, common, [
      generator.evaluator('sample-one'),
      generator.evaluator('sample-two')
    ]), 'evaluation', apiRole);
  }
}
