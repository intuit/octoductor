import { GlobalSecurityGroup } from "./constructs/security-group";
import { S3Bucket } from "./constructs/s3-bucket";
import { HttpNamespace } from "@aws-cdk/aws-servicediscovery"
import { Construct, RemovalPolicy } from '@aws-cdk/core';
import { ILogGroup, LogGroup, RetentionDays } from "@aws-cdk/aws-logs";
import { ConfigurationParameters } from "./configuration-parameters";
import { IBucket } from "@aws-cdk/aws-s3";
import { ISecurityGroup } from "@aws-cdk/aws-ec2";

export class CommonInfra {
    readonly octoductorBucket: IBucket;
    readonly securityGroup: ISecurityGroup;
    readonly logGroup: ILogGroup;
    readonly namespace: HttpNamespace;

    constructor(readonly scope: Construct, readonly params: ConfigurationParameters) {
        this.octoductorBucket = new S3Bucket(scope, 's3-bucket', 'octoductor-' + params.env);
        this.securityGroup = new GlobalSecurityGroup(scope, 'global-sg', params.vpc);
        this.logGroup = new LogGroup(scope, "octoductor-log-group", {
            logGroupName: '/octoductor-' + params.env,
            removalPolicy: RemovalPolicy.DESTROY,
            retention: RetentionDays.ONE_WEEK
        });
        this.namespace = new HttpNamespace(scope, 'namespace', {
            name: 'octoductor-' + params.env
        });
    }
}
