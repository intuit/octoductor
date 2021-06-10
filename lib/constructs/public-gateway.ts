import { DomainNameOptions, EndpointType, LogGroupLogDestination, MethodLoggingLevel, RestApi } from "@aws-cdk/aws-apigateway";
import { Construct } from '@aws-cdk/core';
import { ILogGroup } from "@aws-cdk/aws-logs";
import { ILambda } from "../model/i-lambda";
import { setLambdaEndpoints } from "./gateways-helper";
import { RecordTarget, ARecord, IHostedZone } from '@aws-cdk/aws-route53';
import * as alias from "@aws-cdk/aws-route53-targets";

export class PublicGateway extends RestApi {
    constructor(scope: Construct, id: string, integrations: ILambda[], environment: string, domain: DomainNameOptions, zone: IHostedZone, logGroup: ILogGroup) {
        super(scope, id, {
            restApiName: "PublicApi",
            description: "This service handles external interactions",
            cloudWatchRole: true,
            deploy: true,
            deployOptions: {
                cacheClusterEnabled: false,
                cachingEnabled: false,
                loggingLevel: MethodLoggingLevel.ERROR,
                accessLogDestination: new LogGroupLogDestination(logGroup),
                stageName: 'octoductor'
            },
            endpointConfiguration: {
                types: [EndpointType.REGIONAL]
            },
            domainName: domain
        });

        new ARecord(this, 'PublicDnsARecord', {
            zone: zone,
            recordName: environment,
            target: RecordTarget.fromAlias(new alias.ApiGateway(this))
        });

        setLambdaEndpoints(this, integrations);
    }
}
