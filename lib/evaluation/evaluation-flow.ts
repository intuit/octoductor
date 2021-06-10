import { join } from 'path';
import { IBucket } from "@aws-cdk/aws-s3";
import { Runtime } from "@aws-cdk/aws-lambda"
import { PolicyStatement } from "@aws-cdk/aws-iam";
import { Construct, Duration } from "@aws-cdk/core";
import { IVpc, SubnetType } from "@aws-cdk/aws-ec2";
import { PythonFunction } from "@aws-cdk/aws-lambda-python";
import { INamespace } from "@aws-cdk/aws-servicediscovery"
import { LambdaInvoke } from "@aws-cdk/aws-stepfunctions-tasks";
import { StateMachine, Parallel } from "@aws-cdk/aws-stepfunctions";
import { ConfigurationParameters} from "../configuration-parameters";

import { Badge } from "./badge";
import { Notifier } from "./notifier";
import { CollectorFunction } from './collector';
import { ScoreGenerator } from "./score-generator";
import { CommonInfra } from "../common-infra";
import { CommonLayerSingleton } from '../common-layer';

class Relay extends LambdaInvoke {
    constructor(scope: Construct, id: string, vpc: IVpc) {
        super(scope, id + 'Invocation', {
            lambdaFunction: new PythonFunction(scope, id, {
                entry: join(__dirname, '..', '..', 'octoductor', 'scoring', 'relay'),
                vpc: vpc,
                vpcSubnets: { subnetType: SubnetType.PRIVATE },
                layers: [CommonLayerSingleton.getInstance(scope).getLayer()],
                timeout: Duration.minutes(1)
            })
        })
    }
}

class Collector extends LambdaInvoke {
    constructor(scope: Construct, id: string, common: CommonInfra) {
        super(scope, id + 'Invocation', {
            lambdaFunction: new CollectorFunction(scope, id, common),
            inputPath: "$.*.Payload",
        });
    }
}

class Scoring extends LambdaInvoke {
    constructor(scope: Construct, id: string, common: CommonInfra) {
        super(scope, id + 'Invocation', {
            lambdaFunction: new ScoreGenerator(scope, id, common),
            inputPath: "$.Payload",
        });
    }
}

class BadgeGenerator extends LambdaInvoke {
    constructor(scope: Construct, id: string, common: CommonInfra) {
        super(scope, id + 'Invocation', {
            lambdaFunction: new Badge(scope, id, common),
            inputPath: "$.Payload",
        });
    }
}

class Notification extends LambdaInvoke {
    constructor(scope: Construct, id: string, common: CommonInfra) {
        super(scope, id + 'Invocation', {
            lambdaFunction: new Notifier(scope, id, common),
            inputPath: "$.Payload",
        });
    }
}

export class PythonEvaluatorGenerator {
    readonly lambdaEnv: { [key: string]: string; }
    
    constructor(readonly scope: Construct, readonly params: ConfigurationParameters, readonly namespace: INamespace, readonly bucket: IBucket) {
        this.lambdaEnv = {
            NAMESPACE: namespace.namespaceName,
            GITHUB_SECRET: params.githubSecret.secretArn,
            GITHUB_DOMAIN: params.githubDomain,
            APPLICATION_ID: params.githubAppId,
            S3_BUCKET: bucket.bucketName,
        }
    }

    public evaluator(name: string): PythonEvaluator {
        const environment = { ...this.lambdaEnv, REQUIREMENT: name }
        const lambda = new PythonEvaluator(this.scope, name, this.params.vpc, environment)
        this.params.githubSecret.grantRead(lambda.role!)
        this.bucket.grantReadWrite(lambda.role!)
        return lambda
    }
}

export class PythonEvaluator extends PythonFunction {
    constructor(readonly scope: Construct, readonly name: string, readonly vpc: IVpc, readonly lambdaEnv: { [key: string]: string; } = {}) {
        super(scope, name, {
            entry: join(__dirname, '..', '..', 'octoductor', 'scoring', name),
            vpc: vpc,
            vpcSubnets: { subnetType: SubnetType.PRIVATE },
            environment: lambdaEnv,
            runtime: Runtime.PYTHON_3_7,
            layers: [CommonLayerSingleton.getInstance(scope).getLayer()],
            timeout: Duration.minutes(1)
        });

        this.role!.addToPrincipalPolicy(new PolicyStatement({
            actions: ['servicediscovery:DiscoverInstances'],
            resources: ['*']
        }));
    }
}

export class EvaluationFlow extends StateMachine {
    constructor(scope: Construct, common: CommonInfra, evaluators: PythonEvaluator[]) {
        let evaluations = new Parallel(scope, 'octoductor Evaluations');
        for (let e of evaluators) {
            evaluations.branch(EvaluationFlow.evaluator(e));
        }
        super(scope, 'evaluation', {
            definition:
                new Relay(scope, 'relay', common.params.vpc)
                    .next(evaluations)
                    .next(new Collector(scope, 'collector', common))
                    .next(new Scoring(scope, 'score-generator', common))
                    .next(new BadgeGenerator(scope, 'badge', common))
                    .next(new Notification(scope, 'notification', common)),
            timeout: Duration.minutes(5)
        });
    }

    private static evaluator(func: PythonEvaluator): LambdaInvoke {
        return new LambdaInvoke(func.scope, func.name + 'Invocation', {
            lambdaFunction: func,
            inputPath: "$.Payload"
        })
    }
}
